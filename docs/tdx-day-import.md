# 通达信日线导入

通达信日线 `.day` 文件通常位于：

- 上海：`vipdoc/sh/lday/sh600000.day`
- 深圳：`vipdoc/sz/lday/sz000001.day`

本仓库默认忽略 `data/` 和 `tdx/`，请把本地行情文件放在这些目录下，避免误提交。

## 检查文件

```bash
python scripts/import_tdx_day.py data/tdx/vipdoc/sh/lday/sh600000.day --dry-run
```

输出会显示识别出的代码、交易所、记录数、起止日期和最后一根 K 线。

## 写入 vn.py 数据库

```bash
python scripts/import_tdx_day.py data/tdx/vipdoc/sh/lday/sh600000.day --save-vnpy
```

脚本会将通达信日线转换为 vn.py `BarData`，再调用 `get_database().save_bar_data(bars)` 写入当前 vn.py 数据库。默认交易所映射：

- `sh` -> `SSE`
- `sz` -> `SZSE`

如果文件名不是通达信标准格式，可以显式指定：

```bash
python scripts/import_tdx_day.py ./some.day --symbol 600000 --exchange SSE --save-vnpy
```
