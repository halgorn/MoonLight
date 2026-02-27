#pragma once

#include <variant>
#include <vector>
#include <string>
#include <memory>
#include <iostream>
#include <cstdint>

namespace moonlight {

// Forward declaration
class Value;

// Alias for Value list to help with recursive definition
using ValueList = std::vector<Value>;

// Wrapper for GPU pointer to use in variant
struct DevicePointer {
    void* ptr;
    DevicePointer(void* p = nullptr) : ptr(p) {}
    operator void*() const { return ptr; }
};

// Value type that can hold any MoonLight value
// Note: Using ValueList instead of std::vector<Value> directly
class Value {
public:
    using VariantType = std::variant<
        int,                          // Integer
        double,                       // Float
        std::string,                  // String
        bool,                         // Boolean
        ValueList,                    // List/Array
        DevicePointer                 // GPU pointer (device memory)
    >;
    
    VariantType data;
    
    // Constructors
    Value() : data(0) {}
    Value(int i) : data(i) {}
    Value(double f) : data(f) {}
    Value(const std::string& s) : data(s) {}
    Value(bool b) : data(b) {}
    Value(const ValueList& l) : data(l) {}
    Value(DevicePointer p) : data(p) {}
    
    // Implicit conversions
    operator const VariantType&() const { return data; }
    operator VariantType&() { return data; }
};

// Helper to access variant
inline const Value::VariantType& getVariant(const Value& v) {
    return v.data;
}

inline Value::VariantType& getVariant(Value& v) {
    return v.data;
}

// Helper functions for Value
bool isInteger(const Value& v);
bool isFloat(const Value& v);
bool isString(const Value& v);
bool isBoolean(const Value& v);
bool isList(const Value& v);
bool isPointer(const Value& v);

// Get value with type checking (moved to .cpp to avoid MSVC issues)
int getInteger(const Value& v);
double getFloat(const Value& v);
std::string getString(const Value& v);
bool getBoolean(const Value& v);

// getList moved to .cpp to avoid recursive variant issues
std::vector<Value>& getList(Value& v);
const std::vector<Value>& getList(const Value& v);

void* getPointer(const Value& v);

// Convert Value to string for printing
std::string valueToString(const Value& v);

// Type conversion helpers
Value convertToFloat(const Value& v);
Value convertToInteger(const Value& v);
Value convertToString(const Value& v);

} // namespace moonlight

