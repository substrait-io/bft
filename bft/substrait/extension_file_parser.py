from collections import namedtuple
from collections.abc import Iterable
from typing import Dict, List, NamedTuple

import yaml

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader, SafeDumper

from typing import BinaryIO

from ..core.function import FunctionBuilder, LibraryBuilder


class ValueArg(NamedTuple):
    name: str
    description: str
    type: str


class EnumArg(NamedTuple):
    name: str
    description: str
    options: List[str]


class Implementation(NamedTuple):
    args: List[ValueArg | EnumArg]
    options: Dict[str, List[str]]
    return_type: str


class ScalarFunction(NamedTuple):
    name: str
    description: str
    implementations: List[Implementation]


class ExtensionsFile(NamedTuple):
    scalar_functions: List[ScalarFunction]


class ExtensionFileVisitor(object):
    def __init__(self):
        self.location_stack = []

    def __fail(self, err):
        loc = "/".join(self.location_stack)
        raise Exception(f"Error visiting extension file.  Location={loc} Message={err}")

    def __visit_list(self, visitor, obj, attr, required=False):
        if attr in obj:
            val = obj[attr]
            results = []
            if not isinstance(val, Iterable):
                self.__fail(f"Expected attribute {attr} to be iterable")
            for idx, item in enumerate(val):
                self.location_stack.append(f"{attr}[{idx}]")
                results.append(visitor(item))
                self.location_stack.pop()
            return results
        elif required:
            self.__fail(f"Expected required attribute {attr}")
        else:
            return []

    def __get_or_die(self, obj, attr):
        if attr in obj:
            return obj[attr]
        self.__fail(f"Expected required attribute {attr}")

    def __get_or_else(self, obj, attr, default):
        if attr in obj:
            return obj[attr]
        return default

    def visit_ext_file(self, parsed_file):
        scalar_functions = self.__visit_list(
            self.visit_scalar_function, parsed_file, "scalar_functions"
        )
        return ExtensionsFile(scalar_functions)

    def visit_impl_arg(self, arg):
        name = self.__get_or_else(arg, "name", None)
        description = self.__get_or_else(arg, "description", None)
        value = self.__get_or_else(arg, "value", None)
        if value:
            return ValueArg(name, description, value)
        else:
            options = self.__get_or_else(arg, "options", None)
            if options is None:
                self.__fail(
                    "Argument encountered that did not have any value or options"
                )
            return EnumArg(name, description, options)

    def visit_implementation(self, impl):
        args = self.__visit_list(self.visit_impl_arg, impl, "args")
        options = self.__get_or_else(impl, "options", {})
        opts = {}
        for key in options.keys():
            values = self.__get_or_die(options[key], "values")
            opts[key] = values
        return_type = self.__get_or_die(impl, "return")
        return Implementation(args, opts, return_type)

    def visit_scalar_function(self, func):
        name = self.__get_or_die(func, "name")
        description = self.__get_or_else(func, "description", None)
        implementations = self.__visit_list(self.visit_implementation, func, "impls")
        return ScalarFunction(name, description, implementations)


class ExtensionFileParser(object):
    def parse(self, f: BinaryIO) -> None:
        data = yaml.load(f, SafeLoader)
        return ExtensionFileVisitor().visit_ext_file(data)


def add_extensions_file_to_library(ext_file: ExtensionsFile, library: LibraryBuilder):
    for scalar_func in ext_file.scalar_functions:
        builder: FunctionBuilder = library.get_function(scalar_func.name)
        if scalar_func.description is not None:
            builder.try_set_description(scalar_func.description)
        for impl in scalar_func.implementations:
            for opt_name, opt_values in impl.options.items():
                builder.note_option(opt_name, opt_values)
            arg_types = []
            for arg in impl.args:
                if isinstance(arg, ValueArg):
                    arg_types.append(arg.type)
                else:
                    arg_types.append("|".join(arg.options))
            builder.note_kernel(arg_types, impl.return_type, impl.options.keys())
