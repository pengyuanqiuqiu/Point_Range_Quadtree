from math import sqrt
from random import uniform

class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

class Box():
    def __init__(self, center, half_size):
        self.center = center 
        self.half_size = float(half_size)
    def contains_point(self, point):
        left_bound = self.center.x - self.half_size
        right_bound = self.center.x + self.half_size
        bottom_bound = self.center.y - self.half_size
        top_bound = self.center.y + self.half_size
        if (point.x >= left_bound and point.x <= right_bound
                and point.y >=bottom_bound and point.y <=top_bound):
            return True
        return False
    def intersect(self, other_box):
        # self bottom left corner
        aX1 = self.center.x - self.half_size
        aY1 = self.center.y - self.half_size
        # self top right corner
        aX2 = self.center.x + self.half_size
        aY2 = self.center.y + self.half_size
        #print "corner of self: (%s, %s) and (%s,%s)" % (aX1, aY1, aX2, aY2)
        
        # other_box bottom left corner
        bX1 = other_box.center.x - other_box.half_size
        bY1 = other_box.center.y - other_box.half_size
        # other_box top right corner
        bX2 = other_box.center.x + other_box.half_size
        bY2 = other_box.center.y + other_box.half_size

        #print "corner of other: (%s, %s) and (%s,%s)" % (bX1, bY1, bX2, bY2)
        #print "aX1 < bx2: %s" % ( aX1 < bX2)
        #print "aX2 > bx1: %s" % ( aX2 > bX1)
        #print "aY1 < bY2: %s" % ( aY1 < bY2)
        #print "aY2 > bY1: %s" % ( aY2 > bY1)

        if aX1 < bX2 and aX2 > bX1 and aY1 < bY2 and aY2 > bY1:
            return True
        return False

class PRQuadTree():
    QT_NODE_CAPACITY = 1

    def __init__(self, box):
        self.box = box
        self.points = []
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

    def insert(self, point):
        if not self.box.contains_point(point):
            # point does not belong to this box
            return False
        if len(self.points) < self.QT_NODE_CAPACITY:
            self.points.append(point)
            return True
        
        if self.nw == None:
            self._subdivide()

        if self.nw.insert(point):
            return True
        if self.ne.insert(point):
            return True
        if self.sw.insert(point):
            return True
        if self.se.insert(point):
            return True

    def query_range(self, rng):
        final_points = []
        if not self.box.intersect(rng):
            return final_points
        for point in self.points:
            if rng.contains_point(point):
                final_points.append(point)
        if self.nw == None:
            return final_points
        
        nw_q = self.nw.query_range(rng)
        if len(nw_q) > 0:
            final_points.extend(nw_q)
        ne_q = self.ne.query_range(rng)
        if len(ne_q) > 0:
            final_points.extend(ne_q)
        sw_q = self.sw.query_range(rng)
        if len(sw_q) > 0:
            final_points.extend(sw_q)
        se_q = self.se.query_range(rng)
        if len(se_q) > 0:
            final_points.extend(se_q)

        return final_points

    def query_k_nearest(self, point, k):

        def _sort_key(p):
            return sqrt( pow(point.x-p.x, 2) + pow(p.y-point.y,2))
        nearby = None
        for i in range(1,20):
            rng = Box(point, pow(2, i))
            nearby = self.query_range(rng)
            if len(nearby) >= k:
                break
        return sorted(nearby, key=_sort_key)[:k]
            
    
    def _subdivide(self):
        hs = self.box.half_size / 2

        nw_x = self.box.center.x - hs
        nw_y = self.box.center.y + hs
        nw_center = Point(nw_x, nw_y)
        nw_box = Box(nw_center, hs)
        self.nw = PRQuadTree(nw_box)
        #print "nw: %s" % nw_center

        ne_x = self.box.center.x + hs
        ne_y = self.box.center.y + hs
        ne_center = Point(ne_x, ne_y)
        ne_box = Box(ne_center, hs)
        self.ne = PRQuadTree(ne_box)
        #print "ne: %s" % ne_center

        sw_x = self.box.center.x - hs
        sw_y = self.box.center.y - hs
        sw_center = Point(sw_x, sw_y)
        sw_box = Box(sw_center, hs)
        self.sw = PRQuadTree(sw_box)
        #print "sw: %s" % sw_center

        se_x = self.box.center.x + hs
        se_y = self.box.center.y - hs
        se_center = Point(se_x, se_y)
        se_box = Box(se_center, hs)
        self.se = PRQuadTree(se_box)
        #print "se: %s" % se_center

    def print_all_points(self, root):
        out = ""
        for point in root.points:
            out += "%s, " % point
        if root.nw != None:
            out += self.print_all_points(root.nw)
        if root.ne != None:
            out += self.print_all_points(root.ne)
        if root.sw != None:
            out += self.print_all_points(root.sw)
        if root.se != None:
            out += self.print_all_points(root.se)
        return out

    def __str__(self):
        def _print_msg(loc, name):
            if len(loc.points) == 0:
                return "%s point: no points\n" % (name)
            else:
                return "%s point: %s\n" % (name, loc.points[0])

        tree = ""
        if self.nw != None:
            tree += _print_msg(self.nw, "nw")
        if self.ne != None:
            tree += _print_msg(self.ne, "ne")
        if self.sw != None:
            tree += _print_msg(self.sw, "sw")
        if self.se != None:
            tree += _print_msg(self.se, "se")
        return tree

def test():
    x = Point(2.3,2.5)
    b = Box(Point(5,5), 50)
    b2 = Box(Point(50,50), 50)

    print b.intersect(b2)
    qt = PRQuadTree(b2)

    qt.insert(Point(1,1))
    qt.insert(Point(4,14))
    qt.insert(Point(14,14))
    qt.insert(Point(16,4))
    qt.insert(Point(1,2))
    qt.insert(Point(2,3))
    qt.insert(Point(5,3))
    
    for x in range(100):
        qt.insert(Point(uniform(0.0,100.0), uniform(0.0,100.0)))

    #print qt.print_all_points(qt)

    pt = Point(2,2)
    nearby = qt.query_k_nearest(pt, 20)
    c = 1
    for point in nearby:
        print "%s: %s" % (c, point)
        c+=1
test()
