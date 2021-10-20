#rectangles.py
#
#Rectangles
#   Creates rectangles which can be... manipulated. Deals with 
#   computer graphics elucidian coordinates. Order of points is
#   topleft (1), topright (2), bottomright(3), bottomleft (4).
#   Of course, when making a rectangle you dont have to conform
#   to this order, but it is how default rectangles are made and
#   other calculations. Note: Rectangles are just anything with
#   four (4) points, so more like a quadrilateral. Eh whatever.
#
#Edit History:
#   [001]   aw  12/21/20    Initial Creation of Coordinate,
#                           Vector, Line, and Rectangle classes. 

TOPLEFT = 0
TOPRIGHT = 1
BOTRIGHT = 2
BOTLEFT = 3

class Coordinate:
    def __init__(self, x: float = 0, y: float = 0,
                tuple_coord: tuple = None):
        self.x = x
        self.y = y
        if tuple_coord != None:
            self.x = tuple_coord[0]
            self.y = tuple_coord[1]

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return str(self)

    def to_tuple(self) -> tuple:
        '''
        Returns the Coordinate as a tuple.
        '''
        return (self.x,self.y)

    def distance(self, c: 'Coordinate' = None) -> float:
        '''
        Returns the distance between two coordinates, defaulting
        to the distance to the origin.
        '''
        x = 0
        y = 0
        if c != None:
            x = c.x
            y = c.y
        
        return ((self.x-x)**2+(self.y-y)**2)**(.5)

    def add(self, c: 'Coordinate', f: float = 1) -> None:
        '''
        Adds a coordinate to the current coordinate.
        '''
        self.x += c.x*f
        self.y += c.y*f

    def add_copy(self, c: 'Coordinate', f: float = 1) -> 'Coordinate':
        '''
        Adds a coordinate to the current one and then copies it.
        '''
        return Coordinate(self.x+c.x*f, self.y+c.y*f)

    def vector(self, c: 'Coordinate' = None) -> 'Vector':
        '''
        Returns the vector from the current coordinate to c.
        Defaults to moving towards the origin if no coordinate
        specified.
        '''
        coord = c if c != None else Coordinate(0,0)
        x = coord.x - self.x
        y = coord.y - self.y
        return Vector(x,y)

    def equals(self, c: 'Coordinate') -> bool:
        '''
        Takes another coordinate and returns whether the two 
        are equal.
        '''
        return self.x == c.x and self.y == c.y

    def copy(self) -> 'Coordinate':
        '''
        Returns a copy of the current Coordinate.
        '''
        return Coordinate(self.x, self.y)


class Vector(Coordinate):
    def __str__(self):
        return f'<{self.x}, {self.y}>'
    
    def unit_vector(self) -> 'Vector':
        '''
        Returns the unit vector of the vector.
        '''
        if self.x == 0 and self.y ==0:
            return self.copy()

        speed = self.speed()
        return Vector(self.x/speed,self.y/speed)

    def unit(self) -> 'Vector':
        '''
        The same as unit_vector()
        '''
        return self.unit_vector()

    def speed(self) -> float:
        '''
        Returns the speed of the vector.
        '''
        return self.distance()
        
    def equals(self, v: 'Vector') -> bool:
        '''
        Returns whether this vector is functionally equal to
        another vector
        '''
        #Unit vectors
        v1u = self.unit()
        v2u = v.unit()

        return (v1u.x == v2u.x and v1u.y == v2u.y) or \
               (-v1u.x == v2u.x and -v1u.y == v2u.y)

    def copy(self) -> 'Vector':
        '''
        Returns a copy of the vector.
        '''
        return Vector(self.x, self.y)


class Line:
    def __init__(self, c: Coordinate, v: Vector):
        self._point = c
        self._vector = v

    def __str__(self):
        return f'{self._point}, {self._vector}'

    def __repr__(self):
        return str(self)

    def slope(self) -> float:
        '''
        m. Returns None if the x component of the vector 
        is 0.
        '''
        if self._vector.x == 0:
            return None

        return self._vector.y/self._vector.x

    def intersects(self, l: 'Line') -> Coordinate:
        '''
        Takes another line and returns where the two intersect.
        Returns None if they are parallel (cring.)
        '''
        p1 = self._point
        v1 = self._vector
        p2 = l._point
        v2 = l._vector

        if v1.equals(v2):
            return None

        if p1.equals(p2):
            return p1.copy()

        x = None
        
        if self._vector.x == 0:
            x = self._point.x
        elif l._vector.x == 0:
            x = l._point.x

        if x == None:
            m1 = self.slope()
            m2 = l.slope()
            if m1 == m2:
                return None
            x = (p2.y-p1.y+m1*p1.x-m2*p2.x)/(m1-m2)

        y = None
        if self._vector.x == 0:
            m = l.slope()
            y = m*(x-p2.x)+p2.y
        else:
            m = self.slope()
            y = m*(x-p1.x)+p1.y
        return Coordinate(x, y)

    def y_intersect(self) -> Coordinate:
        '''
        Returns the y-intersect of the line :).
        '''
        return self.intersects(Line(Coordinate(0,0),Vector(0,1)))

    def x_intersect(self) -> Coordinate:
        '''
        Returns the x-intersect of the line.
        '''
        return self.intersects(Line(Coordinate(0,0),Vector(1,0)))

    def contains(self, point: Coordinate) -> bool:
        '''
        Returns whether or not the line contains a point, point.
        '''
        if self._vector.x == 0:
            return self._point.x == point.x

        if self._point.equals(point):
            return True

        m = self.slope()
        dist = point.x-self._point.x
        y = m*dist + self._point.y

        return point.y == y        

    def point(self) -> Coordinate:
        '''
        Returns a copy of the line's point.
        '''
        return self._point.copy()

    def vector(self) -> Vector:
        '''
        Returns a copy of the line's vector.
        '''
        return self._vector.copy()



