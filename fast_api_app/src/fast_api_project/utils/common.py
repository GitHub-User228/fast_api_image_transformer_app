import os
import io
import math
from typing import Dict
from pathlib import Path

import PIL
import yaml
import aioredis
from PIL import Image
from jinja2 import Template
from ensure import ensure_annotations
from PIL import UnidentifiedImageError
from fastapi.testclient import TestClient
from jinja2.exceptions import TemplateError
from fastapi import HTTPException, Response, UploadFile

from fast_api_project import logger
from fast_api_project.config.path_config import path_vars
from fast_api_project.exceptions import EnvironmentVariableUndefined


@ensure_annotations
def read_yaml(path: Path) -> Dict:
    """
    Reads a yaml file, and returns a dict.

    Args:
        path_to_yaml (Path):
            Path to the yaml file

    Returns:
        Dict:
            The yaml content as a dict.

    Raises:
        ValueError:
            If there are missing environment variables
            or the file is not a YAML file
        FileNotFoundError:
            If the file is not found.
        yaml.YAMLError:
            If there is an error parsing the yaml file.
        TemplateError:
            If there is an error rendering the template.
    """
    if path.suffix not in [".yaml", ".yml"]:
        logger.error(f"Invalid file type for YAML file: {path}")
        raise ValueError(f"The file {path} is not a YAML file")
    try:
        with open(path, "r") as file:
            template = Template(
                file.read(), undefined=EnvironmentVariableUndefined
            )
            content = yaml.safe_load(template.render(os.environ))
        logger.info("YAML file has been succesfully read")
        return content
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise
    except TemplateError as e:
        logger.error(f"Error rendering YAML file: {e}")
        raise
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while reading YAML file: {e}"
        )
        raise


async def read_upload_file(file: UploadFile) -> bytes:
    """
    Reads a file from an UploadFile object and returns its content as bytes.

    Args:
        file (UploadFile):
            The UploadFile object containing the file to be read.

    Returns:
        bytes:
            The content of the file as bytes.

    Raises:
        HTTPException:
            If there is an error reading the file.
    """
    try:
        file_content = await file.read()
        logger.info(
            f"File {file.filename} has been read. Size: {file.size} bytes"
        )
        return file_content
    except FileNotFoundError as e:
        message = f"File {file.filename} not found"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=404, detail=message)
    except PermissionError as e:
        message = f"Permission denied for file {file.filename}"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=403, detail=message)
    except IOError as e:
        message = f"Error reading file {file.filename}"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        message = (
            f"An unexpected error occurred while reading file {file.filename}"
        )
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=500, detail=message)


def decode_bytes_to_str(byte_data: bytes, encoding: str = "utf-8") -> str:
    """
    Decodes bytes to a string using the specified encoding.

    Args:
        byte_data (bytes):
            The byte data to be decoded.
        encoding (str, default 'utf-8'):
            The encoding to use for decoding the byte data.

    Returns:
        str:
            The decoded string.

    Raises:
        HTTPException:
            If there is an error during decoding.
    """
    try:
        decoded_str = byte_data.decode(encoding)
        logger.info("Byte data has been decoded to string.")
        return decoded_str
    except UnicodeDecodeError as e:
        message = "Error decoding byte data"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=400, detail=message)
    except LookupError as e:
        message = "Unknown encoding is specified"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        message = "An unexpected error occurred while decoding byte data"
        logger.error(f"{message}: {e}")
        raise HTTPException(status_code=500, detail=message)


def read_file(file_path: Path, mode: str) -> bytes | str:
    """
    Reads a file from the given path and returns its content.

    Args:
        file_path (Path):
            The path to the file to be read.
        mode (str):
            The mode in which to open the file
            ('rb' for binary, 'r' for text).

    Returns:
        bytes | str:
            The content of the file as bytes or string.

    Raises:
        FileNotFoundError:
            If the specified file is not found.
        PermissionError:
            If there are insufficient permissions to read the file.
        IOError:
            If there is an error reading the file.
    """
    try:
        with open(file_path, mode) as file:
            return file.read()
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        raise
    except IOError as e:
        logger.error(f"IO error while reading file: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading file: {e}")
        raise


def read_test_image(image_file: str) -> bytes:
    """
    Reads a test image from a file located in the image data directory.

    Args:
        image_file (str):
            The name of the image file to be read. The file should be
            located in the directory specified by the 'image_data_path'
            environment variable.

    Returns:
        bytes:
            The image data as bytes.
    """
    image_path = Path(os.path.join(path_vars.image_data_path, image_file))
    return read_file(image_path, "rb")


