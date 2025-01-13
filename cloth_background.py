import json
import random
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
from PIL import Image
from websockets_api import get_prompt_images
from settings import COMFY_UI_PATH, CLOTH_BACKGROUND_WORKFLOW

# Save input image and reference image into the input folder inside ComfyUI with unique filenames
def save_input_image(img, img_cloth, img_bg):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    
    input_dir = Path(COMFY_UI_PATH) / "input"
    input_dir.mkdir(parents=True, exist_ok=True) 

    input_img = input_dir / f"img_{timestamp}_{unique_id}.jpg"
    input_img_cloth = input_dir / f"img_cloth_{timestamp}_{unique_id}.jpg"
    input_img_bg = input_dir / f"img_bg_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image_cloth = Image.fromarray(img_cloth)
    pillow_image_bg = Image.fromarray(img_bg)
    pillow_image.save(str(input_img)) 
    pillow_image_cloth.save(str(input_img_cloth))
    pillow_image_bg.save(str(input_img_bg))  
    
    return input_img.name, input_img_cloth.name, input_img_bg.name

def process(img, img_cloth, img_bg, prompt_clothing_type):
    with open(CLOTH_BACKGROUND_WORKFLOW, "r", encoding="utf-8") as f:
        prompt = json.load(f)

    # Set a random seed for reproducibility
    prompt["3"]["inputs"]["seed"] = random.randint(0, 999999999999999)

    default_prompt_clothing_type = "clothing, pants"
    final_prompt = prompt_clothing_type.strip() if prompt_clothing_type.strip() else default_prompt_clothing_type
    prompt["6"]["inputs"]["prompt"] = final_prompt

    
    img_filename, img_cloth_filename, img_bg_filename = save_input_image(img, img_cloth, img_bg)

    # Map the input images into the workflow
    prompt["1"]["inputs"]["image"] = img_filename
    prompt["49"]["inputs"]["image"] = img_cloth_filename
    prompt["37"]["inputs"]["image"] = img_bg_filename
    
    images = get_prompt_images(prompt)
    return images

# Gradio interface for cloth swapping tool
def create_cloth_background_interface():
    cloth_swaping = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=500), 
            gr.Image(label="Input Image Cloth Reference: ", type="numpy", height=500),  
            gr.Image(label="Input Image Background ", type="numpy", height=500),  
            gr.Textbox(label="Prompt Clothing Type: ", placeholder="Enter clothing types (default: clothing, pants)"),
        ],
        outputs=[gr.Gallery(label="Outputs: ", height=500)]
    )
    cloth_swaping.queue()
    cloth_swaping.launch()

if __name__ == "__main__":
    create_cloth_background_interface()