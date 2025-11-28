#include <iostream>
#include <string>
#include <locale>
#include <memory>
using namespace std;

// Базовый класс для тестирования перекрытия методов
class Base {
public:
    Base() {
        cout << "Base constructor" << endl;
    }

    void method1() {
        cout << "Base::method1()" << endl;
        this->method2();
    }

    void method2() {
        cout << "Base::method2()" << endl;
    }

    ~Base() {
        cout << "Base destructor" << endl;
    }
};

// Класс-потомок для тестирования перекрытия методов
class Desc : public Base {
public:
    Desc() {
        cout << "Desc constructor" << endl;
    }

    void method2() {
        cout << "Desc::method2()" << endl;
    }

    ~Desc() {
        cout << "Desc destructor" << endl;
    }
};

// Базовый класс с виртуальными методами
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

// Потомок с переопределением виртуальных методов
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

// Классы для тестирования проверки типов
class TypeBase {
public:
    TypeBase() {
        cout << "TypeBase constructor" << endl;
    }

    virtual string classname() const {
        return "TypeBase";
    }

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

// Классы для тестирования передачи объектов в функции
class BaseParam {
public:
    BaseParam() {
        cout << "BaseParam constructor" << endl;
    }

    BaseParam(const BaseParam& obj) {
        cout << "BaseParam copy constructor" << endl;
    }

    BaseParam(BaseParam* obj) {
        cout << "BaseParam pointer constructor" << endl;
    }

    virtual ~BaseParam() {
        cout << "BaseParam destructor" << endl;
    }

    virtual void show() {
        cout << "Это объект BaseParam" << endl;
    }
};

class DescParam : public BaseParam {
public:
    DescParam() {
        cout << "DescParam constructor" << endl;
    }

    DescParam(const DescParam& obj) {
        cout << "DescParam copy constructor" << endl;
    }

    DescParam(DescParam* obj) {
        cout << "DescParam pointer constructor" << endl;
    }

    virtual ~DescParam() {
        cout << "DescParam destructor" << endl;
    }

    virtual void show() override {
        cout << "Это объект DescParam" << endl;
    }

    void specialMethod() {
        cout << "Специальный метод DescParam" << endl;
    }
};

// Функции для передачи объектов
void func1(BaseParam obj) {
    cout << "--- Внутри func1(BaseParam obj) ---" << endl;
    obj.show();
    cout << "--- Выход из func1 ---" << endl;
}

void func2(BaseParam* obj) {
    cout << "--- Внутри func2(BaseParam* obj) ---" << endl;
    obj->show();

    DescParam* descPtr = dynamic_cast<DescParam*>(obj);
    if (descPtr) {
        cout << "Безопасное приведение удалось: ";
        descPtr->specialMethod();
    }
    else {
        cout << "Безопасное приведение не удалось" << endl;
    }
    cout << "--- Выход из func2 ---" << endl;
}

void func3(BaseParam& obj) {
    cout << "--- Внутри func3(BaseParam& obj) ---" << endl;
    obj.show();

    DescParam* descPtr = dynamic_cast<DescParam*>(&obj);
    if (descPtr) {
        cout << "Безопасное приведение удалось: ";
        descPtr->specialMethod();
    }
    else {
        cout << "Безопасное приведение не удалось" << endl;
    }
    cout << "--- Выход из func3 ---" << endl;
}

// Функции для возврата объектов
BaseParam func1_return() {
    cout << "--- Внутри func1_return() ---" << endl;
    BaseParam localObj;
    localObj.show();
    cout << "--- Возврат из func1_return ---" << endl;
    return localObj;
}

BaseParam* func2_return() {
    cout << "--- Внутри func2_return() ---" << endl;
    static BaseParam localObj;
    localObj.show();
    cout << "--- Возврат из func2_return ---" << endl;
    return &localObj;
}

BaseParam& func3_return() {
    cout << "--- Внутри func3_return() ---" << endl;
    static BaseParam localObj;
    localObj.show();
    cout << "--- Возврат из func3_return ---" << endl;
    return localObj;
}

BaseParam func4_return() {
    cout << "--- Внутри func4_return() ---" << endl;
    BaseParam* dynamicObj = new BaseParam();
    dynamicObj->show();
    cout << "--- Возврат из func4_return ---" << endl;
    return *dynamicObj;
}

BaseParam* func5_return() {
    cout << "--- Внутри func5_return() ---" << endl;
    BaseParam* dynamicObj = new BaseParam();
    dynamicObj->show();
    cout << "--- Возврат из func5_return ---" << endl;
    return dynamicObj;
}

BaseParam& func6_return() {
    cout << "--- Внутри func6_return() ---" << endl;
    BaseParam* dynamicObj = new BaseParam();
    dynamicObj->show();
    cout << "--- Возврат из func6_return ---" << endl;
    return *dynamicObj;
}

// Классы для умных указателей
class BaseSmart {
public:
    BaseSmart() {
        cout << "BaseSmart constructor" << endl;
    }

