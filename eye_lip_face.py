import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
from PIL import Image
import random
from websockets_api import get_prompt_images
from settings import EYE_LIP_FACE_WORKFLOW, COMFY_UI_PATH
from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)

def save_input_image(img):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    
    input_dir = Path(COMFY_UI_PATH) / "input"
    input_dir.mkdir(parents=True, exist_ok=True) 

    input_img = input_dir / f"img_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image.save(str(input_img)) 
    
    return input_img.name

def process(img, eyes_color, eyes_shape, lips_color, lips_shape, face_shape, slider):
    try:
        with open(EYE_LIP_FACE_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed for reproducibility
        prompt["27"]["inputs"]["seed"] = random.randint(0,9999999999999999)
        prompt["21"]["inputs"]["face_shape_weight"] = slider
        prompt["21"]["inputs"].update({
            "eyes color": eyes_color =="True",
            "eyes shape" : eyes_shape == "True",
            "lip color": lips_color == "True",
            "lip shape": lips_shape == "True",
            "face shape": face_shape == "True"
        })
        img_filename = save_input_image(img)

        prompt["14"]["inputs"]["image"] = img_filename
        
        images = get_prompt_images(prompt)
        return images
    
    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

# Gradio interface for cloth swapping tool
def eye_lip_face_interface():
    eye_lip_face = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=1024), 
            gr.Dropdown(value="-", choices=["-", "random 🎲", "Amber", "Blue", "Brown", "Green", "Hazel", "Red"], label="Eyes Color: "),
            gr.Dropdown(value="-", choices=["-", "random 🎲", "Almond Eyes Shape", "Asian Eyes Shape", "Close-Set Eyes Shape","Deep Set Eyes Shape", "Double Eyelid Eyes Shape", "Downturned Eyes Shape","Hooded Eyes Shape", "Monolid Eyes Shape", "Oval Eyes Shape","Protruding Eyes Shape", "Round Eyes Shape", "Upturned Eyes Shape"], label="Eyes Shape: "),
            gr.Dropdown(value="-", choices=["-", "random 🎲", "Berry lips", "Brown Lips", "Burgundy Lips", "Coral Lips", "Glossy Red Lips", "Peach Lips", "Pink Lips", "Plum Lips", "Red Lips"], label="Lip Color: "),
            gr.Dropdown(value="-", choices=["-", "random 🎲", "Biting Lips", "Bow-shaped Lips", "Closed Lips", "Cupid's Bow Lips","Defined Cupid's Bow Lips", "Flat Cupid's Bow Lips", "Full Lips","Heart-shaped Lips", "Large Lips", "Medium Lips", "Neutral Lips","Parted Lips", "Plump Lips", "Pouting Lips", "Round Lips","Small Lips", "Smiling Lips", "Soft Cupid's Bow Lips", "Thin Lips","Upper Lip Mole Lips", "Wide Lips"], label="Lip Shape: "),
            gr.Dropdown(value="-", choices=["-", "random 🎲", "Circle", "Diamond", "Heart", "Heart with Pointed Chin", "Heart with Rounded Chin", "Heart with V-Shape Chin", "Inverted Triangle", "Long", "Oblong", "Oval", "Pear", "Rectangle", "Round", "Round with Defined Cheekbones", "Round with High Cheekbones", "Round with Soft Cheekbones", "Square", "Square Oval", "Square Round", "Square with Rounded Jaw", "Square with Sharp Jaw", "Square with Soft Jaw", "Triangle"], label="Face Shape: "),
            gr.Slider(minimum=0, maximum=1.3, step=0.01, value=1.3, label="Face Shape Weight")
            ],
            outputs=[gr.Gallery(label="Outputs: ", height=500)]
            )

    eye_lip_face.queue()
    eye_lip_face.launch()

if __name__ == "__main__":
    eye_lip_face_interface()