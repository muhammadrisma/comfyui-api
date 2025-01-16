import json
import uuid
import random
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image
from fastapi import HTTPException
import gradio as gr
from websockets_api import get_prompt_images
from settings import EYE_LIP_FACE_WORKFLOW, COMFY_UI_PATH

logger = logging.getLogger(__name__)

def save_input_image(img):
    """
    Saves the input image to the ComfyUI input directory with a unique name.

    Args:
        img (numpy.ndarray): Image data in numpy array format.

    Returns:
        str: The name of the saved image file.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())
        input_dir = Path(COMFY_UI_PATH) / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        input_img = input_dir / f"img_{timestamp}_{unique_id}.jpg"
        pillow_image = Image.fromarray(img)
        pillow_image.save(str(input_img))
        return input_img.name
    except Exception as e:
        logger.error(f"Error saving input image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save input image.")

def process(img, eyes_color, eyes_shape, lips_color, lips_shape, face_shape, slider):
    """
    Processes the input image and generates new images based on the provided parameters.

    Args:
        img (numpy.ndarray): Input image.
        eyes_color (str): Selected eye color.
        eyes_shape (str): Selected eye shape.
        lips_color (str): Selected lip color.
        lips_shape (str): Selected lip shape.
        face_shape (str): Selected face shape.
        slider (float): Denoising weight.

    Returns:
        list: A list of generated images.
    """
    try:
        with open(EYE_LIP_FACE_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Set a random seed and update prompt details
        prompt["27"]["inputs"].update({
            "seed": random.randint(0, 9999999999999999),
            "denoise": slider
        })
        prompt["21"]["inputs"].update({
            "eyes_color": eyes_color,
            "eyes_shape": eyes_shape,
            "lips_color": lips_color,
            "lips_shape": lips_shape,
            "face_shape": face_shape
        })

        img_filename = save_input_image(img)
        prompt["14"]["inputs"]["image"] = img_filename

        # Generate images using the prompt
        images = get_prompt_images(prompt)
        return images
    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")

def eye_lip_face_interface():
    """
    Gradio interface for eye, lip, and face shape customization tool.
    """
    eye_lip_face = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=1024),
            gr.Dropdown(
                value="-",
                choices=["-", "random 🎲", "Amber", "Blue", "Brown", "Green", "Hazel", "Red"],
                label="Eyes Color: "
            ),
            gr.Dropdown(
                value="-",
                choices=[
                    "-", "random 🎲", "Almond Eyes Shape", "Asian Eyes Shape", "Close-Set Eyes Shape",
                    "Deep Set Eyes Shape", "Double Eyelid Eyes Shape", "Downturned Eyes Shape",
                    "Hooded Eyes Shape", "Monolid Eyes Shape", "Oval Eyes Shape",
                    "Protruding Eyes Shape", "Round Eyes Shape", "Upturned Eyes Shape"
                ],
                label="Eyes Shape: "
            ),
            gr.Dropdown(
                value="-",
                choices=[
                    "-", "random 🎲", "Berry lips", "Burgundy Lips", "Coral Lips",
                    "Glossy Red Lips", "Peach Lips", "Pink Lips", "Plum Lips", "Red Lips"
                ],
                label="Lip Color: "
            ),
            gr.Dropdown(
                value="-",
                choices=[
                    "-", "random 🎲", "Biting Lips", "Bow-shaped Lips", "Cupid's Bow Lips", "Full Lips",
                    "Heart-shaped Lips", "Large Lips", "Parted Lips", "Plump Lips", "Pouting Lips", "Round Lips"
                ],
                label="Lip Shape: "
            ),
            gr.Dropdown(
                value="-",
                choices=[
                    "-", "random 🎲", "Circle", "Diamond", "Heart", "Heart with Pointed Chin",
                    "Heart with Rounded Chin", "Heart with V-Shape Chin", "Inverted Triangle", "Long",
                    "Oblong", "Oval", "Pear", "Rectangle", "Round", "Round with Defined Cheekbones",
                    "Round with High Cheekbones", "Round with Soft Cheekbones", "Square", "Square Oval",
                    "Square Round", "Square with Rounded Jaw", "Square with Sharp Jaw", "Square with Soft Jaw",
                    "Triangle"
                ],
                label="Face Shape: "
            ),
            gr.Slider(minimum=0, maximum=0.4, step=0.01, value=0.35, label="Weight")
        ],
        outputs=[gr.Gallery(label="Outputs: ", height=500)]
    )

    eye_lip_face.queue()
    eye_lip_face.launch()

if __name__ == "__main__":
    eye_lip_face_interface()
