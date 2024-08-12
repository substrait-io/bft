from decimal import Decimal
from typing import NamedTuple

from bft.core.yaml_parser import BaseYamlParser


class TestDecimalResult(NamedTuple):
    cases: Decimal | list[Decimal]

class TestCaseVisitor():
    def visit(self, testcase):
        return TestDecimalResult(testcase)
class DecimalTestCaseParser(BaseYamlParser[TestDecimalResult]):
    def get_visitor(self) -> TestCaseVisitor:
        return TestCaseVisitor()

def test_yaml_parser_decimal_tag():
    parser = DecimalTestCaseParser()
    # parser returns list of parsed values
    assert   parser.parse(b"!decimal 1") == [TestDecimalResult(Decimal('1'))]
    assert   parser.parse(b"!decimal 1.78766") == [TestDecimalResult(Decimal('1.78766'))]
    assert parser.parse(b"!decimal null") == [TestDecimalResult(None)]
    assert parser.parse(b"!decimallist [1.2, null, 7.547]") == [TestDecimalResult([Decimal('1.2'), None, Decimal('7.547')])]
