import logging
import os
from argparse import ArgumentParser

import gitlab
import gitlab.const

from prettytable import PrettyTable
from dotenv import load_dotenv
from gitlab.v4.objects.projects import Project

from typing import Dict

import config

# Note: We only currently support a single global config
managed_fields = config.CONFIG["default"]

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def manage_project_settings(project: Project, fix: bool = False, depth=0) -> Dict:
    # Fetch the project by ID to get detailed information, including the default branch
    print("   " * depth, f"Checking {project.name}... ")

    project_changes = []
    push_rule_changes = []

    protected_branches = project.protectedbranches.list()
    push_rules = project.pushrules.get()

    output_fields = {
        "project": project.name,
        "default_branch": project.default_branch,
        "protected branches": ", ".join([b.name for b in protected_branches]),
    }

    for field, expected in managed_fields.items():
        if field == "remove_source_branch_after_merge":
            if fix:
                if project.remove_source_branch_after_merge is not expected:
                    project_changes.append(
                        f"remove_source_branch_after_merge: {project.remove_source_branch_after_merge} -> {expected}"
                    )
                    project.remove_source_branch_after_merge = expected
            output_fields[field] = project.remove_source_branch_after_merge

        if field == "only_allow_merge_if_pipeline_succeeds":
            if fix:
                if project.only_allow_merge_if_pipeline_succeeds is not expected:
                    project_changes.append(
                        f"only_allow_merge_if_pipeline_succeeds: {project.only_allow_merge_if_pipeline_succeeds} -> {expected}"
                    )
                    project.only_allow_merge_if_pipeline_succeeds = expected
            output_fields[field] = project.only_allow_merge_if_pipeline_succeeds

        # Set merge method to FF for projects with a singular 'main' branch only.
        # https://docs.gitlab.com/ee/user/project/merge_requests/methods/#fast-forward-merge
        if field == "merge_method":
            if fix:
                managed_fields["merge_method"]
                if project.merge_method != "ff":
                    # We only do FF if we have a singular 'main' branch
                    if project.default_branch == "main":
                        project_changes.append(
                            f"merge_method: {project.default_branch} -> ff"
                        )
                        project.merge_method = "ff"
            output_fields[field] = project.merge_method

        if field == "merge_access_levels":
            merge_access_levels_default_branch = []
            for branch in protected_branches:
                if branch.name == project.default_branch:
                    default_protected_branch = project.branches.get(branch.name)

                    for level in branch.merge_access_levels:
                        merge_access_levels_default_branch.append(
                            level["access_level_description"]
                        )

            output_fields[field] = ",".join(merge_access_levels_default_branch)

            if fix:
                try:
                    if (
                        len(merge_access_levels_default_branch) != 1
                        or merge_access_levels_default_branch[0]
                        != "Developers + Maintainers"
                    ):
                        project_changes.append(
                            f"Merge rule: {project.squash_option} -> default_on"
                        )
                        project.protectedbranches.delete(default_protected_branch.name)
                        project.protectedbranches.create(
                            {
                                "name": default_protected_branch.name,
                                "merge_access_level": gitlab.const.AccessLevel.DEVELOPER,
                                "push_access_level": gitlab.const.AccessLevel.NO_ACCESS,
                                "allow_force_push": False,
                            }
                        )
                except TypeError as e:
                    logging.exception(e)

        # Enable squash and merge by default (can be opted out of)
        # https://docs.gitlab.com/ee/user/project/merge_requests/squash_and_merge.html#set-default-squash-options-for-a-merge-request
        if field == "squash_option":
            if fix:
                if project.squash_option != expected:
                    project_changes.append(
                        f"squash_options: {project.squash_option} -> {expected}"
                    )
                    project.squash_option = expected

            output_fields[field] = project.squash_option

        if field == "merge_requests_template":
            # Set merge request template if available

            if fix:
                # Check if the merge request template is different from the current one
                if project.merge_requests_template != expected:
                    project_changes.append(
                        "merge_requests_template: updated from template file"
                    )
                    project.merge_requests_template = expected

            # Curate the output so it doesn't break table
            if project.merge_requests_template is None:
                output_fields[field] = project.merge_requests_template
            elif project.merge_requests_template != expected:
                output_fields[field] = "Unexpected Template"
            else:
                output_fields[field] = "Template matches configuration"

        # Prevent pushing secret files
        # https://docs.gitlab.com/ee/user/project/repository/push_rules.html#prevent-pushing-secrets-to-the-repository
        if field == "prevent_secrets":
            if fix:
                if push_rules.prevent_secrets is not expected:
                    push_rule_changes.append(
                        f"prevent_secrets: {push_rules.prevent_secrets} -> {expected}"
                    )
                    push_rules.prevent_secrets = expected
            output_fields[field] = push_rules.prevent_secrets

    if fix:
        if push_rule_changes:
            push_rules.save()

        if project_changes:
            project.save()

        if not project_changes and not push_rule_changes:
            print(f"No changes for {project.name}")
        else:
            print(project.name)
            for change in push_rule_changes + project_changes:
                print(f"{change}")

    return output_fields


