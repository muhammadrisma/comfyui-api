from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to execute database queries
def execute_query(query, params=None):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        if 'conn' in locals():
            conn.close()

# Helper function to generate image stream
def generate_image_stream(results):
    for idx, row in enumerate(results):
        yield f"--boundary\r\n"
        yield f"Content-Type: image/png\r\n"
        yield f"Content-Disposition: inline; filename=image_{idx}.png\r\n\r\n"
        yield row['image_data']
        yield b"\r\n"
    yield "--boundary--\r\n"

# GET all images for a client based on client_id
@app.get("/images/{client_id}")
def get_images_by_client_id(client_id: str):
    query = """
        SELECT image_data
        FROM generated_images
        WHERE client_id = %s
    """
    results = execute_query(query, (client_id,))
    
    if not results:
        raise HTTPException(status_code=404, detail="No images found for client_id")
    
    return StreamingResponse(generate_image_stream(results), media_type="multipart/x-mixed-replace; boundary=boundary")

# GET all images for a client based on client_id and prompt_id
@app.get("/images/{client_id}/{prompt_id}")
def get_images_by_client_and_prompt(client_id: str, prompt_id: str):
    query = """
        SELECT image_data
        FROM generated_images
        WHERE client_id = %s AND prompt_id = %s
    """
    results = execute_query(query, (client_id, prompt_id))
    
    if not results:
        raise HTTPException(status_code=404, detail="No images found for the given client_id and prompt_id")
    
    return StreamingResponse(generate_image_stream(results), media_type="multipart/x-mixed-replace; boundary=boundary")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
