"""对话记忆存储模块 - 核心实现

基于蒸馏原理优化，持久化多轮对话作为蒸馏学习数据源
"""

import json
import time
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DialogRecord:
    """对话记录"""
    timestamp: float
    dialog: List[Dict[str, str]]
    answer: str
    is_evolved: bool = False
    quality_score: float = 0.0


class DialogMemoryStore:
    """对话记忆存储器"""

    def __init__(
        self,
        memory_path="./data/dialog_memory.jsonl",
        min_answer_len=5,
        max_memory_size=10000
    ):
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.min_answer_len = min_answer_len
        self.max_memory_size = max_memory_size
        self._memory_cache = []
        self._load_memory()

    def _load_memory(self):
        """从文件加载记忆"""
        if not self.memory_path.exists():
            return

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        record = DialogRecord(**data)
                        self._memory_cache.append(record)
                    except Exception as e:
                        logger.warning(f"解析记忆记录失败: {e}")

            logger.info(f"加载了 {len(self._memory_cache)} 条对话记忆")
        except Exception as e:
            logger.error(f"加载记忆文件失败: {e}")

    def _save_memory(self):
        """保存记忆到文件"""
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                for record in self._memory_cache[-self.max_memory_size:]:
                    f.write(json.dumps(asdict(record), ensure_ascii=False))
                    f.write("\n")
        except Exception as e:
            logger.error(f"保存记忆文件失败: {e}")

    def save_dialog(self, dialog, answer, quality_score=0.0):
        """保存对话记录"""
        if not answer or len(answer) < self.min_answer_len:
            logger.debug("回答过短，跳过保存")
            return None

        record = DialogRecord(
            timestamp=time.time(),
            dialog=dialog,
            answer=answer,
            is_evolved=False,
            quality_score=quality_score
        )

        self._memory_cache.append(record)

        if len(self._memory_cache) > self.max_memory_size * 2:
            self._memory_cache = self._memory_cache[-self.max_memory_size:]

        self._save_memory()
        logger.debug(f"保存对话记录，当前记忆数: {len(self._memory_cache)}")

        return record

    def get_uncurated_dialogs(self, limit=50, min_quality=0.0):
        """获取未蒸馏的对话记录"""
        records = [
            r for r in self._memory_cache
            if not r.is_evolved and r.quality_score >= min_quality
        ]
        return records[-limit:]

    def mark_evolved(self, records):
        """标记对话记录为已蒸馏"""
        timestamps = {r.timestamp for r in records}

        for record in self._memory_cache:
            if record.timestamp in timestamps:
                record.is_evolved = True

        self._save_memory()
        logger.info(f"标记了 {len(records)} 条对话为已蒸馏")

    def get_stats(self):
        """获取记忆统计信息"""
        total = len(self._memory_cache)
        evolved = sum(1 for r in self._memory_cache if r.is_evolved)
        unevolved = total - evolved

        return {
            "total": total,
            "evolved": evolved,
            "unevolved": unevolved
        }


dialog_memory = DialogMemoryStore()
