import logging
from typing import Dict, List

import gitlab
from gitlab.v4.objects.projects import Project

from rich.console import Console
from gitlab_config.colors import Colors, color_cell, colorize

console = Console()
logger = logging.getLogger(__name__)


# WIP, there must be a way to generalize the management of rpoject fields
def manage_project_setting(
    project: Project, setting: str, expected: str, fix: bool
) -> Dict:
    # print(getattr(project, setting), expected, fix)
    changed = False
    if getattr(project, setting) != expected:
        changed = True
        if fix:
            setattr(project, setting, expected)

    return {
        "value": color_cell(getattr(project, setting), changed, fix),
        "changed": changed,
    }


def manage_project_settings(project: Project, config: Dict, fix: bool = False) -> Dict:
    # Fetch the project by ID to get detailed information, including the default branch

    project_changed = False
    managed_fields = config.get(project.name, config["default"])

    project_changes = []
    push_rule_changes = []

    protected_branches = project.protectedbranches.list()
    push_rules = project.pushrules.get()

    output_fields = {
        "project": {
            "value": project.name,
        },
        "default_branch": {
            "value": project.default_branch,
        },
        "protected branches": {
            "value": ", ".join([b.name for b in protected_branches]),
        },
    }

    for field, expected in managed_fields.items():
        changed = False

        if field == "remove_source_branch_after_merge":
            if project.remove_source_branch_after_merge != expected:
                changed = True
                project_changes.append(
                    f"remove_source_branch_after_merge: {project.remove_source_branch_after_merge} -> {expected}"
                )
                if fix:
                    project.remove_source_branch_after_merge = expected

            output_fields[field] = {
                "value": color_cell(
                    project.remove_source_branch_after_merge, changed, fix
                ),
                "changed": changed,
            }

        if field == "only_allow_merge_if_pipeline_succeeds":
            if project.only_allow_merge_if_pipeline_succeeds is not expected:
                changed = True
                project_changes.append(
                    f"only_allow_merge_if_pipeline_succeeds: {project.only_allow_merge_if_pipeline_succeeds} -> {expected}"
                )
                if fix:
                    project.only_allow_merge_if_pipeline_succeeds = expected
            output_fields[field] = {
                "value": color_cell(
                    project.only_allow_merge_if_pipeline_succeeds, changed, fix
                ),
                "changed": changed,
            }

        # Set merge method to FF for projects with a singular 'main' branch only.
        # https://docs.gitlab.com/ee/user/project/merge_requests/methods/#fast-forward-merge
        if field == "merge_method":
            if project.merge_method != "ff" and project.default_branch == "main":
                changed = True
                project_changes.append(f"merge_method: {project.default_branch} -> ff")
                if fix:
                    project.merge_method = "ff"

            output_fields[field] = {
                "value": color_cell(project.merge_method, changed, fix),
                "changed": changed,
            }

        if field == "merge_access_levels":
            merge_access_levels_default_branch = []

            default_protected_branch = None
            for branch in protected_branches:
                if branch.name == project.default_branch:
                    default_protected_branch = project.branches.get(branch.name)

                    for level in branch.merge_access_levels:
                        merge_access_levels_default_branch.append(
                            level["access_level_description"]
                        )

            if default_protected_branch is None:
                print(
                    colorize(
                        f"WARNING: The default branch for '{project.path}' is not protected! See: https://docs.gitlab.com/user/project/repository/branches/protected/",
                        Colors.YELLOW,
                    )
                )

            try:
                if (
                    len(merge_access_levels_default_branch) != 1
                    or merge_access_levels_default_branch[0]
                    != "Developers + Maintainers"
                ):
                    changed = True
                    project_changes.append(
                        f"Merge rule: {project.squash_option} -> default_on"
                    )

                    if fix:
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

            output_fields[field] = {
                "value": ",".join(merge_access_levels_default_branch),
                "changed": changed,
            }

        # Enable squash and merge by default (can be opted out of)
        # https://docs.gitlab.com/ee/user/project/merge_requests/squash_and_merge.html#set-default-squash-options-for-a-merge-request
        if field == "squash_option":
            if project.squash_option != expected:
                changed = True
                project_changes.append(
                    f"squash_options: {project.squash_option} -> {expected}"
                )
                if fix:
                    project.squash_option = expected

            output_fields[field] = {
                "value": color_cell(project.squash_option, changed, fix),
                "changed": changed,
            }

        if field == "merge_requests_template":
            if project.merge_requests_template != expected:
                changed = True
                project_changes.append(
                    "merge_requests_template: updated from template file"
                )

                if fix:
                    project.merge_requests_template = expected

            # Curate the output so it doesn't break table
            if project.merge_requests_template is None:
                output = project.merge_requests_template
            elif project.merge_requests_template != expected:
                output = "Unexpected Template"
            else:
                output = "Template matches configuration"

            output_fields[field] = {
                "value": color_cell(output, changed, fix),
                "changed": changed,
            }

        # Prevent pushing secret files
        # https://docs.gitlab.com/ee/user/project/repository/push_rules.html#prevent-pushing-secrets-to-the-repository
        if field == "prevent_secrets":
            if push_rules.prevent_secrets is not expected:
                changed = True
                push_rule_changes.append(
                    f"prevent_secrets: {push_rules.prevent_secrets} -> {expected}"
                )
                if fix:
                    push_rules.prevent_secrets = expected

            output_fields[field] = {
                "value": color_cell(push_rules.prevent_secrets, changed, fix),
                "changed": changed,
            }

        if push_rule_changes:
            project_changed = True
            if fix:
                push_rules.save()

        if project_changes:
            project_changed = True
            if fix:
                project.save()

    return (output_fields, project_changed)


def manage_projects(
    gl: gitlab.Gitlab,
    project_ids: List[str],
    config: Dict,
    fix: bool = False,
) -> Dict:
    rows = []
    change_count = 0
    for i, project_id in enumerate(project_ids):
        project = gl.projects.get(project_id)
        print(
            f"Managing project ({i + 1}/{len(project_ids)}): [{project.id}] {project.path}"
        )
        try:
            row, changed = manage_project_settings(project, config, fix=fix)
            rows.append(row)
            if changed:
                change_count += 1
        except Exception as e:
            logging.exception(e)

    return (rows, change_count)
