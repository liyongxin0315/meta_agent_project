"""对话蒸馏进化模块 - 核心实现

基于蒸馏原理优化，让API大模型帮助Agent总结优化规则，沉淀元知识
"""

import json
import time
import threading
from pathlib import Path
from typing import List
from dataclasses import dataclass, asdict

from meta_agent.core.logging import get_logger
from meta_agent.llm.dialog_memory import dialog_memory

logger = get_logger(__name__)


@dataclass
class EvolutionResult:
    """进化结果"""
    timestamp: float
    dialog_count: int
    good_points: List[str]
    bad_points: List[str]
    optimize_rules: List[str]
    meta_knowledge: str


class DistillEvolver:
    """蒸馏进化器"""

    DEFAULT_EVOLVE_PROMPT = """
你是元Agent进化器，对以下对话做蒸馏学习，输出JSON：

对话数据：{dialogs}

请输出JSON，包含以下字段：
1. good_points: 回答优点（数组）
2. bad_points: 回答不足（数组）
3. optimize_rules: 3-5条Agent优化规则
4. meta_knowledge: 沉淀的元知识（一句话）

严格输出JSON，无多余内容。
"""

    def __init__(
        self,
        evolve_path="./data/evolution_knowledge.jsonl",
        evolve_prompt=None,
        enable_auto_evolve=True
    ):
        self.evolve_path = Path(evolve_path)
        self.evolve_path.parent.mkdir(parents=True, exist_ok=True)
        self.evolve_prompt = evolve_prompt or self.DEFAULT_EVOLVE_PROMPT
        self.enable_auto_evolve = enable_auto_evolve
        self._evolution_cache = []
        self._load_evolution()
        self._evolve_lock = threading.Lock()

    def _load_evolution(self):
        """加载进化知识"""
        if not self.evolve_path.exists():
            return

        try:
            with open(self.evolve_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        result = EvolutionResult(**data)
                        self._evolution_cache.append(result)
                    except Exception as e:
                        logger.warning(f"解析进化记录失败: {e}")

            logger.info(f"加载了 {len(self._evolution_cache)} 条进化记录")
        except Exception as e:
            logger.error(f"加载进化文件失败: {e}")

    def _save_evolution(self, result):
        """保存进化结果"""
        try:
            with open(self.evolve_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(result), ensure_ascii=False))
                f.write("\n")
            self._evolution_cache.append(result)
        except Exception as e:
            logger.error(f"保存进化文件失败: {e}")

    def build_evolve_prompt(self, dialogs):
        """构建蒸馏进化提示词"""
        dialog_data = []
        for dialog in dialogs:
            dialog_data.append({
                "dialog": dialog.dialog,
                "answer": dialog.answer,
                "quality_score": dialog.quality_score
            })

        return self.evolve_prompt.format(
            dialogs=json.dumps(dialog_data, ensure_ascii=False)
        )

    def parse_evolve_result(self, response, dialog_count):
        """解析进化结果"""
        try:
            result = json.loads(response)
            return EvolutionResult(
                timestamp=time.time(),
                dialog_count=dialog_count,
                good_points=result.get("good_points", []),
                bad_points=result.get("bad_points", []),
                optimize_rules=result.get("optimize_rules", []),
                meta_knowledge=result.get("meta_knowledge", "")
            )
        except Exception as e:
            logger.warning(f"解析进化结果失败: {e}，使用默认值")
            return EvolutionResult(
                timestamp=time.time(),
                dialog_count=dialog_count,
                good_points=[],
                bad_points=[],
                optimize_rules=[],
                meta_knowledge=""
            )

    def evolve(
        self,
        llm_chat_func,
        memory_store=None,
        limit=50,
        model="gpt-4o-mini"
    ):
        """执行蒸馏进化"""
        if not self.enable_auto_evolve:
            logger.debug("自动进化已禁用")
            return None

        with self._evolve_lock:
            memory = memory_store or dialog_memory
            dialogs = memory.get_uncurated_dialogs(limit=limit)

            if not dialogs:
                logger.debug("没有待蒸馏的对话")
                return None

            logger.info(f"开始蒸馏进化，处理 {len(dialogs)} 条对话")

            try:
                prompt = self.build_evolve_prompt(dialogs)
                messages = [{"role": "user", "content": prompt}]

                response = llm_chat_func(
                    messages=messages,
                    model=model,
                    temperature=0.3
                )

                evolve_result = self.parse_evolve_result(response, len(dialogs))
                self._save_evolution(evolve_result)

                memory.mark_evolved(dialogs)

                logger.info(f"蒸馏进化完成，生成了 {len(evolve_result.optimize_rules)} 条优化规则")
                return evolve_result

            except Exception as e:
                logger.error(f"蒸馏进化失败: {e}")
                return None

    def evolve_async(
        self,
        llm_chat_func,
        memory_store=None,
        limit=50,
        model="gpt-4o-mini"
    ):
        """异步执行蒸馏进化（不阻塞业务）"""
        thread = threading.Thread(
            target=self.evolve,
            args=(llm_chat_func, memory_store, limit, model),
            daemon=True
        )
        thread.start()

    def get_latest_evolution(self):
        """获取最新的进化结果"""
        if not self._evolution_cache:
            return None
        return self._evolution_cache[-1]

    def get_evolution_system_prompt(self):
        """获取进化知识的系统提示词"""
        latest = self.get_latest_evolution()
        if not latest:
            return ""

        parts = []

        if latest.optimize_rules:
            parts.append("【优化规则】\n" + "\n".join(f"- {rule}" for rule in latest.optimize_rules))

        if latest.meta_knowledge:
            parts.append(f"【元知识】\n{latest.meta_knowledge}")

        return "\n\n".join(parts) if parts else ""


distill_evolver = DistillEvolver()
