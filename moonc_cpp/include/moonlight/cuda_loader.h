#pragma once

#include <string>
#include <vector>
#include <memory>

// Include CUDA Driver API types
#ifdef MOONLIGHT_HAS_CUDA
#include <cuda.h>
#else
// Forward declarations if CUDA not available
typedef void* CUmodule;
typedef void* CUfunction;
typedef void* CUevent;
typedef void* CUstream;
typedef int CUresult;
#endif

namespace moonlight {

class CUDALoader {
public:
    CUDALoader();
    ~CUDALoader();
    
    // Initialize CUDA
    bool initialize();
    
    // Load PTX code into a module
    CUmodule loadPTX(const std::string& ptx_code);
    
    // Get function from module
    CUfunction getFunction(CUmodule module, const std::string& function_name);
    
    // Launch kernel
    bool launchKernel(CUfunction function, 
                      unsigned int grid_x, unsigned int grid_y, unsigned int grid_z,
                      unsigned int block_x, unsigned int block_y, unsigned int block_z,
                      unsigned int shared_mem_bytes,
                      void** kernel_params);
    
    // Memory management
    void* allocateDeviceMemory(size_t size);
    void freeDeviceMemory(void* ptr);
    bool copyHostToDevice(void* dst, const void* src, size_t size);
    bool copyDeviceToHost(void* dst, const void* src, size_t size);
    
    // Synchronization
    bool synchronize();
    
    // CUDA Events for timing
    CUevent createEvent();
    bool recordEvent(CUevent event, CUstream stream = nullptr);
    bool synchronizeEvent(CUevent event);
    float getElapsedTime(CUevent start, CUevent stop);  // Returns time in milliseconds
    void destroyEvent(CUevent event);
    
    // Error handling
    std::string getLastError() const;
    static std::string getCUDAErrorString(CUresult error);
    
private:
    bool initialized_;
    std::string last_error_;
    
    // Helper methods
    bool checkCUDAError(CUresult result, const std::string& operation);
};

} // namespace moonlight

