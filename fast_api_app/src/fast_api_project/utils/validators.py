import re
from typing import Annotated

from PIL import Image
from fastapi import UploadFile, HTTPException, Depends

from fast_api_project import logger
from fast_api_project.settings import (
    ImageSettingsDependency,
    PromptSettingsDependency,
    ModelSettingsDependency,
)
from fast_api_project.utils.common import (
    bytes_to_pil_image,
    read_upload_file,
    decode_bytes_to_str,
)


async def validate_image(
    image: UploadFile, settings: ImageSettingsDependency
) -> Image.Image:
    """
    Validates the uploaded image based on its content type and size and
    returns the image if it is valid. In case of bigger image (in terms
    of width and height) it is downscaled to the maximum width and
    height.

    Args:
        image (UploadFile):
            The uploaded image to be validated.
        settings (ImageSettings):
            The image settings for the application.

    Returns:
        Image.Image:
            The validated image

    Raises:
        HTTPException:
            Raised in case when:
                - content type is not in the allowed file types
                - file extension is not in the allowed file extensions
                - the image size is greater than the maximum allowed
                  file size
                - an error occurs while reading the image file
                - an error occurs while resizing the image
                - an unexpected error occurs
    """

    # Checking if the image content type is in the allowed file types
    if image.content_type not in settings.allowed_file_types:
        message = (
            f"ERROR 400. Invalid image file type: {image.content_type} "
            f"while allowed image types are "
            f"{list(map(lambda x: x.value, settings.allowed_file_types))}"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Check if the prompt file extension is in the allowed extensions
    if (
        image.filename.split(".")[-1].lower()
        not in settings.allowed_file_extensions
    ):
        message = (
            f"ERROR 400. Invalid image file extension: {image.filename} "
            f"while allowed extensions are "
            f"{list(map(lambda x: x.value, settings.allowed_file_extensions))}"
        )
        logger.error(message)
        raise HTTPException(status_code=422, detail=message)

    # Checking if the image size is <= maximum allowed file size
    if image.size > settings.max_file_size:
        message = (
            f"ERROR 400. Image too large: {image.size} bytes while "
            f"maximum allowed image size is {settings.max_file_size} bytes"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Reading the image
    content = await read_upload_file(image)

    # Converting the image bytes to a PIL image
    content = await bytes_to_pil_image(image=content)

    # Reducing the size of the image to the maximum size
    content.thumbnail((settings.max_width, settings.max_height))

    return content


async def validate_prompt(
    prompt: UploadFile, settings: PromptSettingsDependency
) -> str:
    """
    Validates and sanitizes the input prompt based on its length and
    content. If the prompt is valid, it returns the sanitized prompt.

    Args:
        prompt (UploadFile):
            The input prompt file to be validated and sanitized.
        settings (PromptSettings):
            The prompt settings for the application.

    Returns:
        str:
            The sanitized prompt

    Raises:
        HTTPException:
            Raised in case when the prompt has:
                - content type not in the allowed file types
                - file extension is not in the allowed file extensions
                - an error reading or decoding its content
                - length greater than the maximum allowed prompt length
                - content that contains harmful characters
    """

    # Checking if the prompt content type is in the allowed file types
    if prompt.content_type not in settings.allowed_file_types:
        message = (
            f"ERROR 400. Invalid prompt file type: {prompt.content_type} "
            f"while allowed file types are "
            f"{list(map(lambda x: x.value, settings.allowed_file_types))}"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Check if the prompt file extension is in the allowed extensions
    if (
        not prompt.filename.split(".")[-1].lower()
        in settings.allowed_file_extensions
    ):
        message = (
            f"ERROR 400. Invalid prompt file extension: {prompt.filename} "
            f"while allowed extensions are "
            f"{list(map(lambda x: x.value, settings.allowed_file_extensions))}"
        )
        logger.error(message)
        raise HTTPException(status_code=422, detail=message)

    # Reading the prompt content
    prompt_content = await read_upload_file(file=prompt)

    # Decode and strip the prompt
    prompt_text = decode_bytes_to_str(byte_data=prompt_content)
    prompt_text = prompt_text.strip()

    # Sanitize the prompt
    sanitized_prompt = re.sub(r"[<>&;]", "", prompt_text)

    # Check if the prompt is too long
    if len(sanitized_prompt) > settings.max_prompt_length:
        message = (
            f"ERROR 400. Prompt too long: {len(sanitized_prompt)} characters "
            f"while the maximum allowed length is "
            f"{settings.max_prompt_length} characters"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Check if the prompt was modified during sanitization
    if sanitized_prompt != prompt_text:
        message = (
            f"Prompt was sanitized. Original: '{prompt_text}', "
            f"Sanitized: '{sanitized_prompt}'"
        )
        logger.warning(message)
        raise HTTPException(
            status_code=400,
            detail="Unsafe prompt. Avoid using characters: <>&;",
        )

    return sanitized_prompt


async def validate_model_parameters(
    settings: ModelSettingsDependency,
    num_inference_steps: int = 10,
    image_guidance_scale: int = 7,
) -> dict[int]:
    """
    Validates the model parameters based on their values and settings.
    Specifically, it checks if the number of inference steps and image
    guidance scale are within the allowed ranges.

    Args:
        num_inference_steps (int, default 10):
            The number of inference steps to be validated.
        image_guidance_scale (int, default 7):
            The image guidance scale to be validated.
        settings (ModelSettings):
            The model settings for the application.

    Returns:
        dict[int]:
            A dict containing the validated num_inference_steps and
            image_guidance_scale.
    """

    # Check the type of arguments
    if not isinstance(num_inference_steps, int):
        message = f"ERROR 400. Number of inference steps must be an integer"
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)
    if not isinstance(image_guidance_scale, int):
        message = f"ERROR 400. Image guidance scale must be an integer"
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Check if the number of inference steps is within allowed range
    if (num_inference_steps < settings.min_inference_steps) or (
        num_inference_steps > settings.max_inference_steps
    ):
        message = (
            f"ERROR 400. Number of inference steps is out of range "
            f"{settings.min_inference_steps}-"
            f"{settings.max_inference_steps}"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    # Check if the image guidance scale is within allowed range
    if (image_guidance_scale < settings.min_image_guidance_scale) or (
        image_guidance_scale > settings.max_image_guidance_scale
    ):
        message = (
            f"ERROR 400. Image guidance scale is out of range "
            f"{settings.min_image_guidance_scale}-"
            f"{settings.max_image_guidance_scale}"
        )
        logger.error(message)
        raise HTTPException(status_code=400, detail=message)

    return {
        "num_inference_steps": num_inference_steps,
        "image_guidance_scale": image_guidance_scale,
    }


# Defining the dependencies for the validators
prompt_validator_dependency = Annotated[str, Depends(validate_prompt)]
image_validator_dependency = Annotated[Image.Image, Depends(validate_image)]
model_parameters_validator_dependency = Annotated[
    dict[int], Depends(validate_model_parameters)
]
