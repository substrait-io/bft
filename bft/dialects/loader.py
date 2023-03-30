from pathlib import Path
from typing import List

from .parser import DialectFileParser
from .types import DialectFile, DialectsLibrary


def load_dialects(dialects_dir: str) -> DialectsLibrary:
    parser = DialectFileParser()
    dialect_files: List[DialectFile] = []
    for dialect_path in Path(dialects_dir).rglob("*.yaml"):
        with open(dialect_path, "rb") as dialect_f:
            for dialect_file in parser.parse(dialect_f):
                dialect_files.append(dialect_file)
    return DialectsLibrary(dialect_files)
