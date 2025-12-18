from typing import List
from lxml import etree
from .table_extractor import TableExtractor
from .cell_extractor import CellExtractor
from ..models import TableSplitResult, ExtractorResult, TableInfo


class Extractor:
    table_split_results: List[TableSplitResult]
    extractor_results: List[ExtractorResult]

    def __init__(self, table_split_results: List[TableSplitResult]):
        self.table_split_results = table_split_results
        self.extractor_results = []

    def extract(self) -> List[ExtractorResult]:
        for table_split_result in self.table_split_results:
            extractor_result = ExtractorResult(
                table_info=TableInfo(),
                cell_info_list=[],
                table_type=table_split_result.table_type,
            )
            xml_element = etree.fromstring(table_split_result.table_xml.encode("UTF-8"))
            extractor_result.table_info = TableExtractor().extract(xml_element)
            extractor_result.cell_info_list = CellExtractor().extract_all(xml_element)
            self.extractor_results.append(extractor_result)
        return self.extractor_results
