from lxml import etree
from word_xml_python.core import WORD_NAMESPACES
from ..models import TableSplitResult
from typing import List


class SplitVerifier:
    """表格分割验证器"""

    table_split_result: List[TableSplitResult]  # 修复类型注解

    def __init__(self, table_split_result: List[TableSplitResult]):
        self.table_split_result = table_split_result

    def verify_and_fix(self) -> List[TableSplitResult]:
        for index in range(len(self.table_split_result)):
            result_table = self.table_split_result[index]
            if result_table.table_type == "RepeatTable":
                self._verify_repeat_table(result_table)
        return self.table_split_result

    def _verify_repeat_table(self, result_table: TableSplitResult):
        table_element = etree.fromstring(result_table.table_xml.encode("UTF-8"))

        for cell in table_element.findall(".//w:tc", WORD_NAMESPACES):
            tc_pr = cell.find("w:tcPr", WORD_NAMESPACES)
            if tc_pr is not None:
                v_merge = tc_pr.find("w:vMerge", WORD_NAMESPACES)
                if v_merge is not None:
                    tc_pr.remove(v_merge)

                grid_span = tc_pr.find("w:gridSpan", WORD_NAMESPACES)
                if grid_span is not None:
                    tc_pr.remove(grid_span)

        result_table.table_xml = etree.tostring(
            table_element, pretty_print=True, encoding="UTF-8"
        ).decode("UTF-8")

        return result_table
