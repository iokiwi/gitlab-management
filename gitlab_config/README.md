# GitLab Config

Script for managing consistent config across all GitLab projects in a Group

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quickstart

```bash
cd gitlab_config
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