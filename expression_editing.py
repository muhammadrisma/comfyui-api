import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
from PIL import Image
from websockets_api import get_prompt_images
from dotenv import load_dotenv

load_dotenv()
COMFY_UI_PATH = Path(os.getenv("COMFY_UI_PATH"))
EXPRESSION_WORKFLOW = Path(os.getenv("EXPRESSION_WORKFLOW"))

# Save input image and reference image into the input folder inside ComfyUI with unique filenames
def save_input_image(img):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    input_img = Path(COMFY_UI_PATH) / f"input/img_{timestamp}_{unique_id}.jpg"

    pillow_image = Image.fromarray(img)
    pillow_image.save(input_img)

    return input_img.name

# Main processing function
def process(img, rotate_pitch, rotate_yaw, rotate_roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile):
    try:
        with open(EXPRESSION_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        # Validate JSON keys
        if "14" not in prompt or "inputs" not in prompt["14"]:
            raise KeyError("Key '14.inputs' is missing in the JSON structure.")
        if "15" not in prompt or "inputs" not in prompt["15"]:
            raise KeyError("Key '15.inputs' is missing in the JSON structure.")

        # Update expression values in the prompt
        prompt["14"]["inputs"].update({
            "rotate_pitch": rotate_pitch,
            "rotate_yaw": rotate_yaw,
            "rotate_roll": rotate_roll,
            "blink": blink,
            "eyebrow": eyebrow,
            "wink": wink,
            "pupil_x": pupil_x,
            "pupil_y": pupil_y,
            "aaa": aaa,
            "eee": eee,
            "woo": woo,
            "smile": smile
        })

        img_filename = save_input_image(img)
        prompt["15"]["inputs"]["image"] = img_filename

        images = get_prompt_images(prompt)
        return images
    except Exception as e:
        print(f"Error during processing: {e}")
        raise

# Gradio interface for the expression editing tool
def create_gradio_interface():
    expression_editing = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Input Image: ", type="numpy", height=500), 
            gr.Slider(value=0, minimum=-20.0, maximum=20.0, step=0.1, label="Rotate Pitch"),
            gr.Slider(value=0, minimum=-20.0, maximum=20.0, step=0.1, label="Rotate Yaw"),
            gr.Slider(value=0, minimum=-20.0, maximum=20.0, step=0.1, label="Rotate Roll"),
            gr.Slider(value=0, minimum=-20.0, maximum=5.0, step=0.1, label="Blink"),
            gr.Slider(value=0, minimum=-10.0, maximum=15.0, step=0.1, label="Eyebrow"),
            gr.Slider(value=0, minimum=0.0, maximum=25.0, step=0.1, label="Wink"),
            gr.Slider(value=0, minimum=-15.0, maximum=15.0, step=0.1, label="Pupil X"),
            gr.Slider(value=0, minimum=-15.0, maximum=15.0, step=0.1, label="Pupil Y"),
            gr.Slider(value=0, minimum=-30.0, maximum=120.0, step=0.1, label="AAA"),
            gr.Slider(value=0, minimum=-20.0, maximum=15.0, step=0.1, label="EEE"),
            gr.Slider(value=0, minimum=-20.0, maximum=15.0, step=0.1, label="WOO"),
            gr.Slider(value=0, minimum=-0.2, maximum=1.3, step=0.1, label="Smile"),
        ],
        outputs=[gr.Gallery(label="Outputs: ", height=500)] 
    )
    expression_editing.queue()
    expression_editing.launch()

if __name__ == "__main__":
    create_gradio_interface()
