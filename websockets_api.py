import os
import io
import json
import urllib.parse
import urllib.request
import uuid
import websocket
import psycopg2
from psycopg2.extras import execute_values 
from PIL import Image

from db_config import DB_CONFIG
from dotenv import load_dotenv
load_dotenv()

SERVER_ADDRESS = "127.0.0.1:8188"

server_address = SERVER_ADDRESS
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "type": folder_type}
    
    # Add 'subfolder' to the data only if it's not None
    if subfolder:
        data["subfolder"] = subfolder
    
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        "http://{}/view?{}".format(server_address, url_values)
    ) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(
        "http://{}/history/{}".format(server_address, prompt_id)
    ) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)["prompt_id"]
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done
        else:
            continue  # Previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for _ in history["outputs"]:
        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            if "images" in node_output:
                images_output = []
                for image in node_output["images"]:
                    try:
                        # Use .get() to safely access keys and handle missing 'subfolder'
                        image_data = get_image(
                            filename=image.get("filename"),
                            subfolder=image.get("subfolder"),  # Might be None
                            folder_type=image.get("type")
                        )
                        images_output.append(image_data)
                    except Exception as e:
                        print(f"Error retrieving image for node {node_id}: {e}")
            else:
                images_output = []

            output_images[node_id] = images_output

    return output_images

def save_images_to_db(client_id, prompt_id, images):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    image_records = [
        (str(client_id), str(prompt_id), io.BytesIO(image.tobytes()).getvalue())
        for image in images
    ]
    
    insert_query = """
        INSERT INTO generated_images (client_id, prompt_id, image_data)
        VALUES %s   
    """
    execute_values(cursor, insert_query, image_records)
    
    conn.commit()
    cursor.close()
    conn.close()
    
def get_prompt_images(prompt):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    outputs = []
    for node_id in images:
        # print(f"Processing node {node_id}...")
        for image_data in images[node_id]:
            try:
                image = Image.open(io.BytesIO(image_data))
                outputs.append(image)
            except Exception as e:
                print(f"Error processing image for node {node_id}: {e}")
    
    ws.close()
    
    # save to db
    prompt_id = queue_prompt(prompt)["prompt_id"]
    save_images_to_db(client_id, prompt_id, outputs)
    return outputs
