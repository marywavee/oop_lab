#include <iostream>
#include <string>
#include <locale>
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

class TypeBase {
public:
    TypeBase() {
        cout << "TypeBase constructor" << endl;
    }

    // Метод для получения имени класса
    virtual string classname() const {
        return "TypeBase";
    }

    // Метод для проверки принадлежности классу
    virtual bool isA(const string& className) const {
        return className == "TypeBase";
    }

    virtual ~TypeBase() {
        cout << "TypeBase destructor" << endl;
    }
};

class TypeDesc : public TypeBase {
public:
    TypeDesc() {
        cout << "TypeDesc constructor" << endl;
    }

    virtual string classname() const override {
        return "TypeDesc";
    }

    virtual bool isA(const string& className) const override {
        return className == "TypeDesc" || TypeBase::isA(className);
    }

    virtual ~TypeDesc() {
        cout << "TypeDesc destructor" << endl;
    }
};

class TypeDesc2 : public TypeDesc {
public:
    TypeDesc2() {
        cout << "TypeDesc2 constructor" << endl;
    }

    virtual string classname() const override {
        return "TypeDesc2";
    }

    virtual bool isA(const string& className) const override {
        return className == "TypeDesc2" || TypeDesc::isA(className);
    }

    void specialMethod() {
        cout << "TypeDesc2::specialMethod() - специальный метод потомка" << endl;
    }

    virtual ~TypeDesc2() {
        cout << "TypeDesc2 destructor" << endl;
    }
};

void testOverriding() {
    cout << "=== Тестирование перекрытия методов ===" << endl;

    cout << "\n1. Объект Base:" << endl;
    Base base;
    base.method1(); // Вызовет Base::method2()

    cout << "\n2. Объект Desc:" << endl;
    Desc desc;
    desc.method1(); // Вызовет Base::method2() (!)

    cout << "\n3. Прямые вызовы методов:" << endl;
    base.method2();  // Base::method2()
    desc.method2();  // Desc::method2()

    cout << "\n4. Через указатель на базовый класс:" << endl;
    Base* basePtr = &desc;
    basePtr->method2(); // Base::method2() (!)
}

void testVirtualMethods() {
    cout << "\n=== Тестирование виртуальных методов ===" << endl;

    cout << "\n1. Объект VirtualBase:" << endl;
    VirtualBase vbase;
    vbase.method1(); // Вызовет VirtualBase::method2()

    cout << "\n2. Объект VirtualDesc:" << endl;
    VirtualDesc vdesc;
    vdesc.method1(); // Вызовет VirtualDesc::method2()!

    cout << "\n3. Через указатель на базовый класс:" << endl;
    VirtualBase* vbasePtr = &vdesc;
    vbasePtr->method2(); // VirtualDesc::method2()!

    cout << "\n4. Тест с динамическим выделением памяти:" << endl;
    VirtualBase* ptr = new VirtualDesc();
    ptr->method1(); // Вызовет VirtualDesc::method2()
    delete ptr;     // Вызовет правильные деструкторы благодаря виртуальности
}

void testTypeChecking() {
    cout << "\n=== Тестирование проверки типов ===" << endl;

    TypeBase base;
    TypeDesc desc;
    TypeDesc2 desc2;

    TypeBase* ptr1 = &base;
    TypeBase* ptr2 = &desc;
    TypeBase* ptr3 = &desc2;

    cout << "\n1. Использование метода classname():" << endl;
    cout << "ptr1->classname(): " << ptr1->classname() << endl;
    cout << "ptr2->classname(): " << ptr2->classname() << endl;
    cout << "ptr3->classname(): " << ptr3->classname() << endl;

    cout << "\n2. Использование метода isA():" << endl;
    cout << "ptr2->isA(\"TypeBase\"): " << ptr2->isA("TypeBase") << endl;
    cout << "ptr2->isA(\"TypeDesc\"): " << ptr2->isA("TypeDesc") << endl;
    cout << "ptr2->isA(\"TypeDesc2\"): " << ptr2->isA("TypeDesc2") << endl;

    cout << "\n3. Ручная проверка типа и приведение:" << endl;
    if (ptr2->isA("TypeDesc")) {
        TypeDesc* manualCast = (TypeDesc*)ptr2;
        cout << "Ручное приведение успешно" << endl;
    }

    cout << "\n4. Опасное приведение (без проверки):" << endl;
    // TypeDesc2* dangerousCast = (TypeDesc2*)ptr2; // Опасно
    // dangerousCast->specialMethod(); // Неопределенное поведение

    cout << "\n5. Безопасное приведение с проверкой:" << endl;
    if (ptr3->isA("TypeDesc2")) {
        TypeDesc2* safeCast = (TypeDesc2*)ptr3;
        safeCast->specialMethod(); // Безопасно
    }

    cout << "\n6. Использование dynamic_cast:" << endl;
    TypeDesc2* dynamicCast = dynamic_cast<TypeDesc2*>(ptr3);
    if (dynamicCast) {
        cout << "dynamic_cast успешен" << endl;
        dynamicCast->specialMethod();
    }
    else {
        cout << "dynamic_cast не удался" << endl;
    }

    // Попытка приведения неподходящего типа
    TypeDesc2* failedCast = dynamic_cast<TypeDesc2*>(ptr2);
    if (!failedCast) {
        cout << "dynamic_cast для неподходящего типа вернул nullptr" << endl;
    }
}

int main() {
    setlocale(LC_ALL, "ru");
    testOverriding();
    testVirtualMethods();
    testTypeChecking();
    return 0;
}