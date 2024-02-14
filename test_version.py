# test version.py
import os

import pytest

from src.core.settings import POETRY_CONFIG_FIlE
from src.utils.file_utils import create_temp_dir
from src.utils.file_utils import remove_dir
from version import get_version
from version import load_version


def test_load_version(capsys):
    """
    testing options
    1) wrong directory (no file in current directory)
    2) wrong toml structure (could not parse file)
    3) absent keys (no version info)
    """
    # checking execution of load_version (explicit) - should be loaded on module import!
    version_divided = get_version().split('.')

    assert len(version_divided) == 3, 'Version should contains three parts'
    for version_part in version_divided:
        assert len(version_part) > 0, 'Part of version info should be filled'
        for digit in version_part:
            assert digit.isdigit(), 'Version should contain only digits!'

    # different faulty scenarios
    current_dir = os.getcwd()
    temp_dir = create_temp_dir()
    try:
        # cwd to temporarily dir
        os.chdir(temp_dir)
        # case 1 - absent file
        with pytest.raises(ValueError):
            load_version(POETRY_CONFIG_FIlE)  # no pyproject.toml in temporarily directory
        captured = capsys.readouterr()
        assert (
            captured.out.index('Error while loading pyproject.toml file') != -1
        ), 'Wrong error message on case #1 : absent pyproject.toml, mismatch notification in header'
        assert (
            captured.out.index('Error while loading pyproject.toml file') != -1
        ), f'No such file or directory: {str(temp_dir.joinpath(POETRY_CONFIG_FIlE))!r}'

        # case 2 - wrong toml structure

        wrong_toml_structure_file_name = 'notoml.toml'
        with open(wrong_toml_structure_file_name, mode='w') as f:
            f.write('{"version": "0.1.0"}')  # JSON instead of toml
        with pytest.raises(ValueError):
            load_version(wrong_toml_structure_file_name)  # wrong toml in temporarily directory
        captured = capsys.readouterr()
        assert (
            captured.out.index(
                f'Error while parsing {wrong_toml_structure_file_name} file, '
                'details: Invalid statement (at line 1, column 1)'
            )
            != -1
        ), 'Wrong error message on case #2 : wrong toml file, mismatch in notification'
        # case 3, wrong toml file
        wrong_toml_content_file_name = 'badtoml.toml'
        with open(wrong_toml_content_file_name, mode='w') as f:
            f.write(
                '[tool.poetry]\n'
                'name = "blacklist"\n'
                'description = ""\n'
                'authors = ["Dmitriev Andrey <justkeepwalking@yandex.ru>"]\n'
                'readme = "README.md"\n'
            )
        with pytest.raises(ValueError):
            load_version(wrong_toml_content_file_name)  # no 'version' in toml file
        captured = capsys.readouterr()
        assert (
            captured.out.index("Error while parsing file - wrong version info record (KeyError), details: 'version'")
            != -1
        ), 'Wrong error message on case #3 : no version in toml file, mismatch in notification'
        # case 4. Wrong version info
        bad_version_file_name = 'bad_version.toml'
        with open(bad_version_file_name, mode='w') as f:
            f.write('[tool.poetry]\n')
            f.write('version = "1.8.A"')  # alpha letter in version info
        with pytest.raises(ValueError):
            load_version(bad_version_file_name)  # alpha letter in version info
        captured = capsys.readouterr()
        print(captured.out)
        assert (
            captured.out.index(
                "Error while transforming version info, details:  invalid literal for int() with base 10: 'A'"
            )
            != -1
        ), 'Wrong error message on case #4 : bad version info, mismatch in notification'

    finally:
        os.chdir(current_dir)
        remove_dir(temp_dir)
