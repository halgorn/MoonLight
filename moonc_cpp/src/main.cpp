#include "moonlight/lexer.h"
#include "moonlight/parser.h"
#include "moonlight/ast.h"
#include "moonlight/ptx_generator.h"
#include "moonlight/cuda_loader.h"
#include "moonlight/executor.h"
#include "moonlight/memory_manager.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>

void printUsage(const char* program_name) {
    std::cout << "MoonLight Compiler v2.0.0\n";
    std::cout << "Usage: " << program_name << " [options] <file.gpu>\n\n";
    std::cout << "Options:\n";
    std::cout << "  -r, --run          Run source file directly (interpreter mode)\n";
    std::cout << "  -c, --check        Check syntax only\n";
    std::cout << "  -S                 Generate PTX assembly only\n";
    std::cout << "  -o <file>          Output file name\n";
    std::cout << "  -O, --optimize     Enable optimizations\n";
    std::cout << "  -v, --verbose      Verbose output\n";
    std::cout << "  -h, --help         Show this help message\n";
    std::cout << "  --version          Show version information\n";
}

void printVersion() {
    std::cout << "MoonLight Compiler v2.0.0\n";
    std::cout << "Copyright (c) 2025 MoonLight Contributors\n";
    std::cout << "Built with C++17\n";
#ifdef MOONLIGHT_HAS_LLVM
    std::cout << "LLVM backend: enabled\n";
#else
    std::cout << "LLVM backend: disabled\n";
#endif
#ifdef MOONLIGHT_HAS_CUDA
    std::cout << "CUDA support: enabled\n";
#else
    std::cout << "CUDA support: disabled\n";
#endif
}

std::string readFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

