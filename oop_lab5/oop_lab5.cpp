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

class VirtualBase {
public:
    VirtualBase() {
        cout << "VirtualBase constructor" << endl;
    }

    void method1() {
        cout << "VirtualBase::method1()" << endl;
        this->method2(); // Вызов виртуального method2
    }

    // Виртуальный метод
    virtual void method2() {
        cout << "VirtualBase::method2()" << endl;
    }

    // Виртуальный деструктор
    virtual ~VirtualBase() {
        cout << "VirtualBase destructor" << endl;
    }
};

class VirtualDesc : public VirtualBase {
public:
    VirtualDesc() {
        cout << "VirtualDesc constructor" << endl;
    }

    // Переопределяем виртуальный метод
    virtual void method2() override {
        cout << "VirtualDesc::method2()" << endl;
    }

    virtual ~VirtualDesc() override {
        cout << "VirtualDesc destructor" << endl;
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

void testVirtualMethods() {
    cout << "\n=== Testing virtual methods ===" << endl;

    cout << "\n1. VirtualBase object:" << endl;
    VirtualBase vbase;
    vbase.method1(); // Вызовет VirtualBase::method2()

    cout << "\n2. VirtualDesc object:" << endl;
    VirtualDesc vdesc;
    vdesc.method1(); // Вызовет VirtualDesc::method2()!

    cout << "\n3. Through base pointer:" << endl;
    VirtualBase* vbasePtr = &vdesc;
    vbasePtr->method2(); // VirtualDesc::method2()!

    cout << "\n4. Dynamic allocation test:" << endl;
    VirtualBase* ptr = new VirtualDesc();
    ptr->method1(); // Вызовет VirtualDesc::method2()
    delete ptr;     // Вызовет правильные деструкторы благодаря виртуальности
}

int main() {
    testOverriding();
    testVirtualMethods();
    return 0;
}