# GitLab Config

Script for managing consistent config across all GitLab projects in a Group

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quickstart

```bash
cd gitlab_config
```


### Install dependendencies

```bash
cp .env.example .env
```

Source a GitLab [Personal Access Token](https://docs.gitlab.com/user/profile/personal_access_tokens/) from [User Settings / Access Tokens](https://gitlab.com/-/user_settings/personal_access_tokens/) and put it into `.env` (**NOT** `.env.example`!)

 * Scope: `Owner` or `Maintainer` - requires at least maintainer role in all repos managed
 * Permissions: `api`

### Create a config file
And modify to taste

```bash
cp config.yaml.example config.yaml
```

### Run the script

Note the script operates in a no-op mode by default and will not update anything unless the `--fix` flag is passed.

```bash
# Run the tool for one or more projects
$ uv run gitlab-config --projects [PROJECT_ID_1] [PROJECT_ID_2]

# Run the script recursively. E.g. on your top level groups and for all subgroups
$ uv run gitlab-config --recursive --groups [GROUP_ID_1] [GROUP_ID_2]

# Help and usage
$ uv run gitlab-config -h
```

```
usage: gitlab-config [-h] (--groups GROUPS [GROUPS ...] | --projects PROJECTS [PROJECTS ...]) [--limit LIMIT] [-r] [-f]

options:
  -h, --help            show this help message and exit
  --groups GROUPS [GROUPS ...]
                        Groups to manage
  --projects PROJECTS [PROJECTS ...]
                        Projects to manage
  --limit LIMIT         Stop after doing <n> projects. Helpful for testing
  -r, --recursive       Recursively run on subgroups of the current group
  -f, --fix             Script will not make changes unless this flag is passed. E.g. Script is no-op by default.
```

Install globally
```bash
uv tool install -e .
```

## Contributing

Note the script operates in a no-op mode by default and will not update anything unless the `--fix` flag is passed.

The `--limit <n>` option stops the script after checking `<n>` projects which is usefull for testing on a limited scale.

Would love some unit tests.
