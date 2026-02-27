// MoonLight Profiler Runtime
// Provides profiling utilities for kernel execution

#include <cuda_runtime.h>
#include <stdio.h>
#include <time.h>

// Profiling context
struct ProfilerContext {
    cudaEvent_t start_event;
    cudaEvent_t stop_event;
    float elapsed_ms;
    int kernel_count;
    char kernel_names[100][256];
    float kernel_times[100];
};

// Create profiler context
extern "C" ProfilerContext* create_profiler() {
    ProfilerContext* ctx = (ProfilerContext*)malloc(sizeof(ProfilerContext));
    cudaEventCreate(&ctx->start_event);
    cudaEventCreate(&ctx->stop_event);
    ctx->elapsed_ms = 0.0f;
    ctx->kernel_count = 0;
    return ctx;
}

// Start profiling
extern "C" void profiler_start(ProfilerContext* ctx) {
    cudaEventRecord(ctx->start_event);
}

// Stop profiling
extern "C" void profiler_stop(ProfilerContext* ctx) {
    cudaEventRecord(ctx->stop_event);
    cudaEventSynchronize(ctx->stop_event);
    cudaEventElapsedTime(&ctx->elapsed_ms, ctx->start_event, ctx->stop_event);
}

// Record kernel execution
extern "C" void profiler_record_kernel(ProfilerContext* ctx, const char* kernel_name, float time_ms) {
    if (ctx->kernel_count < 100) {
        strncpy(ctx->kernel_names[ctx->kernel_count], kernel_name, 255);
        ctx->kernel_times[ctx->kernel_count] = time_ms;
        ctx->kernel_count++;
    }
}

// Get elapsed time
extern "C" float profiler_get_elapsed(ProfilerContext* ctx) {
    return ctx->elapsed_ms;
}

// Print profiling report
extern "C" void profiler_print_report(ProfilerContext* ctx) {
    printf("=== Profiling Report ===\n");
    printf("Total time: %.3f ms\n", ctx->elapsed_ms);
    printf("\nKernels:\n");
    for (int i = 0; i < ctx->kernel_count; i++) {
        printf("  %s: %.3f ms\n", ctx->kernel_names[i], ctx->kernel_times[i]);
    }
}

// Free profiler context
extern "C" void free_profiler(ProfilerContext* ctx) {
    if (ctx) {
        cudaEventDestroy(ctx->start_event);
        cudaEventDestroy(ctx->stop_event);
        free(ctx);
    }
}

