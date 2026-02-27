#include "moonlight/value.h"
#include <sstream>

namespace moonlight {

bool isInteger(const Value& v) {
    return std::holds_alternative<int>(getVariant(v));
}

bool isFloat(const Value& v) {
    return std::holds_alternative<double>(getVariant(v));
}

bool isString(const Value& v) {
    return std::holds_alternative<std::string>(getVariant(v));
}

bool isBoolean(const Value& v) {
    return std::holds_alternative<bool>(getVariant(v));
}

bool isList(const Value& v) {
    return std::holds_alternative<ValueList>(getVariant(v));
}

bool isPointer(const Value& v) {
    return std::holds_alternative<DevicePointer>(getVariant(v));
}

int getInteger(const Value& v) {
    return std::get<int>(getVariant(v));
}

double getFloat(const Value& v) {
    const auto& var = getVariant(v);
    if (std::holds_alternative<int>(var)) {
        return static_cast<double>(std::get<int>(var));
    }
    return std::get<double>(var);
}

std::string getString(const Value& v) {
    return std::get<std::string>(getVariant(v));
}

bool getBoolean(const Value& v) {
    return std::get<bool>(getVariant(v));
}

ValueList& getList(Value& v) {
    return std::get<ValueList>(getVariant(v));
}

const ValueList& getList(const Value& v) {
    return std::get<ValueList>(getVariant(v));
}

void* getPointer(const Value& v) {
    return std::get<DevicePointer>(getVariant(v)).ptr;
}

std::string valueToString(const Value& v) {
    if (isInteger(v)) {
        return std::to_string(getInteger(v));
    } else if (isFloat(v)) {
        std::stringstream ss;
        ss << getFloat(v);
        return ss.str();
    } else if (isString(v)) {
        return getString(v);
    } else if (isBoolean(v)) {
        return getBoolean(v) ? "True" : "False";
    } else if (isList(v)) {
        std::stringstream ss;
        ss << "[";
        const auto& list = getList(v);
        for (size_t i = 0; i < list.size(); ++i) {
            if (i > 0) ss << ", ";
            ss << valueToString(list[i]);
        }
        ss << "]";
        return ss.str();
    } else if (isPointer(v)) {
        return "<GPU pointer>";
    }
    return "<unknown>";
}

Value convertToFloat(const Value& v) {
    if (isFloat(v)) {
        return v;
    } else if (isInteger(v)) {
        return static_cast<double>(getInteger(v));
    } else if (isString(v)) {
        try {
            return std::stod(getString(v));
        } catch (...) {
            return 0.0;
        }
    }
    return 0.0;
}

Value convertToInteger(const Value& v) {
    if (isInteger(v)) {
        return v;
    } else if (isFloat(v)) {
        return static_cast<int>(getFloat(v));
    } else if (isString(v)) {
        try {
            return std::stoi(getString(v));
        } catch (...) {
            return 0;
        }
    }
    return 0;
}

Value convertToString(const Value& v) {
    if (isString(v)) {
        return v;
    }
    return valueToString(v);
}

} // namespace moonlight