    virtual ~BaseSmart() {
        cout << "BaseSmart destructor" << endl;
    }

    virtual void show() {
        cout << "Это объект BaseSmart" << endl;
    }
};

class DescSmart : public BaseSmart {
public:
    DescSmart() {
        cout << "DescSmart constructor" << endl;
    }

    virtual ~DescSmart() {
        cout << "DescSmart destructor" << endl;
    }

    virtual void show() override {
        cout << "Это объект DescSmart" << endl;
    }

    void specialMethod() {
        cout << "Специальный метод DescSmart" << endl;
    }
};

// Функции для умных указателей
unique_ptr<BaseSmart> createUniqueBase() {
    cout << "--- Создание unique_ptr в функции ---" << endl;
    return make_unique<BaseSmart>();
}

shared_ptr<BaseSmart> createSharedBase() {
    cout << "--- Создание shared_ptr в функции ---" << endl;
    return make_shared<BaseSmart>();
}

void takeUniquePtr(unique_ptr<BaseSmart> ptr) {
    cout << "--- Внутри takeUniquePtr ---" << endl;
    ptr->show();
    cout << "--- Выход из takeUniquePtr ---" << endl;
}

void takeSharedPtr(shared_ptr<BaseSmart> ptr) {
    cout << "--- Внутри takeSharedPtr ---" << endl;
    ptr->show();
    cout << "Счетчик ссылок: " << ptr.use_count() << endl;
    cout << "--- Выход из takeSharedPtr ---" << endl;
}

void testOverriding() {
    cout << "\n=== 1. ТЕСТИРОВАНИЕ ПЕРЕКРЫТИЯ МЕТОДОВ ===" << endl;

    cout << "\n1. Объект Base:" << endl;
    Base base;
    base.method1();

    cout << "\n2. Объект Desc:" << endl;
    Desc desc;
    desc.method1();

    cout << "\n3. Прямые вызовы методов:" << endl;
    base.method2();
    desc.method2();

    cout << "\n4. Через указатель на базовый класс:" << endl;
    Base* basePtr = &desc;
    basePtr->method2();
}

void testVirtualMethods() {
    cout << "\n=== 2. ТЕСТИРОВАНИЕ ВИРТУАЛЬНЫХ МЕТОДОВ ===" << endl;

    cout << "\n1. Объект VirtualBase:" << endl;
    VirtualBase vbase;
    vbase.method1();

    cout << "\n2. Объект VirtualDesc:" << endl;
    VirtualDesc vdesc;
    vdesc.method1();

    cout << "\n3. Через указатель на базовый класс:" << endl;
    VirtualBase* vbasePtr = &vdesc;
    vbasePtr->method2();

    cout << "\n4. Тест с динамическим выделением памяти:" << endl;
    VirtualBase* ptr = new VirtualDesc();
    ptr->method1();
    delete ptr;
}

void testTypeChecking() {
    cout << "\n=== 3. ТЕСТИРОВАНИЕ ПРОВЕРКИ ТИПОВ ===" << endl;

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

    cout << "\n4. Безопасное приведение с проверкой:" << endl;
    if (ptr3->isA("TypeDesc2")) {
        TypeDesc2* safeCast = (TypeDesc2*)ptr3;
        safeCast->specialMethod();
    }

    cout << "\n5. Использование dynamic_cast:" << endl;
    TypeDesc2* dynamicCast = dynamic_cast<TypeDesc2*>(ptr3);
    if (dynamicCast) {
        cout << "dynamic_cast успешен" << endl;
        dynamicCast->specialMethod();
    }

    TypeDesc2* failedCast = dynamic_cast<TypeDesc2*>(ptr2);
    if (!failedCast) {
        cout << "dynamic_cast для неподходящего типа вернул nullptr" << endl;
    }
}

void testObjectPassing() {
    cout << "\n=== 4. ТЕСТИРОВАНИЕ ПЕРЕДАЧИ ОБЪЕКТОВ В ФУНКЦИИ ===" << endl;

    cout << "\n1. Передача BaseParam по значению:" << endl;
    BaseParam base1;
    func1(base1);

    cout << "\n2. Передача BaseParam по указателю:" << endl;
    func2(&base1);

    cout << "\n3. Передача BaseParam по ссылке:" << endl;
    func3(base1);

    cout << "\n4. Передача DescParam по значению (срезка!):" << endl;
    DescParam desc1;
    func1(desc1);

    cout << "\n5. Передача DescParam по указателю:" << endl;
    func2(&desc1);

    cout << "\n6. Передача DescParam по ссылке:" << endl;
    func3(desc1);
}

void testObjectReturn() {
    cout << "\n=== 5. ТЕСТИРОВАНИЕ ВОЗВРАТА ОБЪЕКТОВ ИЗ ФУНКЦИЙ ===" << endl;

    cout << "\n1. func1_return() - возврат по значению:" << endl;
    BaseParam result1 = func1_return();

    cout << "\n2. func2_return() - возврат указателя:" << endl;
    BaseParam* result2 = func2_return();

    cout << "\n3. func3_return() - возврат ссылки:" << endl;
    BaseParam& result3 = func3_return();

    cout << "\n4. func5_return() - возврат динамического указателя:" << endl;
    BaseParam* result5 = func5_return();
    delete result5;
}

void testSmartPointers() {
    cout << "\n=== 6. ТЕСТИРОВАНИЕ УМНЫХ УКАЗАТЕЛЕЙ ===" << endl;

    cout << "\n1. unique_ptr:" << endl;
    unique_ptr<BaseSmart> uptr1 = make_unique<BaseSmart>();
    uptr1->show();

    cout << "\n2. shared_ptr:" << endl;
    shared_ptr<BaseSmart> sptr1 = make_shared<BaseSmart>();
    sptr1->show();
    cout << "Счетчик ссылок: " << sptr1.use_count() << endl;

    cout << "\n3. Полиморфизм с умными указателями:" << endl;
    unique_ptr<BaseSmart> uptr2 = make_unique<DescSmart>();
    uptr2->show();

    cout << "\n4. Передача unique_ptr в функцию:" << endl;
    takeUniquePtr(move(uptr2));

    cout << "\n5. Передача shared_ptr в функцию:" << endl;
    takeSharedPtr(sptr1);
    cout << "Счетчик ссылок после функции: " << sptr1.use_count() << endl;
}


int main() {
    setlocale(LC_ALL, "ru");
    testOverriding();
    testVirtualMethods();
    testTypeChecking();
    testObjectPassing();
    testObjectReturn();
    testSmartPointers();
    return 0;
}