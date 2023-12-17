# PRTS - Analyzer

用于游戏[明日方舟](https://ak.hypergryph.com/)的，数据提取及分析的相关脚本

目前实现的脚本文件及对应功能包括但不限于：

- `adb.py`: 基于ADB的触屏、截图等常用操作
- `operator_data.py`: 从PRTS.Wiki获取全干员图鉴
- `operators/detect.py`: 从详情页的截图提取单个干员相关信息
- `dump_operators.py`: 在干员详情页按次序扫描所有干员，提取信息并汇总输出至json文件
- `extract_trust.py`: 根据operators.json文件统计干员信赖值信息，输出至trust.csv
