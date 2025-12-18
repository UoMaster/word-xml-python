"""
Word XML Python - Word XML文档处理库

一个用于解析和处理Word XML文档的Python库，特别适用于处理表格数据。
"""

from .models import TableInfo, CellInfo, TableSplitResult
from .extractors import TableExtractor, CellExtractor
from .split import TableSplitter
from .vlmap import Vlmap, MapVerifier

__version__ = "0.1.0"
__all__ = [
    "TableInfo",
    "CellInfo",
    "TableExtractor",
    "CellExtractor",
    "TableSplitter",
    "TableSplitResult",
    "process_word_table",
    "process_word_table_from_xml",
    "export_to_csv",
    "export_to_str",
    "Vlmap",
    "MapVerifier",
]
