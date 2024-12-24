# Expression Editing Tool & Cloth Swap API
## Notes(Important)
Input Image should be had HD resolution so it can produces better results.
## Overview

The **Expression Editing Tool** is a Python-based application that utilizes Gradio for an interactive interface, enabling users to manipulate facial expressions in images through various adjustable parameters. It leverages the Pillow library for image handling and processes the input based on customizable JSON prompts.

Additionally, the **Cloth Swap API** provides an interface for swapping clothes between images using the ComfyUI framework. It utilizes user inputs to identify which clothes to swap and processes the images accordingly. This script is designed to save images with unique filenames, ensuring that each output retains its uniqueness.

## Expression Editing Tool Features

- **Upload an Image**: Users can upload an image where facial expressions are applied.
- **Adjust Facial Attributes**: Modify pitch, yaw, roll orientations, and various expressions like blink, eyebrow position, wink, pupil coordinates, and smile intensity.
- **Output Generation**: The tool generates modified images based on the user-defined parameters.

## Cloth Swap API Functionality

### Main Function: `process(img, img_ref, top_clothes, bottom_clothes)`

This function handles the cloth swapping operation and performs the following key tasks:

1. Loads a predefined workflow from a JSON file (`CLOTH_SWAP_WORKFLOW`).
2. Sets a random seed for reproducibility in image processing.
3. Maps the user inputs for clothing targets (top and bottom).
4. Calls the `save_input_image()` function to save the input and reference images with unique filenames.
5. Updates the workflow with the filenames of the saved images.
6. Calls `get_prompt_images()` to process and retrieve the resulting images.

### Helper Function: `save_input_image(img, img_ref)`

This function saves the input images into a defined input folder within the ComfyUI directory, ensuring each filename is unique by appending a timestamp and a UUID.

#### Parameters:
- `img`: The primary input image (numpy array).
- `img_ref`: The reference image for clothing comparison (numpy array).

#### Returns:
- The names of the saved input image and the reference image.

## Requirements
Ensure Your already installed ComfyUI framework, then you should place `SERVER_ADRESS` and `COMFY_UI_PATH` in `settings.py` file.
Your Comfyui should contain costume nodes and model that you will use for cloth swap and expression editing workflow.

Ensure that you have the following libraries installed:

```bash
pip install -r requirements
```

Additionally, for the Cloth Swap API, ensure the following packages are installed:

- `json`
- `random`
- `uuid`
- `datetime`
- `pathlib`
- `PIL` (from the Pillow library)

Both tools expect the following files in your working directory:

- `settings.py`: Must define the constants `COMFY_UI_PATH`, `EXPRESSION_WORKFLOW`, and `CLOTH_SWAP_WORKFLOW`.
- `websockets_api.py`: Must contain a valid implementation of the `get_prompt_images` function.

## File Structure

```
your_project_directory/
├── workflows/
│   ├── expression_editing.json
│   └── cloth_swap.json
├── expression_editing.py
├── cloth_swap.py
├── settings.py
└── websockets_api.py
```

## How to Use

### For Expression Editing Tool

1. **Launch the Application**:
   Run the `expression_editing.py` script:

   ```bash
   python expression_editing.py
   ```

2. **Interact with the Interface**: 
   - Upload an image via the "Input Image" field.
   - Adjust the sliders to define the desired expressions (e.g., Rotate Pitch, Blink, Smile).

3. **View Outputs**:
   After adjustments, the modified images will appear in the output gallery.

### For Cloth Swap API

1. **Set Up**:
   Adjust the `COMFY_UI_PATH` and `CLOTH_SWAP_WORKFLOW` in the `settings.py` file to point to the appropriate directories.

2. **Run the Script**:
   Execute the `cloth_swap.py` to launch the Gradio interface.

## User Interface

### Expression Editing Tool Inputs

- **Input Image**: The image to edit expressions (Type: Image Upload).
- Adjustable sliders for various facial attributes.

### Cloth Swap API Inputs

1. **Input Image**: The main image for clothing swap (Type: numpy array, Height: 500).
2. **Input Image Reference**: The reference image (Type: numpy array, Height: 500).
3. **Target Top Clothes**: Dropdown for specifying swapping (Choices: `True`, `False`).
4. **Target Bottom Clothes**: Dropdown for specifying swapping (Choices: `True`, `False`).

### Outputs

Both tools display processed images after operations in output galleries.

### Interface
1. **cloth swap** : ![!\[alt text\](expression.png)](<Interface demo/cloth_swap.png>)
2. **expression editing** : ![!\[alt text\](expression.png)](<Interface demo/expression.png>)

## References

- ComfyUI Workflow:
1. Expression Editing: [link](https://www.youtube.com/watch?v=q0Vf-ZZsbzI&t=150s)
2. Cloth Swap: [link](https://youtu.be/WXmkLih9jfk?si=6vHraq-s49P4DLPb)

- Thanks to tutorial from YT Code Crafters Corner "Build a Character Portrait Generator with ComfyUI API, Python, WebSocket and Gradio": 
1. https://youtu.be/kmZqoLJ2Dhk?si=DNN4nE5mue5cXzx2
2. https://youtu.be/1iPcRGyj7-E?si=zaAQ88xsFFSI8CBI
3. https://youtu.be/zajODlpfOs4?si=depOaJViLMTNPAnlS