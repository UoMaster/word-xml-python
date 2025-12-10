from dataclasses import dataclass


@dataclass
class XmlMeta:
    """XML元数据"""

    tag: str
    body: str

    def __repr__(self) -> str:
        return f"XmlMeta(type={self.tag}, body={self.body})"
