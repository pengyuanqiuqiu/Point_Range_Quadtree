'''
Implementation of a Point Range Quadtree.

Author: Pawel Szczurko
'''

from math import sqrt
from random import uniform

class Point():
    '''
    Represents an (x,y) coordinate point on a grid.
    '''

    def __init__(self, x, y):
        '''
        Constructs a coordinate Point.

        Args:
            x: x-position
            y: y-position
        '''
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        '''
        Overwritting the default to string method
        of the Point class.
        '''
        return "(%s, %s)" % (self.x, self.y)

class Box():
    '''
    Class defining a square on the coordinate system via a center point and
    half of square width.
    '''

    def __init__(self, center, half_size):
        '''
        Construct a Box object. 

        Args:
            center: a Point type specifying the center of the square
            half_size: half the length of the square
        '''
        self.center = center 
        self.half_size = float(half_size)

    def contains_point(self, point):
        '''
        Verifies that the given point is within this square.

        Args:
            point: a Point type to check if it's in the square

        Returns:
            A boolean indicating whether the point is within the square
        '''
        left_bound = self.center.x - self.half_size
        right_bound = self.center.x + self.half_size
        bottom_bound = self.center.y - self.half_size
        top_bound = self.center.y + self.half_size
        if (point.x >= left_bound and point.x <= right_bound
                and point.y >=bottom_bound and point.y <=top_bound):
            return True
        return False

    def intersect(self, other_box):
        '''
        Checks if the provided box/square intersects with this square.

        Args:
            other_box: another Box object

        Returns:
            A boolean indicating if the two intersect anywhere
        '''
        # self bottom left corner
        aX1 = self.center.x - self.half_size
        aY1 = self.center.y - self.half_size
        # self top right corner
        aX2 = self.center.x + self.half_size
        aY2 = self.center.y + self.half_size
        
        # other_box bottom left corner
        bX1 = other_box.center.x - other_box.half_size
        bY1 = other_box.center.y - other_box.half_size
        # other_box top right corner
        bX2 = other_box.center.x + other_box.half_size
        bY2 = other_box.center.y + other_box.half_size

        if aX1 < bX2 and aX2 > bX1 and aY1 < bY2 and aY2 > bY1:
            return True
        return False

class PRQuadTree():
    '''
    Class representing a Point Range Quadtree.
    '''
    
    # number of coordinate points to store per node
    QT_NODE_CAPACITY = 1

    def __init__(self, box):
        '''
        Constructs a PR Quadtree given an initial square.

        Args:
            box: a Box representing initial square
        '''
        self.box = box
        self.points = []
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

    def insert(self, x, y):
        '''
        Inserts a point into the PRQuadtree.

        Args:
            x: x-coordinate of point
            y: y-coordinate of point

        Returns:
            A boolean returning true on success, false on failure.
        '''
        point = Point(x, y)
        if not self.box.contains_point(point):
            # point does not belong to this box
            return False
        if len(self.points) < self.QT_NODE_CAPACITY:
            self.points.append(point)
            return True
        
        if self.nw == None:
            self._subdivide()

        if self.nw.insert(x,y):
            return True
        if self.ne.insert(x,y):
            return True
        if self.sw.insert(x,y):
            return True
        if self.se.insert(x,y):
            return True

    def query_range(self, rng):
        '''
        Returns the points in the provided range.

        Args:
            rng: a Box range from which to retrieve points

        Returns:
            A list of points within the provided range
        '''
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
        '''
        Returns k points closest to the provided point.

        Args:
            point: a Point from which to search for other points.
            k: number of closest points to return
        
        Returns:
            A list of k closest points
        ''' 
        def _sort_key(p):
            '''
            Internal method used to provide python method with a key
            (coordinate distance) on which to sort.

            Args:
                p: Point to sort

            Returns:
                A coordinate distance between the search point and 
                the provided point
            '''
            return sqrt( pow(point.x-p.x, 2) + pow(p.y-point.y,2))
        nearby = None
        for i in range(1,20):
            rng = Box(point, pow(2, i))
            nearby = self.query_range(rng)
            if len(nearby) >= k:
                break
        return sorted(nearby, key=_sort_key)[:k]
            
    
    def _subdivide(self):
        '''
        Divides a node into nw,ne,sw,se pieces so that a new point 
        can be inserted.
        '''
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
        '''
        Prints all points stored in the PRQuadtree.

        Args:
            root: start point, or the root of the Quadtree

        Returns:
            out: a string with coordinates
        '''
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
        '''
        Prints the points of the nw,ne,sw,se blocks of the
        given PRQuadTree node.

        Returns:
            A string of points in the blocks
        '''
        def _print_msg(loc, name):
            '''
            Generates string based on the number of points stored in the
            provided node.

            Args:
                loc: a PRQuadTree node (ie nw,ne,sw,se)

            Returns:
                A string with point and name
            '''
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

