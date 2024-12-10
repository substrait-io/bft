from typing import List, NamedTuple


class Option(NamedTuple):
    name: str
    values: List[str]


class Kernel(NamedTuple):
    arg_types: List[str]
    return_type: str
    available_options: List[str]
    variadic: str


class FunctionDefinition(object):
    def __init__(
        self,
        name: str,
        uri: str,
        description: str,
        options: List[Option],
        kernels: List[Kernel],
    ):
        self.name = name
        self.uri = uri
        self.description = description
        self.options = options
        self.kernels = kernels

    @property
    def details(self):
        return []

    @property
    def properties(self):
        return


class FunctionBuilder(object):
    def __init__(self, name: str):
        self.name = name
        self.uri: str = None
        self.description: str = None
        self.options = {}
        self.kernels = []

    def set_description(self, description: str):
        self.description = description

    def set_uri(self, uri: str):
        self.uri = uri

    def try_set_description(self, description: str):
        if self.description is None:
            self.description = description

    def note_option(self, name: str, values: List[str]):
        if name in self.options:
            existing_values = self.options[name]
            # Merge existing values and new values using set union
            self.options[name] = list(set(existing_values).union(values))
        else:
            # Add the new values directly if the option does not exist
            self.options[name] = values

    def note_kernel(
        self,
        arg_types: List[str],
        return_type: str,
        available_options: List[str],
        variadic: int,
    ):
        self.kernels.append(Kernel(arg_types, return_type, available_options, variadic))

    def finish(self) -> FunctionDefinition:
        if self.description is None:
            self.description = "Description is missing and would go here"
        opts = []
        for key, values in self.options.items():
            opts.append(Option(key, values))
        return FunctionDefinition(
            self.name, self.uri, self.description, opts, self.kernels
        )


class LibraryBuilder(object):
    def __init__(self):
        self.functions = {}

    def get_function(self, name, category):
        full_name = f"{category}_{name}"
        if name not in self.functions:
            self.functions[full_name] = FunctionBuilder(full_name)
        return self.functions[full_name]

    def function_names(self) -> List[str]:
        return sorted(self.functions.keys())

    def finish(self) -> List[FunctionDefinition]:
        built_functions = []
        for func_name in sorted(self.functions.keys()):
            built_functions.append(self.functions[func_name].finish())
        return built_functions
