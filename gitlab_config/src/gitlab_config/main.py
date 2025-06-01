import argparse
import logging

import gitlab
from prettytable import PrettyTable

from gitlab_config import config
from gitlab_config.groups import get_projects_for_groups
from gitlab_config.projects import manage_projects

log_level = getattr(logging, config.CONFIG["GITLAB_CONFIG_LOG_LEVEL"], logging.WARNING)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Groups subcommand
    groups_parser = subparsers.add_parser(
        "groups",
        help="Manage projects level settings across one or more groups and, optionally, their sub-groups",
    )
    groups_parser.add_argument("groups", nargs="+", help="Group ids or names")
    groups_parser.add_argument(
        "--limit", type=int, help="Stop after doing <n> projects. Helpful for testing"
    )
    groups_parser.add_argument(
        "-r",
        "--recursive",
        default=False,
        action="store_true",
        help="Recursively search sub-groups of specified group(s)",
    )
    groups_parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless this flag is passed. E.g. Script is no-op by default.",
    )

    # Projects subcommand
    projects_parser = subparsers.add_parser("projects", help="Manage projects")
    projects_parser.add_argument("projects", nargs="+", help="Projects ids")
    projects_parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless this flag is passed. E.g. Script is no-op by default.",
    )

    return parser.parse_args()


def main() -> None:
    args = get_args()

    gl = gitlab.Gitlab(config.CONFIG["GITLAB_URL"], private_token=config.GITLAB_TOKEN)

    if args.command == "projects":
        project_ids = args.projects
    elif args.command == "groups":
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
