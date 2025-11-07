#include <iostream>

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
};




int main()
{
    Point p;
    Point p2(1, 2);
    Point p3(p2);
    cout << "Hello World!\n";
}
