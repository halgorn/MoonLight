#pragma once

#include "moonlight/cuda_loader.h"
#include <string>
#include <map>
#include <memory>

namespace moonlight {

class MemoryManager {
public:
    MemoryManager(CUDALoader* loader);
    ~MemoryManager();
    
    // Allocate device memory: device[size]
    void* allocateDevice(size_t size, const std::string& var_name);
    
    // Register variable name with existing pointer
    void registerVariable(const std::string& var_name, void* ptr, size_t size);
    
    // Free device memory: free(ptr)
    void freeDevice(void* ptr);
    void freeDevice(const std::string& var_name);
    
    // Get device pointer for variable
    void* getDevicePointer(const std::string& var_name);
    
    // Get array size for variable
    size_t getArraySize(const std::string& var_name);
    
    // Set array size (for tracking)
    void setArraySize(const std::string& var_name, size_t size);
    
    // Check if variable has device memory
    bool hasDeviceMemory(const std::string& var_name);
    
    // Cleanup all allocations
    void cleanup();
    
private:
    CUDALoader* cuda_loader_;
    std::map<std::string, void*> device_pointers_;  // var_name -> device pointer
    std::map<std::string, size_t> array_sizes_;     // var_name -> size in bytes
    std::map<void*, std::string> pointer_to_var_;   // device pointer -> var_name (for cleanup)
};

} // namespace moonlight

