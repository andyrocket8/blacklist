from abc import ABC
from abc import abstractmethod


class AbstractDBList(ABC):
    @abstractmethod
    def create(self):
        pass
