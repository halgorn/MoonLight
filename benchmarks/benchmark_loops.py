# Python Benchmark: Loops e Operações Matemáticas

def sum_of_squares(n):
    total = 0
    for i in range(n):
        total = total + i * i
    return total

def nested_loops(n):
    sum_val = 0
    for i in range(n):
        for j in range(n):
            sum_val = sum_val + i * j
    return sum_val

def main():
    n = 10000
    
    print("Teste 1: Sum of Squares")
    result1 = sum_of_squares(n)
    print(f"Resultado: {result1}")
    
    print("Teste 2: Nested Loops (1000x1000)")
    result2 = nested_loops(1000)
    print(f"Resultado: {result2}")

if __name__ == "__main__":
    main()

