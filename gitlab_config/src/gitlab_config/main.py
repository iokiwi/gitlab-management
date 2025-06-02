import sys
import logging
from typing import List

import gitlab
from prettytable import PrettyTable
from rich.console import Console

from gitlab_config import config
from gitlab_config.cli import parse_args
from gitlab_config.groups import get_projects_for_groups
from gitlab_config.projects import manage_projects

log_level = config.CONFIG.get("GITLAB_CONFIG_LOG_LEVEL", "WARNING")
log_level = getattr(logging, log_level)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main(args: List[str] | None = None) -> None:
    args = parse_args(args)
    console = Console()

    if not args.fix:
        console.print(
            "No changes will be made unless the --fix flag is specified", style="yellow"
        )

    gl = gitlab.Gitlab(
        config.CONFIG.get("GITLAB_URL", "https://gitlab.com"),
        private_token=config.GITLAB_TOKEN,
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


if __name__ == "__main__":
    main(sys.argv[1:])
