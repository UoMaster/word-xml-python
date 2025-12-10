import copy
import json
import os
from word_xml_python import Vlmap, MapVerifier
from lxml import etree
import pyperclip


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    xml_path = os.getenv("XML_PATH", os.path.join(project_root, "word_meta/word/document.xml"))
    xml_bytes = open(xml_path, "rb").read()
    # 读取环境变量
    model = os.getenv("MODEL")
    if model == "vl":
        s = get_vl_map(xml_bytes)
        print("vl_map:")
        print(s)
        pyperclip.copy(s)
    elif  model == "vl_v":
        # 读取同级目录的 json.txt 文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_string = open(os.path.join(script_dir, "json.txt"), "r").read()
        get_map_verifier(xml_bytes, json_string)


def get_vl_map(xml_string: bytes) -> str:
    # 读取xml文件

    tree = etree.fromstring(xml_string)
    rootnamespaces = tree.nsmap
    # 创建Vlmap对象
    vlmap = Vlmap(etree.tostring(tree.find(".//w:tbl", rootnamespaces)))
    # 解析表格
    return vlmap.parse_and_tip()


def get_map_verifier(xml_string: bytes, json_string: str) -> MapVerifier:
    tree = etree.fromstring(xml_string)
    rootnamespaces = tree.nsmap
    # 创建Vlmap对象
    trs = tree.find(".//w:tbl", rootnamespaces).findall(".//w:tr", rootnamespaces)
    map_verifier = MapVerifier(
        verifier_meta=json.loads(json_string), trs=trs, namespaces=rootnamespaces, 
    )
    errors = map_verifier.verify()
    if errors:
        print(errors)
    else:
        print("没有错误")


if __name__ == "__main__":
    main()
