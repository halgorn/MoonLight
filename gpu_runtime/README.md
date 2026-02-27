# GPU Runtime Library

Low-level GPU runtime components for MoonLight's 100% GPU-first architecture.

## Components

### Work Queue (`queue.cuh`, `queue.cu`)

Lock-free, thread-safe work queue for GPU-resident persistent kernels.

**Features:**
- Lock-free circular buffer
- Atomic operations
- Exponential backoff
- Template-based (any type)
- Host and device operations

**Usage:**
```cpp
// C++ Direct Usage
#include "queue.cuh"

// Create queue
GPUQueue<Task>* queue = create_gpu_queue<Task>(1024);

// Host operations
enqueue_from_host(queue, task);
dequeue_to_host(queue, &result);

// Device operations (in kernel)
__global__ void kernel(GPUQueue<Task>* queue) {
    Task t = queue->dequeue_wait();
    queue->enqueue(result);
}

// Cleanup
destroy_gpu_queue(queue);
```

**MoonLight Usage:**
```moonlight
# Automatic with MoonLight syntax
work_queue = gpu_queue[Task, 1024]
enqueue_host(work_queue, task)
result = dequeue_wait(work_queue)
```

## Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| GPU enqueue | <50ns | >100M ops/s |
| GPU dequeue | <100ns | >100M ops/s |
| Host enqueue | ~1μs | ~1M ops/s |
| Host dequeue | ~1μs | ~1M ops/s |

## Building

### Compile Test
```bash
nvcc -o test_queue ../tests/gpu_runtime/test_queue.cu queue.cu -std=c++11
./test_queue
```

### Include in Project
```cpp
#include "gpu_runtime/queue.cuh"
```

Link with: `gpu_runtime/queue.cu`

## Implementation Details

### Circular Buffer
- Power-of-2 capacity (automatically rounded up)
- Bitwise AND for index calculation (fast modulo)

### Thread Safety
- Atomic head/tail pointers
- Memory fences for visibility
- Lock-free algorithm

### Backoff Strategy
- Exponential: 1 → 2 → 4 → 8 → ... → 1024
- Reduces contention in high-load scenarios

## Requirements

- CUDA Toolkit 11.0+
- C++11 or later
- GPU with compute capability 3.5+

## Future Components

Coming in future weeks:
- Memory pools
- Device-side allocators
- Priority queues
- Bounded queues
- Statistics/monitoring

## See Also

- `docs/WORK_QUEUE_API.md` - Complete API reference
- `examples/persistent/` - Usage examples
- `tests/gpu_runtime/` - Test suite

