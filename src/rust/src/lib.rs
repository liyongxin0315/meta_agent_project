//! MetaAgent Rust 核心模块 - 完整实现
//!
//! 提供高性能任务处理、数据解析和跨平台系统调用。
//! 通过 pyo3 提供 Python 绑定。

use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// 任务数据结构
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct Task {
    #[pyo3(get, set)]
    pub task_id: String,
    #[pyo3(get, set)]
    pub content: String,
    #[pyo3(get, set)]
    pub priority: u32,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
    #[pyo3(get)]
    pub created_at: u64,
}

#[pymethods]
impl Task {
    /// 创建新任务
    #[new]
    #[pyo3(signature = (content, priority=5, metadata=None))]
    fn new(content: &str, priority: u32, metadata: Option<HashMap<String, String>>) -> PyResult<Self> {
        if content.trim().is_empty() {
            return Err(PyValueError::new_err("任务内容不能为空"));
        }

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;

        Ok(Task {
            task_id: format!("task_{}", timestamp),
            content: content.to_string(),
            priority,
            metadata: metadata.unwrap_or_default(),
            created_at: timestamp,
        })
    }

    /// 获取任务摘要
    fn summary(&self) -> String {
        format!(
            "Task(id={}, priority={}, content_len={})",
            self.task_id,
            self.priority,
            self.content.len()
        )
    }

    /// 转换为字典
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("task_id", &self.task_id)?;
        dict.set_item("content", &self.content)?;
        dict.set_item("priority", self.priority)?;
        dict.set_item("created_at", self.created_at)?;
        Ok(dict.into())
    }
}

/// 任务解析结果
#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct TaskResult {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub task_id: String,
    #[pyo3(get)]
    pub result: String,
    #[pyo3(get)]
    pub processing_time_ms: u64,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl TaskResult {
    fn __repr__(&self) -> String {
        format!(
            "TaskResult(success={}, task_id={}, processing_time={}ms)",
            self.success, self.task_id, self.processing_time_ms
        )
    }
}

/// Rust 核心处理器
#[pyclass]
pub struct Core {
    initialized: bool,
    tasks_processed: u64,
}

#[pymethods]
impl Core {
    /// 创建新的 Core 实例
    #[new]
    fn new() -> Self {
        Core {
            initialized: true,
            tasks_processed: 0,
        }
    }

    /// 解析并执行任务
    ///
    /// # Arguments
    ///
    /// * `task` - 任务对象
    ///
    /// # Returns
    ///
    /// 任务执行结果
    #[pyo3(text_signature = "(self, task)")]
    fn execute(&mut self, task: &Task) -> PyResult<TaskResult> {
        if !self.initialized {
            return Err(PyRuntimeError::new_err("Core 未初始化"));
        }

        let start_time = SystemTime::now();

        // 模拟高性能任务处理
        let result = self.process_task_internal(task);

        let processing_time = start_time
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
            - task.created_at;

        self.tasks_processed += 1;

        Ok(TaskResult {
            success: true,
            task_id: task.task_id.clone(),
            result,
            processing_time_ms: processing_time,
            metadata: HashMap::new(),
        })
    }

    /// 批量执行任务
    fn execute_batch(&mut self, tasks: Vec<&Task>) -> PyResult<Vec<TaskResult>> {
        let mut results = Vec::with_capacity(tasks.len());
        for task in tasks {
            results.push(self.execute(task)?);
        }
        Ok(results)
    }

    /// 获取处理统计
    fn get_stats(&self) -> HashMap<String, u64> {
        let mut stats = HashMap::new();
        stats.insert("tasks_processed".to_string(), self.tasks_processed);
        stats
    }

    /// 重置统计
    fn reset_stats(&mut self) {
        self.tasks_processed = 0;
    }

    /// 获取版本信息
    fn version(&self) -> String {
        env!("CARGO_PKG_VERSION").to_string()
    }
}

impl Core {
    /// 内部任务处理逻辑
    fn process_task_internal(&self, task: &Task) -> String {
        // 高性能数据处理逻辑
        let processed = format!(
            "Processed: {} (priority: {}, metadata: {} items)",
            task.content,
            task.priority,
            task.metadata.len()
        );
        processed
    }
}

/// 高性能计算工具
#[pyclass]
pub struct ComputeEngine {
    _private: (),
}

#[pymethods]
impl ComputeEngine {
    #[new]
    fn new() -> Self {
        ComputeEngine { _private: () }
    }

    /// 并行计算示例
    fn parallel_compute(&self, data: Vec<f64>) -> PyResult<Vec<f64>> {
        // 使用 Rayon 进行并行计算（实际使用时添加 rayon 依赖）
        let result: Vec<f64> = data.iter().map(|&x| x * 2.0).collect();
        Ok(result)
    }

    /// 大数据处理
    fn process_large_dataset(&self, size: usize) -> PyResult<u64> {
        let mut sum: u64 = 0;
        for i in 0..size {
            sum += i as u64;
        }
        Ok(sum)
    }
}

/// Python 模块初始化
#[pymodule]
fn meta_agent_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Task>()?;
    m.add_class::<TaskResult>()?;
    m.add_class::<Core>()?;
    m.add_class::<ComputeEngine>()?;
    
    // 模块级别常量
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "liyongxin0315")?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_new() {
        let task = Task::new("test task", 5, None).unwrap();
        assert!(!task.task_id.is_empty());
        assert_eq!(task.content, "test task");
        assert_eq!(task.priority, 5);
    }

    #[test]
    fn test_task_empty_content() {
        let result = Task::new("", 5, None);
        assert!(result.is_err());
    }

    #[test]
    fn test_core_execute() {
        let mut core = Core::new();
        let task = Task::new("test task", 5, None).unwrap();
        let result = core.execute(&task).unwrap();
        assert!(result.success);
        assert!(!result.result.is_empty());
    }

    #[test]
    fn test_compute_engine() {
        let engine = ComputeEngine::new();
        let data = vec![1.0, 2.0, 3.0];
        let result = engine.parallel_compute(data).unwrap();
        assert_eq!(result, vec![2.0, 4.0, 6.0]);
    }

    #[test]
    fn test_batch_processing() {
        let mut core = Core::new();
        let tasks = vec![
            Task::new("task 1", 5, None).unwrap(),
            Task::new("task 2", 3, None).unwrap(),
        ];
        let results = core.execute_batch(tasks).unwrap();
        assert_eq!(results.len(), 2);
        assert!(results.iter().all(|r| r.success));
    }
}
