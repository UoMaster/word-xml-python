"""
Word XML Python - Word XML文档处理库

一个用于解析和处理Word XML文档的Python库，特别适用于处理表格数据。
"""

from typing import List
from .models import TableInfo, CellInfo
from .parser import WordXMLParser
from .extractors import TableExtractor, CellExtractor
from .exporters import CSVExporter
from .split import TableSplitter

__version__ = "0.1.0"
__all__ = [
    "TableInfo",
    "CellInfo",
    "WordXMLParser",
    "TableExtractor",
    "CellExtractor",
    "CSVExporter",
    "TableSplitter"
]


# 便捷函数
def process_word_table(file_path: str) -> tuple[TableInfo, List[List[CellInfo]]]:
    """
    处理Word表格的便捷函数
    
    Args:
        file_path: Word XML文档路径
        
    Returns:
        (表格信息, 单元格信息列表)
        
    Example:
        >>> table_info, cell_list = process_word_table("document.xml")
        >>> print(table_info)
        >>> print(f"找到 {len(cell_list)} 个单元格")
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
    
    cell_meta_list: List[List[CellInfo]] = []
    for table in tables:
      # 提取表格信息
      table_extractor = TableExtractor(parser.get_namespaces())
      table_info = table_extractor.extract(table)
      
      # 提取单元格信息
      cell_extractor = CellExtractor(parser.get_namespaces())
      cell_list = cell_extractor.extract_all(table)
      cell_meta_list.append(cell_list)
    
    return table_info, cell_meta_list


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
