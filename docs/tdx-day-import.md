# 通达信日线导入

通达信日线 `.day` 文件通常位于：

- 上海：`vipdoc/sh/lday/sh600000.day`
- 深圳：`vipdoc/sz/lday/sz000001.day`
- 北交所：`vipdoc/bj/lday/bj920578.day`

当前本地目录也兼容 `vipdoc/hsjday/{sh,sz,bj}/lday/*.day` 这种层级。

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
- `bj` -> `BSE`

如果文件名不是通达信标准格式，可以显式指定：

```bash
python scripts/import_tdx_day.py ./some.day --symbol 600000 --exchange SSE --save-vnpy
```

## 批量扫描

先扫描整个目录，确认数据能解析：

```bash
python scripts/import_tdx_directory.py data/tdx/vipdoc --dry-run
```

如果只想抽样：

```bash
python scripts/import_tdx_directory.py data/tdx/vipdoc --dry-run --limit 20
```

脚本会输出总文件数、总 K 线数、起止日期、解析失败数、价格异常文件数和零成交记录数。质量报告可以写到本地 `reports/`，该目录默认不提交：

```bash
python scripts/import_tdx_directory.py data/tdx/vipdoc --dry-run --report reports/tdx_day_quality.json
```

默认只处理 A 股股票代码：

- 上海：`600`、`601`、`603`、`605`、`688`、`689`
- 深圳：`000`、`001`、`002`、`003`、`300`、`301`、`302`
- 北交所：`43`、`83`、`87`、`88`、`92`

指数、基金、债券、B 股等文件会被跳过。如果确实要扫描全部 `.day` 文件，使用：

```bash
python scripts/import_tdx_directory.py data/tdx/vipdoc --dry-run --market all
```
