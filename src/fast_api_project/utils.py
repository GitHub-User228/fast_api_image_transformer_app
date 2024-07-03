import os
import yaml
from ensure import ensure_annotations
from pathlib import Path

import torch
from diffusers import StableDiffusionInstructPix2PixPipeline

from fast_api_project import logger, PROJECT_PATH



@ensure_annotations
def read_yaml(path_to_yaml: Path, 
              verbose: bool = True) -> dict:
    """
    Reads a yaml file, and returns a dict.

    Args:
        path_to_yaml (Path): Path to the yaml file.
        verbose (bool): Whether to show logger's messages.

    Returns:
        content (dict): The yaml content as a dict.
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            if verbose: logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return content
    except ValueError:
        logger.info("Value exception: empty yaml file")
        raise ValueError("yaml file is empty")
    except Exception as e:
        logger.info(f"An exception has occurred: {e}")
        raise e
    


def download_model():
    """
    Download a Hugging Face model to the specified directory
    """
    config = read_yaml(Path(os.path.join(PROJECT_PATH, 'src/fast_api_project/config.yaml')))['fast_api_handler_config']
    model = StableDiffusionInstructPix2PixPipeline.from_pretrained(pretrained_model_name_or_path=config['model_checkpoint'], 
                                                                   torch_dtype=torch.float16, 
                                                                   safety_checker=None, 
                                                                   offload_folder="offload", 
                                                                   offload_state_dict = True)
    model.save_pretrained(os.path.join(PROJECT_PATH, 'models'))
    del model
    torch.cuda.empty_cache()