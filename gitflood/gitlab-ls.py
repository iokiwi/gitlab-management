import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

access_token = os.environ["GITLAB_TOKEN"]


def ls(group):
    gitlab_domain = "https://gitlab.com"
    url = f"{gitlab_domain}/api/v4/groups/{group}/projects?per_page=100"
    headers = {"PRIVATE-TOKEN": access_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = json.loads(response.text)
        for project in projects:
            # Skip archive and hydra-oas
            if not project["archived"] and not project["path"] == "hyrda-oas":
                print(project["ssh_url_to_repo"])
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    pass