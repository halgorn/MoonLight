#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int soma(int a, int b) {
    return (a + b);
}


int main() {
    int x = 10;
    float y = 3.14;
    const char* nome = "Bruno";
    int flag = True;
    int nulo = 0;
    int resultado = soma(5, 10);
    printf("%d\n", resultado);
    auto dobro = [=](int x) -> int { return (x * 2); };
    printf("%d\n", dobro(4));
    return 0;
}
