#include <iostream>
#include <string>

using namespace std;

// Базовый класс для тестирования передачи объектов
class Base {
public:
    Base() {
        cout << "Base constructor" << endl;
    }

    // Конструктор копирования
    Base(const Base& obj) {
        cout << "Base copy constructor" << endl;
    }

    // Конструктор из указателя
    Base(Base* obj) {
        cout << "Base pointer constructor" << endl;
    }

    virtual ~Base() {
        cout << "Base destructor" << endl;
    }

    virtual void show() {
        cout << "Это объект Base" << endl;
    }
};

// Класс-потомок
class Desc : public Base {
public:
    Desc() {
        cout << "Desc constructor" << endl;
    }

    // Конструктор копирования
    Desc(const Desc& obj) {
        cout << "Desc copy constructor" << endl;
    }

    // Конструктор из указателя
    Desc(Desc* obj) {
        cout << "Desc pointer constructor" << endl;
    }

    virtual ~Desc() {
        cout << "Desc destructor" << endl;
    }

    virtual void show() override {
        cout << "Это объект Desc" << endl;
    }

    void specialMethod() {
        cout << "Специальный метод Desc" << endl;
    }
};

// Функции для тестирования передачи объектов
void func1(Base obj) {
    cout << "--- Внутри func1(Base obj) ---" << endl;
    obj.show();
    cout << "--- Выход из func1 ---" << endl;
}

void func2(Base* obj) {
    cout << "--- Внутри func2(Base* obj) ---" << endl;
    obj->show();

    // Попытка безопасного приведения
    Desc* descPtr = dynamic_cast<Desc*>(obj);
    if (descPtr) {
        cout << "Безопасное приведение удалось: ";
        descPtr->specialMethod();
    }
    else {
        cout << "Безопасное приведение не удалось" << endl;
    }
    cout << "--- Выход из func2 ---" << endl;
}

void func3(Base& obj) {
    cout << "--- Внутри func3(Base& obj) ---" << endl;
    obj.show();

    // Попытка безопасного приведения
    Desc* descPtr = dynamic_cast<Desc*>(&obj);
    if (descPtr) {
        cout << "Безопасное приведение удалось: ";
        descPtr->specialMethod();
    }
    else {
        cout << "Безопасное приведение не удалось" << endl;
    }
    cout << "--- Выход из func3 ---" << endl;
}

void testObjectPassing() {
    cout << "\n=== Тестирование передачи объектов в функции ===" << endl;

    cout << "\n--- Тест 1: Передача Base по значению ---" << endl;
    {
        Base base;
        cout << "До вызова func1:" << endl;
        func1(base);
        cout << "После вызова func1:" << endl;
    }

    cout << "\n--- Тест 2: Передача Base по указателю ---" << endl;
    {
        Base base;
        cout << "До вызова func2:" << endl;
        func2(&base);
        cout << "После вызова func2:" << endl;
    }

    cout << "\n--- Тест 3: Передача Base по ссылке ---" << endl;
    {
        Base base;
        cout << "До вызова func3:" << endl;
        func3(base);
        cout << "После вызова func3:" << endl;
    }

    cout << "\n--- Тест 4: Передача Desc по значению ---" << endl;
    {
        Desc desc;
        cout << "До вызова func1:" << endl;
        func1(desc); // Произойдет срезка (slicing)!
        cout << "После вызова func1:" << endl;
    }

    cout << "\n--- Тест 5: Передача Desc по указателю ---" << endl;
    {
        Desc desc;
        cout << "До вызова func2:" << endl;
        func2(&desc);
        cout << "После вызова func2:" << endl;
    }

    cout << "\n--- Тест 6: Передача Desc по ссылке ---" << endl;
    {
        Desc desc;
        cout << "До вызова func3:" << endl;
        func3(desc);
        cout << "После вызова func3:" << endl;
    }

    cout << "\n--- Тест 7: Динамическое создание объектов ---" << endl;
    {
        Base* basePtr = new Base();
        Desc* descPtr = new Desc();

        cout << "Вызов func2 с динамическим Base:" << endl;
        func2(basePtr);

        cout << "Вызов func2 с динамическим Desc:" << endl;
        func2(descPtr);

        cout << "Вызов func3 с динамическим Base:" << endl;
        func3(*basePtr);

        cout << "Вызов func3 с динамическим Desc:" << endl;
        func3(*descPtr);

        delete basePtr;
        delete descPtr;
    }
}

// Остальные классы и функции из предыдущих коммитов
class VirtualBase {
public:
    VirtualBase() {
        cout << "VirtualBase constructor" << endl;
    }

    void method1() {
        cout << "VirtualBase::method1()" << endl;
        this->method2();
    }

    virtual void method2() {
        cout << "VirtualBase::method2()" << endl;
    }

    virtual ~VirtualBase() {
        cout << "VirtualBase destructor" << endl;
    }
};

class VirtualDesc : public VirtualBase {
public:
    VirtualDesc() {
        cout << "VirtualDesc constructor" << endl;
    }

    virtual void method2() override {
        cout << "VirtualDesc::method2()" << endl;
    }

    virtual ~VirtualDesc() override {
        cout << "VirtualDesc destructor" << endl;
    }
};

void testVirtualMethods() {
    cout << "\n=== Тестирование виртуальных методов ===" << endl;

    VirtualBase vbase;
    vbase.method1();

    VirtualDesc vdesc;
    vdesc.method1();

    VirtualBase* vbasePtr = &vdesc;
    vbasePtr->method2();

    VirtualBase* ptr = new VirtualDesc();
    ptr->method1();
    delete ptr;
}

int main() {
    setlocale(LC_ALL, "ru");
    testVirtualMethods();
    testObjectPassing();
    return 0;
}