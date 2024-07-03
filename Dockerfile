FROM python:3.10.14

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

RUN python3 scripts/download_model.py

CMD ["fastapi", "run", "app/main.py", "--port", "80"]