# 贡献指南

感谢你为 MetaAgent 项目做出贡献！

## 📋 目录

- [行为准则](#-行为准则)
- [贡献方式](#-贡献方式)
- [开发环境设置](#-开发环境设置)
- [提交规范](#-提交规范)
- [Pull Request 流程](#-pull-request-流程)
- [代码规范](#-代码规范)

---

## 🤝 行为准则

本项目采用 [贡献者公约](https://www.contributor-covenant.org/) 作为行为准则。请尊重所有贡献者和用户。

---

## 🎯 贡献方式

### 1. 报告问题

发现 Bug？请创建 [Issue](https://github.com/liyongxin0315/meta_agent_project/issues)：

- 使用清晰的标题
- 描述复现步骤
- 提供预期行为和实际行为
- 附上相关日志或截图

### 2. 功能建议

有新功能想法？请创建 Issue：

- 描述功能用途
- 说明使用场景
- 提供实现思路（可选）

### 3. 提交代码

- Fork 仓库
- 创建特性分支
- 编写代码和测试
- 提交 Pull Request

### 4. 改进文档

- 修正拼写错误
- 补充使用说明
- 添加示例代码

---

## 🛠️ 开发环境设置

### 1. Fork 并克隆仓库

```bash
# Fork 仓库到个人账户
# 访问 https://github.com/liyongxin0315/meta_agent_project 点击 Fork

# 克隆到本地
git clone https://github.com/YOUR_USERNAME/meta_agent_project.git
cd meta_agent_project

# 添加上游仓库
git remote add upstream https://github.com/liyongxin0315/meta_agent_project.git
```

### 2. 安装依赖

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 创建虚拟环境并安装依赖
poetry install --with dev
```

### 3. 配置预提交钩子

```bash
# 安装预提交钩子（可选）
poetry run pre-commit install
```

---

## 📝 提交规范

### Commit Message 格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

### 示例

```bash
# 新功能
git commit -m "feat(llm): 添加 LLM 缓存功能"

# Bug 修复
git commit -m "fix(core): 修复依赖注入容器初始化问题"

# 文档更新
git commit -m "docs(readme): 补充安装说明"

# 重构
git commit -m "refactor(hotload): 优化热加载器性能"
```

---

## 🔄 Pull Request 流程

### 1. 创建分支

```bash
# 同步上游仓库
git fetch upstream
git checkout main
git merge upstream/main

# 创建特性分支
git checkout -b feature/your-feature-name
```

### 2. 开发和测试

```bash
# 编写代码
# ...

# 运行测试
poetry run pytest

# 代码格式化
poetry run black src/ tests/
poetry run isort src/ tests/

# 代码检查
poetry run flake8 src/ tests/
poetry run mypy src/
```

### 3. 提交更改

```bash
git add .
git commit -m "feat: 实现你的功能"
```

### 4. 推送并创建 PR

```bash
# 推送到远程
git push origin feature/your-feature-name

# 访问 GitHub 创建 Pull Request
# https://github.com/liyongxin0315/meta_agent_project/pulls
```

### 5. PR 要求

- ✅ 标题清晰描述更改
- ✅ 关联相关 Issue
- ✅ 通过所有 CI 检查
- ✅ 测试覆盖率 ≥ 80%
- ✅ 代码符合规范

---

## 📏 代码规范

### Python 代码

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# ✅ 好的代码
def calculate_total(items: list[float]) -> float:
    """计算总金额。
    
    Args:
        items: 项目列表
        
    Returns:
        总金额
    """
    return sum(items)

# ❌ 避免
def calc(l):  # 命名不清晰
    return sum(l)  # 缺少文档
```

### 类型注解

使用类型注解：

```python
from typing import Optional, List, Dict

def process_data(
    data: Dict[str, any],
    options: Optional[List[str]] = None
) -> Dict[str, any]:
    ...
```

### 文档字符串

遵循 [PEP 257](https://pep257.org/) 规范：

```python
class DataProcessor:
    """数据处理器。
    
    提供数据清洗、转换和验证功能。
    
    Attributes:
        config: 处理器配置
        cache: 缓存实例
    """
    
    def process(self, data: dict) -> dict:
        """处理数据。
        
        Args:
            data: 原始数据
            
        Returns:
            处理后的数据
            
        Raises:
            ValueError: 数据格式错误时
        """
        ...
```

---

## 🧪 测试要求

### 单元测试

```python
# tests/unit/test_example.py
def test_calculate_total():
    """测试总金额计算。"""
    items = [1.0, 2.0, 3.0]
    assert calculate_total(items) == 6.0
```

### 集成测试

```python
# tests/integration/test_api.py
def test_api_endpoint(client):
    """测试 API 端点。"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
```

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试
poetry run pytest tests/unit/test_example.py -v

# 生成覆盖率报告
poetry run pytest --cov=src/meta_agent --cov-report=html
```

---

## 📚 文档更新

### README.md

- 更新功能说明
- 补充使用示例
- 修正错误信息

### API 文档

- 更新接口说明
- 补充参数描述
- 添加示例代码

---

## ❓ 常见问题

### Q: 如何获取帮助？

A: 创建 [Issue](https://github.com/liyongxin0315/meta_agent_project/issues) 或参与讨论。

### Q: 多久能收到回复？

A: 通常在 1-3 个工作日内回复。

### Q: 可以提交部分完成的功能吗？

A: 可以，请标记为 `[WIP]` (Work In Progress)。

---

## 🙏 致谢

感谢所有贡献者！你们的付出让这个项目变得更好。

---

<div align="center">

**开始贡献吧！** 🚀

[⬆ 返回顶部](#-贡献指南)

</div>
