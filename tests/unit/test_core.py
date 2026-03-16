# -*- coding: utf-8 -*-
"""
单元测试 - 核心模块
"""

import pytest
from meta_agent.models.task import Task, TaskStatus


class TestTask:
    """任务模型测试"""

    def test_task_creation(self, sample_task):
        """测试任务创建"""
        assert sample_task.task_id == "test_001"
        assert sample_task.content == "Test task content"
        assert sample_task.priority == 5
        assert sample_task.status == TaskStatus.PENDING

    def test_task_start(self, sample_task):
        """测试任务开始"""
        sample_task.start()
        assert sample_task.status == TaskStatus.RUNNING
        assert sample_task.started_at is not None

    def test_task_complete(self, sample_task):
        """测试任务完成"""
        sample_task.complete()
        assert sample_task.status == TaskStatus.COMPLETED
        assert sample_task.completed_at is not None

    def test_task_fail(self, sample_task):
        """测试任务失败"""
        sample_task.fail("Test error")
        assert sample_task.status == TaskStatus.FAILED
        assert sample_task.error == "Test error"


class TestTaskStatus:
    """任务状态枚举测试"""

    def test_status_values(self):
        """测试状态值"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
