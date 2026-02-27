# Python Benchmark: Manipulação de Arrays

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
    return arr

def array_operations(n):
    # Criar array
    arr = []
    for i in range(n):
        arr.append(i)
    
    # Somar elementos
    total = 0
    for i in range(len(arr)):
        total = total + arr[i]
    
    return total

def main():
    print("Teste 1: Array Operations (10000 elementos)")
    result1 = array_operations(10000)
    print(f"Soma total: {result1}")
    
    print("Teste 2: Bubble Sort (1000 elementos)")
    arr = list(range(1000, 990, -1))
    sorted_arr = bubble_sort(arr)
    print(f"Primeiros 10: {sorted_arr[:10]}")

if __name__ == "__main__":
    main()

