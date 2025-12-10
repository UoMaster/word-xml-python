import os
import sys
import zipfile
import shutil
from pathlib import Path


def extract_docx_to_meta(docx_path: str, output_dir: str = "word_meta") -> str:
    project_root = Path(__file__).parent
    meta_dir = project_root / output_dir

    if meta_dir.exists():
        shutil.rmtree(meta_dir)
    meta_dir.mkdir(parents=True)

    with zipfile.ZipFile(docx_path, "r") as zip_ref:
        zip_ref.extractall(meta_dir)

    return str(meta_dir)


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

    if not docx_path.lower().endswith(".docx"):
        print("✗ 请选择.docx文件")
        return

    print(f"处理文件: {docx_path}")

    try:
        output_path = extract_docx_to_meta(docx_path)
        print(f"✓ 已将元文件解压到: {output_path}")

        for root, dirs, files in os.walk(output_path):
            level = root.replace(output_path, "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = "  " * (level + 1)
            for file in files:
                print(f"{sub_indent}{file}")

    except zipfile.BadZipFile:
        print("✗ 错误: 所选文件不是有效的docx文件")
    except Exception as e:
        print(f"✗ 错误: {e}")


if __name__ == "__main__":
    main()
