from bft.dialects.types import Dialect, DialectsLibrary
from bft.testers.base_tester import BaseTester

from .runner import DatafusionRunner


class DatafustionTester(BaseTester):
    def get_runner(self, dialect: Dialect):
        return DatafusionRunner(dialect)

    def get_dialect(self, library: DialectsLibrary):
        return library.get_dialect_by_name("datafusion")
