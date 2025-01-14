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
from db_config import DB_CONFIG
from websockets_api import get_prompt_images
from fastapi.staticfiles import StaticFiles
from settings import COMFY_UI_PATH, RESULTS_PATH, CLOTH_SWAP_WORKFLOW, EXPRESSION_WORKFLOW, CLOTH_BACKGROUND_WORKFLOW, API_ADDRESS, MAKEUP_WORKFLOW, EYEDETAILS_WORKFLOW, EYE_LIP_FACE_WORKFLOW, HAIR_WORKFLOW

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
            "url": f"http://{API_ADDRESS}/images/{row['id']}",
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

        # Save images and handle saving errors in one block
        try:
            prompt["17"]["inputs"]["image"] = save_image(input_image)
            prompt["18"]["inputs"]["image"] = save_image(ref_image)
        except HTTPException as save_exception:
            logger.error(f"Error saving images: {save_exception.detail}")
            raise save_exception

        images = get_prompt_images(prompt)
        return {"success": True, "images": images}

    except json.JSONDecodeError as json_error:
        logger.error(f"Error decoding JSON from workflow file: {json_error}")
        raise HTTPException(status_code=500, detail="Workflow file error.")
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

        # Create a dictionary for inputs to avoid repetitive code
        inputs = {
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
        }

        prompt["14"]["inputs"].update(inputs)

        # Save the image and handle potential errors
        try:
            prompt["15"]["inputs"]["image"] = save_image(input_image)
        except Exception as e:
            logger.error(f"Error saving input image: {e}")
            raise HTTPException(status_code=500, detail="Error saving input image.")

        # get_prompt_images could raise its own errors
        images = get_prompt_images(prompt)
        return {"success": True, "images": images}

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from workflow file: {e}")
        raise HTTPException(status_code=500, detail="Workflow file error.")
    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

# Endpoint for cloth and background replacement
@app.post("/cloth-background")
async def cloth_background(
    input_img: UploadFile = File(...),
    input_img_cloth: UploadFile = File(...),
    input_img_bg: UploadFile = File(...),
    prompt_clothing_type: str = "clothing,"
):
    try:
        # Load the workflow prompt
        with open(CLOTH_BACKGROUND_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Generate a random seed
        prompt["3"]["inputs"]["seed"] = random.randint(0, 999999999999999)

        # Validate prompt clothing type
        final_prompt = prompt_clothing_type.strip() or "clothing, pants"
        if len(final_prompt) > 100:
            logger.error("Prompt clothing type is too long")
            raise HTTPException(status_code=400, detail="Prompt clothing type is too long")

        prompt["6"]["inputs"]["prompt"] = final_prompt

        # Map the input images into the workflow and handle saving
        try:
            prompt["1"]["inputs"]["image"] = save_image(input_img)
            prompt["49"]["inputs"]["image"] = save_image(input_img_cloth)
            prompt["37"]["inputs"]["image"] = save_image(input_img_bg)
        except Exception as e:
            logger.error(f"Error saving one or more images: {e}")
            raise HTTPException(status_code=500, detail="Error saving images.")

        # Process the images and return the result
        images = get_prompt_images(prompt)
        return {"success": True, "images": images}

    except json.JSONDecodeError as e:
        logger.error(f"Error reading workflow file: {e}")
        raise HTTPException(status_code=500, detail="Workflow file error.")
    except Exception as e:
        logger.error(f"Cloth background processing error: {e}")
        raise HTTPException(status_code=500, detail="Cloth background processing failed.")

# Endpoint for makeup editing
@app.post("/makeup-edit/")
async def makeup_edit(
    img: UploadFile = File(...),
    makeup_style: str = "-",
    eyeshadow: bool = False,
    eyeliner: bool = False,
    mascara: bool = False,
    blush : bool = False,
    lipstick: bool = False,
    lip_gloss: bool = False,
    slider: float =0
    ):

    try:
        with open(MAKEUP_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Validate and convert slider value
        try:
            slider_value = float(slider)
        except ValueError:
            raise ValueError(f"Invalid slider value: {slider}. Please provide a number between 0 and 1.")

        # Set dynamic inputs in the workflow
        prompt["13"]["inputs"]["denoise"] = slider_value
        prompt["9"]["inputs"].update({
            "makeup_style": makeup_style,
            "eyeshadow": eyeshadow == "True",
            "eyeliner": eyeliner == "True",
            "mascara": mascara == "True",
            "blush": blush == "True",
            "lipstick": lipstick == "True",
            "lip_gloss": lip_gloss == "True"
        })

        # Save the input image
        prompt["1"]["inputs"]["image"] = save_image(img)

        # Call the image generation function
        images = get_prompt_images(prompt)
        return images

    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

# Endpoint for eye_details
@app.post("/eye_details-edit/")
async def eye_details_edit(
    img: UploadFile = File(...),
    freckles: float = 0,
    eyes_details: float = 0,
    iris_details: float = 0,
    circular_iris: float = 0,
    circular_pupil: float = 0
):
    try:
        with open(EYEDETAILS_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed for reproducibility
        prompt["8"]["inputs"]["seed"] = random.randint(0,999999999999999)
        prompt["5"]["inputs"].update({
            "freckles": freckles =="False",
            "eyes detail": eyes_details =="True",
            "iris detail" : iris_details == "True",
            "circular iris": circular_iris == "True",
            "circular pupil": circular_pupil == "True",
        })
        prompt["1"]["inputs"]["image"] = save_image(img)
        
        images = get_prompt_images(prompt)
        return images

    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

# Endpoint for eye_lip_face editing
@app.post("/eye_lip_face-edit/")
async def eye_lip_face_edit(
    img: UploadFile = File(...),
    eyes_color: bool=True,
    eyes_shape: bool=True,
    lips_color: bool=True,
    lips_shape: bool=True,
    face_shape: bool=True,
    slider: float =0
    ):
    try:
        with open(EYE_LIP_FACE_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed for reproducibility
        prompt["27"]["inputs"]["seed"] = random.randint(0,9999999999999999)
        prompt["27"]["inputs"]["denoise"] = slider
        prompt["21"]["inputs"].update({
            "eyes color": eyes_color =="True",
            "eyes shape" : eyes_shape == "True",
            "lip color": lips_color == "True",
            "lip shape": lips_shape == "True",
            "face shape": face_shape == "True"
        })

        prompt["14"]["inputs"]["image"] = save_image(img)
        
        images = get_prompt_images(prompt)
        return images

    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

@app.post("/hair-edit/")
async def hair_edit(
    img: UploadFile = File(...),
    hair_color: str="-",
    hairstyle: str="-",
    slider: float =0
    ):
    try:
        with open(HAIR_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        prompt["156"]["inputs"]["seed"] = random.randint(0, 99999999999999999)
        
        # Set the hairstyle description
        text2 = f"{hairstyle}, with {hair_color} hair color"

        prompt["228"]["inputs"]["text"] = text2
        prompt["156"]["inputs"]["denoise"] = slider

        prompt["138"]["inputs"]["image"] = save_image(img)

        # Call the function to process the prompt and get the result images
        images = get_prompt_images(prompt)
        return images
    
    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

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
        image_url = f"http://{API_ADDRESS}/results/{Path(row['image_output_path']).name}"
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
        image_url = f"http://{API_ADDRESS}/results/{Path(row['image_output_path']).name}"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)