import logging
from typing import List

import gitlab
from gitlab.v4.objects.projects import GroupProject

logger = logging.getLogger(__name__)


def get_projects_for_group(
    gl: gitlab.Gitlab,
    group_id: str,
    limit: int = None,
    recurse: bool = False,
) -> List[GroupProject]:
    group = gl.groups.get(group_id, simple=True)

    page = 1
    per_page = 20

    if limit and limit < per_page:
        per_page = limit

    group_projects = []
    while True:
        logger.info(
            f"Getting projects for group: [{group.id}] {group.full_path}, include_subgroups: {recurse}"
        )
        logger.debug(
            f"page: {page}, per_page: {per_page}, limit: {limit}, include_subgroups: {recurse}"
        )

        projects_page = group.projects.list(
            page=page,
            per_page=20,
            archived=False,
            order_by="name",
            sort="asc",
            include_subgroups=recurse,
            simple=True,
        )

        if not projects_page:
            break

        group_projects.extend(projects_page)
        page += 1

        if limit and len(group_projects) >= limit:
            group_projects = group_projects[:limit]
            break

    return group_projects


def get_projects_for_groups(
    gl: gitlab.Gitlab,
    groups_ids: list[str],
    limit: int = None,
    recurse: bool = False,
) -> List[GroupProject]:
    unique_projects = dict()
    for group_id in groups_ids:
        group_projects = get_projects_for_group(
            gl, group_id, limit=limit, recurse=recurse
        )
        for project in group_projects:
            unique_projects[project.id] = project

        if limit and len(unique_projects) >= limit:
            break

    return list(unique_projects.values())
