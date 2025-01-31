import json
import random
import uuid
from datetime import datetime
from pathlib import Path
import os
import gradio as gr
from PIL import Image
import numpy as np

from websockets_api import get_prompt_images
from settings import COMFY_UI_PATH, FLUX_CHARACTER_FACE_WORKFLOW
from template_prompt import character_generation_prompt


def ensure_directory_exists(directory: Path):
    """ Ensure the directory exists and has write permissions. """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Write permission denied for directory: {directory}")
    except Exception as e:
        print(f"Error ensuring directory exists: {e}")
        raise


def save_input_image(image, image_bg):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())

    input_dir = Path(COMFY_UI_PATH) / "input"
    ensure_directory_exists(input_dir)

    input_image = input_dir / f"img_{timestamp}_{unique_id}.jpg"
    input_image_bg = input_dir / f"img_bg_{timestamp}_{unique_id}.jpg"

    try:
        pillow_image = Image.fromarray(image.astype(np.uint8)) if isinstance(image, np.ndarray) else image
        pillow_image_bg = Image.fromarray(image_bg.astype(np.uint8)) if isinstance(image_bg, np.ndarray) else image_bg

        pillow_image.save(input_image)
        pillow_image_bg.save(input_image_bg)

        return input_image.name, input_image_bg.name
    except PermissionError:
        print(f"Permission denied while saving images to {input_dir}. Try running as administrator.")
        return None, None
    except Exception as e:
        print(f"Error saving images: {e}")
        return None, None


def process(img, img_bg, person_prompt, style_choice, custom_style):
    try:
        with open(FLUX_CHARACTER_FACE_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed for reproducibility
        prompt["25"]["inputs"]["noise_seed"] = random.randint(0, 99999999999999999)

        # Default Person Description
        default_person_prompt = "A man in middle, full body, clean-shaven, medium side-swept hairstyle"
        prompt["113"]["inputs"]["text"] = person_prompt.strip() if person_prompt and person_prompt.strip() else default_person_prompt

        # Style Selection Logic
        if style_choice == "No":
            prompt["79"]["inputs"]["text"] = custom_style.strip() if custom_style.strip() else "Custom style not provided"
        else:
            prompt["79"]["inputs"]["text"] = character_generation_prompt[int(style_choice)]  # Direct dictionary lookup

        # Save images and update paths
        img_filename, img_bg_filename = save_input_image(img, img_bg)
        if not img_filename or not img_bg_filename:
            return "Error: Unable to save images. Check permissions."

        prompt["42"]["inputs"]["image"] = str(img_filename)
        prompt["85"]["inputs"]["background_image"] = str(img_bg_filename)

        images = get_prompt_images(prompt)
        return images if images else "No images generated."

    except Exception as e:
        print(f"Error during processing: {e}")
        return f"Processing error: {e}"


def toggle_custom_style(style_choice):
    """ Show custom style textbox only when 'No' is selected """
    return gr.update(visible=(style_choice == "No"))


def character_generation_face_swap():
    with gr.Blocks() as app:
        gr.Markdown("### Character Generation with Face Swap")

        img = gr.Image(label="Input Image", type="numpy", height=250)
        img_bg = gr.Image(label="Input Background Image", type="numpy", height=250)
        person_prompt = gr.Textbox(label="Character Description Prompt", placeholder="Default(A man in middle, full body, clean-shaven, medium side-swept hairstyle)")

        style_choice = gr.Dropdown(choices=["1", "2", "3", "No"], label="Character Style Prompt")
        custom_style = gr.Textbox(label="Custom Character Style", placeholder="Enter custom style (only if 'No' is selected)", visible=False)

        output_gallery = gr.Gallery(label="Output", height=500)

        style_choice.change(toggle_custom_style, inputs=[style_choice], outputs=[custom_style])

        submit_button = gr.Button("Generate")
        submit_button.click(
            fn=process,
            inputs=[img, img_bg, person_prompt, style_choice, custom_style],
            outputs=[output_gallery]
        )

    app.launch()


if __name__ == "__main__":
    character_generation_face_swap()
