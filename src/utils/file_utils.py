# some awesome file utils
import tempfile
from os import chmod as os_chmod
from os import remove as os_remove
from os import rmdir as os_rmdir
from os import walk as os_walk
from pathlib import Path
from typing import Optional
from typing import Union

StrPath = Union[str, Path]


def create_temp_dir(base_path: Optional[StrPath] = None) -> Path:
    """
    Create temp file (Use stdlib module tempfile)
    :param Optional[str, Path] base_path: base path to temp dir
    :return: Path: path to created folder
    """
    base_path = str(base_path) if base_path is not None else None
    tmp_dir_name = tempfile.mkdtemp(suffix=None, prefix=None, dir=base_path)
    return Path(tmp_dir_name)


def remove_dir(dir_path: Union[str, Path]):
    """
    Remove dir with all siblings
    :param Union[str, Path] dir_path: path to erased folder
    :return: None
    """
    for root, dirs, files in os_walk(dir_path, topdown=False):
        for name in files:
            try:
                os_chmod(Path(root).joinpath(name), 0o777)
            except PermissionError:
                pass
            os_remove(Path(root).joinpath(name))
        for name in dirs:
            os_rmdir(Path(root).joinpath(name))
    os_rmdir(dir_path)
