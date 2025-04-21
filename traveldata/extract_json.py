import sys
import json
import argparse
import os # 添加 os 模块导入
from typing import Any, List, Dict, Union, Optional

try:
    from jsonpath import jsonpath
except ImportError:
    print("请先安装jsonpath包：pip install jsonpath")
    sys.exit(1)

import csv

def extract_json_fields(data: Any, paths: List[str], default=None, warn_missing=True) -> Dict[str, Any]:
    if isinstance(data, list):
        results = []
        for idx, item in enumerate(data):
            row = {}
            for path in paths:
                try:
                    value = jsonpath(item, path)
                    if value is False or value is None:
                        if warn_missing:
                            # 更具体的警告信息
                            print(f"警告：第{idx}项 路径 '{path}' 未找到或返回空值。请检查路径语法（例如，数组是否应使用 '[*]' 而非 '[ ]'？）或确认该项确实包含此路径。将使用默认值 {default}")
                        row[path] = default
                    else:
                        # 如果jsonpath返回列表，通常我们期望的是单个值或第一个值
                        # 这里可以根据实际需要调整，例如取第一个元素 value[0]
                        # 但为了保持通用性，暂时保留原样或根据需求明确处理方式
                        row[path] = value
                except Exception as e:
                    # 捕获可能的jsonpath解析错误
                    if warn_missing:
                        print(f"警告：第{idx}项 处理路径 '{path}' 时出错：{e}。请检查路径语法。将使用默认值 {default}")
                    row[path] = default
            results.append(row)
        return results
    else:
        results = {}
        for path in paths:
            try:
                value = jsonpath(data, path)
                if value is False or value is None:
                    if warn_missing:
                         # 更具体的警告信息
                        print(f"警告：路径 '{path}' 未找到或返回空值。请检查路径语法或确认JSON数据包含此路径。将使用默认值 {default}")
                    results[path] = default
                else:
                    # 同上，处理可能的列表返回
                    results[path] = value
            except Exception as e:
                 # 捕获可能的jsonpath解析错误
                if warn_missing:
                    print(f"警告：处理路径 '{path}' 时出错：{e}。请检查路径语法。将使用默认值 {default}")
                results[path] = default
        return results

