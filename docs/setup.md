# 环境安装

本项目优先使用 Anaconda/Miniconda 管理独立环境，避免污染系统 Python。

## Mac

官方 Mac 安装指南要求 Python 3.10，并建议先安装 TA-Lib 系统库。

```bash
brew install ta-lib
conda env create -f environment.yml
conda activate trade-vnpy
python -m pytest
```

如果 `ta-lib` 的 Python 包安装失败，先确认 `brew --prefix ta-lib` 能正常输出路径，再重新执行：

```bash
python -m pip install numpy==1.26.4
python -m pip install ta-lib
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
