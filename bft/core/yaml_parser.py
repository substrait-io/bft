from abc import ABC, abstractmethod
from typing import BinaryIO, Generic, Iterable, List, TypeVar

import yaml

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader

T = TypeVar("T")


class BaseYamlVisitor(ABC, Generic[T]):
    def __init__(self):
        self.__location_stack: List[str] = []

    def _fail(self, err):
        loc = "/".join(self.__location_stack)
        raise Exception(f"Error visiting case file.  Location={loc} Message={err}")

    def _visit_list(self, visitor, obj, attr, required=False):
        if attr in obj:
            val = obj[attr]
            results = []
            if not isinstance(val, Iterable):
                self._fail(f"Expected attribute {attr} to be iterable")
            for idx, item in enumerate(val):
                self.__location_stack.append(f"{attr}[{idx}]")
                results.append(visitor(item))
                self.__location_stack.pop()
            return results
        elif required:
            self._fail(f"Expected required attribute {attr}")
        else:
            return []

    def __visit_or_maybe_die(self, visitor, obj, attr, required, default=None):
        if attr in obj:
            val = obj[attr]
            self.__location_stack.append(f"{attr}")
            visited = visitor(val)
            self.__location_stack.pop()
            return visited
        elif required:
            self._fail(f"Expected required attribte {attr}")
        else:
            return default

    def _visit_or_die(self, visitor, obj, attr):
        return self.__visit_or_maybe_die(visitor, obj, attr, False)

    def _visit_or_else(self, visitor, obj, attr, default):
        return self.__visit_or_maybe_die(visitor, obj, attr, True, default)

    def _get_or_die(self, obj, attr):
        if attr in obj:
            return obj[attr]
        self._fail(f"Expected required attribute {attr}")

    def _get_or_else(self, obj, attr, default):
        if attr in obj:
            return obj[attr]
        return default

    @abstractmethod
    def visit(yamlobj) -> T:
        pass


class BaseYamlParser(ABC, Generic[T]):
    @abstractmethod
    def get_visitor(self) -> BaseYamlVisitor[T]:
        pass

    def parse(self, f: BinaryIO) -> List[T]:
        objs = yaml.load_all(f, SafeLoader)
        visitor = self.get_visitor()
        return [visitor.visit(obj) for obj in objs]
