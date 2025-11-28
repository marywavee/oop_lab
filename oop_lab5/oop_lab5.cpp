#include <iostream>
#include <string>
#include <locale>
using namespace std;

// Базовый класс для тестирования возврата объектов
class Base {
public:
    Base() {
        cout << "Base constructor" << endl;
    }

    Base(const Base& obj) {
        cout << "Base copy constructor" << endl;
    }

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

    Desc(const Desc& obj) {
        cout << "Desc copy constructor" << endl;
    }

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

// Функции, возвращающие статические объекты
Base func1() {
    cout << "--- Внутри func1() ---" << endl;
    Base localObj;
    localObj.show();
    cout << "--- Возврат из func1 ---" << endl;
    return localObj;
}

Base* func2() {
    cout << "--- Внутри func2() ---" << endl;
    static Base localObj; // static чтобы объект не уничтожался при выходе
    localObj.show();
    cout << "--- Возврат из func2 ---" << endl;
    return &localObj;
}

Base& func3() {
    cout << "--- Внутри func3() ---" << endl;
    static Base localObj; // static чтобы объект не уничтожался при выходе
    localObj.show();
    cout << "--- Возврат из func3 ---" << endl;
    return localObj;
}

// Функции, возвращающие динамические объекты
Base func4() {
    cout << "--- Внутри func4() ---" << endl;
    Base* dynamicObj = new Base();
    dynamicObj->show();
    cout << "--- Возврат из func4 ---" << endl;
    return *dynamicObj; // ОПАСНО! Утечка памяти!
}

Base* func5() {
    cout << "--- Внутри func5() ---" << endl;
    Base* dynamicObj = new Base();
    dynamicObj->show();
    cout << "--- Возврат из func5 ---" << endl;
    return dynamicObj;
}

Base& func6() {
    cout << "--- Внутри func6() ---" << endl;
    Base* dynamicObj = new Base();
    dynamicObj->show();
    cout << "--- Возврат из func6 ---" << endl;
    return *dynamicObj; // ОПАСНО! Нужно запомнить указатель для удаления!
}

void testObjectReturn() {
    cout << "\n=== Тестирование возврата объектов из функций ===" << endl;

    cout << "\n--- Функции со статическими объектами ---" << endl;

    cout << "\n1. func1() - возврат по значению:" << endl;
    {
        Base result = func1();
        cout << "После получения результата func1:" << endl;
        result.show();
    }

    cout << "\n2. func2() - возврат указателя:" << endl;
    {
        Base* result = func2();
        cout << "После получения результата func2:" << endl;
        result->show();
    }

    cout << "\n3. func3() - возврат ссылки:" << endl;
    {
        Base& result = func3();
        cout << "После получения результата func3:" << endl;
        result.show();
    }

    cout << "\n--- Функции с динамическими объектами ---" << endl;

    cout << "\n4. func4() - возврат по значению (опасно!):" << endl;
    {
        Base result = func4();
        cout << "После получения результата func4:" << endl;
        result.show();
        // Утечка памяти! Динамический объект не удален
    }

    cout << "\n5. func5() - возврат указателя (правильно):" << endl;
    {
        Base* result = func5();
        cout << "После получения результата func5:" << endl;
        result->show();
        delete result; // Важно удалить!
        cout << "После delete result:" << endl;
    }

    cout << "\n6. func6() - возврат ссылки (опасно!):" << endl;
    {
        Base& result = func6();
        cout << "После получения результата func6:" << endl;
        result.show();
        // Утечка памяти! Нет способа удалить объект
    }

    cout << "\n--- Дополнительные тесты ---" << endl;

    cout << "\n7. Многократный вызов func2 (static):" << endl;
    {
        Base* result1 = func2();
        Base* result2 = func2();
        cout << "result1 == result2: " << (result1 == result2) << " (один и тот же static объект)" << endl;
    }

    cout << "\n8. Многократный вызов func5 (dynamic):" << endl;
    {
        Base* result1 = func5();
        Base* result2 = func5();
        cout << "result1 == result2: " << (result1 == result2) << " (разные динамические объекты)" << endl;
        delete result1;
        delete result2;
    }
}

// Функции для тестирования передачи объектов (из предыдущего коммита)
void func1_param(Base obj) {
    cout << "--- Внутри func1_param(Base obj) ---" << endl;
    obj.show();
}

void func2_param(Base* obj) {
    cout << "--- Внутри func2_param(Base* obj) ---" << endl;
    obj->show();
}

void func3_param(Base& obj) {
    cout << "--- Внутри func3_param(Base& obj) ---" << endl;
    obj.show();
}

void testObjectPassing() {
    cout << "\n=== Тестирование передачи объектов в функции ===" << endl;

    cout << "\nПередача Base по значению:" << endl;
    Base base;
    func1_param(base);

    cout << "\nПередача Base по указателю:" << endl;
    func2_param(&base);

    cout << "\nПередача Base по ссылке:" << endl;
    func3_param(base);

    cout << "\nПередача Desc по значению (срезка!):" << endl;
    Desc desc;
    func1_param(desc);
}

int main() {
    setlocale(LC_ALL, "ru");
    testObjectPassing();
    testObjectReturn();
    return 0;
}