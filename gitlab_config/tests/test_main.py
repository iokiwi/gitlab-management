import pytest

from gitlab_config.main import main
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_config():
    with patch('gitlab_config.config.load_yaml_config', return_value={"test": "config"}):
        yield

class TestProjectsSubcommand:
    def test_projects_basic_args(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "unchanged"}], 0)

        args = ["projects", "123", "456"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, ["123", "456"], mocker.ANY, fix=False
        )

    def test_projects_with_fix_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "changed"}], 1)

        args = ["projects", "123", "--fix"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, ["123"], mocker.ANY, fix=True
        )

    def test_projects_single_id(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "999", "status": "unchanged"}], 0)

        args = ["projects", "999"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, ["999"], mocker.ANY, fix=False
        )

    def test_projects_multiple_ids(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = (
            [{"id": "1", "status": "unchanged"}, {"id": "2", "status": "unchanged"}],
            0,
        )

        args = ["projects", "1", "2", "3", "4", "5"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, ["1", "2", "3", "4", "5"], mocker.ANY, fix=False
        )


class TestGroupsSubcommand:
    def test_groups_basic_args(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [
            mocker.Mock(id=123),
            mocker.Mock(id=456),
        ]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "unchanged"}], 0)

        args = ["groups", "acme-org"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["acme-org"], limit=None, recurse=False
        )
        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, [123, 456], mocker.ANY, fix=False
        )

    def test_groups_with_fix_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [mocker.Mock(id=123)]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "changed"}], 1)

        args = ["groups", "test-group", "--fix"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, [123], mocker.ANY, fix=True
        )

    def test_groups_with_recursive_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [mocker.Mock(id=789)]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "789", "status": "unchanged"}], 0)

        args = ["groups", "parent-group", "--recursive"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["parent-group"], limit=None, recurse=True
        )

    def test_groups_with_limit(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [
            mocker.Mock(id=100),
            mocker.Mock(id=200),
        ]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "100", "status": "unchanged"}], 0)

        args = ["groups", "test-group", "--limit", "5"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["test-group"], limit=5, recurse=False
        )

    def test_groups_all_flags_combined(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [
            mocker.Mock(id=123),
            mocker.Mock(id=456),
        ]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "changed"}], 2)

        args = [
            "groups",
            "acme-org",
            "012345678",
            "--fix",
            "--recursive",
            "--limit",
            "10",
        ]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["acme-org", "012345678"], limit=10, recurse=True
        )
        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, [123, 456], mocker.ANY, fix=True
        )

    def test_groups_multiple_groups(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [
            mocker.Mock(id=111),
            mocker.Mock(id=222),
            mocker.Mock(id=333),
        ]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "111", "status": "unchanged"}], 0)

        args = ["groups", "group1", "group2", "group3"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value,
            ["group1", "group2", "group3"],
            limit=None,
            recurse=False,
        )


class TestArgumentCombinations:
    def test_projects_short_fix_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "123", "status": "changed"}], 1)

        args = ["projects", "123", "-f"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, ["123"], mocker.ANY, fix=True
        )

    def test_groups_short_recursive_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [mocker.Mock(id=456)]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "456", "status": "unchanged"}], 0)

        args = ["groups", "test-group", "-r"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["test-group"], limit=None, recurse=True
        )

    def test_groups_short_fix_flag(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [mocker.Mock(id=789)]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "789", "status": "changed"}], 1)

        args = ["groups", "test-group", "-f"]
        main(args)

        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, [789], mocker.ANY, fix=True
        )

    def test_groups_mixed_short_long_flags(self, mocker):
        mock_gitlab = mocker.patch("gitlab_config.main.gitlab.Gitlab")
        mock_get_projects_for_groups = mocker.patch(
            "gitlab_config.main.get_projects_for_groups"
        )
        mock_get_projects_for_groups.return_value = [mocker.Mock(id=999)]
        mock_manage_projects = mocker.patch("gitlab_config.main.manage_projects")
        mock_manage_projects.return_value = ([{"id": "999", "status": "changed"}], 1)

        args = ["groups", "test-group", "-f", "--recursive", "--limit", "3"]
        main(args)

        mock_get_projects_for_groups.assert_called_once_with(
            mock_gitlab.return_value, ["test-group"], limit=3, recurse=True
        )
        mock_manage_projects.assert_called_once_with(
            mock_gitlab.return_value, [999], mocker.ANY, fix=True
        )


class TestErrorCases:
    def test_no_command_provided(self):
        with pytest.raises(SystemExit):
            main([])

    def test_invalid_command(self):
        with pytest.raises(SystemExit):
            main(["invalid"])

    def test_projects_no_ids(self):
        with pytest.raises(SystemExit):
            main(["projects"])

    def test_groups_no_names(self):
        with pytest.raises(SystemExit):
            main(["groups"])

    def test_groups_invalid_limit_value(self):
        with pytest.raises(SystemExit):
            main(["groups", "test-group", "--limit", "not-a-number"])
