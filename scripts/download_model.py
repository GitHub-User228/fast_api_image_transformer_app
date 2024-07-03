import os
import sys
from pathlib import Path

PROJECT_PATH = Path(Path(__file__).parent.absolute()).parent.absolute()

sys.path.append(os.path.join(PROJECT_PATH, "src"))

from fast_api_project.utils import download_model



download_model()