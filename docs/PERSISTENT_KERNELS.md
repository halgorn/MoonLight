# Persistent Kernels Guide

## What are Persistent Kernels?

Persistent kernels are CUDA kernels that run continuously, waiting for work instead of launching and terminating. This eliminates kernel launch overhead and enables real-time processing.

## Benefits

- **Zero Launch Overhead**: Kernels stay resident, no launch cost
- **Low Latency**: Immediate processing of incoming work
- **Real-time Processing**: Suitable for streaming applications
- **Better GPU Utilization**: Continuous execution

## Syntax

```moonlight
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) break  # Stop signal
        process(task)
    }
}
```

## Work Queue System

Persistent kernels use GPU queues for work distribution:

```moonlight
# Create queue
queue = gpu_queue(capacity)

# Enqueue from host
enqueue_host(queue, data)

# Dequeue in kernel
task = dequeue_wait(queue)
```

## Example: Video Processing

```moonlight
cuda persistent kernel def video_processor(queue) {
    while (true) {
        frame = dequeue_wait(queue)
        if (frame == nullptr) break
        
        # Process frame
        gpu[blocks, threads] process_frame(frame)
        
        # Send result
        enqueue(output_queue, processed_frame)
    }
}
```

## Best Practices

1. **Use for Continuous Workloads**: Persistent kernels excel when work arrives continuously
2. **Proper Cleanup**: Always check for stop signals
3. **Queue Management**: Size queues appropriately for your workload
4. **Error Handling**: Handle queue empty conditions gracefully

## Performance Considerations

- **Launch Overhead**: Eliminated (kernel stays resident)
- **Memory**: Kernel state persists in registers/shared memory
- **Synchronization**: Use queues for coordination, not CPU-GPU sync

## See Also

- `examples/persistent/` - Complete examples
- `benchmarks/persistent/` - Performance benchmarks

