import argparse
import logging
import os

import gitlab
from dotenv import load_dotenv
from prettytable import PrettyTable

from gitlab_config import config
from gitlab_config.groups import get_projects_for_groups
from gitlab_config.projects import manage_projects

log_level = getattr(logging, os.environ.get("LOG_LEVEL", "WARNING").upper())
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--groups", nargs="+", help="Groups to manage")
    group.add_argument("--projects", nargs="+", help="Projects to manage")

    parser.add_argument(
        "--limit", type=int, help="Stop after doing <n> projects. Helpful for testing"
    )

    parser.add_argument(
        "-r",
        "--recursive",
        default=False,
        action="store_true",
        help="Recursively get projects from subgroups",
    )

    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless this flag is passed. E.g. Script is no-op by default.",
    )

    return parser.parse_args()


def main() -> None:
    args = get_args()
    load_dotenv()

    GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
    GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")

    gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

    if args.projects:
        project_ids = args.projects

    if args.groups:
        projects = get_projects_for_groups(
            gl,
            list(args.groups),
            limit=args.limit,
            recurse=args.recursive,
        )
        project_ids = [project.id for project in projects]

    rows = manage_projects(gl, project_ids, config, fix=args.fix)

    table = PrettyTable()
    table.align = "l"
    table.field_names = rows[0].keys()

    for row in rows:
        table.add_row(row.values())

    print(table)


if __name__ == "__main__":
    main()
