import os
import sys
import torch
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response

PROJECT_PATH = Path(Path(__file__).parent.absolute()).parent.absolute()
sys.path.append(os.path.join(PROJECT_PATH, "src"))

from fast_api_project import logger
from fast_api_project.utils import read_yaml
from fast_api_project.fast_api_handler import FastAPIHandler



config = read_yaml(Path(os.path.join(PROJECT_PATH, 'src/fast_api_project/config.yaml')))
app = FastAPI()
content = None



@app.post("/images/")
async def create_upload_file(prompt: str = config['default_prompt'], 
                             file: UploadFile = File(...)):
    handler = FastAPIHandler(config=config['fast_api_handler_config'])
    global content
    try:
        content = await file.read()
        logger.info(f"File {file.filename} has been read")

        try:
            content = handler.handle(prompt=prompt, image=content)
            if type(content) == bytes:
                logger.info(f"Image {file.filename} has been successfully transformed")
        except Exception as e:
            content = {'Error message': f"An exception occured while transforming the image {file.filename}: {e}"}
            logger.info(content['Error message'])
    except Exception as e:
        content = {'Error message': f"An exception occured while reading the file {file.filename}: {e}"}
        logger.info(content['Error message'])
    del handler
    torch.cuda.empty_cache()
    


@app.get("/images/")
async def get_modified_file():
    global content
    if type(content) == bytes:
        response = Response(content=content)
        return response
    return content