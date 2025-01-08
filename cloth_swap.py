import os
import json
import random
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
from PIL import Image
from websockets_api import get_prompt_images
from dotenv import load_dotenv

load_dotenv()
COMFY_UI_PATH = os.getenv("COMFY_UI_PATH")
CLOTH_SWAP_WORKFLOW = os.getenv("CLOTH_SWAP_WORKFLOW")
RESULTS_PATH = os.getenv("RESULTS_PATH")

# Save input image and reference image into the input folder inside ComfyUI with unique filenames
def save_input_image(img, img_ref):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    
    input_dir = Path(COMFY_UI_PATH) / "input"
    input_dir.mkdir(parents=True, exist_ok=True) 

    input_img = input_dir / f"img_{timestamp}_{unique_id}.jpg"
    input_img_ref = input_dir / f"img_ref_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image_ref = Image.fromarray(img_ref)
    pillow_image.save(str(input_img)) 
    pillow_image_ref.save(str(input_img_ref))  
    
    return input_img.name, input_img_ref.name 

# Save output images into the output folder inside ComfyUI with unique filenames
# def save_output_images(images):
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     unique_id = str(uuid.uuid4())

#     result_dir = Path(RESULTS_PATH)
#     result_dir.mkdir(parents=True, exist_ok=True)

#     output_filenames = []
#     for i, img in enumerate(images):
#         result_img = result_dir / f"output_img_{timestamp}_{unique_id}_{i}.jpg"
#         if isinstance(img, Image.Image):
#             img.save(str(result_img))
#         else: 
#             pillow_image = Image.fromarray(img)
#             pillow_image.save(str(result_img))
#         output_filenames.append(result_img.name)

#     return output_filenames

def process(img, img_ref, top_clothes, bottom_clothes, torso, left_Arm, right_Arm, left_leg, rigth_leg):
    with open(CLOTH_SWAP_WORKFLOW, "r", encoding="utf-8") as f:
        prompt = json.load(f)

    # Set a random seed for reproducibility
    prompt["1"]["inputs"]["seed"] = random.randint(0, 999999999999999)

    # Map the top_clothes and bottom_clothes inputs
    prompt["13"]["inputs"].update({
        "top_clothes" : top_clothes == "True",
        "bottom_clothes": bottom_clothes == "True",
        "torso_skin": torso == "True",
        "left_arm": left_Arm == "True",
        "right_arm": right_Arm == "True",
        "left_leg": left_leg == "True",
        "right_leg": rigth_leg == "True"
    })
    img_filename, img_ref_filename = save_input_image(img, img_ref)

    # Map the input images into the workflow
    prompt["17"]["inputs"]["image"] = img_filename
    prompt["18"]["inputs"]["image"] = img_ref_filename

    # print(f"Updated prompt: {json.dumps(prompt, indent=2)}")
    
    images = get_prompt_images(prompt)
    # Save output images to disk
    # save_output_images(images)
    
    return images

# Gradio interface for cloth swapping tool
def create_cloth_swapping_interface():
    cloth_swaping = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=500), 
            gr.Image(label="Input Image Reference: ", type="numpy", height=500),  
            gr.Dropdown(value="True", choices=["True", "False"], label="Target Top Clothes (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Bottom Clothes (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Torso (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Left Arm (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Right Arm (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Left Leg (True/False): "),
            gr.Dropdown(value="False", choices=["True", "False"], label="Target Right Leg (True/False): ")
        ],
        outputs=[gr.Gallery(label="Outputs: ", height=500)]
    )
    cloth_swaping.queue()
    cloth_swaping.launch()

if __name__ == "__main__":
    create_cloth_swapping_interface()