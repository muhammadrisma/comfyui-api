import os
import numpy as np
import json
import uuid
from datetime import datetime
from pathlib import Path
import gradio as gr
import random
import random
from PIL import Image
from websockets_api import get_prompt_images
from settings import HAIR_WORKFLOW, COMFY_UI_PATH
from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)

def save_input_image(img):
    if isinstance(img, str):
        raise ValueError(f"Expected an image array, but got a string: {img}")
    elif isinstance(img, Image.Image):
        img = np.array(img)
    elif not isinstance(img, np.ndarray):
        raise TypeError(f"Expected img to be a NumPy array, got {type(img)} instead.")

    # Ensure the 'input' directory exists
    input_dir = Path(COMFY_UI_PATH) / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())
    input_img_path = input_dir / f"img_{timestamp}_{unique_id}.jpg"

    # Save the image
    pillow_image = Image.fromarray(img)
    pillow_image.save(input_img_path)

    #print(f"Image saved at: {input_img_path}")  # Debugging line
    return input_img_path 

# Dictionary for hairstyles
hairstyles = {
    "-":" ",
    "Boho Twisted Crown": "Boho Twisted Crown: Create loose twists around the head, This casual style adds romantic charm to everyday looks, with no accessories.",
    "Braided Heart Design": "Shape braids into a heart pattern at the back for a romantic and symbolic style.",
    "Woven Basket Crown": "Create a basket weave pattern around the crown area for a textured style with dimensional interest.",
    "Multi-Twisted Updo": "Form various-sized twists and pin them randomly to craft a creative updo perfect for formal events.",
    "Low Textured Knot": "Gather hair at the nape, twist and knot loosely, securing with pins for a style that balances polish with casual charm.",
    "Boho Waves": "Effortlessly create loose, natural beachy waves for a carefree, wind-swept look.",
    "Dutch Braid": "Braid three strands under each other to create a Dutch braid that stands out above the rest of the hair.",
    "French Twist": "Twist hair and pin it up at the back for a classic and elegant French twist.",
    "Half-Up Half-Down": "Divide hair into two parts, tying the upper portion into a bun or braid while letting the rest flow freely.",
    "Layered Hair with Curtain Bangs": "Pair layered haircuts that create volume and texture with curtain bangs parted down the middle for a trendy look.",
    "Side-Swept Bangs": "Layer hair and sweep it to the side, framing the face with stylish fringes.",
    "Soft Curls": "Style feminine curls to fall gracefully over the shoulders for a romantic appearance.",
    "Top Knot": "Pull hair back and tie it into a sleek top knot for a refined and modern look.",
    "Sleek and Straight": "Straighten and smooth down hair for a simple, sleek, and polished style.",
    "Waterfall Braid": "Braid hair diagonally across the back of the head, resembling a cascading waterfall.",
    "Sleek Bob": "A blunt bob haircut with a sleek finish for a modern and professional vibe.",
    "Effortless Waves": "loose waves with blonde highlights and a side part for an effortlessly chic look.",
    "Sophisticated Mane": "shiny and straight hair in a rich auburn color cascades luxuriously down the back.",
    "Punky Rebellion": "spiky hair dyed a vibrant blue with shaved sides and a silver undercut for a punk-inspired style.",
    "Textured Updo": "Create a textured updo, curly hair, leaving loose strands to frame the face. Add a touch of purple for personality.",
    "Braided Masterpiece": "Intricately braid hair into a Mohawk style using vibrant red and black extensions for a bold look.",
    "Defying Gravity": "Defy gravity, flowing hair in a vibrant ombre color, styled upward dynamically.",
    "Mythical Inspiration": "flowing silver hair with intricate braids and woven flowers for a mythical, elven-inspired look.",
    "Underwater Dreams": "Achieve a mermaid-inspired hairstyle, textured hair adorned with seashells and seaweed.",
    "Undercut with Style": "Pair a high fade on the sides with a neatly styled pompadour, enhanced by dark brown hair with red tips.",
    "Curly Bob with Bangs": "curly bob with blunt bangs, styled in a vibrant red for a playful and striking statement.",
    "Silky Straight": "straight hair with a glossy shine and a center part for a timeless and elegant style.",
    "Blunt Bob with Layers": "Straight, blunt bob with subtle layers and a light blonde color to add youthful volume and charm.",
    "Beach Waves with Straight Hair": "straight hair styled with loose beach waves at the ends, enhanced by subtle blonde highlights.",
    "Classic Crew Cut": "A classic crew cut with a clean fade and dark brown hair, perfect for a timeless and professional look.",
    "Messy Quiff with Textured Sides": "Style hair into a messy quiff with textured sides and light brown tones with blonde highlights.",
    "Hair with Bun": "Gather, straight hair into a messy bun at the back, leaving loose strands for a relaxed yet rugged look.",
    "Vintage Pin-Up": "Vintage pin-up curls with a voluminous shape, styled with a red bandana for added flair.",
    "1950s Rockabilly Hair": "A high, slicked-back pompadour with sideburns, styled with a hint of grease for a 1950s rockabilly vibe.",
    "Glamorous 1920s Waves": "Glamorous 1920s-inspired finger waves paired with a jeweled headband for a sophisticated vintage style.",
    "1970s Disco": "A voluminous 1970s disco-inspired afro with chunky highlights for a bold, groovy look.",
    "Avant-Garde": "An avant-garde hairstyle featuring intricate braids and vibrant blue highlights in geometric shapes.",
    "Gravity-Defying e": "flowing pink hair styled upward with butterfly clips, creating a gravity-defying whimsical style.",
    "Mystical Inspired by Nature": "Nature-inspired cascading green hair adorned with vines, leaves, and flowers for a mystical look.",
    "Punk-Inspired": "Shave one side and dye the other in a rainbow of colors for a bold punk-inspired hairstyle.",
    "Professional Job Interview": "A polished ponytail with a center part, ideal for a professional and confident appearance.",
    "Polished Haircut for Business": "A clean, haircut with a fade, perfect for business meetings and a sharp, professional look.",
    "Elegant Bun for a Formal Event": "Elegant and detailed bun hairstyle adorned with a decorative hairpiece for formal occasions.",
    "Protective for Natural Hair": "Protective cornrows with colorful beads, offering style and practicality for natural hair.",
    "Twist-Out for Curly Hair": "Twist-out curls styled with bouncy volume for a chic and lively appearance.",
    "Braided Updo": "Braided updo with intricate designs that protect hair ends and create eye-catching patterns.",
    "Hot Summer Day": "layered cut with a side part for a lightweight and airy style, perfect for hot summer days.",
    "Winter Wonderland": "braids adorned with snowflake accessories and icy blue highlights for a winter-inspired look.",
    "Windy Day": "A braided headband keeps hair secure while remaining stylish, ideal for a windy day."
}

