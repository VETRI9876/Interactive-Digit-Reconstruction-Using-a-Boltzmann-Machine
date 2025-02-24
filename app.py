from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import numpy as np
import pickle
import cv2
from PIL import Image
import io
import base64
import os

app = FastAPI()

# Load templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load the trained RBM model
MODEL_PATH = "model/rbm_model.pkl"


with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

weights = model_data["weights"]
visible_bias = model_data["visible_bias"]
hidden_bias = model_data["hidden_bias"]

# Reconstruct digit using the RBM model
def reconstruct_digit(visible_input):
    hidden_probs = 1 / (1 + np.exp(-(np.dot(visible_input, weights) + hidden_bias)))
    hidden_states = hidden_probs > np.random.rand(*hidden_probs.shape)
    visible_reconstructed = 1 / (1 + np.exp(-(np.dot(hidden_states, weights.T) + visible_bias)))
    return visible_reconstructed

# Convert image to 784-dimension vector (flatten it)
def image_to_vector(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    image = cv2.resize(image, (28, 28))  # Resize to 28x28 pixels
    image = image / 255.0  # Normalize to [0, 1]
    return image.flatten()

# Convert vector back to an image and resize it
def vector_to_image(vector):
    image = vector.reshape(28, 28)  # Reshape to 28x28 image
    image = (image * 255).astype(np.uint8)  # Convert to 0-255 range
    image_pil = Image.fromarray(image)
    image_pil = image_pil.resize((220, 237))  # Resize for better visibility
    return image_pil

# Convert an image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, image: UploadFile):
    try:
        # Ensure 'static' directory exists
        if not os.path.exists("static"):
            os.makedirs("static")

        # Read the uploaded image
        file_content = await image.read()
        pil_image = Image.open(io.BytesIO(file_content))
        np_image = np.array(pil_image)

        # Preprocess the image
        pixel_array = image_to_vector(np_image)
        pixel_array = pixel_array.reshape(1, 784)

        # Reconstruct the digit
        reconstructed = reconstruct_digit(pixel_array)
        reconstructed_image = vector_to_image(reconstructed.flatten())

        # Save the reconstructed image
        reconstructed_image_path = "static/reconstructed_image.png"
        reconstructed_image.save(reconstructed_image_path)

        # Convert images to base64
        original_image_base64 = image_to_base64(pil_image)
        reconstructed_image_base64 = image_to_base64(reconstructed_image)

        # Render result.html with base64 images
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "original_image_base64": original_image_base64,
                "reconstructed_image_base64": reconstructed_image_base64,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "result.html", {"request": request, "error": f"An error occurred: {str(e)}"}
        )
