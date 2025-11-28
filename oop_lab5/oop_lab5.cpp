#include <iostream>
#include <string>
using namespace std;

// Базовый класс
class Base {
public:
    Base() {
        cout << "Base constructor" << endl;
    }

    // Обычный метод (не виртуальный)
    void method1() {
        cout << "Base::method1()" << endl;
        this->method2(); // Вызов method2 из этого же класса
    }

    // Метод, который будет перекрываться
    void method2() {
        cout << "Base::method2()" << endl;
    }

    ~Base() {
        cout << "Base destructor" << endl;
    }
};

// Класс-потомок
class Desc : public Base {
public:
    Desc() {
        cout << "Desc constructor" << endl;
    }

    // Перекрываем method2 (не виртуальный!)
    void method2() {
        cout << "Desc::method2()" << endl;
    }

    ~Desc() {
        cout << "Desc destructor" << endl;
    }
};

void testOverriding() {
    cout << "=== Testing method overriding ===" << endl;

    cout << "\n1. Base object:" << endl;
    Base base;
    base.method1(); // Вызовет Base::method2()

    cout << "\n2. Desc object:" << endl;
    Desc desc;
    desc.method1(); // Вызовет Base::method2() (!)

    cout << "\n3. Direct method calls:" << endl;
    base.method2();  // Base::method2()
    desc.method2();  // Desc::method2()

    cout << "\n4. Through base pointer:" << endl;
    Base* basePtr = &desc;
    basePtr->method2(); // Base::method2() (!)
}

int main() {
    testOverriding();
    return 0;
}