def process(img, hair_color, hairstyle, slider):
    try:
        with open(HAIR_WORKFLOW, "r", encoding="utf-8") as f:
            prompt = json.load(f)

        prompt["156"]["inputs"]["seed"] = random.randint(0, 99999999999999999)
        
        # Set the hairstyle description
        text2 = f"{hairstyle}, with {hair_color} hair color"

        prompt["228"]["inputs"]["text"] = text2
        prompt["156"]["inputs"]["denoise"] = slider

        # Save the image and get its path
        img_filename = save_input_image(img)
        # Convert Path to string to avoid serialization issues
        prompt["138"]["inputs"]["image"] = str(img_filename)

        # Call the function to process the prompt and get the result images
        images = get_prompt_images(prompt)
        return images
    
    except Exception as e:
        logger.error(f"Expression editing error: {e}")
        raise HTTPException(status_code=500, detail="Expression editing processing failed.")
    
hair_color_choices = ["-", "Black", "Brown", "Blonde", "Red", "Pink", "Blue", "Green", "Purple", "White", "Grey"]
hairstyle_choices = list(hairstyles.keys()) # Use the keys of the dictionary for hairstyle options

def hair_interface():
    hair = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(type="numpy", label="Upload Image"),  # Input as numpy array
            gr.Dropdown(choices=hair_color_choices, label="Hair Color"),  # Dropdown for hair color
            gr.Dropdown(choices=hairstyle_choices, label="Hairstyle"),  # Dropdown for hairstyle
            gr.Slider(minimum=0, maximum=1, step=0.01, value=0.75, label="Weight")  # Slider input
        ],
        outputs=[gr.Gallery(label="Outputs: ")]  # Output images in a gallery
    )
    hair.queue()
    hair.launch()

if __name__ == "__main__":
    hair_interface()