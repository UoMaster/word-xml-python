import json
from word_xml_python import Vlmap, MapVerifier
from lxml import etree

MOKE_JSON = """
[
{
"name": "基本信息",
"rows": [1, 2],
"type": "Form",
"reason": "单行字段结构，包含姓名、部门、申请时间、紧急联系电话等基本信息"
},
{
"name": "请假信息",
"rows": [3, 4, 5, 6, 7, 8],
"type": "Form",
"reason": "包含请假类型、时间、时长、事由等单行或跨行字段，无重复数据结构"
},
{
"name": "工作交接表",
"rows": [9, 10, 11],
"type": "RepeatTable",
"reason": "有明确的表头行（序号、负责学校、临时处理人、临时处理人电话），下方包含多行结构相同的空白行用于填写重复数据"
},
{
"name": "审批信息",
"rows": [12, 13],
"type": "Form",
"reason": "包含负责人审批和主管领导审批的单行字段"
}
]
"""


def main():
    xml_bytes = open(
        "/Users/wuhongbin/Code/word-xml-python/word_meta/word/document.xml", "rb"
    ).read()
    # get_map_verifier(xml_bytes, MOKE_JSON)
    print(get_vl_map(xml_bytes))


def get_vl_map(xml_string: bytes) -> str:
    # 读取xml文件

    tree = etree.fromstring(xml_string)
    rootnamespaces = tree.nsmap
    # 创建Vlmap对象
    vlmap = Vlmap(etree.tostring(tree.find(".//w:tbl", rootnamespaces)))
    # 解析表格
    return vlmap.parse()


def get_map_verifier(xml_string: bytes, json_string: str) -> MapVerifier:
    tree = etree.fromstring(xml_string)
    rootnamespaces = tree.nsmap
    # 创建Vlmap对象
    trs = tree.find(".//w:tbl", rootnamespaces).findall(".//w:tr", rootnamespaces)
    map_verifier = MapVerifier(
        verifier_meta=json.loads(json_string), trs=trs, namespaces=rootnamespaces, 
    )
    print(map_verifier.verify())


if __name__ == "__main__":
    main()
