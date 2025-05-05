# Gitflood - Gitleaks across everything all at once

Requires

 * [uv](https://docs.astral.sh/uv/getting-started/installation/)
 * A [GitLab Personal Access Token](https://docs.gitlab.com/user/profile/personal_access_tokens/#create-a-personal-access-token)
     * Roles: `read_api`, `read_repsitory`
     * Role: `Developer` or higher
 * SSH based access with a RSA or ECDSA key setup.
 * Developer or higher roles in all repo's you want to list and scan.

# Quickstart

Put the token in you env

```bash
echo GITLAB_TOKEN="<token>" >> .env
```

List all gitlab repos a given gitlab groups

E.g. To clone all repos, and both an redacted and unredacted deeps can of both

```bash
./gitflood.sh git --redacted --clean
# Maybe the script can do this automatically for us
zip -r results/project_redacted_$(date +'%Y%m%d%H%M%S').zip ./results/redacted
```

```
GitFlood - A script for running gitleaks across many repos at once.

usage: git-flood.sh [--h] [mode] [OPTIONS]

arguments:

  mode: The git leaks subcommand to run {dir,git}. Per the gitleaks docs:
    dir         scan directories or files for secrets
    git         scan git repositories for secrets

optional arguments:
    --clean            Delete the repos/ directory and reclone everyting
    --redact           {true,false,both}
    -h,--help          Show this help screen and exit.
```

To just list all repos in given GitLab groups

```bash
uv run gitlab-ls.py
```

Never share the unredacted results!

