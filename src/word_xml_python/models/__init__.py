"""数据模型模块"""

from .xml_meta import XmlMeta
from .verifier import VerifierMeta, ErrorInfo
from .spit import TableSplitResult
from .extractor import ExtractorResult, TableInfo, CellInfo, CellPBody, CellRBody

__all__ = [
    "TableInfo",
    "ExtractorResult",
    "CellInfo",
    "CellPBody",
    "CellRBody",
    "XmlMeta",
    "VerifierMeta",
    "ErrorInfo",
    "TableSplitResult",
]
