from pathlib import Path
from typing import List

import pytest

from bft.dialects.loader import load_dialects
from bft.dialects.types import DialectsLibrary


@pytest.fixture(scope="session")
def dialects() -> DialectsLibrary:
    dialects_dir = Path(__file__) / ".." / ".." / ".." / "dialects"
    return load_dialects(str(dialects_dir.resolve()))
