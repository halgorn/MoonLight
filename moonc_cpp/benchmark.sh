#!/bin/bash
# Benchmark MoonLight 100% Independente
# Linux/macOS Script

MOONC="./build/moonc"
TEST_FILE="test_vector_add.gpu"

# Verificar se moonc existe
if [ ! -f "$MOONC" ]; then
    echo "Erro: moonc não encontrado. Compile primeiro!"
    echo "Execute: cd build && cmake .. && make"
    exit 1
fi

# Verificar se arquivo de teste existe
if [ ! -f "$TEST_FILE" ]; then
    echo "Erro: $TEST_FILE não encontrado!"
    exit 1
fi

echo "=== MoonLight Performance Test ==="
echo "Compilador: $MOONC"
echo "Teste: $TEST_FILE"
echo ""

# Teste 1: Apenas gerar PTX
echo "Teste 1: Geração de PTX..."
START=$(date +%s.%N)
$MOONC $TEST_FILE -S -o test.ptx 2>&1 > /dev/null
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "  Tempo: ${ELAPSED} segundos"
if [ -f "test.ptx" ]; then
    PTX_SIZE=$(stat -f%z test.ptx 2>/dev/null || stat -c%s test.ptx 2>/dev/null)
    echo "  PTX gerado: ${PTX_SIZE} bytes"
fi

# Teste 2: Compilar e executar (primeira vez)
echo ""
echo "Teste 2: Compilação + Execução (primeira vez)..."
START=$(date +%s.%N)
$MOONC -r $TEST_FILE -v 2>&1 > /dev/null
END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
echo "  Tempo: ${ELAPSED} segundos"

# Teste 3: Múltiplas execuções
echo ""
echo "Teste 3: Múltiplas execuções (5x)..."
TIMES=()
for i in {1..5}; do
    START=$(date +%s.%N)
    $MOONC -r $TEST_FILE 2>&1 > /dev/null
    END=$(date +%s.%N)
    ELAPSED=$(echo "$END - $START" | bc)
    TIMES+=($ELAPSED)
    printf "  Execução %d: %.3f segundos\n" $i $ELAPSED
done

# Calcular estatísticas
SUM=0
MIN=${TIMES[0]}
MAX=${TIMES[0]}
for t in "${TIMES[@]}"; do
    SUM=$(echo "$SUM + $t" | bc)
    if (( $(echo "$t < $MIN" | bc -l) )); then
        MIN=$t
    fi
    if (( $(echo "$t > $MAX" | bc -l) )); then
        MAX=$t
    fi
done
AVG=$(echo "scale=3; $SUM / ${#TIMES[@]}" | bc)
echo "  Média: ${AVG} segundos"
echo "  Min: ${MIN} segundos"
echo "  Max: ${MAX} segundos"

echo ""
echo "=== Teste Concluído ==="

