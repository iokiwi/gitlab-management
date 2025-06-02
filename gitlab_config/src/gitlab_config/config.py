import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_yaml_config(filename: Path = "config.yaml"):
    try:
        with open(filename, "r") as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file '{filename}' not found. Please ensure '{filename}' exists."
        )
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse '{filename}' as YAML: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error reading config file '{filename}': {str(e)}")


def get_config(filename: Path | None = None):
    if filename is None:
        filename = os.environ.get("GITLAB_CONFIG_YAML_FILEPATH", "config.yaml")

    config = load_yaml_config(filename)
    config["GITLAB_TOKEN"] = os.environ.get("GITLAB_TOKEN")
    return config
