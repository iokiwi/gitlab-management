import logging
from typing import Dict, List

import gitlab
from gitlab.v4.objects.projects import Project

logger = logging.getLogger(__name__)


# TODO: For each field, report if it changed or should change
# Display it as yellow or red if it will change. Display it as blue or green if it did change.
# Create styled text without printing
# styled_text = Text("No changes will be made unless the --fix flag is passed", style="yellow")
# console.print(styled_text)
# styled_string = console.render_str(Text("Hello", style="yellow"))
# print(styled_string)
def manage_project_settings(project: Project, config: Dict, fix: bool = False) -> Dict:
    # Fetch the project by ID to get detailed information, including the default branch

    changed = False
    managed_fields = config.get(project.name, config["default"])

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

            output_fields[field] = ",".join(merge_access_levels_default_branch)

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
            changed = True
            push_rules.save()

        if project_changes:
            changed = True
            project.save()

        if not project_changes and not push_rule_changes:
            print(f"No changes for {project.name}")
        else:
            print(project.name)
            for change in push_rule_changes + project_changes:
                print(f"{change}")

    return (output_fields, changed)


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
