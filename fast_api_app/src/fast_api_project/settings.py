from enum import Enum
from pathlib import Path
from functools import lru_cache
from typing import Set, Literal, Annotated


from pydantic import Field
from fastapi import Depends
from pydantic_settings import BaseSettings

from fast_api_project.utils.common import read_yaml
from fast_api_project.config.path_config import path_vars


# Reading config file
config = read_yaml(Path(f"{path_vars.config_path}/app_config.yaml"))


class AllowedImageTypes(str, Enum):
    """Enum for allowed image MIME types."""

    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"
    GIF = "image/gif"
    WEBP = "image/webp"


class AllowedImageFileExtensions(str, Enum):
    """Enum for allowed image file extenstions."""

    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"


class AllowedPromptTypes(str, Enum):
    """Enum for allowed prompt MIME types."""

    PLAIN = "text/plain"


class AllowedPromptFileExtensions(str, Enum):
    """Enum for allowed prompt file extensions."""

    TEXT = "txt"


class ImageSettings(BaseSettings):
    """
    Settings for the application, which checks the input image file
    size and type.

    Attributes:
        max_file_size (int):
            Maximum allowed file size in bytes.
        allowed_file_types (Set[AllowedImageTypes]):
            Set of allowed file types.
        allowed_file_extensions (Set[AllowedImageFileExtensions]):
            Set of allowed file extensions.
        max_width (int):
            Image width to which the image will be resized if it is
            larger.
        max_height (int):
            Image height to which the image will be resized if it is
            larger.
    """

    max_file_size: int = Field(
        config["constraints"]["image"]["max_file_size"],
        description="Maximum allowed file size in bytes",
        ge=10485760 // 4,
        le=10485760,
    )
    allowed_file_types: Set[AllowedImageTypes] = Field(
        config["constraints"]["image"]["allowed_types"],
        description="List of allowed file types",
        min_items=1,
    )
    allowed_file_extensions: Set[AllowedImageFileExtensions] = Field(
        config["constraints"]["image"]["allowed_extensions"],
        description="List of allowed file extensions",
        min_items=1,
    )
    max_width: int = Field(
        config["constraints"]["image"]["max_width"],
        description=(
            "Image width to which the image will be resized if it is larger"
        ),
        ge=512,
        le=1536,
    )
    max_height: int = Field(
        config["constraints"]["image"]["max_height"],
        description=(
            "Image height to which the image will be resized "
            "if it is larger"
        ),
        ge=512,
        le=1536,
    )


class PromptSettings(BaseSettings):
    """
    Settings for the application, which checks the input prompt.

    Attributes:
        allowed_file_types (Set[AllowedPromptTypes]):
            Set of allowed file types.
        allowed_file_extensions (Set[AllowedPromptFileExtensions]):
            Set of allowed file extensions.
        max_prompt_length (int):
            Maximum allowed prompt length.
    """

    allowed_file_types: Set[AllowedPromptTypes] = Field(
        config["constraints"]["prompt"]["allowed_types"],
        description="List of allowed file types",
        min_items=1,
    )
    allowed_file_extensions: Set[AllowedPromptFileExtensions] = Field(
        config["constraints"]["prompt"]["allowed_extensions"],
        description="List of allowed file extensions",
        min_items=1,
    )
    max_prompt_length: int = Field(
        config["constraints"]["prompt"]["max_length"],
        description="Maximum allowed prompt length",
        ge=1,
        le=256,
    )


class GlobalRequestRateLimitSettings(BaseSettings):
    """
    Settings for global request rate limiting.

    Attributes:
        times (int):
            Maximum number of requests allowed within a time period.
        seconds (Literal[60]):
            Time period in seconds.
    """

    times: int = Field(
        config["constraints"]["request_rate_limit"]["global"]["times"],
        description="Maximum number of requests allowed within a time window",
        ge=1,
        le=10,
    )

    seconds: Literal[60] = Field(
        config["constraints"]["request_rate_limit"]["global"]["seconds"],
        description="Time window in seconds",
    )


class IPRequestRateLimitSettings(BaseSettings):
    """
    Settings for ip request rate limiting.

    Attributes:
        times (int):
            Maximum number of requests allowed within a time period.
        seconds (Literal[60]):
            Time period in seconds.
    """

    times: int = Field(
        config["constraints"]["request_rate_limit"]["per_ip"]["times"],
        description="Maximum number of requests allowed within a time window",
        ge=1,
        le=4,
    )

    seconds: Literal[60] = Field(
        config["constraints"]["request_rate_limit"]["per_ip"]["seconds"],
        description="Time window in seconds",
    )


class ModelSettings(BaseSettings):
    """
    Settings for the model used in the application.

    Attributes:
        hf_model_checkpoint (Literal["timbrooks/instruct-pix2pix"]):
            The checkpoint to use for the model.
        min_inference_steps (int):
            The minimum number of inference steps for the model.
        max_inference_steps (int):
            The maximum number of inference steps for the model.
        min_image_guidance_scale (int):
            The minimum image guidance scale for the model.
        max_image_guidance_scale (int):
            The maximum image guidance scale for the model.
        device (Literal["cuda", "cpu"]):
            The device to use for transformations.
    """

    hf_model_checkpoint: Literal["timbrooks/instruct-pix2pix"] = Field(
        config["model_config"]["hf_model_checkpoint"],
        description="Checkpoint of the model",
    )
    min_inference_steps: int = Field(
        config["constraints"]["model"]["num_inference_steps"]["min"],
        description="Minimum number of inference steps for the model",
        ge=1,
        le=5,
    )
    max_inference_steps: int = Field(
        config["constraints"]["model"]["num_inference_steps"]["max"],
        description="Maximum number of inference steps for the model",
        ge=6,
        le=10,
    )
    min_image_guidance_scale: int = Field(
        config["constraints"]["model"]["image_guidance_scale"]["min"],
        description="Minimum image guidance scale for the model",
        ge=1,
        le=10,
    )
    max_image_guidance_scale: int = Field(
        config["constraints"]["model"]["image_guidance_scale"]["max"],
        description="Maximum image guidance scale for the model",
        ge=11,
        le=20,
    )
    device: Literal["cuda", "cpu"] = Field(
        config["model_config"]["device"],
        description="Device to use for transformations",
    )


@lru_cache
def get_image_settings() -> ImageSettings:
    """
    Returns the image settings.
    """
    return ImageSettings()


@lru_cache
def get_prompt_settings() -> PromptSettings:
    """
    Returns the prompt settings.
    """
    return PromptSettings()


@lru_cache
def get_global_request_rate_limit_settings() -> GlobalRequestRateLimitSettings:
    """
    Returns the global request rate limit settings.
    """
    return GlobalRequestRateLimitSettings()


@lru_cache
def get_ip_request_rate_limit_settings() -> IPRequestRateLimitSettings:
    """
    Returns the IP request rate limit settings.
    """
    return IPRequestRateLimitSettings()


@lru_cache
def get_model_settings() -> ModelSettings:
    """
    Returns the model settings.
    """
    return ModelSettings()


ImageSettingsDependency = Annotated[ImageSettings, Depends(get_image_settings)]
PromptSettingsDependency = Annotated[
    PromptSettings, Depends(get_prompt_settings)
]
ModelSettingsDependency = Annotated[ModelSettings, Depends(get_model_settings)]
