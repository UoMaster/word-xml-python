"""基础使用示例 - 展示完整API的使用方法"""

from word_xml_python import (
    WordXMLParser,
    TableExtractor,
    CellExtractor,
    CSVExporter,
    TableInfo,
    CellInfo
)


def example_full_api():
    """使用完整API进行处理"""
    
    file_path = "path/to/your/document.xml"
    
    # 1. 解析XML文档
    print("步骤1: 解析XML文档...")
    parser = WordXMLParser(file_path)
    parser.parse()
    
    # 2. 查找表格元素
    print("步骤2: 查找表格...")
    table_element = parser.find_table()
    if table_element is None:
        print("错误: 未找到表格元素")
        return
    
    # 3. 提取表格信息
    print("步骤3: 提取表格信息...")
    table_extractor = TableExtractor(parser.get_namespaces())
    table_info = table_extractor.extract(table_element)
    
    print(f"表格大小: {table_info.row} 行 x {table_info.col} 列")
    
    # 4. 提取单元格信息
    print("步骤4: 提取单元格信息...")
    cell_extractor = CellExtractor(parser.get_namespaces())
    cell_list = cell_extractor.extract_all(table_element)
    
    print(f"找到 {len(cell_list)} 个单元格")
    
    # 5. 查看单元格详情
    print("\n单元格详情（前10个）:")
    for i, cell in enumerate(cell_list[:10], 1):
        print(f"{i:2d}. {cell}")
    
    # 6. 导出到CSV
    print("\n步骤5: 导出到CSV...")
    output_path = "table_data.csv"
    CSVExporter.export(cell_list, output_path)
    print(f"已导出到: {output_path}")


def example_with_filtering():
    """带过滤的示例"""
    
    from word_xml_python import process_word_table
    
    file_path = "path/to/your/document.xml"
    
    # 处理表格
    table_info, cell_list = process_word_table(file_path)
    
    # 筛选有合并的单元格
    merged_cells = [
        cell for cell in cell_list 
        if cell.col_span > 1 or cell.row_span > 1
    ]
    
    print(f"总单元格数: {len(cell_list)}")
    print(f"合并单元格数: {len(merged_cells)}")
    
    # 显示合并单元格详情
    print("\n合并单元格:")
    for cell in merged_cells:
        print(f"  位置: {cell.key}")
        if cell.col_span > 1:
            print(f"    - 跨 {cell.col_span} 列")
        if cell.row_span > 1:
            print(f"    - 跨 {cell.row_span} 行")


def example_data_analysis():
    """数据分析示例"""
    
    from word_xml_python import process_word_table
    import pandas as pd
    
    file_path = "path/to/your/document.xml"
    
    # 处理表格
    table_info, cell_list = process_word_table(file_path)
    
    # 转换为DataFrame进行分析
    data = [cell.to_dict() for cell in cell_list]
    df = pd.DataFrame(data)
    
    # 统计信息
    print("数据统计:")
    print(f"  总单元格数: {len(df)}")
    print(f"  列合并最大值: {df['col_span'].max()}")
    print(f"  行合并最大值: {df['row_span'].max()}")
    print(f"  有列合并的单元格: {(df['col_span'] > 1).sum()}")
    print(f"  有行合并的单元格: {(df['row_span'] > 1).sum()}")
    
    # 按行分组统计
    print("\n按行统计:")
    df['row'] = df['key'].str.split('-').str[0].astype(int)
    row_stats = df.groupby('row').size()
    print(row_stats)


if __name__ == "__main__":
    print("Word XML Python - 使用示例\n")
    
    print("=" * 60)
    print("示例1: 使用完整API")
    print("=" * 60)
    # example_full_api()  # 取消注释以运行
    
    print("\n" + "=" * 60)
    print("示例2: 带过滤的处理")
    print("=" * 60)
    # example_with_filtering()  # 取消注释以运行
    
    print("\n" + "=" * 60)
    print("示例3: 数据分析")
    print("=" * 60)
    # example_data_analysis()  # 取消注释以运行
    
    print("\n提示: 取消注释相应函数以运行示例")

