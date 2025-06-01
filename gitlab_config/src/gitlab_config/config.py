import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_yaml_config(filename: Path = "config.yaml"):
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
        return config


CONFIG = load_yaml_config()
# LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
# GITLAB_CONFIG_LOG_LEVEL = os.environ.get("GITLAB_CONFIG_LOG_LEVEL", LOG_LEVEL)
# GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
