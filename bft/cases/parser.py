import math
from typing import BinaryIO, Iterable, List

from bft.core.yaml_parser import BaseYamlParser, BaseYamlVisitor

from .types import Case, CaseFile, CaseGroup, CaseLiteral, ProtoCase


class CaseFileVisitor(BaseYamlVisitor[CaseFile]):
    def __init__(self):
        super().__init__()
        self.__groups = {}

    def __resolve_proto_case(self, case: ProtoCase, function: str) -> Case:
        if case.group not in self.__groups:
            raise Exception(
                "A case referred to group {case.group} which was not defined in the file"
            )
        grp = self.__groups[case.group]
        return Case(function, grp, case.args, case.result, case.options)

    def visit_group(self, group):
        id = self._get_or_die(group, "id")
        description = self._get_or_die(group, "description")
        self.__groups[id] = CaseGroup(id, description)
        return id

    def visit_literal(self, lit):
        value = self._get_or_die(lit, "value")
        data_type = self._get_or_die(lit, "type")
        # YAML/JSON can't represent infinity or nan
        # so its a special case
        if data_type.startswith("fp"):
            if isinstance(value, str):
                if value.lower().startswith("inf"):
                    value = "'" + "Infinity" + "'"
                elif value.lower().startswith("-inf"):
                    value = "'" + "-Infinity" + "'"
                elif value.lower().startswith("nan"):
                    value = math.nan
                else:
                    raise ValueError(f"Unrecognized fp32 string literal {value}")
        return CaseLiteral(value, data_type)

    def visit_literal_result(self, lit):
        value = self._get_or_die(lit, "value")
        data_type = self._get_or_die(lit, "type")
        # YAML/JSON can't represent infinity or nan
        # so its a special case
        if data_type.startswith("fp"):
            if isinstance(value, str):
                if value.lower().startswith("inf"):
                    value = math.inf
                elif value.lower().startswith("-inf"):
                    value = -math.inf
                elif value.lower().startswith("nan"):
                    value = math.nan
                else:
                    raise ValueError(f"Unrecognized fp32 string literal {value}")
        return CaseLiteral(value, data_type)

    def visit_result(self, res):
        special = self._get_or_else(res, "special", None)
        if special is None:
            return self.visit_literal_result(res)
        return special

    def visit_case(self, case):
        grp = self._get_or_die(case, "group")
        if not isinstance(grp, str):
            grp = self.visit_group(grp)
        result = self._visit_or_die(self.visit_result, case, "result")
        args = self._visit_list(self.visit_literal, case, "args")
        opts = self._get_or_else(case, "options", {})
        opt_tuples = []
        for opt_key in sorted(opts.keys()):
            opt_tuples.append((opt_key, opts[opt_key]))
        return ProtoCase(grp, args, result, opt_tuples)

    def visit(self, case_file):
        func_name = self._get_or_die(case_file, "function")
        proto_cases = self._visit_list(self.visit_case, case_file, "cases")
        cases = [self.__resolve_proto_case(c, func_name) for c in proto_cases]
        return CaseFile(func_name, cases)


class CaseFileParser(BaseYamlParser[CaseFile]):
    def get_visitor(self) -> CaseFileVisitor:
        return CaseFileVisitor()
