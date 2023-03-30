from typing import List, NamedTuple

from .yaml_parser import BaseYamlParser, BaseYamlVisitor


class IndexFunctionsFile(NamedTuple):
    location: str
    canonical_uri: str

class IndexFile(NamedTuple):
    function_files: List[IndexFunctionsFile]
    case_directories: List[str]
    dialect_directories: List[str]
    supplement_directories: List[str]

class IndexFileVisitor(BaseYamlVisitor[IndexFile]):
    def __init__(self):
        super().__init__()

    def visit_function_file(self, function_file):
        location = self._get_or_die(function_file, "location")
        canonical_uri = self._get_or_die(function_file, "canonical")
        return IndexFunctionsFile(location, canonical_uri)

    def visit(self, index_file):
        substrait = self._get_or_die(index_file, "substrait")
        function_files = self._visit_list(self.visit_function_file, substrait, "extensions")
        case_files = self._get_or_else(index_file, "cases", [])
        dialect_files = self._get_or_else(index_file, "dialects", [])
        supplement_files = self._get_or_else(index_file, "supplements", [])
        return IndexFile(function_files, case_files, dialect_files, supplement_files)


class IndexFileParser(BaseYamlParser[IndexFile]):
    def get_visitor(self) -> IndexFile:
        return IndexFileVisitor()

def load_index(index_path: str) -> IndexFile:
    parser = IndexFileParser()
    with open(index_path, 'rb') as f:
        return parser.parse(f)[0]