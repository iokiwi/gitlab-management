import logging
import os
from argparse import ArgumentParser

import gitlab
import gitlab.const

from prettytable import PrettyTable
from dotenv import load_dotenv
from gitlab.v4.objects.projects import Project


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def extract_project_details(project: Project, fix: bool = False):
    # Fetch the project by ID to get detailed information, including the default branch
    print(f"Checking {project.name}... ", end="")

    protected_branches = project.protectedbranches.list()
    push_rules = project.pushrules.get()

    for branch in protected_branches:
        if branch.name == project.default_branch:
            default_protected_branch = project.branches.get(branch.name)

    merge_access_levels_default_branch = []
    for level in branch.merge_access_levels:
        merge_access_levels_default_branch.append(level["access_level_description"])

    if fix:
        project_changes = []
        push_rule_changes = []

        # Ensure the default protected branch does not allow anyone to push
        # and allows developers and maintainers to merge.
        try:
            if (
                len(merge_access_levels_default_branch) != 1
                or merge_access_levels_default_branch[0] != "Developers + Maintainers"
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

        # Delete the branch after mergeing
        if project.remove_source_branch_after_merge is not True:
            project.append(
                f"remove_source_branch_after_merge: {project.remove_source_branch_after_merge} -> True"
            )
            project.remove_source_branch_after_merge = True

        # Set merge method to FF for projects with a singular 'main' branch only.
        # https://docs.gitlab.com/ee/user/project/merge_requests/methods/#fast-forward-merge
        if project.merge_method != "ff":
            # We only do FF if we have a singular 'main' branch
            if project.default_branch == "main":
                project_changes.append(f"merge_method: {project.default_branch} -> ff")
                project.merge_method = "ff"

        # Enable squash and merge by default (can be opted out of)
        # https://docs.gitlab.com/ee/user/project/merge_requests/squash_and_merge.html#set-default-squash-options-for-a-merge-request
        if project.squash_option != "default_on":
            project_changes.append(
                f"squash_options: {project.squash_option} -> default_on"
            )
            project.squash_option = "default_on"

        # Prevent pushing secret files
        # https://docs.gitlab.com/ee/user/project/repository/push_rules.html#prevent-pushing-secrets-to-the-repository
        if push_rules.prevent_secrets is not True:
            push_rule_changes.append(
                f"prevent_secrets: {push_rules.prevent_secrets} -> True"
            )
            push_rules.prevent_secrets = True

        # Push Rules to manage
        # TODO: Reject unverified users
        # TODO: Reject inconsistent username
        # TODO: Check whether the commit autor is a GitLab user

        if push_rule_changes:
            push_rules.save()

        if project_changes:
            project.save()

        if not project_changes and not push_rule_changes:
            print(f"No changes for {project.name}")
        else:
            print(project.name)
            for change in push_rule_changes + project_changes:
                print(f"\t{change}")

    # TODO: Check status of 'Enable Merged Results'

    return [
        project.name,
        project.default_branch,
        project.squash_option,
        push_rules.prevent_secrets,
        project.remove_source_branch_after_merge,
        project.only_allow_merge_if_pipeline_succeeds,
        project.merge_method,
        ", ".join([b.name for b in protected_branches]),
        ",".join(merge_access_levels_default_branch),
    ]


def main():
    parser = ArgumentParser()
    # TODO: Add argument to specify a project by name and / or ID
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--limit", type=int)

    args = parser.parse_args()

    load_dotenv()
    # GitLab private token
    GITLAB_URL = "https://gitlab.com"
    PRIVATE_TOKEN = os.environ.get("GITLAB_TOKEN")
    GROUP_ID = os.environ.get("GROUP_ID")

    gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
    group = gl.groups.get(GROUP_ID)

    # List all projects in the group
    print(f"Getting projects for {group.name} ({group.id})")
    group_projects = group.projects.list(get_all=True, archived=False)

    table = PrettyTable()
    table.align = "l"
    table.field_names = [
        "project",
        "default_branch",
        "squash_option",
        "prevent_secrets",
        "remove_source_branch_after_merge",
        "only_allow_merge_if_pipeline_succeed",
        "merge_method",
        "protected branches",
        "merge_access_levels",
        # ""
    ]

    count = 0
    for group_project in group_projects:

        project_details = gl.projects.get(group_project.id)

        try:
            row = extract_project_details(project_details, args.fix)
            table.add_row(row)
        except Exception as e:
            # log and continue
            logging.exception(e)

        if count == args.limit:
            print(f"Limit of {args.limit} reached. Exiting")
            break
        count += 1

    print(table)


if __name__ == "__main__":
    main()
