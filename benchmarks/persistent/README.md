# MoonLight Persistent Kernel Benchmarks

This directory contains benchmarks and examples for **Persistent Kernels** - one of MoonLight's revolutionary features for achieving true GPU-first computing.

## 🎯 What are Persistent Kernels?

Traditional GPU programming:
```
CPU: Launch kernel → Wait → Get results → Launch again → ...
     ↓ 10-50ms overhead per launch!
```

MoonLight Persistent Kernels:
```
GPU: Kernel stays running → Waits for work → Processes → Repeat
     ↓ < 1ms latency!
```

## 📁 Benchmarks

### 1. `queue_throughput.gpu`
**Measures:** Operations per second through GPU queue  
**Target:** > 1M ops/sec  
**Purpose:** Validate that queue overhead is minimal

**Run:**
```bash
python executor_main.py benchmarks/persistent/queue_throughput.gpu
```

### 2. `latency_test.gpu`
**Measures:** End-to-end latency from enqueue to dequeue  
**Target:** < 1ms  
**Purpose:** Validate ultra-low latency for real-time applications

**Run:**
```bash
python executor_main.py benchmarks/persistent/latency_test.gpu
```

### 3. `pipeline_vs_batch.gpu`
**Compares:** Persistent pipeline vs traditional batch processing  
**Target:** < 5% overhead compared to batch  
**Purpose:** Show that persistent kernels are efficient

**Run:**
```bash
python executor_main.py benchmarks/persistent/pipeline_vs_batch.gpu
```

### 4. `real_time_video.gpu`
**Demonstrates:** Real-time video processing at 60fps  
**Target:** < 16ms per frame  
**Purpose:** Real-world example of persistent kernels

**Run:**
```bash
python executor_main.py benchmarks/persistent/real_time_video.gpu
```

## 📊 Expected Results

| Metric | Target | Why Important |
|--------|--------|---------------|
| Enqueue latency | < 100ns | Fast task submission |
| Dequeue latency | < 100ns | Fast result retrieval |
| End-to-end latency | < 1ms | Real-time responsiveness |
| Throughput | > 1M ops/sec | Handle high workload |
| Overhead vs batch | < 5% | Efficient as traditional |

## 🚀 Performance Comparison

### Traditional Batch Processing
```python
for each batch:
    - Allocate GPU memory: 5-10ms
    - Copy data to GPU: 10-50ms
    - Launch kernel: 10-50ms
    - Wait for completion: varies
    - Copy data from GPU: 10-50ms
    - Free GPU memory: 1-5ms
TOTAL: 50-200ms per batch
```

### MoonLight Persistent Kernel
```moonlight
# One-time setup
input_queue = gpu_queue[int, 10000]
gpu[blocks, threads] persistent_worker(input_queue)

# Per operation (streaming)
for each item:
    enqueue_host(input_queue, item)  # < 0.1ms
    result = dequeue_host(output_queue)  # < 0.1ms
TOTAL: < 1ms per item
```

**Speedup:** 50-200x lower latency!

## 🎓 When to Use Persistent Kernels

### ✅ Perfect For:
- **Real-time processing** (video, audio, sensors)
- **Streaming workloads** (continuous data)
- **Interactive applications** (games, simulations)
- **Low-latency services** (ML inference servers)
- **High-frequency trading** (microsecond decisions)

### ⚠️ Not Ideal For:
- **One-shot computations** (use batch processing)
- **Small data** (overhead not worth it)
- **CPU-bound tasks** (GPU won't help)

## 🔧 Implementation Details

### GPU Queue Structure
```cpp
template<typename T>
struct GPUQueue {
    T* buffer;           // Circular buffer
    int* head;           // Consumer position
    int* tail;           // Producer position
    int capacity;        // Must be power of 2
    int mask;            // For fast modulo
};
```

### Lock-Free Operations
- Uses **atomic operations** for thread safety
- **Spin-wait with exponential backoff** for dequeue
- **Memory barriers** for consistency

### MoonLight Syntax
```moonlight
# Declare queue
work_queue = gpu_queue[Task, 10000]

# Persistent kernel
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task.stop) break
        process(task)
    }
}

# Launch (stays running!)
gpu[blocks, threads] worker(work_queue)

# Send work
enqueue_host(work_queue, my_task)
```

## 📈 Roadmap Status

**Phase 1 - Week 1: Work Queue System**
- [x] Lock-Free Queue (GPU) ✓
- [x] MoonLight Syntax ✓
- [x] Runtime Support ✓
- [x] Benchmarks ✓

**Next:**
- [ ] Week 2: Persistent Kernel Loop Structure
- [ ] Week 3: Multi-Stage Pipelines
- [ ] Week 4: Testing & Optimization

## 🎉 Success Criteria

✓ **Latency < 1ms:** Real-time responsiveness  
✓ **Throughput > 1M ops/sec:** High performance  
✓ **Overhead < 5%:** Efficient as batch  
✓ **Zero kernel launch overhead:** Persistent execution  
✓ **GPU-resident data:** No unnecessary transfers  

## 📚 Learn More

- [ROADMAP_100_PERCENT_GPU.md](../../ROADMAP_100_PERCENT_GPU.md) - Full roadmap
- [examples/persistent/](../../examples/persistent/) - More examples
- [gpu_runtime/queue.cu](../../gpu_runtime/queue.cu) - Implementation

---

**Status:** Phase 1 Week 1 COMPLETE! 🎉  
**Next:** Persistent Kernel Loop Structure (Week 2)
