import json
import random
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
from PIL import Image

from settings import COMFY_UI_PATH , CLOTH_SWAP_WORKFLOW
from websockets_api import get_prompt_images

# Save input image and reference image into the input folder inside ComfyUI with unique filenames
def save_input_image(img, img_ref):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    input_img = Path(COMFY_UI_PATH) / f"input/img_{timestamp}_{unique_id}.jpg"
    input_img_ref = Path(COMFY_UI_PATH) / f"input/img_ref_{timestamp}_{unique_id}.jpg"
    
    # print(f"img type: {type(img)}, img_ref type: {type(img_ref)}") 

    pillow_image = Image.fromarray(img)
    pillow_image_ref = Image.fromarray(img_ref)
    pillow_image.save(input_img)
    pillow_image_ref.save(input_img_ref)
    
    return input_img.name, input_img_ref.name 

def process(img, img_ref, top_clothes, bottom_clothes, left_Arm, right_Arm):
    with open(CLOTH_SWAP_WORKFLOW, "r", encoding="utf-8") as f:
        prompt = json.load(f)

    # Set a random seed for reproducibility
    prompt["1"]["inputs"]["seed"] = random.randint(0, 99999999999)

    # Map the top_clothes and bottom_clothes inputs
    prompt["13"]["inputs"].update({
        "top_clothes" : top_clothes == "True",
        "bottom_clothes": bottom_clothes == "True",
        "left_arm": left_Arm == "True",
        "right_arm": right_Arm == "True",
    })
    img_filename, img_ref_filename = save_input_image(img, img_ref)

    # Map the input images into the workflow
    prompt["17"]["inputs"]["image"] = img_filename
    prompt["18"]["inputs"]["image"] = img_ref_filename

    # print(f"Updated prompt: {json.dumps(prompt, indent=2)}")
    
    images = get_prompt_images(prompt)
    return images

cloth_swaping = gr.Interface(
    fn=process,
    inputs=[
        gr.Image(label="Input Image: ", type="numpy" , height=500), 
        gr.Image(label="Input Image Reference: ", type="numpy", height=500),  
        gr.Dropdown(value="True",choices=["True", "False"], label="Target Top Clothes (True/False): "),
        gr.Dropdown(value="False", choices=["True", "False"], label="Target Bottom Clothes (True/False): "),
        gr.Dropdown(value="False", choices=["True", "False"], label="Target Left Arm (True/False): "),
        gr.Dropdown(value="False", choices=["True", "False"], label="Target Right Arm (True/False): "),
    ],
    outputs=[gr.Gallery(label="Outputs: ", height=500), ]  
)

cloth_swaping.queue()
cloth_swaping.launch()
