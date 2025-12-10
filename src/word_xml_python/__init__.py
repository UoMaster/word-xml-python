"""
Word XML Python - Word XML文档处理库

一个用于解析和处理Word XML文档的Python库，特别适用于处理表格数据。
"""

from typing import List
from .models import TableInfo, CellInfo
from .parser import WordXMLParser
from .extractors import TableExtractor, CellExtractor
from .exporters import CSVExporter
from .split import TableSplitter, TableSplitResult
from .vlmap import Vlmap, MapVerifier

__version__ = "0.1.0"
__all__ = [
    "TableInfo",
    "CellInfo",
    "WordXMLParser",
    "TableExtractor",
    "CellExtractor",
    "CSVExporter",
    "TableSplitter",
    "TableSplitResult",
    "process_word_table",
    "process_word_table_from_xml",
    "export_to_csv",
    "export_to_str",
    "Vlmap",
    "MapVerifier",
]


# 便捷函数
def process_word_table(file_path: str) -> List[TableSplitResult]:
    """
    处理Word表格的便捷函数

    Args:
        file_path: Word XML文档路径

    Returns:
        表格分割结果列表，每个结果包含表格信息和单元格信息

    Example:
        >>> tables = process_word_table("document.xml")
        >>> for table in tables:
        >>>     print(f"表格类型: {table.table_type}")
        >>>     print(f"单元格数量: {len(table.table_cell_list)}")
    """
    # 解析XML
    parser = WordXMLParser(file_path)
    parser.parse()
    # 查找表格
    table_element = parser.find_table()
    if table_element is None:
        raise ValueError("未找到表格元素")

    table_splitter = TableSplitter(table_element, parser.get_namespaces())
    table_splitter.split()
    tables = table_splitter.getTables()

    for table_meta in tables:
        # 提取表格信息
        table_extractor = TableExtractor(parser.get_namespaces())
        table_info = table_extractor.extract(table_meta.table)
        table_meta.table_info = table_info
        # 提取单元格信息
        cell_extractor = CellExtractor(parser.get_namespaces())
        cell_list = cell_extractor.extract_all(table_meta.table)
        table_meta.table_cell_list = cell_list
        table_meta.table_cell_csv_str = export_to_str(cell_list)

    for table_meta in tables:
        print(table_meta.table_type)
    return tables


def process_word_table_from_xml(xml_string: str) -> List[TableSplitResult]:
    """
    处理Word表格的便捷函数（从XML字符串）

    Args:
        xml_string: Word XML文档字符串内容

    Returns:
        表格分割结果列表，每个结果包含表格信息和单元格信息

    Example:
        >>> xml_content = "<w:document>...</w:document>"
        >>> tables = process_word_table_from_xml(xml_content)
        >>> for table in tables:
        >>>     print(f"表格类型: {table.table_type}")
        >>>     print(f"单元格数量: {len(table.table_cell_list)}")
    """
    # 解析XML
    parser = WordXMLParser(xml_string=xml_string)
    parser.parse()
    # 查找表格
    table_element = parser.find_table()
    if table_element is None:
        raise ValueError("未找到表格元素")

    table_splitter = TableSplitter(table_element, parser.get_namespaces())
    table_splitter.split()
    tables = table_splitter.getTables()

    for table_meta in tables:
        # 提取表格信息
        table_extractor = TableExtractor(parser.get_namespaces())
        table_info = table_extractor.extract(table_meta.table)
        table_meta.table_info = table_info
        # 提取单元格信息
        cell_extractor = CellExtractor(parser.get_namespaces())
        cell_list = cell_extractor.extract_all(table_meta.table)
        table_meta.table_cell_list = cell_list
        table_meta.table_cell_csv_str = export_to_str(cell_list)

    return tables


def export_to_csv(cell_list: list[CellInfo], output_path: str) -> None:
    """
    导出单元格数据到CSV文件的便捷函数

    Args:
        cell_list: 单元格信息列表
        output_path: 输出文件路径

    Example:
        >>> export_to_csv(cell_list, "output.csv")
    """
    CSVExporter.export(cell_list, output_path)


def export_to_str(cell_list: list[CellInfo]) -> str:
    """
    将单元格信息转换为 csv 字符串

    Args:
        cell_list: 单元格信息列表
    """
    return CSVExporter.export_str(cell_list)
