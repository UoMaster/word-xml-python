"""Word XML解析器"""

from typing import Dict, Optional
from lxml import etree
from lxml.etree import _Element


class WordXMLParser:
    """Word XML文档解析器"""

    def __init__(self, file_path: Optional[str] = None, xml_string: Optional[str] = None):
        """
        初始化解析器

        Args:
            file_path: Word XML文档路径（可选）
            xml_string: Word XML字符串内容（可选）
            
        注意：file_path 和 xml_string 必须提供其中一个
        """
        if file_path is None and xml_string is None:
            raise ValueError("必须提供 file_path 或 xml_string 参数")
        if file_path is not None and xml_string is not None:
            raise ValueError("file_path 和 xml_string 不能同时提供")
            
        self.file_path = file_path
        self.xml_string = xml_string
        self.tree: _Element | None = None
        self.namespaces: Dict[str, str] = {}

    def parse(self) -> _Element:
        """
        解析XML文档

        Returns:
            解析后的XML树根节点
        """
        if self.file_path:
            with open(self.file_path, "rb") as f:
                content = f.read()
        else:
            # 如果是字符串，转换为bytes
            content = self.xml_string.encode('utf-8') if isinstance(self.xml_string, str) else self.xml_string

        self.tree = etree.fromstring(content)
        self._process_namespaces()

        return self.tree

    def _process_namespaces(self) -> None:
        """处理XML命名空间"""
        if self.tree is None:
            raise ValueError("XML树未初始化，请先调用parse()方法")

        self.namespaces = self.tree.nsmap.copy()

        # 处理默认命名空间
        if None in self.namespaces:
            self.namespaces["w"] = self.namespaces.pop(None)

    def get_namespaces(self) -> Dict[str, str]:
        """
        获取命名空间映射

        Returns:
            命名空间字典
        """
        return self.namespaces

    def find_table(self) -> _Element | None:
        """
        查找文档中的表格元素

        Returns:
            表格元素，如果未找到返回None
        """
        if self.tree is None:
            raise ValueError("XML树未初始化，请先调用parse()方法")

        return self.tree.find(".//w:tbl", self.namespaces)