def read_test_prompt(prompt_file: str) -> str:
    """
    Reads a test prompt from a file located in the prompt data directory.

    Args:
        prompt_file (str):
            The name of the prompt file to be read. The file should be
            located in the directory specified by the 'prompt_data_path'
            environment variable.

    Returns:
        str:
            The content of the prompt file, stripped of leading
            and trailing whitespaces.
    """
    prompt_path = Path(os.path.join(path_vars.prompt_data_path, prompt_file))
    return read_file(prompt_path, "r").strip()


def get_response(
    client: TestClient,
    image_file: Path | bytes = Path("valid_image.jpg"),
    prompt_file: Path | str = Path("valid_prompt.txt"),
    num_inference_steps: int | str = 1,
    guidance_scale: float | str = 1,
    image_file_name: str = "image.jpg",
    prompt_file_name: str = "prompt.txt",
    image_mime_type: str = "image/jpeg",
    prompt_mime_type: str = "text/plain",
) -> Response:
    """
    Sends a POST request to the API with an image and a prompt file.

    Args:
        client (TestClient):
            The client used to make the API request.
        image_file (Path | bytes, default Path('valid_image.jpg')):
            The image file to be sent. Can be either a Path object
            pointing to the image file or the image data as bytes.
        prompt_file (Path | str, default Path('valid_prompt.txt')):
            The prompt file to be sent. Can be either a Path object
            pointing to the prompt file or the prompt data as a string.
        num_inference_steps (int | str, default 1):
            The number of inference steps for the image generation
            process.
        guidance_scale (int | str, default 1):
            The guidance scale for the image generation process.
        image_file_name (str, default "image.jpg"):
            The name of the image file in the request.
        prompt_file_name (str, default "prompt.txt"):
            The name of the prompt file in the request
        image_mime_type (str, default "image/jpeg"):
            The MIME type of the image file.
        prompt_mime_type (str, default "text/plain"):
            The MIME type of the prompt file.

    Returns:
        response:
            The response from the API.
    """

    # Reading valid image file
    if isinstance(image_file, Path):
        image_data = read_test_image(image_file)
    elif isinstance(image_file, bytes):
        image_data = image_file

    # Reading valid prompt file
    if isinstance(prompt_file, Path):
        prompt = read_test_prompt(prompt_file)
    else:
        prompt = prompt_file

    # Construct the request files and data
    files = {
        "image": (image_file_name, image_data, image_mime_type),
        "prompt": (prompt_file_name, prompt, prompt_mime_type),
    }
    data = {
        "num_inference_steps": num_inference_steps,
        "image_guidance_scale": guidance_scale,
    }

    # Response from the API
    response = client.post(url="/images", files=files, data=data)
    return response


async def bytes_to_pil_image(image: bytes) -> Image.Image:
    """
    Converts input image in the form of bytes to the form of
    Image.Image

    Args:
        bytes_image (bytes):
            Image as bytes

    Returns:
        Image.Image:
            Image as Image.Image

    Raises:
        HTTPException:
            If the image is not in the correct format
            or there is an error during the conversion
    """
    try:
        output = PIL.Image.open(io.BytesIO(image))
        output = PIL.ImageOps.exif_transpose(output)
        output = output.convert("RGB")
    except PIL.UnidentifiedImageError as e:
        logger.error(f"Unidentified image: {e}")
        raise HTTPException(
            status_code=415,
            detail="Unsupported image file type. Please upload a valid image file.",
        )
    except IOError as e:
        logger.error(f"IO error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. Please upload a valid image file.",
        )
    except Exception as e:
        message = (
            f"Unexpected error occured while converting image"
            f"in the form of bytes to the form of PIL.Image.Image: {str(e)}"
        )
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)
    return output


async def pil_image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Transforms input image in the form of Image.Image
    to bytes

    Args:
        image (Image.Image):
            Input image

    Returns:
        bytes:
            Image as bytes

    Raises:
        HTTPException:
            If the image is not in the correct format
            or there is an error during the conversion
    """
    try:
        with io.BytesIO() as output:
            image.save(output, format=format)
            return output.getvalue()
    except ValueError as e:
        message = f"Unsupported target image format: {format}"
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)
    except UnidentifiedImageError as e:
        message = "Error during image conversion"
        logger.error(f"{message}: {str(e)}")
        raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        message = (
            f"An unexpected error occurred while converting an image to bytes"
        )
        logger.error(f"{message}: {str(e)}")
        raise HTTPException(status_code=500, detail=message)


def calculate_expire_time(pexpire: int) -> int:
    """
    Calculates the expiration time in seconds from a
    provided expiration time in milliseconds.

    Args:
        pexpire (int):
        The expiration time in milliseconds.

    Returns:
        int:
            The expiration time in seconds, rounded up to the
            nearest integer.
    """
    return math.ceil(pexpire / 1000)
