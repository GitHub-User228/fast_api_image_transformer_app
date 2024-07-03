import os
import io
import cv2
import PIL
import numpy as np
from pathlib import Path
from ensure import ensure_annotations

import torch
from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler

from fast_api_project import logger, PROJECT_PATH



class FastAPIHandler:
    """
    Class to transform the input image and return the transformed image
    """
    
    @ensure_annotations
    def __init__(self, config: dict):
        """
        Initialization of the corresponding object

        Args:
            config (dict): dictionary with the necessary config
        
        Attributes:
            config (dict): dictionary with the necessary config
            is_ok_ (bool): whether the image was succesfully transformed
            pipe (object): object of the model that transforms the image
        """
        self.config = config
        self.is_ok_ = True
        path_to_model = os.path.join(PROJECT_PATH, 'models')
        self.pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(pretrained_model_name_or_path=path_to_model, 
                                                                           torch_dtype=torch.float16, 
                                                                           safety_checker=None, 
                                                                           offload_folder="offload", 
                                                                           offload_state_dict = True)
        self.pipe.to(self.config['device'])
        self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
    
    @ensure_annotations
    def bytes_to_pil_image(self, 
                           bytes_image: bytes) -> PIL.Image.Image | str:
        """
        Converts input image in the form of bytes to the form of PIL.Image.Image

        Args:
            bytes_image (bytes): image as bytes

        Returns:
            output (PIL.Image.Image / str): image as PIL.Image.Image (or error message if an exception is raised)
        """
        try:
            output = PIL.Image.open(io.BytesIO(bytes_image))
            output = PIL.ImageOps.exif_transpose(output)
            output = output.convert("RGB")
        except Exception as e:
            self.is_ok_ = False
            output = f'An exception occured while converting an image to PIL.Image.Image: {e}'    
            logger.info(output)
        return output

    @ensure_annotations
    def transform_image(self, 
                        prompt: str,
                        image: PIL.Image.Image) -> PIL.Image.Image | str:
        """
        Transforms image

        Args:
            prompt (str): promt to be used for transformations
            image (PIL.Image.Image): input image

        Returns:
            output (PIL.Image.Image): transformed image
        """
        image.thumbnail((self.config['max_width'], self.config['max_height']))
        try:
            with torch.no_grad():
                output = self.pipe(prompt=prompt, 
                                   image=image,
                                   num_inference_steps=self.config['num_inference_steps'],
                                   image_guidance_scale=self.config['image_guidance_scale']).images[0]
        except Exception as e:
            self.is_ok_ = False
            output = f'An exception occured while transforming the image: {e}'    
            logger.info(output)
        return output

    @ensure_annotations    
    def pil_image_to_bytes(self, image: PIL.Image.Image) -> bytes | str:
        """
        Transforms input image in the form of PIL.Image.Image to bytes

        Args:
            image (PIL.Image.Image): input image

        Returns:
            output (bytes / str): image as bytes (or error message if it was not possible to encode)
        """
        output = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        success, output = cv2.imencode('.png', output)
        if not success:
            output = "Unable to encode the transformed image"
            logger.info(output)
            self.is_ok_ = False
        if self.is_ok_:
            output = output.tobytes()
        return output

    @ensure_annotations   
    def handle(self, 
               prompt: str,
               image: bytes) -> bytes | dict:
        """
        Transforms the input image in the form of bytes and returns the 
        transformed image using the specified promt

        Args:
            prompt (str): promt to be used for transformations
            image (bytes): image as bytes

        Returns:
            response (bytes | dict): transformed image as bytes (or dict in case if an error is occured)
        """
        response = self.bytes_to_pil_image(image)
        if not self.is_ok_:
            return {'Error message': response}
        response = self.transform_image(prompt=prompt, image=response)
        if not self.is_ok_:
            return {'Error message': response}
        response = self.pil_image_to_bytes(response)
        if not self.is_ok_:
            return {'Error message': response}
        self.is_ok_ = True
        return response