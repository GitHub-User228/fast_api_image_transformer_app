import io
from typing import Tuple
from base64 import b64encode

import flask
import requests

from frontend_app.config.path_config import path_vars


def get_response(
    request: flask.Request,
) -> Tuple[requests.Response, io.BytesIO, dict]:
    """
    Sends a request to the FastAPI endpoint with the provided image,
    prompt, and model parameters, and returns the response, the
    original image and the form data which was inputed by the user.

    Args:
        request (flask.Request):
            The Flask request object containing the form and file data.

    Returns:
        Tuple[requests.Response, io.BytesIO, dict]:
            - The response from the FastAPI endpoint
            - The original image stored in RAM.
            - The form data submitted in the request.
    """

    # Get form and file data from the request
    prompt = request.form.get("prompt")
    file = request.files.get("file")
    num_inference_steps = request.form.get("num_inference_steps")
    image_guidance_scale = request.form.get("image_guidance_scale")

    form_data = {
        "prompt": prompt,
        "num_inference_steps": num_inference_steps,
        "image_guidance_scale": image_guidance_scale,
    }

    # Save and read the original image into memory
    original_image = io.BytesIO()
    file.save(original_image)
    original_image.seek(0)

    # Prepare the form data and file data for the request
    data = {
        "num_inference_steps": int(num_inference_steps),
        "image_guidance_scale": float(image_guidance_scale),
    }
    files = {
        "image": (file.filename, original_image, file.content_type),
        "prompt": ("prompt.txt", prompt, "text/plain"),
    }

    # Send the POST request to the FastAPI endpoint with
    # the form and file data
    response = requests.post(
        path_vars.fast_api_endpoint, files=files, data=data
    )
    return response, original_image, form_data


def render_response(
    response: requests.Response,
    original_image: io.BytesIO,
    template_name: str,
    form_data: dict,
) -> flask.Response:
    """
    Renders the response from a request, saving the original and
    transformed images to the file system and returning a rendered
    template with the image URLs.

    Args:
        response (requests.Response):
            The response object from the request.
        original_image (io.BytesIO):
            The original image stored in RAM.
        template_name (str):
            The name of the template to render.
        form_data (dict):
            The form data submitted by the user.

    Returns:
        flask.Response:
            The rendered template response.
    """
    # Check if the request was successful
    if response.status_code == 200:

        # Save and read the transformed image into memory
        transformed_image = io.BytesIO(response.content)
        transformed_image.seek(0)

        # Forming the URLs for the original and transformed images
        original_image_url = (
            f"data:image/png;base64,"
            f"{b64encode(original_image.getvalue()).decode('utf-8')}"
        )
        transformed_image_url = (
            f"data:image/png;base64,"
            f"{b64encode(transformed_image.getvalue()).decode('utf-8')}"
        )

        # Render the template with the images' URLs and the form data
        # and return the response
        return flask.render_template(
            template_name,
            original_image_url=original_image_url,
            image_url=transformed_image_url,
            form_data=form_data,
        )
    # If the request was not successful, display an error message
    else:
        error_message = response.json()["detail"]
        if isinstance(error_message, str):
            error_message = error_message
        else:
            error_message = error_message[0]["msg"]
        return flask.render_template(
            template_name,
            error_message=error_message,
            form_data=form_data,
        )