class Rectangle:
    def __init__(self, verticies: list = None, 
                 topleft: (float, float) = (0,0),
                 width: float = None, height: float = None):
        self._lines = []
        vs = verticies
        if vs == None:
            vs = []
            vs.append(Coordinate(topleft[0],topleft[1]))
            vs.append(Coordinate(topleft[0]+width,topleft[1]))
            vs.append(Coordinate(topleft[0]+width,topleft[1]+height))
            vs.append(Coordinate(topleft[0],topleft[1]+height))

        if len(vs) != 4:
            raise IndexError
        for i in range(4):
            p1 = vs[i]
            p2 = vs[(i+1)%4]
            v = p1.vector(p2)
            self._lines.append(Line(p1.copy(),v))            

    def __str__(self):
        string = 'Rectangle\n'
        for i in self._lines:
            string += str(i) + '\n'

        return string.strip()

    def __repr__(self):
        return str(self)

    def points(self) -> [Coordinate]:
        '''
        Returns all the points in the rectangle.
        '''
        points = []
        for i in self._lines:
            points.append(i.point())

        return points

    def max_x(self) -> float:
        '''
        Returns maximum x value.
        '''
        return compare_all(self.points(), lambda x, y: x.x > y.x).x
    
    def min_x(self) -> float:
        '''
        Returns minimum x value.
        '''
        return compare_all(self.points(), lambda x, y: x.x < y.x).x
    
    def max_y(self) -> float:
        '''
        Returns maximum y value.
        '''
        return compare_all(self.points(), lambda x, y: x.y > y.y).y
    
    def min_y(self) -> float:
        '''
        Returns minimum y value.
        '''
        return compare_all(self.points(), lambda x, y: x.y < y.y).y

    def move(self, v: Vector, f: float = 1) -> None:
        '''
        Moves the rectangle by a vector by a factor of f.
        '''
        for i in self._lines:
            i._point.add(v,f)

    def contains(self, point: Coordinate) -> bool:
        '''
        Returns whether or not the rectangle contains the given
        point.
        '''
        intersections = 0

        for line in self._lines:
            if line.contains(point):
                return True

            p = line.point()
            if point.y >= max(p.y, p.y+line.vector().y) or \
               point.y < min(p.y, p.y+line.vector().y):
                continue

            if point.x < min(p.x, p.x+line.vector().x):
                continue

            intersection = line.intersects(Line(point, Vector(1,0)))
            if intersection == None:
                continue

            if intersection.x < point.x:
                intersections += 1

        return intersections%2 == 1

    def transform(self, point: Coordinate, rect: 'Rectangle') -> Coordinate:
        '''
        Takes a point (within the rectangle, returns None if not) and a new
        rectangle, and converts the point from being in this rectangle
        to being in rect. Yeah.
        '''
        if not self.contains(point):
            return None

        for i in range(len(self._lines)):
            if point.equals(self._lines[i].point()):
                return rect._lines[i].point().copy()

        topleft = self._lines[0].point()
        topleft_dist = point.distance(topleft)
        topleft_vector = topleft.vector(point)
        topleft_line = Line(topleft, topleft_vector)

        #Intersection w/ line created by topright and bottomright

        for i in range(len(self._lines)-2):
            line = self._lines[i+1]
            intersection = topleft_line.intersects(line)

            if intersection == None:
                continue

            dist = intersection.distance(line.point())
            dist_percent = dist/line.vector().speed()
            if dist_percent > 1:
                continue
            topleft_percent = topleft_dist/topleft.distance(intersection)

            topleft2 = rect._lines[0].point()
            line2 = rect._lines[i+1]
            point2 = Coordinate(line2.point().x+line2.vector().x*dist_percent,
                                line2.point().y+line2.vector().y*dist_percent)

            vector2 = topleft2.vector(point2)
            newpoint = Coordinate(topleft2.x+vector2.x*topleft_percent,
                                  topleft2.y+vector2.y*topleft_percent)

            return newpoint

        return None



def compare_all(items: list, f: 'function'):
    '''
    Compares a list of items by criterion described in f.
    '''
    best = None
    for i in items:
        if best == None or f(i, best):
            best = i

    return best


    

            
