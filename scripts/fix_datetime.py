#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复 datetime.utcnow() 弃用问题的脚本

用途：
    Python 3.12+ 已弃用 datetime.utcnow()，推荐使用 datetime.now(timezone.utc)
    本脚本批量替换项目中的 datetime.utcnow() 调用

使用场景：
    - Python 版本升级到 3.12+ 时的兼容性修复
    - 代码审查发现弃用警告时的批量修复

使用方法：
    python fix_datetime.py

输入：
    预定义的需要修复的文件列表（files_to_fix）

输出：
    修复后的文件（直接覆盖原文件）

注意事项：
    - 运行前请备份重要文件
    - 修复后请运行测试确保功能正常
    - TODO: 集成到 CI/CD 流程中自动检测和修复

依赖：
    - Python 3.8+
    - 无外部依赖

作者：MetaAgent Team
日期：2024-03-16
"""

import re
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

# 需要修复的文件列表
# TODO: 定期扫描 src/ 目录，自动发现需要修复的文件
files_to_fix = [
    project_root / "src" / "meta_agent" / "hotload" / "dynamic_registry.py",
    project_root / "src" / "meta_agent" / "llm" / "batch_processor.py",
    project_root / "src" / "meta_agent" / "core" / "event_bus.py",
    project_root / "src" / "meta_agent" / "core" / "service_registry.py",
    project_root / "src" / "meta_agent" / "hotload" / "hot_loader.py",
    project_root / "src" / "meta_agent" / "llm" / "llm_cache.py",
]


def fix_file(file_path: Path) -> None:
    """
    修复单个文件中的 datetime.utcnow() 调用

    Args:
        file_path: 要修复的文件路径

    Returns:
        None

    Raises:
        FileNotFoundError: 文件不存在时
        PermissionError: 无写入权限时
    """
    if not file_path.exists():
        print(f"⚠️  文件不存在：{file_path}")
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # 检查是否已经导入 timezone
        if "from datetime import datetime" in content and "timezone" not in content:
            content = content.replace(
                "from datetime import datetime",
                "from datetime import datetime, timezone"
            )

        # 替换 datetime.utcnow() 为 datetime.now(timezone.utc)
        content = re.sub(
            r'datetime\.utcnow\(\)',
            'datetime.now(timezone.utc)',
            content
        )

        # 只有内容发生变化时才写入
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ 已修复：{file_path}")
        else:
            print(f"ℹ️  无需修复：{file_path}")

    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")


def main() -> None:
    """主函数"""
    print("=" * 60)
    print("批量修复 datetime.utcnow() 弃用问题")
    print("=" * 60)
    print()

    total_files = len(files_to_fix)
    fixed_count = 0

    for i, file_path in enumerate(files_to_fix, 1):
        print(f"[{i}/{total_files}] 处理：{file_path.name}")
        
        # 检查文件是否需要修复
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            if "datetime.utcnow()" in content:
                fix_file(file_path)
                fixed_count += 1
            else:
                print(f"ℹ️  无需修复：{file_path}")
        else:
            print(f"⚠️  文件不存在：{file_path}")

    print()
    print("=" * 60)
    print(f"修复完成！共修复 {fixed_count}/{total_files} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
