from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int


# Change application version here
VERSION = {'major': 1, 'minor': 1, 'patch': 0}

VERSION_INFO = Version(**VERSION)


def get_version():
    return '{}.{}.{}'.format(VERSION_INFO.major, VERSION_INFO.minor, VERSION_INFO.patch)
