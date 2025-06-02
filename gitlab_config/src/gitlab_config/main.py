import logging
import os
import sys
from typing import Dict, List

import gitlab
from prettytable import PrettyTable
from rich.console import Console

from gitlab_config.cli import parse_args
from gitlab_config.config import get_config
from gitlab_config.groups import get_projects_for_groups
from gitlab_config.projects import manage_projects

log_level = os.environ.get("GITLAB_CONFIG_LOG_LEVEL", "WARNING")
log_level = getattr(logging, log_level)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# def main(args: List[str] | None = None, config: Dict | None = None) -> None:
def main(args: List[str] | None = None, config: Dict | None = None) -> None:

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    console = Console()

    if config is None:
        config = get_config()

    if not args.fix:
        console.print(
            "No changes will be made unless the --fix flag is specified", style="yellow"
        )

    gl = gitlab.Gitlab(
        config["GITLAB_URL"],
        private_token=config["GITLAB_TOKEN"],
    )

    if args.command == "projects":
        project_ids = args.project_ids
    elif args.command == "groups":
        projects = get_projects_for_groups(
            gl,
            list(args.group_names_or_ids),
            limit=args.limit,
            recurse=args.recursive,
        )
        project_ids = [project.id for project in projects]

    rows, change_count = manage_projects(gl, project_ids, config, fix=args.fix)

    table = PrettyTable()
    table.align = "l"
    table.field_names = rows[0].keys()

    for row in rows:
        table.add_row(row.values())

    console.print(f"Changed {change_count}/{len(project_ids)} projects", style="green")
    print(table)
    console.print(f"Changed {change_count}/{len(project_ids)} projects", style="green")


def app() -> None:
    return main(sys.argv[1:], get_config())

# if __name__ == "__main__":
#     main(sys.argv[1:], get_config())
