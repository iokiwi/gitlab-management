# Manage GitLab Project Level Merge Request Approvers

Wish.com terraform for policy as code management of consistent GitLab Merge Request Approval ACLs across all projects

Given a list of approval rules with a list of approvers

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quickstart

```bash
cd gitlab-approvers
```

Install dependendencies
```bash
uv sync
```

```bash
cp .env.example .env
```

Source a GitLab [Personal Access Token](https://docs.gitlab.com/user/profile/personal_access_tokens/) from [User Settings / Access Tokens](https://gitlab.com/-/user_settings/personal_access_tokens/)

 * Scope: `Owner` or `Maintainer` - requires Maintaine role in all repos managed
 * Permissions: `api`, `read_api`

Run the script

```bash
uv run python main.py
```

Output should look something like

```
api-project (54574403)
    Managing Rule: 'Infra Approvers' (57527897)
        Approvals_required: 1
        Protected Branches: [] # if no branches are specified then all branches are protected.
        Approvers:
            simon.merrick
            john.smith
        Actions:
            Updating approvals required: 2 -> 2
            Remove Approvers: ['john.smith']
            Add Approvers: ['jane.doe']

api-docs (29357440)
    Managing Rule: 'Infra Approvers' (57527897)
        Approvals_required: 1
        Protected Branches: []
        Approvers:
            simon.merrick
            john.smith
        Actions:
            Updating approvals required: 2 -> 2
            Remove Approvers: ['john.smith']
            Add Approvers: ['jane.doe']
```
