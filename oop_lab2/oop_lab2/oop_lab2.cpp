#include <iostream>
#include <windows.h>

using namespace std;

class Point {
public:
    int x, y;
    Point() { // default constructor
        cout << "[Point] default\n";
        x = 0;
        y = 0;
    }
    Point(int x,int y) { //constructor with parametr
        cout << "[Point] const. param.\n";
        this -> x = x;
        this -> y = y;
    }
    Point(const Point &p) { //copy constructor
        cout << "[Point] copy\n";
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



int main()
{
    setlocale(LC_ALL, "ru");
    test();

}
