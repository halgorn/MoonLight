#!/usr/bin/env python3
"""
MoonLight GPU Benchmark Runner
Compares MoonLight-generated CUDA code vs hand-written CUDA code
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class GPUBenchmarkRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.gpu_bench_dir = Path(__file__).parent
        self.results = []
        
    def check_cuda_available(self):
        """Check if CUDA is available"""
        try:
            result = subprocess.run(['nvcc', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ CUDA compiler (nvcc) found")
                print(result.stdout.split('\n')[3])  # Version line
                return True
            return False
        except FileNotFoundError:
            print("✗ CUDA compiler (nvcc) not found")
            print("  Please install CUDA Toolkit to run GPU benchmarks")
            return False
    
    def compile_cuda_file(self, cu_file, output_name):
        """Compile a .cu file with nvcc"""
        print(f"\n  Compiling {cu_file.name}...")
        
        cmd = [
            'nvcc',
            str(cu_file),
            '-o', str(output_name),
            '-O3',  # Optimization
            '-std=c++11'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"    ✗ Compilation failed:")
                print(f"      {result.stderr}")
                return False
            print(f"    ✓ Compiled successfully")
            return True
        except subprocess.TimeoutExpired:
            print(f"    ✗ Compilation timeout")
            return False
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False
    
    def compile_moonlight_file(self, gpu_file, output_name):
        """Compile a .gpu file with MoonLight transpiler"""
        print(f"\n  Compiling {gpu_file.name} (MoonLight)...")
        
        # First, transpile to C++/CUDA
        moonc_path = self.project_root / 'moonc.py'
        
        if not moonc_path.exists():
            print(f"    ✗ moonc.py not found at {moonc_path}")
            return False
        
        cmd = [
            sys.executable,
            str(moonc_path),
            str(gpu_file),
            '-o', str(output_name),
            '--cuda'  # Enable CUDA mode
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"    ✗ Compilation failed:")
                print(f"      {result.stderr}")
                return False
            print(f"    ✓ Compiled successfully")
            return True
        except subprocess.TimeoutExpired:
            print(f"    ✗ Compilation timeout")
            return False
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return False
    
    def run_executable(self, exe_path):
        """Run an executable and measure time"""
        print(f"\n  Running {exe_path.name}...")
        
        start = time.perf_counter()
        try:
            result = subprocess.run([str(exe_path)], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 min timeout
            elapsed = time.perf_counter() - start
            
            if result.returncode != 0:
                print(f"    ✗ Execution failed:")
                print(f"      {result.stderr}")
                return None, None
            
            print(f"    ✓ Completed in {elapsed:.3f}s")
            return elapsed, result.stdout
        except subprocess.TimeoutExpired:
            print(f"    ✗ Execution timeout (>5min)")
            return None, None
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None, None
    
    def parse_cuda_timing(self, output):
        """Extract timing information from CUDA executable output"""
        timings = {}
        for line in output.split('\n'):
            if 'H->D Transfer:' in line:
                timings['h2d'] = float(line.split(':')[1].strip().split()[0])
            elif 'Kernel:' in line and 'Launching' not in line:
                timings['kernel'] = float(line.split(':')[1].strip().split()[0])
            elif 'D->H Transfer:' in line:
                timings['d2h'] = float(line.split(':')[1].strip().split()[0])
            elif 'Total:' in line:
                timings['total'] = float(line.split(':')[1].strip().split()[0])
            elif 'GFLOPS' in line:
                timings['gflops'] = float(line.split(':')[1].strip().split()[0])
        return timings
    
    def run_benchmark(self, name, moonlight_file, cuda_file):
        """Run a single benchmark comparing MoonLight vs CUDA"""
        print(f"\n{'='*70}")
        print(f"Benchmark: {name}")
        print(f"{'='*70}")
        
        result = {
            'name': name,
            'moonlight_time': None,
            'cuda_time': None,
            'moonlight_timings': None,
            'cuda_timings': None,
            'speedup': None
        }
        
        # Compile and run pure CUDA version
        cuda_exe = self.gpu_bench_dir / f"{cuda_file.stem}_cuda"
        if sys.platform == "win32":
            cuda_exe = cuda_exe.with_suffix('.exe')
        
        if self.compile_cuda_file(cuda_file, cuda_exe):
            cuda_time, cuda_output = self.run_executable(cuda_exe)
            if cuda_time is not None:
                result['cuda_time'] = cuda_time
                result['cuda_timings'] = self.parse_cuda_timing(cuda_output)
            
            # Clean up executable
            if cuda_exe.exists():
                cuda_exe.unlink()
        
        # Compile and run MoonLight version
        moonlight_exe = self.gpu_bench_dir / f"{moonlight_file.stem}_moonlight"
        if sys.platform == "win32":
            moonlight_exe = moonlight_exe.with_suffix('.exe')
        
        if self.compile_moonlight_file(moonlight_file, moonlight_exe):
            moonlight_time, moonlight_output = self.run_executable(moonlight_exe)
            if moonlight_time is not None:
                result['moonlight_time'] = moonlight_time
                result['moonlight_timings'] = self.parse_cuda_timing(moonlight_output)
            
            # Clean up executable
            if moonlight_exe.exists():
                moonlight_exe.unlink()
        
        # Calculate speedup
        if result['cuda_time'] and result['moonlight_time']:
            result['speedup'] = result['cuda_time'] / result['moonlight_time']
            
            print(f"\n  📊 Results:")
            print(f"     Pure CUDA:     {result['cuda_time']:.3f}s")
            print(f"     MoonLight:     {result['moonlight_time']:.3f}s")
            print(f"     Speedup:       {result['speedup']:.2f}x", end="")
            
            if result['speedup'] > 1.0:
                print(" (MoonLight faster! 🚀)")
            elif result['speedup'] > 0.95:
                print(" (Equivalent performance ✓)")
            else:
                print(" (CUDA faster)")
            
            # Show detailed timings if available
            if result['cuda_timings'] and 'kernel' in result['cuda_timings']:
                print(f"\n  🔍 Detailed Timing (CUDA):")
                if 'h2d' in result['cuda_timings']:
                    print(f"     H->D Transfer: {result['cuda_timings']['h2d']:.3f} ms")
                print(f"     Kernel:        {result['cuda_timings']['kernel']:.3f} ms")
                if 'd2h' in result['cuda_timings']:
                    print(f"     D->H Transfer: {result['cuda_timings']['d2h']:.3f} ms")
                if 'gflops' in result['cuda_timings']:
                    print(f"     Performance:   {result['cuda_timings']['gflops']:.2f} GFLOPS")
        
        self.results.append(result)
        return result
    
    def print_summary(self):
        """Print summary of all benchmarks"""
        print(f"\n\n{'='*70}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"{'Benchmark':<30} {'CUDA (s)':<12} {'MoonLight (s)':<15} {'Speedup'}")
        print("-" * 70)
        
        for r in self.results:
            cuda_time = f"{r['cuda_time']:.3f}" if r['cuda_time'] else "FAILED"
            moon_time = f"{r['moonlight_time']:.3f}" if r['moonlight_time'] else "FAILED"
            speedup = f"{r['speedup']:.2f}x" if r['speedup'] else "N/A"
            
            print(f"{r['name']:<30} {cuda_time:<12} {moon_time:<15} {speedup}")
        
        # Calculate averages
        valid_speedups = [r['speedup'] for r in self.results if r['speedup']]
        if valid_speedups:
            avg_speedup = sum(valid_speedups) / len(valid_speedups)
            print(f"\n{'Average Speedup:':<30} {'':<12} {'':<15} {avg_speedup:.2f}x")
            
            if avg_speedup >= 0.95:
                print(f"\n✅ MoonLight achieves {avg_speedup:.1%} of pure CUDA performance!")
            else:
                print(f"\n⚠️  MoonLight is {(1/avg_speedup):.2f}x slower than pure CUDA")
                print(f"    This is expected as transpiler optimizations are still being developed")

def main():
    print("="*70)
    print("MoonLight GPU Benchmark Suite")
    print("="*70)
    
    runner = GPUBenchmarkRunner()
    
    # Check CUDA availability
    if not runner.check_cuda_available():
        print("\n⚠️  CUDA not available. Cannot run GPU benchmarks.")
        print("    Install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads")
        return 1
    
    # Check for GPU
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            gpu_name = result.stdout.strip()
            print(f"✓ GPU detected: {gpu_name}\n")
        else:
            print("⚠️  No GPU detected via nvidia-smi\n")
    except FileNotFoundError:
        print("⚠️  nvidia-smi not found (GPU status unknown)\n")
    
    # Define benchmarks
    benchmark_dir = runner.gpu_bench_dir
    benchmarks = [
        ("Vector Addition (10M elements)", 
         benchmark_dir / "gpu_vector_add.gpu",
         benchmark_dir / "gpu_vector_add.cu"),
        
        ("Matrix Multiplication (1024x1024)",
         benchmark_dir / "gpu_matrix_mult.gpu",
         benchmark_dir / "gpu_matrix_mult.cu"),
    ]
    
    # Run each benchmark
    for name, moon_file, cuda_file in benchmarks:
        if moon_file.exists() and cuda_file.exists():
            runner.run_benchmark(name, moon_file, cuda_file)
        else:
            print(f"\n⚠️  Skipping {name}: files not found")
            if not moon_file.exists():
                print(f"    Missing: {moon_file}")
            if not cuda_file.exists():
                print(f"    Missing: {cuda_file}")
    
    # Print summary
    runner.print_summary()
    
    print(f"\n{'='*70}")
    print("Benchmarks Complete!")
    print(f"{'='*70}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