def output_result(result: Dict[str, Any], fmt: str = 'dict', csv_file: Optional[str] = None):
    if fmt == 'dict':
        print("\n【提取结果】:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif fmt == 'list':
        print("\n【提取结果】:")
        print(json.dumps(result if isinstance(result, list) else list(result.values()), ensure_ascii=False, indent=2))
    elif fmt == 'csv':
        if isinstance(result, list):
            if not result:
                print("无数据")
                return
            keys = result[0].keys()
            rows = [[row.get(k, '') for k in keys] for row in result]
        else:
            keys = result.keys()
            rows = [[v if v is not None else '' for v in result.values()]]
        if not csv_file:
            print("未指定CSV文件名，输出到标准输出：")
            writer = csv.writer(sys.stdout)
            writer.writerow(keys)
            writer.writerows(rows)
        else:
            # 确保输出目录存在
            output_dir = os.path.dirname(csv_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"已创建目录：{output_dir}")
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(keys)
                writer.writerows(rows)
            print(f"已写入CSV文件：{csv_file}")
    else:
        print("不支持的输出格式：", fmt)

def print_help():
    print("""
JSONPath数据提取工具

用法示例：
  1. 从文件提取：
     python extract_json.py -i data.json -p '$.name,$.age'
  2. 从字符串提取：
     python extract_json.py -i '{"name":"张三","age":18}' -p '$.name,$.age'
  3. 输出为CSV：
     python extract_json.py -i data.json -p '$.name,$.age' -f csv --csv-file result.csv

参数说明：
  -i, --input      JSON文件路径或JSON字符串
  -p, --paths      JSONPath路径，多个路径用逗号分隔
  -f, --format     输出格式(dict/list/csv)，默认dict
  --default        字段缺失时的默认值
  --no-warn        字段缺失时不警告
  --csv-file       输出CSV文件名（仅csv格式时有效）
  --quick          常用字段快捷选项（如name,age等，自动转为JSONPath）
  -h, --help       显示帮助信息

更多示例请参考README或使用-h参数。
""")

def extract_json_fields(data: Any, fields: List[str], default=None, warn_missing=True) -> List[Dict[str, Any]]:
    # 针对列表型数据，提取每条记录的指定字段
    results = []
    if isinstance(data, list):
        for idx, item in enumerate(data):
            row = {}
            for field in fields:
                # 深度查找字段，支持嵌套结构
                keys = field.split('.')
                value = item
                try:
                    for key in keys:
                        if isinstance(value, list) and key.isdigit():
                            value = value[int(key)]
                        else:
                            value = value.get(key, default)
                            if value is None:
                                break
                except (KeyError, IndexError, AttributeError):
                    value = default
                
                if value is None and warn_missing:
                    print(f"警告：第{idx}项 字段 '{field}' 未找到。将使用默认值 {default}")
                row[field] = value
            results.append(row)
    elif isinstance(data, dict):
        row = {}
        for field in fields:
            # 深度查找字段，支持嵌套结构
            keys = field.split('.')
            value = data
            try:
                for key in keys:
                    if isinstance(value, list) and key.isdigit():
                        value = value[int(key)]
                    else:
                        value = value.get(key, default)
                        if value is None:
                            break
            except (KeyError, IndexError, AttributeError):
                value = default
                
            if value is None and warn_missing:
                print(f"警告：字段 '{field}' 未找到。将使用默认值 {default}")
            row[field] = value
        results.append(row)
    else:
        print("输入数据格式不正确，必须为列表或字典。")
    return results


def main():
    parser = argparse.ArgumentParser(description='JSON结构化字段提取工具', add_help=False)
    parser.add_argument('-i', '--input', required=True, help='JSON文件路径或JSON字符串')
    parser.add_argument('-f', '--format', default='csv', choices=['csv', 'dict', 'list'], help='输出格式')
    parser.add_argument('--default', default=None, help='字段缺失时的默认值')
    parser.add_argument('--no-warn', action='store_true', help='字段缺失时不警告')
    parser.add_argument('--csv-file', default='result.csv', help='输出CSV文件名')
    parser.add_argument('--fields', default=None, help='要提取的字段名，逗号分隔（如title,desc,nickname,aweme_url）')
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    args = parser.parse_args()

    if args.help:
        print("""
用法示例：
  python extract_json.py -i search_contents_2025-03-28.json --fields title,desc,nickname,aweme_url --csv-file result.csv
参数说明：
  -i, --input      JSON文件路径或JSON字符串
  --fields         要提取的字段名，逗号分隔
  --csv-file       输出CSV文件名
  --default        字段缺失时的默认值
  --no-warn        字段缺失时不警告
  -h, --help       显示帮助信息
""")
        sys.exit(0)

    # 读取JSON数据
    try:
        if args.input.endswith('.json') or args.input.endswith('.txt'):
            with open(args.input, encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.loads(args.input)
    except Exception as e:
        print(f"读取或解析JSON失败：{e}")
        sys.exit(1)

    # 自动推断字段
    if args.fields:
        fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    else:
        # 自动从第一条记录推断所有主字段
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            fields = list(data[0].keys())
        elif isinstance(data, dict):
            fields = list(data.keys())
        else:
            print("无法自动推断字段，请通过--fields指定。")
            sys.exit(1)

    result = extract_json_fields(data, fields, default=args.default, warn_missing=not args.no_warn)

    # 输出为CSV
    if args.format == 'csv':
        if not result:
            print("无数据")
            return
        keys = fields
        rows = [[str(row.get(k, '')) for k in keys] for row in result]
        output_dir = os.path.dirname(args.csv_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(args.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(keys)
            writer.writerows(rows)
        print(f"已写入CSV文件：{args.csv_file}")
    elif args.format == 'dict':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == 'list':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("不支持的输出格式：", args.format)

if __name__ == '__main__':
    main()