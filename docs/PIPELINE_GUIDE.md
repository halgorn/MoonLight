# GPU Pipeline Programming Guide

Complete guide for building multi-stage GPU pipelines in MoonLight.

## Overview

Pipelines enable complex data processing workflows entirely on GPU with multiple stages running concurrently.

## Basic Concept

Traditional approach (slow):
```
CPU: Process stage 1 → Wait
GPU: Stage 1 done
CPU: Process stage 2 → Wait
GPU: Stage 2 done
```

Pipeline approach (fast):
```
GPU Stage 1: Processing item 3
GPU Stage 2: Processing item 2  ← Concurrent!
GPU Stage 3: Processing item 1  ← Concurrent!
```

**3x faster** because all stages run simultaneously!

---

## Simple 3-Stage Pipeline

```moonlight
# Stage kernels
cuda persistent kernel def stage1(input_q, output_q) {
    while (true) {
        data = dequeue_wait(input_q)
        result = preprocess(data)
        enqueue(output_q, result)
    }
}

cuda persistent kernel def stage2(input_q, output_q) {
    while (true) {
        data = dequeue_wait(input_q)
        result = compute(data)
        enqueue(output_q, result)
    }
}

cuda persistent kernel def stage3(input_q, output_q) {
    while (true) {
        data = dequeue_wait(input_q)
        result = postprocess(data)
        enqueue(output_q, result)
    }
}

def main() {
    # Create queues
    q0 = gpu_queue[Data, 512]
    q1 = gpu_queue[Data, 512]
    q2 = gpu_queue[Data, 512]
    q3 = gpu_queue[Data, 512]
    
    # Launch all stages
    gpu[blocks1, threads1] stage1(q0, q1)
    gpu[blocks2, threads2] stage2(q1, q2)
    gpu[blocks3, threads3] stage3(q2, q3)
    
    # Feed and collect
    enqueue_host(q0, data)
    result = dequeue_host(q3)
}
```

---

## Fork-Join Pattern

For parallel paths with different requirements:

```moonlight
# Splitter
cuda persistent kernel def splitter(input, fast_path, slow_path) {
    while (true) {
        data = dequeue_wait(input)
        if (data.is_fast) {
            enqueue(fast_path, data)
        } else {
            enqueue(slow_path, data)
        }
    }
}

# Fast processor (fewer threads)
cuda persistent kernel def fast_proc(input, output) {
    while (true) {
        data = dequeue_wait(input)
        result = quick_process(data)
        enqueue(output, result)
    }
}

# Slow processor (more threads!)
cuda persistent kernel def slow_proc(input, output) {
    while (true) {
        data = dequeue_wait(input)
        result = complex_process(data)
        enqueue(output, result)
    }
}

# Merger
cuda persistent kernel def merger(fast_in, slow_in, output) {
    while (true) {
        # Merge results from both paths
        if (dequeue(fast_in, &fast_result)) {
            enqueue(output, fast_result)
        }
        if (dequeue(slow_in, &slow_result)) {
            enqueue(output, slow_result)
        }
    }
}
```

---

## Load Balancing

### Thread Allocation

```moonlight
# Stage 1: Light preprocessing
gpu[4, 32] stage1(q0, q1)    # 128 threads

# Stage 2: Heavy computation
gpu[16, 32] stage2(q1, q2)   # 512 threads (4x more!)

# Stage 3: Light postprocessing
gpu[4, 32] stage3(q2, q3)    # 128 threads
```

**Rule**: Allocate threads proportional to stage complexity!

### Queue Sizing

```moonlight
# Fast producers need bigger queues
q_after_fast_stage = gpu_queue[Data, 2048]  # Large

# Slow consumers need bigger queues
q_before_slow_stage = gpu_queue[Data, 2048]  # Large

# Balanced stages
q_balanced = gpu_queue[Data, 512]  # Normal
```

---

## Performance Tuning

### 1. Measure Bottlenecks

```moonlight
# Monitor queue sizes
print("Queue 1 size:", get_queue_size(q1))
print("Queue 2 size:", get_queue_size(q2))

# If one queue is always full → next stage is bottleneck
# Solution: Add more threads to slow stage
```

### 2. Adjust Thread Count

```moonlight
# If Stage 2 is bottleneck:
# Before: gpu[4, 32] stage2(q1, q2)    # 128 threads
# After:  gpu[16, 32] stage2(q1, q2)   # 512 threads (4x)
```

### 3. Profile Stages

```moonlight
# Add timing in stages
cuda persistent kernel def stage_with_timing(in_q, out_q) {
    count = 0
    while (true) {
        start = clock64()
        data = dequeue_wait(in_q)
        result = process(data)
        enqueue(out_q, result)
        elapsed = clock64() - start
        
        count = count + 1
        if (count % 1000 == 0) {
            print("Stage avg time:", elapsed / 1000)
        }
    }
}
```

