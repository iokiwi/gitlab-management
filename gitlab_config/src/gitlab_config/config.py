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
        raise FileNotFoundError(f"Config file '{filename}' not found. Please ensure '{filename}' exists.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse '{filename}' as YAML: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error reading config file '{filename}': {str(e)}")


CONFIG = load_yaml_config()
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
