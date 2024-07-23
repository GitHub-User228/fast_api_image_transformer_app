import torch
from PIL import Image
from fastapi import HTTPException
from diffusers import (
    StableDiffusionInstructPix2PixPipeline,
    EulerAncestralDiscreteScheduler,
)

from fast_api_project import logger
from fast_api_project.config.path_config import path_vars
from fast_api_project.settings import ImageSettings, ModelSettings


class FastAPIHandler:
    """
    Class to transform the input image and return the transformed image

    Attributes:
        image_settings (ImageSettings):
            A class containing settings for image processing
        model_settings (ModelSettings):
            A class containing settings of the model
    """

    def __init__(
        self,
        image_settings: ImageSettings,
        model_settings: ModelSettings,
    ):
        """
        Initializes the FastAPIHandler class with the provided
        configuration.

        Args:
            image_settings (ImageSettings):
                A class containing settings for image processing
            model_settings (ModelSettings):
                A class containing settings of the model
        """
        self.image_settings = image_settings
        self.model_settings = model_settings

    async def setup(self) -> None:
        """
        Sets up the FastAPIHandler class by loading the pre-trained model.
        """
        self.pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
            pretrained_model_name_or_path=path_vars.model_path,
            torch_dtype=torch.float16,
            safety_checker=None,
            offload_folder="offload",
            offload_state_dict=True,
        )
        self.pipe.to(self.model_settings.device)
        self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
            self.pipe.scheduler.config
        )

    async def handle(
        self,
        prompt: str,
        image: Image.Image,
        num_inference_steps: int,
        image_guidance_scale: int,
    ) -> Image.Image:
        """
        Transforms image

        Args:
            prompt (str):
                Promt to be used for transformations
            image (Image.Image):
                Input image
            num_inference_steps (int):
                    Number of inference steps
            image_guidance_scale (int):
                Image guidance scale

        Returns:
            Image.Image:
                Transformed image

        Raises:
            Exception:
                If an exception occurs during the transformation
        """
        try:
            # Transforming the image using the pipeline and provided
            # prompt. There is no need in asyncio since PyTorch can
            # run operations ansynchronously by design
            logger.info(
                f"Transforming image with prompt: '{prompt}', "
                f"inference steps: {num_inference_steps}, "
                f"image guidance scale: {image_guidance_scale}"
                f"image size: {image.size}"
            )
            with torch.no_grad():
                output = self.pipe(
                    prompt=prompt,
                    image=image,
                    num_inference_steps=num_inference_steps,
                    image_guidance_scale=image_guidance_scale,
                ).images[0]
            return output
        except (ValueError, TypeError) as e:
            message = f"Image generation failure"
            logger.error(f"{message}: {str(e)}")
            raise HTTPException(status_code=500, detail=message)
        except torch.cuda.OutOfMemoryError as e:
            message = f"GPU out of memory during image transformation"
            logger.error(f"{message}: {str(e)}")
            raise HTTPException(status_code=500, detail=message)
        except RuntimeError as e:
            message = f"Unexpected error during image transformation"
            logger.error(f"{message}: {str(e)}")
            raise HTTPException(status_code=500, detail=message)
        finally:
            torch.cuda.empty_cache()

    async def close(self) -> None:
        """
        Asynchronous method to clean up resources used by the
        FastAPIHandler.
        """
        # Release any resources held by the pipe
        if hasattr(self, "pipe"):
            del self.pipe

        # Clear CUDA cache
        torch.cuda.empty_cache()

        # Log the closure of the handler
        logger.info("FastAPIHandler resources have been released")
