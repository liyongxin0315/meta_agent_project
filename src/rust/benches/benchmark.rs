//! Rust 性能基准测试

use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use meta_agent_rust::{Core, Task, ComputeEngine};

/// 任务解析性能测试
fn benchmark_task_parse(c: &mut Criterion) {
    let mut core = Core::new();
    let task = Task::new("test task content", 5, None).unwrap();

    c.bench_function("task_parse_single", |b| {
        b.iter(|| {
            let _ = core.execute(black_box(&task)).unwrap();
        })
    });
}

/// 批量任务处理性能测试
fn benchmark_batch_processing(c: &mut Criterion) {
    let mut core = Core::new();
    let tasks: Vec<Task> = (0..100)
        .map(|i| Task::new(&format!("task_{}", i), 5, None).unwrap())
        .collect();

    c.bench_function("task_batch_100", |b| {
        b.iter(|| {
            let _ = core.execute_batch(black_box(tasks.clone())).unwrap();
        })
    });
}

/// 不同任务大小性能测试
fn benchmark_task_size(c: &mut Criterion) {
    let mut group = c.benchmark_group("task_size");
    let mut core = Core::new();

    for size in [10, 100, 1000, 10000].iter() {
        let content = "x".repeat(*size);
        let task = Task::new(&content, 5, None).unwrap();

        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            size,
            |b, &_size| {
                b.iter(|| {
                    let _ = core.execute(black_box(&task)).unwrap();
                })
            },
        );
    }
    group.finish();
}

/// 计算引擎性能测试
fn benchmark_compute_engine(c: &mut Criterion) {
    let engine = ComputeEngine::new();

    c.bench_function("parallel_compute_1000", |b| {
        let data: Vec<f64> = (0..1000).map(|i| i as f64).collect();
        b.iter(|| {
            let _ = engine.parallel_compute(black_box(data.clone())).unwrap();
        })
    });
}

/// 大数据集处理性能测试
fn benchmark_large_dataset(c: &mut Criterion) {
    let engine = ComputeEngine::new();

    let mut group = c.benchmark_group("large_dataset");
    for size in [1000, 10000, 100000].iter() {
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            size,
            |b, &size| {
                b.iter(|| {
                    let _ = engine.process_large_dataset(black_box(size)).unwrap();
                })
            },
        );
    }
    group.finish();
}

criterion_group!(
    benches,
    benchmark_task_parse,
    benchmark_batch_processing,
    benchmark_task_size,
    benchmark_compute_engine,
    benchmark_large_dataset,
);

criterion_main!(benches);
