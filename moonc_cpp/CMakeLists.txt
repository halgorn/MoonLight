cmake_minimum_required(VERSION 3.15)
project(MoonLight VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(MOONLIGHT_BUILD_TESTS "Build tests" ON)
option(MOONLIGHT_WITH_LLVM "Enable LLVM backend" ON)
option(MOONLIGHT_WITH_CUDA "Enable CUDA support" ON)

# Compiler flags
if(MSVC)
    add_compile_options(/W4)  # /WX removed to allow warnings
    # Disable specific warnings that are too strict
    add_compile_options(/wd4996)  # Disable deprecated function warnings
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Source files
set(MOONLIGHT_SOURCES
    src/lexer/lexer.cpp
    src/lexer/token.cpp
    src/parser/parser.cpp
    src/ast/ast_node.cpp
    src/codegen/ptx_generator.cpp
    src/runtime/cuda_loader.cpp
    src/runtime/executor.cpp
    src/runtime/memory_manager.cpp
    src/runtime/value.cpp
    src/main.cpp
)

# Headers
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Main executable
add_executable(moonc ${MOONLIGHT_SOURCES})

# LLVM support (optional)
if(MOONLIGHT_WITH_LLVM)
    find_package(LLVM REQUIRED CONFIG)
    message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
    
    include_directories(${LLVM_INCLUDE_DIRS})
    add_definitions(${LLVM_DEFINITIONS})
    
    target_compile_definitions(moonc PRIVATE MOONLIGHT_HAS_LLVM)
    
    # Link LLVM libraries
    llvm_map_components_to_libnames(llvm_libs
        core
        support
        irreader
        executionengine
        mcjit
        native
    )
    target_link_libraries(moonc ${llvm_libs})
endif()

# CUDA support (optional)
if(MOONLIGHT_WITH_CUDA)
    find_package(CUDA)
    if(CUDA_FOUND)
        message(STATUS "Found CUDA ${CUDA_VERSION}")
        include_directories(${CUDA_INCLUDE_DIRS})
        target_compile_definitions(moonc PRIVATE MOONLIGHT_HAS_CUDA)
        # Find CUDA Driver API library
        find_library(CUDA_cuda_LIBRARY
            NAMES cuda
            PATHS
                ${CUDA_TOOLKIT_ROOT_DIR}/lib/x64
                ${CUDA_TOOLKIT_ROOT_DIR}/lib64
                ${CUDA_TOOLKIT_ROOT_DIR}/lib
        )
        if(CUDA_cuda_LIBRARY)
            message(STATUS "Found CUDA Driver API: ${CUDA_cuda_LIBRARY}")
            target_link_libraries(moonc ${CUDA_LIBRARIES} ${CUDA_cudart_LIBRARY} ${CUDA_cuda_LIBRARY})
        else()
            message(WARNING "CUDA Driver API not found, may have linking issues")
            target_link_libraries(moonc ${CUDA_LIBRARIES} ${CUDA_cudart_LIBRARY})
        endif()
    else()
        # Try to find CUDA using find_library
        find_library(CUDA_cudart_LIBRARY
            NAMES cudart
            PATHS
                ${CUDA_TOOLKIT_ROOT_DIR}/lib64
                ${CUDA_TOOLKIT_ROOT_DIR}/lib
                /usr/local/cuda/lib64
                /usr/local/cuda/lib
        )
        find_path(CUDA_INCLUDE_DIR
            NAMES cuda.h
            PATHS
                ${CUDA_TOOLKIT_ROOT_DIR}/include
                /usr/local/cuda/include
        )
        if(CUDA_cudart_LIBRARY AND CUDA_INCLUDE_DIR)
            message(STATUS "Found CUDA libraries")
            include_directories(${CUDA_INCLUDE_DIR})
            target_compile_definitions(moonc PRIVATE MOONLIGHT_HAS_CUDA)
            # Find CUDA Driver API library (for cuLaunchKernel, etc.)
            find_library(CUDA_cuda_LIBRARY
                NAMES cuda
                PATHS
                    ${CUDA_TOOLKIT_ROOT_DIR}/lib64
                    ${CUDA_TOOLKIT_ROOT_DIR}/lib
                    "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib/x64"
                    "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib"
            )
            if(CUDA_cuda_LIBRARY)
                message(STATUS "Found CUDA Driver API: ${CUDA_cuda_LIBRARY}")
                target_link_libraries(moonc ${CUDA_cudart_LIBRARY} ${CUDA_cuda_LIBRARY})
            else()
                message(WARNING "CUDA Driver API not found, linking only cudart")
                target_link_libraries(moonc ${CUDA_cudart_LIBRARY})
            endif()
        else()
            message(WARNING "CUDA not found, CUDA features will be disabled")
        endif()
    endif()
endif()

# Tests
if(MOONLIGHT_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Install
install(TARGETS moonc DESTINATION bin)

# Package
set(CPACK_PACKAGE_NAME "MoonLight")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "GPU-First Programming Language")
include(CPack)

