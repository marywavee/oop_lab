#include <iostream>
#include <windows.h>

using namespace std;

class Point {
public:
    int x, y;
    Point() { // default constructor
        cout << "[Point] Статичический\n";
        x = 0;
        y = 0;
    }
    Point(int x,int y) { //constructor with parametr
        cout << "[Point] С параметрами\n";
        this -> x = x;
        this -> y = y;
    }
    Point(const Point &p) { //copy constructor
        cout << "[Point] Копирования\n";
        x = p.x;
        y = p.y;
    }
    ~Point() { cout << "[~Point]\n"; }


    void setX(int x) { this->x = x; } //access metod
    void setY(int y) { this->y = y; }
    int getX() const { return x; }
    int getY() const { return y; }

  
    void print() const { //metod print
        cout << "Point: x=" << x << ", y=" << y << endl;
    }
};

void test() {

    //static
    cout << "1. Статическое создание:" << endl;
    Point p1;
    p1.print();

    //static + param
    cout << "\n2. Статическое создание с параметрами:" << endl;
    Point p2(10, 20);
    p2.print();

    //dinamic
    cout << "\n3. Динамическое создание:" << endl;
    Point* p3 = new Point(30, 40);
    p3->print();

    // copy constructor
    cout << "\n4. Конструктор копирования:" << endl;
    Point p4(p2);
    p4.print();

    // delete dinamic memory
    cout << "\n5. Удаление динамического объекта:" << endl;
    delete p3;
}


class ColoredPoint : public Point {
private:
    string color;
public:
    ColoredPoint() : Point() {
        color = "black";
        cout << "Вызван конструктор ColoredPoint() без параметров\n";
    }
    ColoredPoint(int x, int y, const string& color) : Point(x, y) {
        this->color = color;
        cout << "Вызван конструктор ColoredPoint(int x, int y, string color)\n";
    }
    ColoredPoint(const ColoredPoint& other) : Point(other) {
        this->color = other.color;
        cout << "Вызван конструктор копирования ColoredPoint(const ColoredPoint& other)\n";
    }
    ~ColoredPoint() {
        cout << "~ColoredPoint()\n";
    }
    void setColor(const string& color) { this->color = color; }
    string getColor() const { return color; }

    void print() const { // переопределенный метод
        cout << "ColoredPoint: x=" << getX() << ", y=" << getY() << ", color=" << color; 
    }

    void printBase() const {
        Point::print();  
    }
 };

void testInheritance() {
    cout << "\n\n\n";
    cout << "1. Создание ColoredPoint статически:\n";
    ColoredPoint cp1(5, 15, "red");
    cp1.print();

    cout << "\n2. Создание ColoredPoint динамически:\n";
    ColoredPoint* cp2 = new ColoredPoint(25, 35, "blue");
    cp2->print();

    cout << "\n3. Вызов методов:";
    cp2->print();        
    cp2->printBase();    

    cout << "\n4. Указатель базового класса на объект наследника:\n";
    Point* basePtr = new ColoredPoint(45, 55, "green");
    basePtr->print();    

    delete cp2;
    delete basePtr; //deleting param
}


class Line {
private:
    Point start;    
    Point* end;     

public:
    Line(int x1, int y1, int x2, int y2) : start(x1, y1) {
        end = new Point(x2, y2);
        cout << "Вызван конструктор Line(int x1, int y1, int x2, int y2)\n";
    }

    Line(const Line& other) : start(other.start) {
        end = new Point(*(other.end));
        cout << "Вызван конструктор копирования Line(const Line& other)\n";
    }

    ~Line() {
        cout << "~Line()\n";
        delete end;  // освобождаем динамическую память
    }

    void print() const {
        cout << "Line: ";
        cout << "start(" << start.getX() << "," << start.getY() << "), ";
        cout << "end(" << end->getX() << "," << end->getY() << ")\n";
    }


    void setStart(int x, int y) {
        start.setX(x);
        start.setY(y);
    }

    void setEnd(int x, int y) {
        end->setX(x);
        end->setY(y);
    }
};

void testComposition() {
    cout << "\n\n\n";

    cout << "1. Создание Line с композицией:\n";
    Line line1(1, 1, 10, 10);
    line1.print();

    cout << "\n2. Конструктор копирования Line:\n";
    Line line2 = line1;
    line2.print();

    cout << "\n3. Изменение точек в line2:\n";
    line2.setStart(2, 2);
    line2.setEnd(20, 20);
    cout << "После изменения line2:\n";
    line2.print();
}

void testAssignment() { // Присваивание и копирование

    cout << "\n\n\n";
    cout << "1. Копирование объектов:\n";
    Point a(1, 2);
    Point b(3, 4);
    cout << "До присваивания:\n";
    a.print();
    b.print();

    a = b;  // присваивание
    cout << "После a = b:\n";
    a.print();
    b.print();

    cout << "\n2. Изменение после присваивания:\n";
    a.setX(100);
    b.setY(200);
    cout << "После изменения:\n";
    a.print();
    b.print();


    cout << "\n3. Копирование указателей:\n";
    Point* ptr1 = new Point(5, 6);
    Point* ptr2 = new Point(7, 8);

    cout << "До присваивания указателей:\n";
    ptr1->print();
    ptr2->print();

    ptr1 = ptr2;  // присваивание указателей
    cout << "После ptr1 = ptr2:\n";
    ptr1->print();
    ptr2->print();

    cout << "\n4. Изменение через указатели:\n";
    ptr1->setX(300);
    cout << "После ptr1->setX(300):\n";
    ptr1->print();
    ptr2->print();

    delete ptr2;
}

int main()
{
    setlocale(LC_ALL, "ru");
    test();
    testInheritance();
    testComposition();


}
