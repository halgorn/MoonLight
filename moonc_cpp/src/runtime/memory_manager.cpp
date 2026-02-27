#include "moonlight/memory_manager.h"
#include <iostream>

namespace moonlight {

MemoryManager::MemoryManager(CUDALoader* loader)
    : cuda_loader_(loader) {
}

MemoryManager::~MemoryManager() {
    cleanup();
}

void* MemoryManager::allocateDevice(size_t size, const std::string& var_name) {
    void* ptr = cuda_loader_->allocateDeviceMemory(size);
    if (ptr != nullptr) {
        device_pointers_[var_name] = ptr;
        array_sizes_[var_name] = size;
        pointer_to_var_[ptr] = var_name;
    }
    return ptr;
}

void MemoryManager::freeDevice(void* ptr) {
    if (ptr != nullptr) {
        cuda_loader_->freeDeviceMemory(ptr);
        auto it = pointer_to_var_.find(ptr);
        if (it != pointer_to_var_.end()) {
            std::string var_name = it->second;
            device_pointers_.erase(var_name);
            array_sizes_.erase(var_name);
            pointer_to_var_.erase(it);
        }
    }
}

void MemoryManager::freeDevice(const std::string& var_name) {
    auto it = device_pointers_.find(var_name);
    if (it != device_pointers_.end()) {
        void* ptr = it->second;
        freeDevice(ptr);
    }
}

void* MemoryManager::getDevicePointer(const std::string& var_name) {
    auto it = device_pointers_.find(var_name);
    if (it != device_pointers_.end()) {
        return it->second;
    }
    return nullptr;
}

size_t MemoryManager::getArraySize(const std::string& var_name) {
    auto it = array_sizes_.find(var_name);
    if (it != array_sizes_.end()) {
        return it->second;
    }
    return 0;
}

void MemoryManager::setArraySize(const std::string& var_name, size_t size) {
    array_sizes_[var_name] = size;
}

void MemoryManager::registerVariable(const std::string& var_name, void* ptr, size_t size) {
    device_pointers_[var_name] = ptr;
    array_sizes_[var_name] = size;
    pointer_to_var_[ptr] = var_name;
}

bool MemoryManager::hasDeviceMemory(const std::string& var_name) {
    return device_pointers_.find(var_name) != device_pointers_.end();
}

void MemoryManager::cleanup() {
    // Free all device memory
    for (auto& pair : device_pointers_) {
        cuda_loader_->freeDeviceMemory(pair.second);
    }
    device_pointers_.clear();
    array_sizes_.clear();
    pointer_to_var_.clear();
}

} // namespace moonlight

