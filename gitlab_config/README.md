# GitLab Config

Script for managing consistent config across all GitLab projects in a Group. Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quickstart

```bash
cd gitlab_config
```

Create a config file and modify to requirements
```bash
cp config.yaml.example config.yaml
```

```bash
cp .env.example .env
```

Create a GitLab [Personal Access Token](https://docs.gitlab.com/user/profile/personal_access_tokens/) from [User Settings / Access Tokens](https://gitlab.com/-/user_settings/personal_access_tokens/) and put it into `.env` (**NOT** `.env.example`!)

 * Scope: `Owner` or `Maintainer` - requires at least maintainer role in all repos managed
 * Permissions: `api`

### Run the script

Note the script operates in a no-op mode by default and will not update anything unless the `--fix` flag is passed.

```bash
# Run the tool for one or more projects
$ uv run gitlab-config projects PROJECT_ID_1 [PROJECT_ID_2...]

# Run the script recursively. E.g. on your top level groups and for all subgroups
$ uv run gitlab-config groups --recursive --limit 10 [GROUP_NAME_OR_ID_1] [GROUP_NAME_OR_ID_2]

# Help and usage
$ uv run gitlab-config -h
```

# Install globally
```bash
uv tool install -e .
```

## Contributing

Note the script operates in a no-op mode by default and will not update anything unless the `--fix` flag is passed.

The `--limit <n>` option stops the script after checking `<n>` projects which is usefull for testing on a limited scale.

<!-- ## Testing

To run all tests:
```bash
uv run pytest
```

To run tests with verbose output:
```bash
uv run pytest -v
```

To run tests with coverage:
```bash
uv run pytest --cov=gitlab_config
```

To run a specific test file:
```bash
uv run pytest tests/test_config.py
```

### Test Structure

Tests are organized in the `tests/` directory with the following structure: -->
