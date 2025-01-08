# Question

update the readme

# Answer

Certainly! Below is an updated version of the README text with improvements for clarity and structure, while preserving the essential information:

---
# FLOW
- Set Database using db.sql file
- Run ComfyUI
- Run Cloth Swap/Expression Editing etc
- Run Restfull Api
# Expression Editing Tool & Cloth Swap API

## Important Notes
- Input images should be of HD resolution to achieve better results.

## Overview

The **Expression Editing Tool** is a Python application that utilizes Gradio for an interactive interface, enabling users to manipulate facial expressions in images through various adjustable parameters. It uses the Pillow library for image handling and processes input based on customizable JSON prompts.

The **Cloth Swap API** allows users to swap clothes between images using the ComfyUI framework. It takes user inputs to identify which clothes to swap and processes the images accordingly. Each output image is saved with a unique filename to ensure uniqueness.

## Features

### Expression Editing Tool
- **Upload an Image**: Users can upload an image for facial expression editing.
- **Adjust Facial Attributes**: Modify attributes such as pitch, yaw, roll orientations, and various expressions (e.g., blink, eyebrow position, wink, pupil coordinates, and smile intensity).
- **Output Generation**: Generate modified images based on user-defined parameters.

### Cloth Swap API Functionality
- **Main Function**: `process(img, img_ref, top_clothes, bottom_clothes)`
  - Loads a predefined workflow from a JSON file (`CLOTH_SWAP_WORKFLOW`).
  - Sets a random seed for reproducibility.
  - Maps user inputs for clothing targets (top and bottom).
  - Calls `save_input_image()` to save input and reference images with unique filenames.
  - Updates the workflow with the filenames of the saved images.
  - Calls `get_prompt_images()` to process and retrieve resulting images.

- **Helper Function**: `save_input_image(img, img_ref)`
  - Saves input images to a specified folder, ensuring unique filenames by appending a timestamp and a UUID.
  
    #### Parameters:
    - `img`: The primary input image (numpy array).
    - `img_ref`: The reference image for clothing comparison (numpy array).
    
    #### Returns:
    - The names of the saved input image and the reference image.

## Requirements
1. Install the ComfyUI framework.
2. Create a `.env` file in your working directory with these variables:
   - `SERVER_ADDRESS`
   - `COMFY_UI_PATH`
   - `CLOTH_SWAP_WORKFLOW`
   - `EXPRESSION_WORKFLOW`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`

3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

4. Additional packages for the Cloth Swap API:
   - `json`
   - `random`
   - `uuid`
   - `datetime`
   - `pathlib`
   - `PIL` (Pillow library)

5. Ensure the following files are in your working directory:
   - `settings.py`: Should define `COMFY_UI_PATH`, `EXPRESSION_WORKFLOW`, and `CLOTH_SWAP_WORKFLOW`.
   - `websockets_api.py`: Must implement the `get_prompt_images` function.

## File Structure
```
your_project_directory/
├── workflows/
│   ├── expression_editing.json
│   └── cloth_swap.json
├── expression_editing.py
├── cloth_swap.py
├── db_config.py
└── websockets_api.py
├── .env
├── README.md
```

## How to Use

### Expression Editing Tool
1. **Launch the Application**:
   Run the `expression_editing.py` script:
   ```bash
   python expression_editing.py
   ```

2. **Interact with the Interface**: 
   - Upload an image through the "Input Image" field.
   - Adjust sliders to define desired expressions (e.g., Rotate Pitch, Blink, Smile).

3. **View Outputs**:
   - The modified images will appear in the output gallery after adjustments.

### Cloth Swap API
1. **Set Up**:
   Adjust `COMFY_UI_PATH` and `CLOTH_SWAP_WORKFLOW` in the `.env` file to point to the correct directories.

2. **Run the Script**:
   Execute `cloth_swap.py` to launch the Gradio interface.

## User Interface

### Inputs

#### Expression Editing Tool
- **Input Image**: The image to edit expressions (Type: Image Upload).
- Adjustable sliders for various facial attributes.

#### Cloth Swap API
1. **Input Image**: The main image for the clothing swap (Type: numpy array, Height: 500).
2. **Input Image Reference**: The reference image (Type: numpy array, Height: 500).
3. **Target Top Clothes**: Dropdown for specifying swapping (Choices: `True`, `False`).
4. **Target Bottom Clothes**: Dropdown for specifying swapping (Choices: `True`, `False`).

### Outputs
Both tools display processed images in output galleries.

### Interface Previews
1. **Cloth Swap**: ![Cloth Swap Interface](Interface%20demo/cloth_swap.png)
2. **Expression Editing**: ![Expression Editing Interface](Interface%20demo/expression.png)
3. **.env**: ![.env File](Interface%20demo/env.png)

## References
- ComfyUI Workflow:
  1. Expression Editing: [Video Link](https://www.youtube.com/watch?v=q0Vf-ZZsbzI&t=150s)
  2. Cloth Swap: [Video Link](https://youtu.be/WXmkLih9jfk?si=6vHraq-s49P4DLPb)

- Acknowledgment to tutorials by YT Code Crafters Corner: 
  - [Video Link 1](https://youtu.be/kmZqoLJ2Dhk?si=DNN4nE5mue5cXzx2)
  - [Video Link 2](https://youtu.be/1iPcRGyj7-E?si=zaAQ88xsFFSI8CBI)
  - [Video Link 3](https://youtu.be/zajODlpfOs4?si=depOaJViLMTNPAnlS)

---

Feel free to further modify it according to specific style or additional information requirements!