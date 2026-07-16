# vn.py A股量化交易工作区

本仓库用于基于 vn.py 搭建 A 股量化交易工作流。

## 目标

- 使用 Anaconda 管理独立 Python 环境
- 安装和运行 vn.py
- 从通达信导入 A 股日线数据
- 使用 vn.py 进行回测和模拟交易
- 后续持续打磨策略、数据管理和交易流程

## 目录

- `docs/`：环境、数据、交易流程文档
- `scripts/`：数据导入和辅助脚本
- `data/`：本地行情数据目录，默认不提交 Git

## 快速开始

```bash
conda env create -f environment.yml
conda activate trade-vnpy
python -m pytest
```

Mac 上安装 vn.py 前需要先安装 TA-Lib 系统库：

```bash
brew install ta-lib
```

通达信 `.day` 文件可先 dry-run 检查：

```bash
python scripts/import_tdx_day.py data/tdx/vipdoc/sh/lday/sh600000.day --dry-run
```

也可以扫描整个通达信日线目录：

```bash
python scripts/import_tdx_directory.py data/tdx/vipdoc --dry-run
```

目录导入默认只处理 A 股股票代码；如需扫描全部 `.day` 文件，可加 `--market all`。

确认无误后再写入 vn.py 数据库：

```bash
python scripts/import_tdx_day.py data/tdx/vipdoc/sh/lday/sh600000.day --save-vnpy
```
