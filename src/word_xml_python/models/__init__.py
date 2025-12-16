"""数据模型模块"""

from .table import TableInfo
from .cell import CellInfo, CellPBody, CellRBody
from .xml_meta import XmlMeta
from .verifier import VerifierMeta, ErrorInfo
from .spit import TableSplitResult

__all__ = [
    "TableInfo",
    "CellInfo",
    "CellPBody",
    "CellRBody",
    "XmlMeta",
    "VerifierMeta",
    "ErrorInfo",
    "TableSplitResult",
]
