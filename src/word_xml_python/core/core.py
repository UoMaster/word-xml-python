from lxml import etree

from word_xml_python.extractors.extractor import Extractor
from word_xml_python.split.split_verifier import SplitVerifier
from ..split import TableSplitter
from ..vlmap import Vlmap, MapVerifier
from ..core.constants import WORD_NAMESPACES


class Core:
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path

    def start(self):
        xml_string = open(self.file_path, "rb").read()
        tree = etree.fromstring(xml_string)
        table_element = tree.find(".//w:tbl", WORD_NAMESPACES)
        for table in table_element:
            vlmap = Vlmap(table_xml_string=etree.tostring(table))

            # 解析表格 并生成ai提示
            ai_tip = vlmap.parse_and_tip()
            print(ai_tip)
            # 访问ai 拿到分割结果 假设是json字符串
            ai_result = []

            trs = table.findall(".//w:tr", WORD_NAMESPACES)
            map_verifier = MapVerifier(verifier_meta=ai_result, trs=trs)
            error_infos = map_verifier.verify()
            if error_infos:
                print(error_infos)
            else:
                table_splitter = TableSplitter(table_element=table)
                split_results = table_splitter.split()

                split_results = SplitVerifier(
                    split_results=split_results
                ).verify_and_fix()
                extractor = Extractor(split_results=split_results)

                return extractor.extract()


__all__ = ["Core"]
