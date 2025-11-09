"""表格信息提取器"""

from typing import Dict
from lxml.etree import _Element

from ..models import TableInfo


class TableExtractor:
    """表格信息提取器"""
    
    def __init__(self, namespaces: Dict[str, str]):
        """
        初始化提取器
        
        Args:
            namespaces: XML命名空间映射
        """
        self.namespaces = namespaces
    
    def extract(self, table_element: _Element) -> TableInfo:
        """
        从表格元素中提取表格信息
        
        Args:
            table_element: 表格XML元素
            
        Returns:
            表格信息对象
        """
        # 获取列数
        tbl_grid = table_element.find("./w:tblGrid", self.namespaces)
        col_count = len(tbl_grid) if tbl_grid is not None else 0
        
        # 获取行数
        rows = table_element.findall(".//w:tr", self.namespaces)
        row_count = len(rows)
        
        return TableInfo(col=col_count, row=row_count)

