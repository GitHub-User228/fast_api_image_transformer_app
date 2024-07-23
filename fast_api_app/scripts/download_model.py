#!/usr/local/bin/python3

from fast_api_project.settings import ModelSettings
from fast_api_project.utils.loader import download_model


def main():
    download_model(settings=ModelSettings())


if __name__ == "__main__":
    main()
