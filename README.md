# GitLab Managamenet

![Ruff](https://github.com/iokiwi/gitlab-management/actions/workflows/ruff.yml/badge.svg)

![gitlab_config Tests](https://github.com/iokiwi/gitlab-management/actions/workflows/test_gitlab_config.yml/badge.svg)

A collection of utilities to ease the management of GitLab groups on GitLabs.com

 * [GitLab Config](./gitlab_config/README.md) - A tool for applying consistent configuration across a number of files.
   * TODO: Maybe this will become a standalone project
 * [GitLab Approvers](./gitlab_approvers/README.md) - A tool for configuring Merge Request Approval rules and Approver ACLs across multiple projects.
   * TODO: Ideally this could be part of the same lifecyle as GitLab Config project
 * [Gitflood](./gitflood/README.md) - Scripts for running [gitleaks](https://github.com/gitleaks/gitleaks) across all projects in a group.

See the README.md in each subfolder for more information
