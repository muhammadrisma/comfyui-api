import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
import random
from PIL import Image
from websockets_api import get_prompt_images
from dotenv import load_dotenv
import urllib.request
from urllib.error import HTTPError, URLError

load_dotenv()
COMFY_UI_PATH = Path(os.getenv("COMFY_UI_PATH"))
EYEDETAILS_WORKFLOW = Path(os.getenv("EYEDETAILS_WORKFLOW"))

def save_input_image(img):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    
    input_dir = Path(COMFY_UI_PATH) / "input"
    input_dir.mkdir(parents=True, exist_ok=True) 

    input_img = input_dir / f"img_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image.save(str(input_img)) 
    
    return input_img.name

def process(img,freckles,eyes_details, iris_details, circular_iris, circular_pupil):
    try:
        with open(EYEDETAILS_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed for reproducibility
        prompt["8"]["inputs"]["seed"] = random.randint(0,999999999999999)
        prompt["5"]["inputs"].update({
            "freckles": freckles =="True",
            "eyes detail": eyes_details =="True",
            "iris detail" : iris_details == "True",
            "circular iris": circular_iris == "True",
            "circular pupil": circular_pupil == "True",
        })
        img_filename = save_input_image(img)

        prompt["1"]["inputs"]["image"] = img_filename
        
        images = get_prompt_images(prompt)
        return images
    
    except HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
        return None
    
    except URLError as e:
        print(f"URLError: {e.reason}")
        return None
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
# Gradio interface for cloth swapping tool
def eyedetails_interface():
    eyedetails = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=1024), 
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=0, label="Freckles:"),
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=0, label="Eye Details:"),
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=0, label="Iris Details:"),
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=0, label="Circular Iris:"),
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=0, label="Circular Pupil:"),
            ],
            outputs=[gr.Gallery(label="Outputs: ", height=500)]
            )

    eyedetails.queue()
    eyedetails.launch()

if __name__ == "__main__":
    eyedetails_interface()