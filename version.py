from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int


# Change application version here
VERSION = {'major': 1, 'minor': 0, 'patch': 0}

VERSION_INFO = Version(**VERSION)
