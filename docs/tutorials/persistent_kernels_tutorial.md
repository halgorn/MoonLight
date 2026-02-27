# Persistent Kernels Tutorial

## Step 1: Create a Work Queue

```moonlight
queue = gpu_queue(100)  # Capacity of 100 items
```

## Step 2: Define a Persistent Kernel

```moonlight
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) break  # Stop signal
        process(task)
    }
}
```

## Step 3: Launch the Kernel

```moonlight
gpu[1, 256] worker(queue)
```

## Step 4: Send Work

```moonlight
for (i = 0; i < 100; i = i + 1) {
    enqueue_host(queue, work_item[i])
}
```

## Step 5: Stop the Kernel

```moonlight
enqueue_host(queue, -1)  # Stop signal
```

## Complete Example

See `examples/persistent/basic_persistent_kernel.gpu` for a complete example.

## Next Steps

- Try `examples/persistent/gpu_server.gpu`
- Explore `examples/persistent/video_stream.gpu`
- Read `PERSISTENT_KERNELS.md` for details

