from bft.dialects.types import Dialect, DialectsLibrary
from bft.testers.base_tester import BaseTester

from .runner import PostgresRunner


class PostgresTester(BaseTester):
    def get_runner(self, dialect: Dialect):
        return PostgresRunner(dialect)

    def get_dialect(self, library: DialectsLibrary):
        return library.get_dialect_by_name("postgres")
