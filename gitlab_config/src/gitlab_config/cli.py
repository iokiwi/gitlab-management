import argparse
from argparse import ArgumentParser
from typing import List


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Groups subcommand
    groups_parser = subparsers.add_parser(
        "groups",
        help="Manage projects level settings across one or more groups and, optionally, their sub-groups",
    )
    groups_parser.add_argument(
        "group_names_or_ids",
        nargs="+",
        help="One or more group names or ids for which to manage or report the configuration.",
    )
    groups_parser.add_argument(
        "--limit", type=int, help="Stop after doing <n> projects. Helpful for testing."
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
    projects_parser = subparsers.add_parser(
        "projects",
        help="Manage project level settings for one or more projects by project id",
    )
    projects_parser.add_argument(
        "project_ids",
        nargs="+",
        help="Projects id of one or more projects for which to manage or report the configuration.",
    )
    projects_parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless this flag is passed. E.g. Script is no-op by default.",
    )

    return parser.parse_args(args)
