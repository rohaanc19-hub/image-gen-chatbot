import os
import io
import requests
from PIL import Image

DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/" + DEFAULT_MODEL


class ImageGenerationError(Exception):
    pass


def get_api_token():
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        raise ImageGenerationError("No Hugging Face API token found. Set HF_API_TOKEN in your .env file.")
    return token


def generate_image(prompt, negative_prompt="", num_images=1):
    token = get_api_token()
    headers = {"Authorization": "Bearer " + token}

    payload = {"inputs": prompt, "parameters": {}}
    if negative_prompt:
        payload["parameters"]["negative_prompt"] = negative_prompt

    images = []
    for _ in range(num_images):
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 503:
            raise ImageGenerationError("The model is still loading on Hugging Face servers. Wait 20 seconds and try again.")

        if response.status_code != 200:
            raise ImageGenerationError("API request failed: " + str(response.status_code) + " " + response.text[:200])

        try:
            image = Image.open(io.BytesIO(response.content))
            images.append(image)
        except Exception as e:
            raise ImageGenerationError("Could not decode image: " + str(e))

    return images
