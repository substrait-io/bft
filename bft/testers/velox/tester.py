from bft.cases.runner import CaseRunner
from bft.dialects.types import Dialect, DialectsLibrary
from bft.testers.base_tester import BaseTester
from bft.testers.velox.runner import VeloxRunner


class VeloxTester(BaseTester):
    def get_runner(self, dialect: Dialect) -> CaseRunner:
        return VeloxRunner(dialect)

    def get_dialect(self, library: DialectsLibrary) -> Dialect:
        return library.get_dialect_by_name("velox_presto")
