# JSON结构化字段批量提取工具

## 项目简介

本工具用于从JSON文件或JSON字符串中批量提取指定字段，并支持导出为CSV、字典或列表格式，适用于数据清洗、批量信息提取等场景。

## 主要功能
- 支持输入JSON文件或直接输入JSON字符串
- 支持批量提取多个字段，支持嵌套字段（如user.name）
- 支持输出为CSV、dict、list三种格式
- 字段缺失可自定义默认值，支持警告提示
- 自动推断字段名，简化操作
- 支持命令行参数，易于集成自动化脚本

## 使用方法

### 1. 从文件提取字段并导出为CSV
```bash
python extract_json.py -i data.json --fields title,desc,nickname,aweme_url --csv-file result.csv
```

### 2. 从JSON字符串提取字段
```bash
python extract_json.py -i '{"name":"张三","age":18}' --fields name,age --format dict
```

### 3. 自动推断字段并导出为CSV
```bash
python extract_json.py -i data.json --csv-file result.csv
```

### 4. 更多参数说明
```bash
python extract_json.py -h
```

## 参数说明
| 参数 | 说明 |
| ---- | ---- |
| -i, --input | JSON文件路径或JSON字符串（必填） |
| --fields | 要提取的字段名，逗号分隔（如title,desc,nickname,aweme_url），可省略自动推断 |
| --csv-file | 输出CSV文件名（仅csv格式时有效，默认result.csv） |
| -f, --format | 输出格式，支持csv、dict、list，默认csv |
| --default | 字段缺失时的默认值 |
| --no-warn | 字段缺失时不警告 |
| -h, --help | 显示帮助信息 |

## 依赖环境
- Python 3.6 及以上
- 依赖库：
  - jsonpath（如需使用JSONPath提取功能）
  - argparse（标准库）
  - csv（标准库）

安装依赖：
```bash
pip install jsonpath
```

## 常见问题
1. **报错“请先安装jsonpath包”**
   - 解决：运行 `pip install jsonpath`
2. **字段缺失时如何处理？**
   - 可通过 `--default` 指定默认值，或加 `--no-warn` 关闭警告。
3. **如何提取嵌套字段？**
   - 使用点号分隔，如 `user.name`。
4. **支持哪些输入格式？**
   - 支持标准JSON文件和JSON字符串。

## 联系与反馈
如有问题或建议，欢迎提交Issue或PR。