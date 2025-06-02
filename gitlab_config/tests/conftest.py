import os

import pytest

@pytest.fixture(autouse=True)
def setup_config_file(monkeypatch):
    """Create a config.yaml file before tests and clean it up after."""

    monkeypatch.setenv("GITLAB_CONFIG_YAML_FILEPATH", "test_config.yaml")

    config_content = """
GITLAB_CONFIG_LOG_LEVEL: "WARNING"
GITLAB_URL: "https://gitlab.com"

default:
    squash_option: default_on
    remove_source_branch_after_merge: True
    merge_method: "merge"
    only_allow_merge_if_pipeline_succeeds: True
    prevent_secrets: True
    merge_access_levels: "Developers + Maintainers"
"""

    # Create config.yaml in current working directory
    test_file = os.environ["GITLAB_CONFIG_YAML_FILEPATH"]
    config_path = os.path.join(os.getcwd(), test_file)

    # Setup: Create the file
    with open(config_path, "w") as f:
        f.write(config_content)

    yield config_path

    # Teardown: Delete the file
    if os.path.exists(config_path):
        os.remove(config_path)
