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
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
