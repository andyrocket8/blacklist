from collections.abc import Hashable
from typing import Type
from typing import TypeVar

# Abstract type for generic definitions
T = TypeVar('T')
TypeT = Type[T]

# Abstract type for hashes
H = TypeVar('H', bound=Hashable)
TypeH = Type[H]

# Abstract type for keys
K = TypeVar('K', bound=Hashable)
TypeK = Type[K]

# Abstract type for set values
V = TypeVar('V')
TypeV = Type[V]

# Abstract type for storages
Internal = TypeVar('Internal')
TypeInternal = Type[Internal]

# TypeVars for Internal DB types
KInternal = TypeVar('KInternal', bound=Hashable)
VInternal = TypeVar('VInternal')
HInternal = TypeVar('HInternal', bound=Hashable)
