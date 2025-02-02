#include <iostream>
using namespace std;

int main() {
    int x = 10;
    int y = 5;
    int z = 0;
    if (x > y) {
        int z = (x - y);
    } else {
        int z = (y - x);
    }
    while (x > 0) {
        int x = (x - 1);
    }
    for (int i = 0; (i < 10); int i = (i + 1);) {
        int y = (y + 1);
    }
    printf("%d\n", z);

    return 0;
}