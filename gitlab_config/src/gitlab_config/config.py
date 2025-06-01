from pathlib import Path

import yaml


def load_yaml_config(filename: Path = "config.yaml"):
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
        return config


CONFIG = load_yaml_config()
