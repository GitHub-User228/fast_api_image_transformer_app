from io import BytesIO

import aioredis
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Depends

from fast_api_project import logger
from fast_api_project.utils.validators import (
    prompt_validator_dependency,
    image_validator_dependency,
)
from fast_api_project.utils.forms import (
    num_inference_steps_form,
    image_guidance_scale_form,
)
from fast_api_project.utils.common import pil_image_to_bytes
from fast_api_project.fast_api_handler import FastAPIHandler
from fast_api_project.settings import (
    ImageSettings,
    ModelSettings,
    get_image_settings,
    get_model_settings,
)
from fast_api_project.utils.limiters import global_limiter, ip_limiter


# Empty variable to store the handler
handler = None


@asynccontextmanager
async def lifespan(
    app: FastAPI,
    image_settings: ImageSettings = get_image_settings(),
    model_settings: ModelSettings = get_model_settings(),
):
    """
    This function is an asynchronous lifespan event handler for the
    FastAPI application.

    It initializes a Redis client and passes it to the FastAPILimiter
    to set up rate limiting for the application. The
    `FastAPILimiter.init()` function is called withx the Redis client
    to initialize the rate limiting functionality for the
    FastAPIapplication.

    It also initializes the FastAPIHandler with the configuration
    settings provided in the corresponding objects. The
    `FastAPIHandler.setup()` function is called to initialize the
    handler.

    Finally, in any case, the handler is closed using the
    `FastAPIHandler.close()` function.

    Args:
        app (FastAPI):
            The FastAPI application instance.
        image_settings (ImageSettings):
            Image settings.
        prompt_settings (PromptSettings):
            Prompt settings.

    Raises:
        HTTPException:
            If there is an error during the setup of the application.
    """
    global handler
    try:
        # Initialising the Redis client
        redis_client = aioredis.from_url(
            "redis://redis:6379", encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_client)
        # Initialising the FastAPIHandler
        handler = FastAPIHandler(image_settings, model_settings)
        await handler.setup()
        logger.info("FastAPIHandler initialized successfully")
        yield
    except aioredis.RedisError as e:
        message = f"Redis error: {str(e)}"
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        message = f"Unexpected error: {str(e)}"
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)
    finally:
        # Closing the FastAPIHandler
        if handler:
            await handler.close()


# Initialisation of the FastAPI app
app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(global_limiter), Depends(ip_limiter)],
)


@app.post(
    "/images/",
    response_model=None,
)
async def transform_image(
    validated_prompt: prompt_validator_dependency,
    validated_image: image_validator_dependency,
    num_inference_steps: num_inference_steps_form,
    image_guidance_scale: image_guidance_scale_form,
) -> StreamingResponse:
    """
    This function handles the POST request to the '/images/' endpoint.
    It transforms an image using a prompt and model parameters, and
    returns the transformed image.

    Args:
        validated_prompt (str):
            Dependency which reads the prompt and returns the validated
            prompt.
        validated_image (Image.Image):
            Dependency which reads the image and returns the validated
            image.
        num_inference_steps (int):
            Number of inference steps for the model.
        image_guidance_scale (float):
            Image guidance scale for the model.

    Returns:
        StreamingResponse:
            A FastAPI StreamingResponse object containing the processed
            image

    Raises:
        HTTPException:
            Raised in case if there is:
                - an error during the reading & validation of the image
                - an error during the reading & validation of the prompt
                - an error during the reading & validation of the model
                    parameters
                - an error during the transformation of the image
                - an unexpected error
    """

    # Initialising the content and handler as global variables
    global handler

    # Transformisng the image using prompt
    try:
        # Transforming the image asynchronously using FastAPIHandler
        content = await handler.handle(
            num_inference_steps=num_inference_steps,
            image_guidance_scale=image_guidance_scale,
            prompt=validated_prompt,
            image=validated_image,
        )
        content = await pil_image_to_bytes(image=content)
        logger.info(f"Image has been successfully transformed")
        # Returning the transformed image
        return StreamingResponse(BytesIO(content), media_type="image/png")
        # return Response(content=content, media_type="image/png")
    except Exception as e:
        message = f"Unexpected error: {str(e)}"
        logger.error(message)
        raise HTTPException(status_code=500, detail=message)
