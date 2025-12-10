"""快速示例 - 演示如何使用word_xml_python库"""

from word_xml_python import process_word_table, export_to_csv

# Word XML文档路径
FILE_PATH = "/Users/wuhongbin/qilin/project/word-learn/word/word/document.xml"


def main():
    """主函数"""

    try:
        # 处理表格
        print(f"\n正在处理文件: {FILE_PATH}")
        tables = process_word_table(FILE_PATH)

        print(tables[0].table_cell_csv_str)
        # 导出到CSV
        for idx, table_meta in enumerate(tables):
            output_file = f"cellInfo_{idx}.csv"
            if table_meta.table_cell_list:
                export_to_csv(table_meta.table_cell_list, output_file)
                print(f"✓ 已导出表格 {idx} ({table_meta.table_type}) 到: {output_file}")
            else:
                print(f"✗ 表格 {idx} 没有单元格数据")

    except FileNotFoundError:
        print(f"\n✗ 错误: 文件未找到 - {FILE_PATH}")
        print("  请确认文件路径是否正确")
    except ValueError as e:
        print(f"\n✗ 错误: {e}")
    except Exception as e:
        print(f"\n✗ 未知错误: {e}")


if __name__ == "__main__":
    main()
