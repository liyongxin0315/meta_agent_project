"""
批量修复 datetime.utcnow() 弃用问题的脚本
"""

import re
from pathlib import Path

project_root = Path(__file__).parent

files_to_fix = [
    project_root / "src" / "meta_agent" / "hotload" / "dynamic_registry.py",
    project_root / "src" / "meta_agent" / "llm" / "batch_processor.py",
    project_root / "src" / "meta_agent" / "core" / "event_bus.py",
    project_root / "src" / "meta_agent" / "core" / "service_registry.py",
    project_root / "src" / "meta_agent" / "hotload" / "hot_loader.py",
    project_root / "src" / "meta_agent" / "llm" / "llm_cache.py",
]


def fix_file(file_path: Path):
    """修复单个文件"""
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    content = file_path.read_text(encoding="utf-8")
    
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
    
    file_path.write_text(content, encoding="utf-8")
    print(f"已修复: {file_path}")


for file_path in files_to_fix:
    fix_file(file_path)

print("\n所有文件修复完成！")
