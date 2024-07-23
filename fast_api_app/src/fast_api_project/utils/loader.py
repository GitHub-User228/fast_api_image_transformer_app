from typing import Generator

import torch
from transformers import HTTPError
from contextlib import contextmanager
from diffusers import StableDiffusionInstructPix2PixPipeline

from fast_api_project import logger
from fast_api_project.settings import ModelSettings
from fast_api_project.config.path_config import path_vars


@contextmanager
def model_context(
    settings: ModelSettings,
) -> Generator[StableDiffusionInstructPix2PixPipeline, None, None]:
    """
    Context manager for loading a model.

    Args:
        settings (ModelSettings):
            The model settings for the application.

    Yields:
        StableDiffusionInstructPix2PixPipeline:
            The loaded model.

    Raises:
        OSError:
            If there is an error accessing local files.
        HTTPError:
            If there is an error downloading the model from the Hub.
        ValueError:
            If there is an invalid model configuration specified.
        RuntimeError:
            If there is an error loading the model.
    """
    model = None
    try:
        model = StableDiffusionInstructPix2PixPipeline.from_pretrained(
            pretrained_model_name_or_path=settings.hf_model_checkpoint,
            torch_dtype=torch.float16,
            safety_checker=None,
            offload_folder="offload",
            offload_state_dict=True,
            cache_dir=path_vars.model_path,
            local_files_only=False,
        )
        yield model
    except OSError as e:
        logger.error(f"Error accessing local files: {str(e)}")
        raise
    except HTTPError as e:
        logger.error(f"Error downloading model from the Hub: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Invalid model configuration: {str(e)}")
        raise
    except RuntimeError as e:
        logger.error(f"Model loading failed: {str(e)}")
        raise
    finally:
        if model:
            del model
            torch.cuda.empty_cache()


def download_model(settings: ModelSettings) -> None:
    """
    Downloads a Hugging Face model to the specified directory

    Args:
        settings (ModelSettings):
            The model settings for the application.

    Raises:
        OSError:
            If there is an error saving the model locally.
        Exception:
            If there is an unexpected error during the model
            download and save process.
    """
    logger.info("Starting model download process")
    try:
        with model_context(settings=settings) as model:
            logger.info(
                "Model loaded successfully, saving it to local directory"
            )
            model.save_pretrained(path_vars.model_path)
            logger.info("Model saved successfully")
    except OSError as e:
        logger.error(f"Error saving model locally: {str(e)}")
        raise
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during model download and "
            f"save: {str(e)}"
        )
        raise
