from lxml import etree

from word_xml_python.extractors.extractor import Extractor
from word_xml_python.models import ExtractorResult
from word_xml_python.split.split_verifier import SplitVerifier
from ..split import TableSplitter
from ..vlmap import Vlmap, MapVerifier
from ..core.constants import WORD_NAMESPACES


class Core:
    """
    核心类
    调度所有模块的执行
    """

    file_path: str
    file_bytes: bytes

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_bytes = open(file_path, "rb").read()

    def get_xml_tables(self) -> list[str]:
        """
        获取所有表格的xml字符串
        """
        tree = etree.fromstring(self.file_bytes)
        tables = tree.findall(".//w:tbl", WORD_NAMESPACES)

        return [
            etree.tostring(table, pretty_print=True, encoding="UTF-8")
            for table in tables
        ]

    def start_all_by_tables(
        self, table_xmls: list[str]
    ) -> list[list[ExtractorResult] | None]:
        """
        一次性处理所有表格
        """
        return [self.start_by_table(table_xml) for table_xml in table_xmls]

    def start_by_table(self, table_xml: str) -> list[ExtractorResult] | None:
        """
        处理单个表格
        """
        vlmap = Vlmap(table_xml_string=table_xml)
        tree = etree.fromstring(table_xml)
        table = tree.find(".//w:tbl", WORD_NAMESPACES)
        # 解析表格 并生成ai提示
        ai_tip = vlmap.parse_and_tip()
        print(ai_tip)
        # 访问ai 拿到分割结果 假设是json字符串
        ai_result = []

        trs = table.findall(".//w:tr", WORD_NAMESPACES)
        map_verifier = MapVerifier(verifier_meta=ai_result, trs=trs)
        error_infos = map_verifier.verify()
        if error_infos:
            return None
        else:
            table_splitter = TableSplitter(table_element=table)
            split_results = table_splitter.split()

            split_results = SplitVerifier(split_results=split_results).verify_and_fix()
            extractor = Extractor(split_results=split_results)

            return extractor.extract()


__all__ = ["Core"]
