import json
from lxml import etree

from word_xml_python.extractors.extractor import Extractor
from word_xml_python.models import ExtractorResult, VerifierMeta
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
    demo_spit_result: list[VerifierMeta]

    def __init__(self, file_path: str, demo_spit_result_str: str):
        self.file_path = file_path
        self.file_bytes = open(file_path, "rb").read()
        raw_result = json.loads(demo_spit_result_str)
        self.demo_spit_result = [VerifierMeta(**item) for item in raw_result]

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

    def start_by_table(self, table_xml: bytes | str) -> list[ExtractorResult] | None:
        """
        处理单个表格
        """
        # 确保是字符串格式
        if isinstance(table_xml, bytes):
            table_xml_str = table_xml.decode("UTF-8")
        else:
            table_xml_str = table_xml

        vlmap = Vlmap(table_xml_string=table_xml_str)
        # table_xml 本身就是 w:tbl 元素，不需要再查找
        table = etree.fromstring(table_xml)
        # 解析表格 并生成ai提示
        vlmap.parse_and_tip()
        # 访问ai 拿到分割结果 假设是json字符串
        ai_result = self.demo_spit_result

        trs = table.findall(".//w:tr", WORD_NAMESPACES)
        map_verifier = MapVerifier(verifier_meta=ai_result, trs=trs)
        error_infos = map_verifier.verify()
        if error_infos:
            return None
        else:
            table_splitter = TableSplitter(tblElement=table, verifier_meta=ai_result)
            split_results = table_splitter.split()

            split_results = SplitVerifier(
                table_split_result=split_results
            ).verify_and_fix()
            extractor = Extractor(table_split_results=split_results)

            return extractor.extract()


__all__ = ["Core"]
