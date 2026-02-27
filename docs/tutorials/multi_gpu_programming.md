# Multi-GPU Programming Tutorial

## Step 1: Enable P2P

```moonlight
enable_p2p(0, 1)  # Enable P2P between GPU 0 and 1
```

## Step 2: Allocate on Different GPUs

```moonlight
gpu[0] d_data0 = device[1000]
gpu[1] d_data1 = device[1000]
```

## Step 3: Launch Kernels

```moonlight
gpu[0][4, 256] kernel1(d_data0, 1000)
gpu[1][4, 256] kernel2(d_data1, 1000)
```

## Step 4: P2P Transfer

```moonlight
p2p_copy(d_data1, d_data0, 1000 * sizeof(float))
```

## Load Balancing

```moonlight
num_gpus = 4
total_size = 1000000
chunk_size = total_size / num_gpus

for (i = 0; i < num_gpus; i = i + 1) {
    gpu[i] process_chunk(data + i * chunk_size, chunk_size)
}
```

## Complete Examples

- `examples/multi_gpu/p2p_transfer.gpu`
- `examples/multi_gpu/auto_balance.gpu`
- `examples/multi_gpu/distributed_pipeline.gpu`

## Next Steps

- Try the examples
- Check `benchmarks/multi_gpu/scaling_test.gpu`
- Read best practices

