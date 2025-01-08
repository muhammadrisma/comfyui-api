
import os
import uuid
import json
import random
import logging
import psycopg2
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
from db_config import DB_CONFIG
from websockets_api import get_prompt_images
from fastapi.staticfiles import StaticFiles
# Load environment variables
load_dotenv()

SERVER_ADDRESS = os.getenv("SERVER_ADDRESS") 
COMFY_UI_PATH = os.getenv("COMFY_UI_PATH")
RESULTS_PATH = os.getenv("RESULTS_PATH")
CLOTH_SWAP_WORKFLOW = os.getenv("CLOTH_SWAP_WORKFLOW")
EXPRESSION_WORKFLOW = os.getenv("EXPRESSION_WORKFLOW")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/results", StaticFiles(directory=RESULTS_PATH), name="results")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to save an input image
def save_image(uploaded_file: UploadFile) -> str:
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = Path(COMFY_UI_PATH) / "input"
    input_path.mkdir(parents=True, exist_ok=True)
    file_name = f"img_{timestamp}_{unique_id}.jpg"
    file_path = input_path / file_name

    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.file.read())
    except Exception as e:
        logger.error(f"Error saving image {file_name}: {e}")
        raise HTTPException(status_code=500, detail="Error saving image.")

    return str(file_path)

# Helper function to execute database queries
def execute_query(query: str, params: tuple = ()) -> list:
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")

# Generic function to construct image response
def construct_image_response(results) -> list:
    return [
        {
            "url": f"http://{SERVER_ADDRESS}/images/{row['id']}",
            "file_size": row["file_size"],
            "file_type": row["file_type"],
            "upload_time": row["upload_time"].isoformat(),
            "prompt_id": row.get("prompt_id"),
            "client_id": row.get("client_id")
        }
        for row in results
    ]

# Endpoint for cloth swapping
@app.post("/cloth-swap/")
async def cloth_swap(
    input_image: UploadFile = File(...),
    ref_image: UploadFile = File(...),
    top_clothes: bool = False,
    bottom_clothes: bool = False,
    torso_skin: bool = False,
    left_arm: bool = False,
    right_arm: bool = False,
    left_leg: bool = False,
    right_leg: bool = False,
):
    try:
        with open(CLOTH_SWAP_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        prompt["1"]["inputs"]["seed"] = random.randint(0, 999999999999999)
        prompt["13"]["inputs"].update({
            "top_clothes": top_clothes,
            "bottom_clothes": bottom_clothes,
            "torso_skin": torso_skin,
            "left_arm": left_arm,
            "right_arm": right_arm,
            "left_leg": left_leg,
            "right_leg": right_leg
        })

        prompt["17"]["inputs"]["image"] = save_image(input_image)
        prompt["18"]["inputs"]["image"] = save_image(ref_image)

        images = get_prompt_images(prompt)
        return {"success": True, "images": images}

    except Exception as e:
        logger.error(f"Cloth swap error: {e}")
        raise HTTPException(status_code=500, detail="Cloth swap processing failed.")

# Endpoint for expression editing
@app.post("/expression-edit/")
async def expression_edit(
    input_image: UploadFile = File(...),
    rotate_pitch: float = 0,
    rotate_yaw: float = 0,
    rotate_roll: float = 0,
    blink: float = 0,
    eyebrow: float = 0,
    wink: float = 0,
    pupil_x: float = 0,
    pupil_y: float = 0,
    aaa: float = 0,
    eee: float = 0,
    woo: float = 0,
    smile: float = 0,
):
    try:
        with open(EXPRESSION_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        prompt["14"]["inputs"].update({
            "rotate_pitch": rotate_pitch,
            "rotate_yaw": rotate_yaw,
            "rotate_roll": rotate_roll,
            "blink": blink,
            "eyebrow": eyebrow,
            "wink": wink,
            "pupil_x": pupil_x,
            "pupil_y": pupil_y,
            "aaa": aaa,
            "eee": eee,
            "woo": woo,
            "smile": smile
        })

        prompt["15"]["inputs"]["image"] = save_image(input_image)

        images = get_prompt_images(prompt)
        return {"success": True, "images": images}

    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

# GET all images for a client based on client_id
# @app.get("/images/{client_id}")
# def get_images_by_client_id(client_id: str):
#     query = """
#         SELECT id, file_size, file_type, upload_time
#         FROM generated_images
#         WHERE client_id = %s
#     """
#     results = execute_query(query, (client_id,))

#     if not results:
#         raise HTTPException(status_code=404, detail="No images found for the given client_id.")

#     images = construct_image_response(results)
    
#     return {
#         "success": True,
#         "images": images,
#         "message": "Images retrieved successfully."
#     }

# GET images by ID
@app.get("/images/{id}")
def get_images_by_id(id: int):
    query = """
        SELECT id, client_id, prompt_id, image_output_path, file_size, file_type, upload_time
        FROM generated_images
        WHERE id = %s
    """
    results = execute_query(query, (id,))

    if not results:
        raise HTTPException(status_code=404, detail="No images found for the given ID.")

    images = []
    for row in results:
        # Modify the image_output_path to use the server URL
        image_url = f"http://{SERVER_ADDRESS}/results/{Path(row['image_output_path']).name}"
        images.append({
            "id": row["id"],
            "client_id": row["client_id"],
            "prompt_id": row["prompt_id"],
            "file_size": row["file_size"],
            "file_type": row["file_type"],
            "upload_time": row["upload_time"],
            "image_url": image_url  # Use the modified URL
        })

    return {"success": True, "images": images, "message": "Images retrieved successfully."}

# GET all images
@app.get("/images")
def get_all_images():
    query = """
        SELECT id, prompt_id, client_id, image_output_path, file_size, file_type, upload_time
        FROM generated_images
    """
    results = execute_query(query)

    if not results:
        raise HTTPException(status_code=404, detail="No images found.")

    images = []
    for row in results:
        # Modify the image_output_path to use the server URL
        image_url = f"http://{SERVER_ADDRESS}/results/{Path(row['image_output_path']).name}"
        images.append({
            "id": row["id"],
            "prompt_id": row["prompt_id"],
            "client_id": row["client_id"],
            "file_size": row["file_size"],
            "file_type": row["file_type"],
            "upload_time": row["upload_time"],
            "image_url": image_url  # Use the modified URL
        })

    return {"success": True, "images": images, "message": "Images retrieved successfully."}

# GET all images for a client based on client_id and prompt_id
# @app.get("/images/{client_id}/{prompt_id}")
# def get_images_by_client_and_prompt(client_id: str, prompt_id: str):
#     query = """
#         SELECT id, file_size, file_type, upload_time
#         FROM generated_images
#         WHERE client_id = %s AND prompt_id = %s
#     """
#     results = execute_query(query, (client_id, prompt_id))

#     if not results:
#         raise HTTPException(status_code=404, detail="No images found for the given client_id and prompt_id.")

#     images = construct_image_response(results)

#     return {
#         "success": True,
#         "images": images,
#         "message": "Images retrieved successfully."
#     }

# @app.get("/images/{image_id}")
# def get_image_by_id(image_id: int):
#     query = """
#         SELECT image_data, file_type
#         FROM generated_images
#         WHERE id = %s
#     """
#     result = execute_query(query, (image_id,))

#     if not result:
#         raise HTTPException(status_code=404, detail="Image not found.")
    
#     image_data = result[0]["image_data"]
#     file_type = result[0]["file_type"]

#     return StreamingResponse(
#         io.BytesIO(image_data),
#         media_type=file_type,
#         headers={"Content-Disposition": f"inline; filename=image_{image_id}.png"},
#     )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
