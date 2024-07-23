import os
from pathlib import Path

import yaml
import coloredlogs
import logging.config
from jinja2 import Template
from aiologger import Logger
from jinja2.exceptions import TemplateError

from fast_api_project.config.path_config import path_vars
from fast_api_project.exceptions import EnvironmentVariableUndefined


# Reading config file
try:
    if os.getenv("CONFIG_PATH") is None:
        raise EnvironmentVariableUndefined("CONFIG_PATH")
    with open(
        Path(f"{path_vars.config_path}/logging_config.yaml"), "r"
    ) as file:
        template = Template(
            file.read(), undefined=EnvironmentVariableUndefined
        )
    rendered_yaml = template.render(os.environ)
    config = yaml.safe_load(rendered_yaml)
    coloredlogs.install()
except FileNotFoundError as e:
    raise FileNotFoundError("Unable to locate the logging configuration file")
except yaml.YAMLError as e:
    raise yaml.YAMLError(f"Error parsing logging configuration file: {e}")
except TemplateError as e:
    raise TemplateError(f"Error rendering logging configuration file: {e}")
except Exception as e:
    raise Exception(
        f"Unexpected error occurred while reading logging configuration "
        f"file: {e}"
    )

# Check and create log directory if not exists
os.makedirs(path_vars.log_path, exist_ok=True)

# Basic logging configuration
logging.config.dictConfig(config)

# Create and provide logger instance
logger = logging.getLogger("fast_api_project")
# logger = Logger.with_default_handlers(name="fast_api_project")
