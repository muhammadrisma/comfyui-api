import os
import json
import uuid
import random
from datetime import datetime
from pathlib import Path
import gradio as gr
from PIL import Image
from websockets_api import get_prompt_images
from dotenv import load_dotenv
import urllib.request
from urllib.error import HTTPError, URLError

load_dotenv()
COMFY_UI_PATH = Path(os.getenv("COMFY_UI_PATH"))
MAKEUP_WORKFLOW = Path(os.getenv("MAKEUP_WORKFLOW"))

# Save input image and reference image into the input folder inside ComfyUI with unique filenames
def save_input_image(img):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    input_img = Path(COMFY_UI_PATH) / f"input/img_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image.save(input_img)

    return input_img.name

def process(img, makeup_style, eyeshadow, eyeliner, mascara, blush, lipstick, lip_gloss, slider):
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
        img_filename = save_input_image(img)
        prompt["1"]["inputs"]["image"] = img_filename

        # Call the image generation function
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
def makeup_interface():
    makeup = gr.Interface(
    fn=process,
    inputs=[
        gr.Image(label="Input Image: ", type="numpy", height=1024),
        gr.Dropdown(value="Boho Makeup", 
                    choices=["-", "random 🎲", "Anime Makeup", "Artistic Makeup", "Avant-garde Makeup", 
                             "Bohemian Makeup", "Boho Makeup", "Classic Makeup", "Cut Crease Makeup", 
                             "Dewy Makeup", "Edgy Makeup", "Festival Makeup", "Glam Makeup", 
                             "Glowy Makeup", "Golden Makeup", "Monochromatic Makeup", "Natural Makeup", 
                             "Party Makeup", "Retro Makeup", "Sunset Eye Makeup", "Vintage Makeup", 
                             "Watercolor Makeup"], 
                    label="Makeup Style: "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Eyeshadow (True/False): "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Eyeliner (True/False): "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Mascara (True/False): "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Blush (True/False): "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Lipstick (True/False): "),
        gr.Dropdown(value="True", choices=["True", "False"], label="Lip Gloss (True/False): "),
        gr.Slider(minimum=0, maximum=1, step=0.01, value=0.5, label="Denoise Weight")
    ],
    outputs=[gr.Gallery(label="Generated Images", height=500)]
)

    makeup.queue()
    makeup.launch()

if __name__ == "__main__":
    makeup_interface()