---

## Best Practices

### 1. Queue Sizes

```moonlight
# Too small: frequent blocking
q_small = gpu_queue[Data, 16]  # ❌

# Good: room for bursts
q_good = gpu_queue[Data, 512]  # ✅

# Too large: memory waste
q_huge = gpu_queue[Data, 100000]  # ❌
```

### 2. Stop Signals

```moonlight
# Always provide clean shutdown
stop_signal = Data(-1, 0.0)

# Send to ALL queues
enqueue_host(q0, stop_signal)
enqueue_host(q1, stop_signal)
enqueue_host(q2, stop_signal)
```

### 3. Error Handling

```moonlight
cuda persistent kernel def robust_stage(in_q, out_q) {
    errors = 0
    while (true) {
        data = dequeue_wait(in_q)
        if (data.id == -1) { break }
        
        # Try processing
        if (is_valid(data)) {
            result = process(data)
            enqueue(out_q, result)
        } else {
            errors = errors + 1
            # Send error marker
            error_data = Data(-2, float(errors))
            enqueue(out_q, error_data)
        }
    }
}
```

---

## Performance Characteristics

### Throughput

| Pipeline Stages | Serial (items/s) | Pipelined (items/s) | Speedup |
|-----------------|------------------|---------------------|---------|
| 1 stage | 10,000 | 10,000 | 1x |
| 2 stages | 5,000 | 10,000 | 2x |
| 3 stages | 3,333 | 10,000 | 3x |
| N stages | 10K/N | 10,000 | Nx |

**Pipeline maintains throughput of slowest stage!**

### Latency

```
Serial pipeline latency = Sum of all stage latencies
Example: 1ms + 5ms + 1ms = 7ms

Pipelined latency = Same (7ms for first item)
But: Next items come every 1ms (limited by slowest stage)!
```

---

## Advanced Patterns

### 1. Fan-Out

```moonlight
# One producer, multiple consumers
cuda persistent kernel def producer(output) {
    for (i = 0; i < 1000; i = i + 1) {
        enqueue(output, create_task(i))
    }
}

# Multiple consumers process in parallel
gpu[4, 32] consumer(queue, results)  # 128 threads
gpu[4, 32] consumer(queue, results)  # +128 threads
gpu[4, 32] consumer(queue, results)  # +128 threads
# Total: 384 threads consuming from same queue!
```

### 2. Fan-In

```moonlight
# Multiple producers
gpu[4, 32] producer1(queue)
gpu[4, 32] producer2(queue)
gpu[4, 32] producer3(queue)

# One consumer
gpu[12, 32] consumer(queue, results)  # Needs more threads!
```

### 3. Cyclic Pipeline

```moonlight
# For iterative refinement
cuda persistent kernel def refine(input_q, output_q, feedback_q) {
    while (true) {
        data = dequeue_wait(input_q)
        result = process(data)
        
        if (good_enough(result)) {
            enqueue(output_q, result)
        } else {
            # Send back for another iteration
            enqueue(feedback_q, result)
        }
    }
}
```

---

## Real-World Examples

### Video Processing Pipeline

```moonlight
gpu[8, 32]  stage_decode(frames_in, raw_frames)
gpu[16, 32] stage_filter(raw_frames, filtered_frames)
gpu[8, 32]  stage_encode(filtered_frames, frames_out)
```

### ML Inference Pipeline

```moonlight
gpu[4, 32]  stage_preprocess(images, normalized)
gpu[32, 32] stage_inference(normalized, predictions)
gpu[4, 32]  stage_postprocess(predictions, results)
```

### Data Analytics Pipeline

```moonlight
gpu[8, 32]  stage_extract(raw_data, extracted)
gpu[16, 32] stage_transform(extracted, transformed)
gpu[8, 32]  stage_load(transformed, results)
```

---

## Troubleshooting

### Problem: Low Throughput

**Symptoms**: Pipeline slower than expected

**Solutions**:
1. Find bottleneck stage (check queue sizes)
2. Add more threads to bottleneck
3. Optimize bottleneck algorithm
4. Split bottleneck into multiple stages

### Problem: High Latency

**Symptoms**: Long time until first result

**Solutions**:
1. Reduce per-stage processing time
2. Use smaller batches
3. Pre-fill pipeline with data

### Problem: Queue Overflow

**Symptoms**: Enqueue fails or blocks

**Solutions**:
1. Increase queue size
2. Speed up consumer
3. Slow down producer
4. Add more consumer threads

---

## See Also

- `WORK_QUEUE_API.md` - Queue operations
- `GPU_FIRST_GUIDE.md` - GPU-first principles
- `examples/persistent/` - Pipeline examples

---

**Version**: Week 3  
**Status**: Production Ready

