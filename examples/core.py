import json
import os
import sys

import pyperclip
from word_xml_python.core.core import Core


def main():
    if len(sys.argv) > 1:
        docx_path = sys.argv[1].strip()
    else:
        print("请输入docx文件路径（可直接拖拽文件到此处）:")
        docx_path = input().strip().strip("'\"")

    if not docx_path:
        print("未提供文件路径，程序退出")
        return

    if not os.path.exists(docx_path):
        print(f"✗ 文件不存在: {docx_path}")
        return

    print(f"处理文件: {docx_path}")
    demo_spit_result_str = """
    [
  {
    "name": "基本信息区域",
    "rows": [1, 2, 3, 4, 5, 6, 7, 8],
    "type": "Form",
    "reason": "包含姓名、部门、请假类型、时间、事由等单行字段，无重复数据行结构"
  },
  {
    "name": "工作交接信息重复表",
    "rows": [9, 10, 11],
    "type": "RepeatTable",
    "reason": "第9行是表头（序号、负责学校、临时处理人、电话），第10-11行是结构相同的空白数据行，用于填写多条交接记录"
  },
  {
    "name": "审批信息区域",
    "rows": [12, 13],
    "type": "Form",
    "reason": "负责人和主管领导审批的单行字段，无重复结构"
  },
  {
    "name": "需通知领导信息左重复表",
    "rows": [14, 15, 16],
    "type": "Left_RepeatTable",
    "split_after_column": 0,
    "reason": "第0列是固定标题'需要通知的领导'（跨3行），第1-5列是重复表结构（领导名称、职位、部门、工号表头+2行空白数据行）"
  }
]
    """
    core = Core(docx_path, demo_spit_result_str)
    table_xmls = core.get_xml_tables()
    results = core.start_all_by_tables(table_xmls)
    serializable_results = [
        [r.model_dump() for r in result] if result is not None else None
        for result in results
    ]
    pyperclip.copy(
        json.dumps(
            serializable_results,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
