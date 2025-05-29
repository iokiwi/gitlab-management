import logging
import os
import argparse

import gitlab

from prettytable import PrettyTable
from dotenv import load_dotenv

from groups import manage_group, manage_groups
from projects import manage_project_settings, manage_projects

logging.basicConfig(level=logging.WARNING)
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
        "-r", "--recurse-subprojects", default=False, action="store_true"
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless this flag is passed. E.g. Script is no-op by default.",
    )

    args = parser.parse_args()
    return args


def main() -> None:

    args = get_args()
    load_dotenv()

    GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
    GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
    gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

    if args.projects:
        rows, count = manage_projects(
            gl, list(args.projects), fix=args.fix, limit=args.limit
        )

    if args.groups:
        rows, count = manage_groups(
            gl,
            list(args.groups),
            fix=args.fix,
            limit=args.limit,
            recurse=args.recurse_subprojects,
        )

    table = PrettyTable()
    table.align = "l"
    table.field_names = rows[0].keys()

    for row in rows:
        table.add_row(row.values())

    print(table)


if __name__ == "__main__":
    main()
