"""元思考模块 - 核心实现

基于蒸馏原理优化，前置元思考：意图分析、上下文规划、蒸馏决策
"""

import json
from typing import List
from dataclasses import dataclass

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MetaThinkResult:
    """元思考结果"""
    intent: str
    need_context: bool
    key_points: List[str]
    need_evolve: bool
    confidence: float = 0.8


class MetaThinker:
    """元思考器"""

    DEFAULT_THINK_PROMPT = """
【元思考任务】
用户输入：{user_input}
历史对话：{history}

请输出JSON，包含以下字段：
1. intent: 用户意图（一句话概括）
2. need_context: 是否需要历史上下文（true/false）
3. key_points: 回答关键要点（数组，3-5条）
4. need_evolve: 本次对话是否值得蒸馏学习（true/false）
5. confidence: 思考置信度（0-1之间的数字）

严格输出JSON，无多余内容。
"""

    def __init__(self, think_prompt=None):
        self.think_prompt = think_prompt or self.DEFAULT_THINK_PROMPT

    def build_think_prompt(self, user_input, history=None):
        """构建元思考提示词"""
        history_str = json.dumps(history or [], ensure_ascii=False)
        return self.think_prompt.format(
            user_input=user_input,
            history=history_str
        )

    def parse_think_result(self, response):
        """解析元思考结果"""
        try:
            result = json.loads(response)
            return MetaThinkResult(
                intent=result.get("intent", "unknown"),
                need_context=bool(result.get("need_context", True)),
                key_points=result.get("key_points", []),
                need_evolve=bool(result.get("need_evolve", True)),
                confidence=float(result.get("confidence", 0.8))
            )
        except Exception as e:
            logger.warning(f"解析元思考结果失败: {e}，使用默认值")
            return MetaThinkResult(
                intent="unknown",
                need_context=True,
                key_points=[],
                need_evolve=True,
                confidence=0.5
            )


meta_thinker = MetaThinker()
