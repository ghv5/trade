# 环境安装

本项目优先使用 Anaconda/Miniconda 管理独立环境，避免污染系统 Python。

## Mac

官方 Mac 安装指南要求 Python 3.10。当前仓库通过 `environment.yml` 从 `conda-forge` 安装 TA-Lib，避免依赖本机 Homebrew。

```bash
conda env create -f environment.yml
conda activate trade-vnpy
python -m pytest
```

如果需要手动排查依赖，可以先确认 Conda 环境中能导入 TA-Lib，再安装 vn.py：

```bash
python -m pip install "numpy>=2.2.3"
python -m pip install vnpy vnpy_ctastrategy vnpy_ctabacktester vnpy_datamanager vnpy_sqlite vnpy_rqdata
```

## 验证

```bash
python - <<'PY'
import vnpy
print(vnpy.__version__)
PY
```

能输出版本号即说明核心包可导入。