def manage_projects(gl: gitlab.Gitlab, project_ids: list[str], **kwargs):

    rows = []
    for project_id in project_ids:
        project = gl.projects.get(project_id)
        try:
            rows.append(manage_project_settings(project, fix, depth=depth + 1))
        except Exception as e:
            logging.exception(e)

        count += 1
        if limit is not None and count == limit:
            print(f"Limit of {limit} reached. Exiting")
            break

    return (rows, count)


def manage_group(
    gl: gitlab.Gitlab,
    group_id: str,
    limit: int = None,
    fix: bool = False,
    recurse: bool = False,
    count: int = 0,
    depth: int = 0,
):
    rows = []

    group = gl.groups.get(group_id)
    print("  " * depth, "📁", f"Getting projects for {group.name} ({group.id})")
    group_projects = group.projects.list(get_all=True, archived=False)
    project_ids = [group_project.id for group_project in group_projects]

    rows, count = manage_projects(
        gl, project_ids, fix=fix, limit=limit, count=count, recurse=recurse, depth=depth
    )

    if recurse:
        subgroups = group.subgroups.list(all=True, archived=False)
        for subgroup in subgroups:
            if limit is not None and count >= limit:
                break

            subrows, count = manage_group(
                gl,
                subgroup.id,
                fix=fix,
                limit=limit,
                count=count,
                recurse=recurse,
                depth=depth + 1,
            )

            rows += subrows

    return (rows, count)


def manage_groups(
    gl: gitlab.Gitlab,
    groups_ids: list[str],
    count: int = 0,
    limit: int = None,
    recurse: bool = False,
):
    rows = []
    for group_id in groups_ids:
        rows, count = manage_group(gl, group_id, count=count)
        if count >= limit:
            break
    return (rows, count)


def main():
    parser = ArgumentParser()
    # TODO: Make this accept multiple values
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--groups", nargs="+", help="Groups to manage")
    group.add_argument("--projects", nargs="+", help="Projects to manage")

    parser.add_argument(
        "--limit", type=int, help="Stop after doing <n> projects. Helpful for testing"
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Script will not make changes unless --fix is passed",
    )
    parser.add_argument(
        "-r", "--recurse-subprojects", default=False, action="store_true"
    )
    args = parser.parse_args()

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


# def manage_group(gl: gitlab.Gitlab, group_id: str, fix=False, limit=None, count=0, recurse=False, depth=0):
#     rows = []

#     group = gl.groups.get(group_id)
#     print("  " * depth, "📁", f"Getting projects for {group.name} ({group.id})")
#     group_projects = group.projects.list(get_all=True, archived=False)

#     manage_projects(
#         gl,
#         group_projects,
#         fix=fix,
#         limit=limit,
#         count=count,
#         recurse=recurse,
#         depth=depth,
#     )
