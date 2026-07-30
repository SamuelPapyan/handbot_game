#include <iostream>

void greeting(std::string name) {
    std::cout << "Hello, " << name << std::endl;
}

int sum(int a, int b) {
    return a + b;
}

int my_func(int a, int b) {
    return a + b;
}

int main() {
    // int a = 5;
    // double b = 2.45678;
    // float f = 2.34f;
    // char c = 'a';
    // std::string s = "hello";
    // // std::cout << "hello tumo" << std::endl;
    // std::cout << a << '\t' << b << '\t' << c << std::endl;

    // int state = 0;
    // switch (state) {
    //     case 0:
    //         std::cout << "xndzor" << std::endl;
    //         break;
    //     case 1:
    //         std::cout << "tandz" << std::endl;
    //         break;
    //     case 2:
    //         std::cout << "nur" << std::endl;
    //         break;
    //     case 3:
    //         std::cout << "elak" << std::endl;
    //         break;
    //     default:
    //         break;
    // }
    std::cout << my_func(10, 20) << std::endl;
    return 0;
}