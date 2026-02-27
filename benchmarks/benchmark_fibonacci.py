# Python Benchmark: Fibonacci Recursivo
# Versão equivalente em Python puro

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def main():
    n = 35
    print(f"Calculando fibonacci({n})...")
    result = fibonacci(n)
    print(f"Resultado: {result}")

if __name__ == "__main__":
    main()

