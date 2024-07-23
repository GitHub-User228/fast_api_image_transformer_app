# DL-FastAPI-App
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![transformers](https://img.shields.io/badge/transformers-green?style=for-the-badge&)
![PIL](https://img.shields.io/badge/PIL-red?style=for-the-badge&)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)


DL application on FastAPI with Docker for transforming any picture according to the specified prompt

## Description

The DL-FastAPI-App is a deep learning application built using FastAPI and Docker. It allows users to transform images based on specified textual prompts. The application leverages state-of-the-art models from Hugging Face to perform image transformations, making it a useful tool for various image processing tasks.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Docker:** Make sure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
- **Docker Compose:** Ensure Docker Compose is installed. It usually comes with Docker Desktop, but you can also install it separately by following the instructions on the [Docker Compose installation page](https://docs.docker.com/compose/install/).
- **Git:** (Optional) If you want to clone the repository, make sure Git is installed. You can download it from [Git's official website](https://git-scm.com/).
- **NVIDIA GPU**: The application utilizes NVIDIA GPU for accelerated image processing. Ensure you have a compatible NVIDIA GPU installed on your machine.


### Key Features

- **Image Transformation:** Transform images according to user-defined prompts using advanced deep learning models.
- **FastAPI Integration:** Provides a robust and high-performance API for handling image transformation requests.
- **Dockerized Deployment:** Easily deploy the application using Docker and Docker Compose.
- **Caching with Redis:** Utilizes Redis for caching requests to improve performance and enable rate limiting.
- **Interactive Documentation:** Access interactive API documentation via Swagger UI.

### Example Use Cases

- **Artistic Style Transfer:** Apply artistic styles to images based on textual descriptions.
- **Creative Image Generation:** Generate creative and unique images by providing imaginative prompts based on the provided image


## Repository Structure

**[docker-compose.yml](./docker-compose.yaml)**: This file contains the configuration for the Docker Compose service. It specifies the services and their dependencies:
   - `redis`: The Redis service for caching requests (used for request rate limiting).
   - `fast_api_app`: Service with the FastAPI app, which is built using [Dockerfile](./fast_api_app/Dockerfile)

**[fast_api_app](./fast_api_app)**: This directory contains the main FastAPI app and the required code and configuration files

1. **[Dockerfile](./fast_api_app/Dockerfile)**: This Dockerfile sets up Ubuntu with Python and all necessary packages [requirements.txt](./fast_api_app/requirements.txt). Also downloads [transformer model](https://huggingface.co/timbrooks/instruct-pix2pix) from Hugging Face. Lastly, the corresponding service starts with the specified entrypoint

2. **[fast_api_project](./fast_api_app/src/fast_api_project)**: This directory contains Python source code and configuration files requried for the app.

3. **[logs](./fast_api_app/src/logs)**: This directory contains log files

4. **[main.py](./fast_api_app/app/main.py)**: Implementation of the functions which handle requests using FastAPI
   
    A POST-request consists of two parameters:
    - prompt : prompt in which a neccessary transformation is specified as a string
    - file : a path to a locally located picture
    
    It returns the transformed picture as a binary file

5. **[data](./fast_api_app/data)**: Directory with test image and prompt data (used internally for testing)

6. **[.env](./fast_api_app/env/.env)** : Environment file with the necessary configuration parameters

7. **[tests](./fast_api_app/tests)**: Directory with a python script which tests the app. Potentially, tests can be elaborated further to make sure that all parts of the app work correctly

8. **[scripts](./fast_api_app/scripts)**: Directory with [entrypoint.sh](./fast_api_app/scripts/entrypoint.sh) script which starts the FastAPI app and [download_model.py](./fast_api_app/scripts/download_model.py) script which downloads the model from Hugging Face and saves it in the corresponding directory at the start of the service (in case it is not present)

## Getting Started

In order to start the app, follow the following steps:

1. Building the image
    ```
    docker compose build
    ```

2. Starting all services
    ```
    docker compose up
    ```

In order to check an interactive documentation, access the following link: ```http://127.0.0.1/docs```

There you can find specific `curl` commands for sending requests to the app

## Running Tests

To ensure that the application is working correctly, you can run the provided test. Follow these steps to run the tests:

1. **Build and Start the Services:**
    Ensure that the Docker services are up and running as described in the "Getting Started" section.
    ```
    docker compose build
    docker compose up
    ```

2. **Access the FastAPI Container:**
    Open a new terminal window and access the running FastAPI container.
    ```
    docker exec -it <fast_api_container_name> /bin/bash
    ```
    Replace `<fast_api_container_name>` with the actual name of your FastAPI container. You can find the container name by running `docker ps`.

3. **Navigate to the Tests Directory:**
    Inside the container, navigate to the **[tests](./fast_api_app/tests)** directory.
    ```
    cd /home/fast_api_app/tests
    ```

4. **Run the Tests:**
    Execute the test script using Python.
    ```
    python3 unit_test.py
    ```

5. **Review Test Results:**
    Review the output of the test script to ensure that all tests pass successfully.

## Troubleshooting

If you encounter any issues while setting up or running the application, here are some common problems and their solutions:

1. **Docker Compose Build Fails:**
   - **Solution:** Ensure that Docker and Docker Compose are installed correctly. Verify that you have an active internet connection to download necessary images and packages.

2. **Service Fails to Start:**
   - **Solution:** Check the logs for any error messages. Logs can be found in the [logs](./fast_api_app/src/logs) directory or in the console inside the corresponding service. Common issues include missing environment variables or incorrect configurations in the [.env](./fast_api_app/env/.env) file or files inside [config](./fast_api_app/src/fast_api_project/config/) directory.

3. **Model Download Issues:**
   - **Solution:** Ensure that the Hugging Face model URL is accessible and that you have internet access. You can manually download the model and place it in the appropriate directory if automatic download fails.

4. **FastAPI Endpoint Not Accessible:**
   - **Solution:** Verify that the FastAPI service is running by checking the Docker container status. Ensure that the port specified in the [docker-compose.yml](./docker-compose.yaml) file is not being used by another application.

5. **Rate Limiting Issues:**
   - **Solution:** If you encounter rate limiting issues, check the Redis service status. Ensure that Redis is running and properly configured in the [docker-compose.yml](./docker-compose.yaml) file.
