import os
import sys
import logging
from pathlib import Path



PROJECT_PATH = Path(Path(Path(Path(__file__).parent.absolute()).parent.absolute()).parent.absolute())

# Logger format string
logging_str = "[%(asctime)s: %(lineno)d: %(name)s: %(levelname)s: %(module)s:  %(message)s]"

# Define log directory and log file path
log_dir = os.path.join(PROJECT_PATH, 'logs')
log_file_path = os.path.join(PROJECT_PATH, log_dir, "running_logs.log")

# Check and create log directory if not exists
os.makedirs(log_dir, exist_ok=True)

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create and provide logger instance
logger = logging.getLogger("logger")