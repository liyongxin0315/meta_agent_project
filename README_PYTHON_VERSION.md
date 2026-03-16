# Python 版本管理指南

本项目使用 Python 3.11，以下是版本管理的说明。

## 当前 Python 版本

- **推荐版本**: Python 3.11
- **项目配置**: `.python-version` 文件指定使用 3.11

## 可用的 Python 版本

使用 `py --list` 查看已安装的版本：
```bash
py --list
```

输出示例：
```
 -V:3.14 *        Python 3.14 (64-bit)
 -V:3.11          Python 3.11 (64-bit)
```

## 如何使用指定版本运行 Python

### 方式 1：使用 py 命令（推荐）
```bash
# 使用 Python 3.11 运行
py -3.11 script.py

# 使用 Python 3.11 安装包
py -3.11 -m pip install package_name

# 使用 Python 3.11 运行 pyright
py -3.11 -m pip install pyright
npx pyright
```

### 方式 2：激活虚拟环境
如果项目使用虚拟环境，确保在虚拟环境中使用正确的 Python 版本。

## 项目依赖安装

使用 Python 3.11 安装项目依赖：
```bash
cd meta_agent_project
py -3.11 -m pip install -e .[dev]
```

或者使用 pip 直接安装：
```bash
py -3.11 -m pip install openai tenacity prometheus-client opentelemetry-api opentelemetry-sdk redis watchdog pydantic pydantic-settings python-json-logger pyyaml pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist pytest-timeout pytest-rerunfailures faker hypothesis bandit black isort flake8 mypy junitparser coverage autoflake
```

## 为什么选择 Python 3.11？

1. **稳定性**: Python 3.11 是稳定版本，有广泛的库支持
2. **性能**: 比 Python 3.10 快约 10-60%
3. **兼容性**: 大多数第三方库都支持 3.11
4. **项目要求**: pyproject.toml 中指定 `python = "^3.10"`，3.11 完全兼容

## 安装其他 Python 版本

如果需要安装其他 Python 版本，可以从 [python.org](https://www.python.org/downloads/) 下载安装。

## 切换默认 Python 版本

修改 `.python-version` 文件内容即可切换项目使用的 Python 版本。
