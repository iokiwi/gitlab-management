import os
from typing import Dict, List
from pathlib import Path

import gitlab
import yaml
from dotenv import load_dotenv
from argparse import ArgumentParser

from gitlab.v4.objects.projects import Project
from gitlab.v4.objects.merge_request_approvals import ProjectApprovalRule

# We only need a single global reference to these
GROUP_MEMBERS = None
GROUP_MEMBERS_BY_IDS = None
GROUP_MEMBERS_BY_USERNAMES = None
ARGS = None


def manage_rule(rule: ProjectApprovalRule, spec: Dict):
    actions = []

    print(f"\tManaging Rule: '{rule.name}' ({rule.id})")
    print(f"\t\tApprovals_required: {rule.approvals_required}")
    print(
        f"\t\tProtected Branches: {[branch['name'] for branch in rule.protected_branches]}"
    )

    print("\t\tApprovers:")
    for user in rule.users:
        print(f"\t\t\t{user['username']}")

    if rule.approvals_required != spec["approvals_required"]:
        rule.approvals_required = spec["approvals_required"]
        actions.append(
            (
                f"Updating approvals required: "
                f"{rule.approvals_required} -> {spec['approvals_required']}"
            )
        )

    applies_to_all_protected_branches = spec.get(
        "applies_to_all_protected_branches", True
    )
    if rule.applies_to_all_protected_branches != applies_to_all_protected_branches:
        print(
            type(rule.applies_to_all_protected_branches),
            type(applies_to_all_protected_branches),
        )
        rule.applies_to_all_protected_branches = applies_to_all_protected_branches
        actions.append(
            (
                f"Updating 'applies_to_all_protected_branches': "
                f"{rule.applies_to_all_protected_branches} -> {applies_to_all_protected_branches}"
            )
        )

    spec_users = {GROUP_MEMBERS_BY_USERNAMES[user].id for user in spec["users"]}
    rule_users = {user["id"] for user in rule.users}

    if spec_users != rule_users:
        diff = rule_users - spec_users
        users_to_remove = [GROUP_MEMBERS_BY_IDS[user].username for user in diff]
        if users_to_remove:
            actions.append(f"Remove Approvers: {users_to_remove}")

        diff = spec_users - rule_users
        users_to_add = [GROUP_MEMBERS_BY_IDS[user].username for user in diff]
        if users_to_add:
            actions.append(f"Add Approvers: {users_to_add}")

        rule.users = list(spec_users)

    print("\t\tActions:")
    for a in actions:
        print(f"\t\t\t{a}")

    if ARGS.fix and len(actions) > 0:
        rule.save()

    pass


class RuleSpecManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = None

    def load_config(self) -> None:
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def get_specs(self) -> Dict:
        return self.config["approval_rules"]

    def get_spec_names(self) -> List[str]:
        return [spec["name"] for spec in self.get_specs().values()]

    def get_spec_by_name(self, name: str) -> Dict:
        for _, spec in self.config["approval_rules"].items():
            if spec["name"] == name:
                return spec
        raise ValueError(f"No spec was found with name matching: {name}")


def manage_project_approval_rules(project: Project, rule_spec_manager: RuleSpecManager):
    project_approval_rules = project.approvalrules.list()
    print(f"{project.name} ({project.id})")

    for rule in project_approval_rules:
        # 1 delete rules that exist that aren't in the spec
        if rule.name not in rule_spec_manager.get_spec_names():
            print(f"\tDeleting rule '{rule.name}'")
            if ARGS.fix:
                rule.delete()
            continue

        # 2 manage the existing rules
        rule_spec = rule_spec_manager.get_spec_by_name(rule.name)
        manage_rule(rule, rule_spec)

    # 3 create approval rules if they don't exist
    rule_names = [rule.name for rule in project_approval_rules]
    for _, spec in rule_spec_manager.get_specs().items():
        if spec["name"] not in rule_names:
            print(f"\tCreating rule '{spec['name']}'")

            if ARGS.fix:
                project.approvalrules.create(
                    {
                        "name": spec["name"],
                        "applies_to_all_protected_branches": spec.get(
                            "applies_to_all_protected_branches", True
                        ),
                        "approvals_required": spec.get("approvals_required", 1),
                        "user_ids": [
                            GROUP_MEMBERS_BY_USERNAMES[user].id
                            for user in spec["users"]
                        ],
                    }
                )


def main():
    global GROUP_MEMBERS
    global GROUP_MEMBERS_BY_IDS
    global GROUP_MEMBERS_BY_USERNAMES
    global ARGS

    parser = ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fix", action="store_true", default=False)

    ARGS = parser.parse_args()

    load_dotenv()
    # GitLab private token
    GITLAB_URL = "https://gitlab.com"
    PRIVATE_TOKEN = os.environ.get("GITLAB_TOKEN")
    GROUP_ID = os.environ.get("GITLAB_PROJECT_ID")

    config_path = Path(__file__).parent / "approval_rules.yml"
    rule_spec_manager = RuleSpecManager(config_path=config_path)
    rule_spec_manager.load_config()

    gl = gitlab.Gitlab(GITLAB_URL, private_token=PRIVATE_TOKEN)
    group = gl.groups.get(GROUP_ID)

    # List all projects in the group
    print(f"Getting projects for {group.name} ({group.id})")
    group_projects = group.projects.list(get_all=True, archived=False)

    print(f"Getting Group Members for {group.name}")
    GROUP_MEMBERS = group.members.list(all=True)
    GROUP_MEMBERS_BY_USERNAMES = {member.username: member for member in GROUP_MEMBERS}
    GROUP_MEMBERS_BY_IDS = {member.id: member for member in GROUP_MEMBERS}

    count = 0
    for group_project in group_projects:

        project = gl.projects.get(group_project.id)
        manage_project_approval_rules(project, rule_spec_manager)

        if count == ARGS.limit:
            print(f"Limit of {ARGS.limit} project(s) checked. Exiting")
            break
        count += 1


if __name__ == "__main__":
    main()
