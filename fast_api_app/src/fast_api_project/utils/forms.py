from typing import Annotated

from fastapi import Form

from fast_api_project.settings import get_model_settings


# Form field for specifying the number of inference steps
num_inference_steps_form = Annotated[
    int,
    Form(
        title="Number of inference steps",
        description="Number of inference steps for the model",
        ge=get_model_settings().min_inference_steps,
        le=get_model_settings().max_inference_steps,
    ),
]

# Form field for specifying the image guidance scale
image_guidance_scale_form = Annotated[
    float,
    Form(
        title="Image guidance scale",
        description="Image guidance scale for the model",
        ge=get_model_settings().min_image_guidance_scale,
        le=get_model_settings().max_image_guidance_scale,
    ),
]
