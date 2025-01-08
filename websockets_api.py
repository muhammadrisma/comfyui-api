import os
import io
import json
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
import websocket
import psycopg2
from psycopg2.extras import execute_values 
from PIL import Image
from datetime import datetime

from db_config import DB_CONFIG
from dotenv import load_dotenv
load_dotenv()

SERVER_ADDRESS = os.getenv("SERVER_ADDRESS") 
RESULTS_PATH = os.getenv("RESULTS_PATH")
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return {}

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "type": folder_type}
    if subfolder:
        data["subfolder"] = subfolder
    url_values = urllib.parse.urlencode(data)
    try:
        with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/view?{url_values}") as response:
            return response.read()
    except Exception as e:
        print(f"Error retrieving image: {e}")
        return None

# Get images url
def get_image_url(filename, subfolder, folder_type):
    data = {"filename": filename, "type": folder_type}
    
    # Add 'subfolder' to the data only if it's not None
    if subfolder:
        data["subfolder"] = subfolder
    
    url_values = urllib.parse.urlencode(data)
    url = "http://{}/view?{}".format(SERVER_ADDRESS, url_values)
    return url

def get_history(prompt_id):
    try:
        with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/history/{prompt_id}") as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return {}

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt).get("prompt_id")
    output_images = {}

    while True:
        try:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing" and message["data"].get("node") is None and message["data"].get("prompt_id") == prompt_id:
                    break
        except websocket.WebSocketException as e:
            print(f"WebSocket error: {e}")
            break

    history = get_history(prompt_id).get(prompt_id, {})
    for node_id, node_output in history.get("outputs", {}).items():
        if "images" in node_output:
            images_output = []
            for image in node_output["images"]:
                image_data = get_image(image.get("filename"), image.get("subfolder"), image.get("type"))
                if image_data:
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def save_images_to_db(client_id, prompt_id, images):
    if not images:
        return
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    image_records = []
    
    # Prepare the results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    result_dir = Path(RESULTS_PATH)
    result_dir.mkdir(exist_ok=True)

    try:
        for image in images:
            # Save the image to RESULTS_PATH
            image_output_path = result_dir / f"result_{client_id}_{timestamp}_{unique_id}.png"
            image.save(image_output_path, format="PNG")
            
            # Prepare the image data for database insertion
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_data = image_bytes.getvalue()
            
            image_records.append((
                client_id,
                prompt_id,
                str(image_output_path),
                len(image_data),
                f"image/{image.format.lower()}",
                datetime.utcnow()
            ))
        
        if image_records:
            insert_query = """
            INSERT INTO generated_images (client_id, prompt_id, image_output_path, file_size, file_type, upload_time)
            VALUES %s
            """
            execute_values(cursor, insert_query, image_records)
            conn.commit()
    except Exception as e:
        print(f"An error occurred during database operation: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_prompt_images(prompt):
    ws = websocket.WebSocket()
    try:
        ws.connect(f"ws://{SERVER_ADDRESS}/ws?clientId={client_id}")
        images = get_images(ws, prompt)
        outputs = []
        
        for node_id, image_data_list in images.items():
            for image_data in image_data_list:
                try:
                    image = Image.open(io.BytesIO(image_data))
                    outputs.append(image)
                except Exception as e:
                    print(f"Error processing image for node {node_id}: {e}")

        prompt_id = queue_prompt(prompt).get("prompt_id")
        save_images_to_db(client_id, prompt_id, outputs)
        return outputs
    except Exception as e:
        print(f"Error managing WebSocket connection: {e}")
    finally:
        ws.close()
