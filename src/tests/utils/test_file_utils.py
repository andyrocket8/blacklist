from src.utils.file_utils import create_temp_dir
from src.utils.file_utils import remove_dir


def test_file_utils():
    """Pytest routine for checking file utils"""
    temp_dir = create_temp_dir()
    assert temp_dir.is_dir() is True, 'Test temporarily directory should be created'
    inside_temp_dir = create_temp_dir(temp_dir)
    assert inside_temp_dir.is_dir() is True, 'Error on checking temporarily directory in temp dir - not a dir'
    temp_file = inside_temp_dir.joinpath('some_file.txt')
    with open(temp_file, mode='w') as f:
        f.write('File contents')
    assert temp_file.is_file() is True, 'Error on checking temporarily created file - not a file'
    remove_dir(temp_dir)
    assert temp_dir.is_dir() is False, 'Test temporarily directory should be removed'