bool checkSyntax(const std::string& source, bool verbose) {
    try {
        // Lexical analysis
        moonlight::Lexer lexer(source);
        auto tokens = lexer.tokenize();
        
        if (verbose) {
            std::cout << "Tokens (" << tokens.size() << "):\n";
            for (const auto& token : tokens) {
                std::cout << "  " << token.toString() << "\n";
            }
            std::cout << "\n";
        }
        
        // Parsing
        moonlight::Parser parser(tokens, verbose);
        auto program = parser.parseProgram();
        
        if (verbose) {
            std::cout << "AST:\n" << program->toString() << "\n\n";
        }
        
        std::cout << "[OK] Syntax is valid (" << program->statements.size() << " statements)\n";
        return true;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Syntax error: " << e.what() << "\n";
        return false;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }
    
    // Parse command line arguments
    std::string input_file;
    std::string output_file;
    bool run_mode = false;
    bool check_mode = false;
    bool optimize = false;
    bool verbose = false;
    bool generate_ptx_only = false;  // -S flag
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "-h" || arg == "--help") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "--version") {
            printVersion();
            return 0;
        } else if (arg == "-r" || arg == "--run") {
            run_mode = true;
        } else if (arg == "-c" || arg == "--check") {
            check_mode = true;
        } else if (arg == "-S") {
            generate_ptx_only = true;
        } else if (arg == "-O" || arg == "--optimize") {
            optimize = true;
        } else if (arg == "-v" || arg == "--verbose") {
            verbose = true;
        } else if (arg == "-o") {
            if (i + 1 < argc) {
                output_file = argv[++i];
            } else {
                std::cerr << "Error: -o requires an argument\n";
                return 1;
            }
        } else if (arg[0] != '-') {
            input_file = arg;
        } else {
            std::cerr << "Unknown option: " << arg << "\n";
            return 1;
        }
    }
    
    if (input_file.empty()) {
        std::cerr << "Error: No input file specified\n";
        printUsage(argv[0]);
        return 1;
    }
    
    try {
        // Read source file
        if (verbose) {
            std::cout << "Reading file: " << input_file << "\n";
        }
        std::string source = readFile(input_file);
        
        // Check mode: just validate syntax
        if (check_mode) {
            return checkSyntax(source, verbose) ? 0 : 1;
        }
        
        // Run mode: compile and execute on GPU
        if (run_mode) {
            std::cout << "Compiling and executing " << input_file << "...\n";
            // Continue to compilation, then execute
        }
        
        // Compile mode
        if (verbose) {
            std::cout << "Compiling " << input_file << "...\n";
        }
        
        // Lexical analysis
        moonlight::Lexer lexer(source);
        auto tokens = lexer.tokenize();
        
        if (verbose) {
            std::cout << "Lexing completed: " << tokens.size() << " tokens\n";
        }
        
        // Parsing
        if (verbose) {
            std::cout << "Parsing...\n";
        }
        
        moonlight::Parser parser(tokens, verbose);
        auto program = parser.parseProgram();
        
        if (verbose) {
            std::cout << "Parsing completed: " << program->statements.size() << " statements\n";
            std::cout << "\nAST:\n" << program->toString() << "\n";
        }
        
        // Code generation (PTX)
        if (verbose) {
            std::cout << "Generating PTX...\n";
        }
        
        moonlight::PTXGenerator ptx_gen;
        ptx_gen.setComputeCapability("sm_75");  // Default to compute capability 7.5
        ptx_gen.setPTXVersion("7.0");
        
        std::string ptx_code = ptx_gen.generatePTX(program);
        
        if (verbose) {
            std::cout << "PTX generated (" << ptx_code.length() << " bytes)\n";
        }
        
        // Save PTX if -S flag is set or output file specified
        if (generate_ptx_only || (!output_file.empty() && output_file.find(".ptx") != std::string::npos)) {
            // Save PTX to file
            std::string ptx_file = output_file;
            if (generate_ptx_only && output_file.empty()) {
                // Generate output filename from input
                ptx_file = input_file;
                size_t dot_pos = ptx_file.find_last_of('.');
                if (dot_pos != std::string::npos) {
                    ptx_file = ptx_file.substr(0, dot_pos) + ".ptx";
                } else {
                    ptx_file += ".ptx";
                }
            }
            
            std::ofstream ptx_out(ptx_file);
            if (ptx_out.is_open()) {
                ptx_out << ptx_code;
                ptx_out.close();
                std::cout << "[SUCCESS] PTX saved to " << ptx_file << "\n";
            } else {
                std::cerr << "[ERROR] Failed to open output file: " << ptx_file << "\n";
                return 1;
            }
        } else if (verbose) {
            std::cout << "\nGenerated PTX:\n";
            std::cout << "----------------------------------------\n";
            std::cout << ptx_code << "\n";
            std::cout << "----------------------------------------\n";
        }
        
        // If not just generating PTX, load and execute on GPU
        if (!generate_ptx_only) {
#ifdef MOONLIGHT_HAS_CUDA
            if (verbose) {
                std::cout << "Loading PTX on GPU...\n";
            }
            
            moonlight::CUDALoader cuda_loader;
            if (!cuda_loader.initialize()) {
                std::cerr << "[ERROR] Failed to initialize CUDA: " << cuda_loader.getLastError() << "\n";
                return 1;
            }
            
            CUmodule module = cuda_loader.loadPTX(ptx_code);
            if (module == nullptr) {
                std::cerr << "[ERROR] Failed to load PTX: " << cuda_loader.getLastError() << "\n";
                return 1;
            }
            
            if (verbose) {
                std::cout << "[SUCCESS] PTX loaded on GPU successfully\n";
            }
            
            // Execute program if run mode or if main() exists
            if (run_mode || !generate_ptx_only) {
                if (verbose) {
                    std::cout << "Executing program...\n";
                }
                
                moonlight::MemoryManager memory_manager(&cuda_loader);
                moonlight::Executor executor;
                executor.setMemoryManager(&memory_manager);
                executor.setCUDALoader(&cuda_loader);
                executor.setPTXModule(module);
                
                try {
                    executor.executeProgram(program);
                    if (verbose) {
                        std::cout << "[SUCCESS] Program executed successfully\n";
                    }
                } catch (const std::exception& e) {
                    std::cerr << "[ERROR] Execution failed: " << e.what() << "\n";
                    return 1;
                }
            } else {
                if (verbose) {
                    std::cout << "[INFO] Kernels are ready to execute\n";
                }
            }
#else
            if (verbose) {
                std::cout << "[INFO] CUDA support not compiled in\n";
                std::cout << "[INFO] PTX generated but not loaded on GPU\n";
            }
            
            // Execute program in CPU-only mode (without GPU)
            if (run_mode) {
                if (verbose) {
                    std::cout << "Executing program (CPU-only mode)...\n";
                }
                
                moonlight::Executor executor;
                
                try {
                    executor.executeProgram(program);
                    if (verbose) {
                        std::cout << "[SUCCESS] Program executed successfully\n";
                    }
                } catch (const std::exception& e) {
                    std::cerr << "[ERROR] Execution failed: " << e.what() << "\n";
                    return 1;
                }
            }
#endif
        }
        
        std::cout << "[SUCCESS] Compilation completed successfully!\n";
        std::cout << "[INFO] AST with " << program->statements.size() << " statements generated\n";
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] " << e.what() << "\n";
        return 1;
    }
}

