#include "moonlight/cuda_loader.h"
#include <cuda.h>
#include <cuda_runtime.h>
#include <iostream>
#include <sstream>

namespace moonlight {

CUDALoader::CUDALoader() : initialized_(false) {
}

CUDALoader::~CUDALoader() {
    // Cleanup if needed
}

bool CUDALoader::initialize() {
    if (initialized_) {
        return true;
    }
    
    CUresult result = cuInit(0);
    if (!checkCUDAError(result, "cuInit")) {
        return false;
    }
    
    // Get device count
    int device_count = 0;
    result = cuDeviceGetCount(&device_count);
    if (!checkCUDAError(result, "cuDeviceGetCount")) {
        return false;
    }
    
    if (device_count == 0) {
        last_error_ = "No CUDA devices found";
        return false;
    }
    
    // Create context for device 0
    CUdevice device;
    result = cuDeviceGet(&device, 0);
    if (!checkCUDAError(result, "cuDeviceGet")) {
        return false;
    }
    
    CUcontext context;
    result = cuCtxCreate(&context, 0, device);
    if (!checkCUDAError(result, "cuCtxCreate")) {
        return false;
    }
    
    initialized_ = true;
    return true;
}

CUmodule CUDALoader::loadPTX(const std::string& ptx_code) {
    if (!initialized_) {
        if (!initialize()) {
            return nullptr;
        }
    }
    
    CUmodule module;
    CUresult result = cuModuleLoadData(&module, ptx_code.c_str());
    
    if (!checkCUDAError(result, "cuModuleLoadData")) {
        return nullptr;
    }
    
    return module;
}

CUfunction CUDALoader::getFunction(CUmodule module, const std::string& function_name) {
    if (module == nullptr) {
        last_error_ = "Invalid module";
        return nullptr;
    }
    
    CUfunction function;
    CUresult result = cuModuleGetFunction(&function, module, function_name.c_str());
    
    if (!checkCUDAError(result, "cuModuleGetFunction")) {
        return nullptr;
    }
    
    return function;
}

bool CUDALoader::launchKernel(CUfunction function,
                              unsigned int grid_x, unsigned int grid_y, unsigned int grid_z,
                              unsigned int block_x, unsigned int block_y, unsigned int block_z,
                              unsigned int shared_mem_bytes,
                              void** kernel_params) {
    if (function == nullptr) {
        last_error_ = "Invalid function";
        return false;
    }
    
    CUresult result = cuLaunchKernel(
        function,
        grid_x, grid_y, grid_z,      // grid dimensions
        block_x, block_y, block_z,   // block dimensions
        shared_mem_bytes,            // shared memory
        nullptr,                     // stream (null = default)
        kernel_params,               // kernel parameters
        nullptr                      // extra options
    );
    
    return checkCUDAError(result, "cuLaunchKernel");
}

void* CUDALoader::allocateDeviceMemory(size_t size) {
    void* ptr = nullptr;
    cudaError_t err = cudaMalloc(&ptr, size);
    if (err != cudaSuccess) {
        last_error_ = "cudaMalloc failed: " + std::string(cudaGetErrorString(err));
        return nullptr;
    }
    return ptr;
}

void CUDALoader::freeDeviceMemory(void* ptr) {
    if (ptr != nullptr) {
        cudaFree(ptr);
    }
}

bool CUDALoader::copyHostToDevice(void* dst, const void* src, size_t size) {
    cudaError_t err = cudaMemcpy(dst, src, size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        last_error_ = "cudaMemcpy H->D failed: " + std::string(cudaGetErrorString(err));
        return false;
    }
    return true;
}

bool CUDALoader::copyDeviceToHost(void* dst, const void* src, size_t size) {
    cudaError_t err = cudaMemcpy(dst, src, size, cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        last_error_ = "cudaMemcpy D->H failed: " + std::string(cudaGetErrorString(err));
        return false;
    }
    return true;
}

bool CUDALoader::synchronize() {
    cudaError_t err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {
        last_error_ = "cudaDeviceSynchronize failed: " + std::string(cudaGetErrorString(err));
        return false;
    }
    return true;
}

std::string CUDALoader::getLastError() const {
    return last_error_;
}

CUevent CUDALoader::createEvent() {
    CUevent event;
    CUresult result = cuEventCreate(&event, CU_EVENT_DEFAULT);
    if (!checkCUDAError(result, "cuEventCreate")) {
        return nullptr;
    }
    return event;
}

bool CUDALoader::recordEvent(CUevent event, CUstream stream) {
    if (event == nullptr) {
        last_error_ = "Invalid event";
        return false;
    }
    CUresult result = cuEventRecord(event, stream);
    return checkCUDAError(result, "cuEventRecord");
}

bool CUDALoader::synchronizeEvent(CUevent event) {
    if (event == nullptr) {
        last_error_ = "Invalid event";
        return false;
    }
    CUresult result = cuEventSynchronize(event);
    return checkCUDAError(result, "cuEventSynchronize");
}

float CUDALoader::getElapsedTime(CUevent start, CUevent stop) {
    if (start == nullptr || stop == nullptr) {
        last_error_ = "Invalid event(s)";
        return -1.0f;
    }
    float elapsed_ms = 0.0f;
    CUresult result = cuEventElapsedTime(&elapsed_ms, start, stop);
    if (!checkCUDAError(result, "cuEventElapsedTime")) {
        return -1.0f;
    }
    return elapsed_ms;
}

void CUDALoader::destroyEvent(CUevent event) {
    if (event != nullptr) {
        cuEventDestroy(event);
    }
}

std::string CUDALoader::getCUDAErrorString(CUresult error) {
    const char* error_string;
    cuGetErrorString(error, &error_string);
    if (error_string) {
        return std::string(error_string);
    }
    return "Unknown CUDA error: " + std::to_string(error);
}

bool CUDALoader::checkCUDAError(CUresult result, const std::string& operation) {
    if (result != CUDA_SUCCESS) {
        last_error_ = operation + " failed: " + getCUDAErrorString(result);
        return false;
    }
    return true;
}

} // namespace moonlight

