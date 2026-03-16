# -*- coding: utf-8 -*-
"""
集成测试 - 跨模块交互
"""

import pytest
from meta_agent.models.task import Task, TaskStatus
from meta_agent.utils.helpers import generate_id


class TestTaskFlow:
    """任务流程集成测试"""

    def test_task_full_lifecycle(self):
        """测试任务完整生命周期"""
        task = Task(
            task_id=generate_id("test_task"),
            content="Integration test task",
            priority=5,
        )
        
        # 初始状态
        assert task.status == TaskStatus.PENDING
        
        # 开始执行
        task.start()
        assert task.status == TaskStatus.RUNNING
        
        # 执行完成
        task.complete()
        assert task.status == TaskStatus.COMPLETED


class TestHelpersIntegration:
    """工具函数集成测试"""

    def test_id_generation_consistency(self):
        """测试 ID 生成一致性"""
        id1 = generate_id("same_content")
        id2 = generate_id("same_content")
        assert id1 == id2

    def test_id_generation_uniqueness(self):
        """测试 ID 生成唯一性"""
        id1 = generate_id("content1")
        id2 = generate_id("content2")
        assert id1 != id2
