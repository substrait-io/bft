import math
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import BinaryIO, Generic, Iterable, List, TypeVar

import yaml

from bft.cases.types import CaseLiteral

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
            for result in results:
                if isinstance(result, CaseLiteral) and isinstance(result.value, list):
                    if len(result.value) > 0:
                        for i, s in enumerate(result.value):
                            lower_s = str(s).lower()
                            if lower_s.startswith("'inf'"):
                                result.value[i] = float("inf")
                            elif lower_s.startswith("'-inf'"):
                                result.value[i] = float("-inf")
                            elif lower_s.startswith("'nan'"):
                                result.value[i] = math.nan
                        results.append(CaseLiteral(result.value, result.type, result.is_not_a_func_arg))
                        results.remove(result)
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

    def get_loader(self):
        loader = yaml.SafeLoader
        """Add tag "!decimal" to the loader """
        loader.add_constructor("!decimal", self.decimal_constructor)
        loader.add_constructor("!decimallist", self.list_of_decimal_constructor)
        return loader

    def decimal_constructor(self, loader: yaml.SafeLoader, node: yaml.nodes.MappingNode):
        return self.get_decimal_value(loader, node)

    def get_decimal_value(self, loader: yaml.SafeLoader, node: yaml.ScalarNode):
        value = loader.construct_scalar(node)
        if isinstance(value, str) and value.lower() == 'null':
            return None
        return Decimal(value)

    def list_of_decimal_constructor(self, loader: yaml.SafeLoader, node: yaml.nodes.MappingNode):
        return [self.get_decimal_value(loader, item) for item in node.value]

    def parse(self, f: BinaryIO) -> List[T]:
        loader = self.get_loader()
        objs = yaml.load_all(f, loader)
        visitor = self.get_visitor()
        return [visitor.visit(obj) for obj in objs]
