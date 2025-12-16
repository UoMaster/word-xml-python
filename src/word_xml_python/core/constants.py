"""常量定义"""

# 需要从tcPr中删除的标签列表
TCPR_DELETE_TAGS = ["w:tcW"]

# Word XML 命名空间
WORD_NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
}

# Word 主命名空间 URI
WORD_NS_URI = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
