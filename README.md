# DL-FastAPI-App
![FastApi](https://img.shields.io/badge/FastApi-blueviolet?style=for-the-badge&)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-blue?style=for-the-badge&)
![transformers](https://img.shields.io/badge/transformers-green?style=for-the-badge&)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![hugging_face](https://img.shields.io/badge/hugging_face-yellow?style=for-the-badge&logoColor=white)
![PIL](https://img.shields.io/badge/PIL-red?style=for-the-badge&)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Ubuntu](https://img.shields.io/badge/Ubuntu-blue?style=for-the-badge&)

DL application on FastAPI with Docker for transforming any picture according to the specified prompt

## Building the Image
```
docker build . -t fast_api_image_transformer_app
```

## Starting the Docker Container
```
docker run --name mycontainer --gpus all -d -p 80:80 fast_api_image_transformer_app 
```

## About the app
In order to check an interactive documentation, access the following link: ```http://127.0.0.1/docs```

A POST-query consists of two parameters:
- prompt : prompt in which a neccessary transformation is specified as a string
- file : a path to a locally located picture

A GET-query returns the transformed picture as a binary file or error message as a dict

The transformed image can also be seen via the following link: ```http://127.0.0.1/images```

An example of how to communicate with the app can be found in [valid_test.sh](./tests/valid_test.sh)

An example of the original image and transformed image can be found in [images](./images) directory