from typing import Dict, List, Tuple
import gitlab

from projects import manage_projects


def manage_group(
    gl: gitlab.Gitlab,
    group_id: str,
    limit: int = None,
    fix: bool = False,
    recurse: bool = False,
    count: int = 0,
    depth: int = 0,
) -> Tuple[List[Dict], int]:
    rows = []

    group = gl.groups.get(group_id)
    print("  " * depth, "📁", f"Getting projects for {group.name} ({group.id})")
    group_projects = group.projects.list(get_all=True, archived=False)
    project_ids = [group_project.id for group_project in group_projects]

    rows, count = manage_projects(
        gl, project_ids, fix=fix, limit=limit, count=count, recurse=recurse, depth=depth
    )

    if recurse:
        subgroups = group.subgroups.list(all=True, archived=False)
        for subgroup in subgroups:
            if limit is not None and count >= limit:
                break

            subrows, count = manage_group(
                gl,
                subgroup.id,
                fix=fix,
                limit=limit,
                count=count,
                recurse=recurse,
                depth=depth + 1,
            )

            rows += subrows

    return (rows, count)


def manage_groups(
    gl: gitlab.Gitlab,
    groups_ids: list[str],
    count: int = 0,
    limit: int = None,
    recurse: bool = False,
):
    rows = []
    for group_id in groups_ids:
        rows, count = manage_group(gl, group_id, count=count)
        if count >= limit:
            break
    return (rows, count)
