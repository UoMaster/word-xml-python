"""快速示例 - 演示如何使用word_xml_python库"""

from word_xml_python import process_word_table, export_to_csv

# Word XML文档路径
FILE_PATH = "/Users/wuhongbin/qilin/project/word-learn/word/word/document.xml"


def main():
    """主函数"""
    
    try:
        # 处理表格
        print(f"\n正在处理文件: {FILE_PATH}")
        table_info, cell_meta_list = process_word_table(FILE_PATH)
        
        # 导出到CSV
        for i, cell_list in enumerate(cell_meta_list):
          output_file = f"cellInfo_{i}.csv"
          export_to_csv(cell_list, output_file)
          i += 1
    
        
    except FileNotFoundError:
        print(f"\n✗ 错误: 文件未找到 - {FILE_PATH}")
        print("  请确认文件路径是否正确")
    except ValueError as e:
        print(f"\n✗ 错误: {e}")
    except Exception as e:
        print(f"\n✗ 未知错误: {e}")


if __name__ == "__main__":
    main()
