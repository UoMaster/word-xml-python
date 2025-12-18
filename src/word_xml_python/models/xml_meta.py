from pydantic import BaseModel


class XmlMeta(BaseModel):
    """XML元数据"""

    tag: str
    body: str

    def __repr__(self) -> str:
        return f"XmlMeta(type={self.tag}, body={self.body})"
