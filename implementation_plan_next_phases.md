# Implementation Plan – MoonLight Phases 2‑6

## Goal Overview
Extend MoonLight beyond the completed **FASE 1 (Persistent Kernels)** and the near‑complete **FASE 1.1 (LLVM Backend)**. The next phases will add GPU‑resident data structures, dynamic parallelism, advanced optimizations, a full ecosystem of libraries, and comprehensive testing & documentation.

---
## Phase 2 – GPU‑Resident Data (3 weeks)
**Objective**: Enable data that never leaves the GPU, providing zero‑copy buffers, memory pools, and unified memory support.

### Tasks
1. **Keyword & Syntax** – Add `gpu_resident` keyword to lexer/parser.
2. **Runtime API** – Implement `gpu_resident_alloc` in `gpu_runtime/` (C++/CUDA) with pooling.
3. **Memory Management** – Expose `gpu_resident` objects to the language (construction, deallocation, reference counting).
4. **Zero‑Copy Integration** – Add host‑to‑device mapping utilities (`map_host`, `unmap_host`).
5. **Examples** – Create `examples/gpu_resident/*.gpu` (vector ops, matrix mul).
6. **Tests** – Add unit tests in `tests/gpu_resident/` for allocation, copy‑less ops, and lifetime.

### Verification
- Run benchmark `benchmarks/gpu_resident/zero_copy.gpu` and confirm < 1 µs transfer latency.
- Ensure existing persistent‑kernel code continues to compile.

---
## Phase 3 – Dynamic Parallelism (4 weeks)
**Objective**: Allow kernels to launch child kernels directly on the GPU.

### Tasks
1. **Parser Extension** – Support `launch` statements inside kernels.
2. **Codegen** – Extend `cuda_codegen.py` to emit `<<<>>>` launch syntax for child kernels.
3. **Runtime Support** – Add helper functions in `gpu_runtime/` for child‑kernel launch and synchronization.
4. **Safety Checks** – Implement static analysis to prevent dead‑lock patterns.
5. **Examples** – Recursive tree traversal, quick‑sort on GPU.
6. **Tests** – Validate correct execution order and resource cleanup.

### Verification
- Execute `benchmarks/dynamic_parallelism/quicksort.gpu` and compare against CPU baseline.
- Profile with `nvprof` to ensure child kernels are launched.

---
## Phase 4 – Advanced Optimizations (3 weeks)
**Objective**: Boost performance via kernel fusion, loop unrolling, and auto‑vectorization.

### Tasks
1. **Optimization Passes** – Implement IR passes in `llvm_backend.py` for fusion and unroll.
2. **Annotations** – Add `@optimize` decorator to control aggressiveness.
3. **Auto‑Vectorizer** – Leverage LLVM’s vectorizer for array operations.
4. **Benchmark Suite** – Extend `benchmarks/optimizations/` with before/after cases.
5. **Documentation** – Update `docs/OPTIMIZATIONS.md`.

### Verification
- Run `benchmarks/optimizations/matrix_mul.gpu` and verify ≥ 2× speed‑up.
- Ensure generated PTX passes validation.

---
## Phase 5 – Complete GPU Ecosystem (4 weeks)
**Objective**: Provide a standard library, package manager, and tooling for production use.

### Tasks
1. **Standard Library** – Implement `std` module (math, collections, io) in `stdlib/`.
2. **Package Manager** – Add `moonpkg` commands for publishing/consuming packages.
3. **Tooling** – Improve `moonc` CLI: `moonc build`, `moonc run`, `moonc test`.
4. **IDE Support** – Provide LSP server stub (future work) and VS Code extension updates.
5. **Production Samples** – End‑to‑end ML inference server, real‑time video pipeline.
6. **Tests** – Full integration test suite covering std lib and packaging.

### Verification
- Publish a sample package to a local repo and consume it in a new project.
- Run the ML inference example and confirm < 1 ms latency.

---
## Phase 6 – Testing & Documentation (2 weeks)
**Objective**: Achieve production‑grade reliability and comprehensive docs.

### Tasks
1. **Test Coverage** – Reach ≥ 90 % line coverage (use `pytest-cov`).
2. **Continuous Integration** – GitHub Actions workflow for lint, test, benchmark.
3. **User Guides** – Complete `docs/GETTING_STARTED.md`, `docs/REFERENCE.md`, and API docs.
4. **Performance Reports** – Auto‑generate benchmark reports on CI.
5. **Release Process** – Tag version, build wheels, publish to PyPI.

### Verification
- CI must pass all jobs on every push.
- Documentation builds without broken links.
- Release artifacts pass `twine check`.

---
## Overall Timeline
| Phase | Duration | Start (approx.) | End (approx.) |
|-------|----------|----------------|--------------|
| 2 – GPU‑Resident Data | 3 weeks | 2025‑12‑02 | 2025‑12‑22 |
| 3 – Dynamic Parallelism | 4 weeks | 2025‑12‑23 | 2026‑01‑19 |
| 4 – Advanced Optimizations | 3 weeks | 2026‑01‑20 | 2026‑02‑09 |
| 5 – Complete Ecosystem | 4 weeks | 2026‑02‑10 | 2026‑03‑09 |
| 6 – Testing & Docs | 2 weeks | 2026‑03‑10 | 2026‑03‑23 |

**Milestones**: each phase ends with a demo (kernel, benchmark, or package) and a CI‑green tag.

---
*Prepared by Antigravity – your AI coding assistant.*
