#images.py
#
#Images
#   Uses a python imaging library to transform images with the 
#   help of the Rectangle class in rectangles.py
#
#Edit History:
#   [001]   aw  12/21/20    Initial Creation of Color and
#                           Image classes.
#   [002]   aw  12/22/20    Added PIL for image loading and
#                           numpy for use with Pillow. Also pygame.
#   [003]   aw  12/22/20    Remade aliasing (?) so it is now
#                           compatible with floats. Optimization 
#                           inbound, but for now, you can just do
#                           aliasing at like .1 lol.

import rectangles
from PIL import Image as Img 
import pygame
import numpy
import time
import struct
import math

_EXAMPLE_IMG = 'pusheen.png'
_EXAMPLE_SAVE = 'edited.png'
_DEBUG = True

PYGAME = 'pygame'
PIL = 'PIL'

class Color:
    def __init__(self, r: int, g: int, b: int, a: int = 255, old = False):
        self.r = max(0,min(r,31 if old else 255))
        self.g = max(0,min(g,63 if old else 255))
        self.b = max(0,min(b,31 if old else 255))
        self.a = 255 if old else max(0,min(a,255)) 
        self._blends = 0
        self._old = old

    @staticmethod
    def int_to_color(value: int, ignore_last = True) -> 'Color':
        '''
        Takes a 4 byte int and uses each byte
        in the int to construct a color. Last byte ignored
        and converted to alpha of 255 if ignore_last.
        '''
        r = (value >> 0) & int("11111111",2)
        g = (value >> 8) & int("11111111",2)
        b = (value >> 16) & int("11111111",2)
        a = 255 if ignore_last else ((value >> 24) & int("11111111",2))
        return Color(r,g,b,a)


    def blank(self) -> bool:
        '''
        Returns whether the color is blank (0 alpha).
        '''
        return self.a == 0

    def filler(self) -> bool:
        '''
        Returns whether the color is filler (0,0,0,0)
        '''
        return self.a == 0 and self.r == 0 and self.b == 0 and self.g == 0
    
    def __str__(self):
        return f'({self.r}, {self.g}, {self.b}, {self.a})'

    def __repr__(self):
        return str(self)
    
    def __eq__(self, right):
        if isinstance(right, Color):
            c2 = right.to_old() if self._old else right.to_new()
            return self.r == c2.r and self.g == c2.g and self.b == c2.b and self.a == c2.a

    @staticmethod
    def average(self, c: 'Color' or ['Color']) -> 'Color':
        '''
        Takes a color (or some) and averages it with another color
        to make a whole new color! Cool !
        '''
        colors = c
        if type(c) == Color:
            colors = [c]
        r = self.r
        g = self.g
        b = self.b
        a = self.a
        
        for i in colors:
            r += i.r
            g += i.g
            b += i.b
            a += i.a
        num = len(colors) + 1

        return Color(r//num,g//num,b//num,a//num)

    @staticmethod
    def average_list(c: ['Color'], filler: int = 0) -> 'Color':
        '''
        Takes a list of colors and an amount of filler (0,0,0,0) 
        colors and gives back the average of the colors.
        '''
        r = 0
        g = 0
        b = 0
        a = 0
        if len(c) == 0 and filler == 0:
            return Color(0,0,0,0)

        for i in c:
            r += i.r
            g += i.g
            b += i.b
            a += i.a
        num = len(c) + filler
        return Color(r//num,g//num,b//num,a//num) 

    def blend(self, c: 'Color' or ['Color']) -> None:
        '''
        Like average but instead just changes this color to the average !!
        '''
        avg = self.average(c)

        self.r = avg.r
        self.g = avg.g
        self.b = avg.b
        self.a = avg.a

    def blend_percent(self, c: 'Color', percent: float) -> None:
        '''
        Blends the current color with a percent of the other color,
        with 100% (1) being completely changing the color to the new
        one, 50% (.5) being half and half (an average), and 0% (0) 
        being not actually affecting the other color at all :).
        '''
        cur_percent = 1-percent

        self.r = int(self.r*cur_percent + c.r*percent)
        self.g = int(self.g*cur_percent + c.g*percent)
        self.b = int(self.b*cur_percent + c.b*percent)
        self.a = int(self.a*cur_percent + c.a*percent)

    def clean_blend(self, c: 'Color') -> None:
        '''
        Nicely blends the colors so each time the amount it is affected
        is scaled properly. Also the first time this is called, it will
        replace the current color wholly (intentional).
        '''
        new_color_percent = 1/(self._blends+1)

        self.blend_percent(c, new_color_percent)

        self._blends += 1

    def to_tuple(self) -> tuple:
        '''
        Returns the color as a tuple.
        '''
        return self.r, self.g, self.b, self.a

    def to_old(self) -> 'Color':
        if self._old: return Color(self.r, self.g,self.b, old = True)
        return Color(self.r//8, self.g//4,self.b//8, old = True)

    def to_new(self) -> 'Color':
        if not self._old: return Color(self.r, self.g, self.b ,self.a)
        return Color(self.r*8, self.g*4, self.b*8)

    def is_old(self):# -> bool:
        return self._old

    def distance_no_sqrt(self, c: 'Color') -> int:
        return (self.a-c.a)**2+(self.g-c.g)**2+(self.b-c.b)**2

    def distance(self, c:'Color') -> float:
        return self.distance_no_sqrt(c)**.5

    def __getitem__(self, index):
        if index == 0: return self.r
        elif index == 1: return self.g
        elif index == 2: return self.b
        elif index == 3: return self.a


class Palette:
    '''
    Note that this is primarily for palette swaps, and in specific, for palette swaps
    with old Pokemon games and their limited color palette. Also the reason for the "old"
    colors (in Color) and converting ints to colors (in Color).
    '''
    def __init__(self, *colors: Color):
        '''
        The first color is ALWAYS the (fully) transparent one.
        '''
        assert len(colors) != 0, 'Cannot have Palette with 0 colors'
        self._old = False
        if colors[0].is_old(): self._old = True
        self._colors = colors

    @staticmethod
    def poke_gen3_palette(file: str) -> 'Palette':
        '''
        Takes a link to a pokemon gen 3 palette file (.pal)
        and returns a palette (new/0-255 colors) from that.
        '''
        NUM_COLORS = 16
        data = open(file, 'rb').read()
        numbers = struct.unpack("I"*NUM_COLORS, data)
        return Palette(*(Color.int_to_color(i) for i in numbers))

    def __getitem__(self, index):
        '''
        Use a color and will return the closest color in the palette excluding
        the transparent color (in the palette's color size). Use an index and 
        will return the color at that position. Over/underindexing will return
        the first (transparent) color.
        '''
        if type(index) is int:
            if 0 <= index < len(self._colors): return self._colors[index]
            return self._colors[0]
        elif isinstance(index, Color):
            if index.a == 0: return self._colors[0]
            color_using = index.to_old() if self._old else index.to_new()
            closest = min(self._colors[1:], key = lambda x: x.distance_no_sqrt(color_using))
            return closest

    def __str__(self):
        return 'Palette('+('3byte' if self._old else '6/8byte')+'):\n'+str(self._colors)

    def swap_color(self, c: Color, p: 'new palette') -> Color:
        '''
        Swaps the color c into the equivalent color in the new palette.
        If the color is not on the current palette, returns the new palette's
        transparency (first) color.
        '''
        for i in range(len(self._colors)):
            if self._colors[i] == c:
                return p[i]
        return p[0]




class Image:
    '''
    This is merely a 2d array/map of Color objects.
    '''
    def __init__(self, colors: [[Color]] = None, 
                 width: int = None, height: int = None):
        self._colors = colors
        if colors == None:
            self._colors = [[Color(0,0,0,0) for i in range(width)] for i in range(height)]
        self._rect = rectangles.Rectangle(width = len(self._colors[0]), height = len(self._colors))

    @staticmethod
    def load(path: str, the_type: str = PIL) -> 'Image':
        '''
        Takes a path leading to an image and turns it into an Image object.
        There is realisically no difference between types. Also, since this
        is really only done once, it doesn't matter that much.
        '''
        if _DEBUG:
            start = time.perf_counter()

        colors = []

        if the_type == PIL:
            image = Img.open(path)
            pixels = image.load()
            for y in range(image.height):
                colors.append([])
                for x in range(image.width):
                    pixel = pixels[x,y]
                    colors[y].append(Color(pixel[0],pixel[1],pixel[2],pixel[3] if len(pixel) == 4 else 255))
        elif the_type == PYGAME:
            image = pygame.image.load(path)
            for y in range(image.get_height()):
                colors.append([])
                for x in range(image.get_width()):
                    color = image.get_at((x,y))
                    colors[y].append(Color(color.r, color.g, color.b, color.a))

        if _DEBUG:
            end = time.perf_counter()
            print(f'Finished loading {path} via {the_type} in {end-start:.4f} seconds.')
        return Image(colors)

    def convert(self, the_type: str = PYGAME) -> 'Image of a given type':
        '''
        Converts the current Image to an image from a
        specific library.
        '''
        if _DEBUG:
            start = time.perf_counter()

        image = None

        if the_type == PIL:
            colors = numpy.zeros((len(self._colors), len(self._colors[0]), 4), dtype = numpy.uint8)
            for i in range(len(self._colors)):
                for j in range(len(self._colors[i])):
                    colors[i,j] = self._colors[i][j].to_tuple()
            if _DEBUG:
                print('Finished numpy array')
            image = Img.fromarray(colors, 'RGBA')
        elif the_type == PYGAME:
            image = pygame.Surface((self.width(),self.height())).convert_alpha()
            for x in range(self.width()):
                for y in range(self.height()):
                    image.set_at((x,y), self._colors[y][x].to_tuple())

        if _DEBUG:
            end = time.perf_counter()
            print(f'Finished converting with {the_type} in {end-start:.4f} seconds')
        return image

    def colors(self) -> [[Color]]:
        '''
        Returns all the colors in the image. :)
        '''
        return self._colors

    def width(self) -> int:
        '''
        Returns the width of the image.
        '''
        return len(self._colors[0])

    def height(self) -> int:
        '''
        Returns the height of the image.
        '''
        return len(self._colors)

    def transform(self, points: [(float, float)] = None,
                  rect: rectangles.Rectangle = None,
                  view: rectangles.Rectangle = None,
                  alias_amount: float = 4, stripped: bool = True) -> 'Image':
        '''
        Transforms the current image onto a rectangle. Okay, actually its a quadrilateral, but
        I'm not changing everything now.
        Points and rect are virtually interchangeable, as points should just be an iterable of 4 pairs of floats, representing
        2D coordinates as the points of the polygon to translate this image to. Also, the coordinates, from left to right in the iterable,
        represent the top left, top right, bottom right, and bottom left vertices of the image.
        If you instead use rect, that is just a valid rectangles.Rectangle.
        The view is optional, and will crop the resulting image to those coordinates.
        The alias_amount is like a clarity, as you increase it gets clearer, but takes longer (of factor O(n^2)). Centered around 1, so 0-1 makes
        the image look worse, but 1+ makes it look better, especially as size increases.
        Stripped takes effect with a view, and will offset the image so the top left corner is 0,0, so it removes the blank color entries.
        Also, know that this is slow.
        '''
        if _DEBUG:
            start = time.perf_counter()
        r = rect
        if r == None:
            if len(points) != 4:
                raise IndexError
            r = rectangles.Rectangle([rectangles.Coordinate(tuple_coord=points[0]),
                                      rectangles.Coordinate(tuple_coord=points[1]),
                                      rectangles.Coordinate(tuple_coord=points[2]),
                                      rectangles.Coordinate(tuple_coord=points[3])])
        max_x = r.max_x()
        min_x = r.min_x()
        max_y = r.max_y()
        min_y = r.min_y()
        movement_strip = rectangles.Vector(min_x, min_y)

        if stripped:
            r.move(movement_strip, -1)
            max_x = r.max_x()
            min_x = r.min_x()
            max_y = r.max_y()
            min_y = r.min_y()

        topleft = (min_x,min_y)
        botright = (max_x,max_y)

        if view != None:
            topleft = (view.min_x(),view.min_y())
            botleft = (view.max_x(),view.max_y())

        new_image_colors = []
        increment_amount = 1/alias_amount
        cur_y = 0
        for y in range(int(max_y)):
            cur_x = 0
            new_image_colors.append([])
            the_y = cur_y
            for x in range(int(max_x)):
                if not (topleft[0] <= x <= botright[0] and \
                        topleft[1] <= y <= botright[1]):
                    cur_x = x
                    new_image_colors[-1].append(Color(0,0,0,0))
                    continue

                colors = []
                blanks = 0

                the_y = cur_y
                the_x = cur_x
                while the_y < y+1:
                    the_x = cur_x
                    while the_x < x+1:
                        image_point = r.transform(
                            rectangles.Coordinate(cur_x,
                                                  cur_y),
                            self._rect)
                        if image_point != None and \
                           0 <= image_point.x < self.width() and \
                           0 <= image_point.y < self.height():
                            colors.append(self._colors[int(image_point.y)][int(image_point.x)])
                        else:
                            blanks += 1
                        the_x += increment_amount
                    the_y += increment_amount
                cur_x = the_x

                if blanks == 0 and len(colors) == 0:
                    temp_x = x
                    temp_y = y
                    if cur_y > y:
                        temp_y = int(the_y - increment_amount)
                    if cur_x > x:
                        temp_x = int(the_x - increment_amount)
                    colors.append(new_image_colors[temp_y][temp_x])
                
                new_image_colors[-1].append(Color.average_list(colors, blanks))
            cur_y = the_y

        new_image = Image(new_image_colors)

        if stripped:
            r.move(movement_strip)

        if _DEBUG:
            end = time.perf_counter()
            print(f'Finished transform in {end-start:.4f} seconds')
        return new_image

    def scale_to_dimension(self, x: int, y: int, alias_amount = 1) -> 'Image':
        r = [(0,0),(x,0),(x,y),(0,y)]
        return self.transform(r, alias_amount = alias_amount)

    def scale(self, scalar: float, alias_amount = 1) -> 'Image':
        r = [(0,0),(self.width()*scalar,0),(self.width()*scalar,self.height()*scalar),(0,self.height()*scalar)]
        return self.transform(r, alias_amount = alias_amount)

    def apply_palette(self, p: Palette) -> 'Image':
        '''
        Like is stated in Palette, pretty much only used for old games with limited palettes.
        Will set every color in this Image to one in the palette p, by finding the closest color
        in the palette to the one being changed.
        '''
        #for row in range(len(self._colors)):
        #    for col in range(len(self._colors[row])):
        #        self._colors[row][col] = p[self._colors[row][col]].to_new()
        return Image([[p[self._colors[row][col]].to_new() for col in range(len(self._colors[row]))] for row in range(len(self._colors))])

    def palette_swap(self, p1: 'current palette', p2: 'new palette'):
        '''
        Will change THIS Image.
        '''
        for row in range(len(self._colors)):
            for col in range(len(self._colors[row])):
                self._colors[row][col] = p1.swap_color(self._colors[row][col], p2)

    def add_right(self, i: 'Image') -> 'Image':
        '''
        Adds an image to the right of this image and returns that.
        So if you had image that looks like \o/, and add_right an image
        that looks like _._, you will get \o/_._
        '''
        new = []
        for row in range(max(self.height(), i.height())):
            new.append([])
            for col in range(self.width()):
                new[row].append(self[row][col] if row < self.height() else Color(0,0,0,0))
            for col in range(i.width()):
                new[row].append(i[row][col] if row < i.height() else Color(0,0,0,0))
        return Image(new)

    def add_down(self, i: 'Image') -> 'Image':
        '''
        Adds an image below this image and returns that.
        '''
        new = []
        for row in range(self.height()):
            new.append([])
            for col in range(max(self.width(), i.width())):
                new[row].append(self[row][col] if col < self.width() else Color(0,0,0,0))
        for row in range(i.height()):
            new.append([])
            for col in range(max(self.width(), i.width())):
                new[-1].append(i[row][col] if col < i.width() else Color(0,0,0,0))
        return Image(new)
    
    def test_many_palettes(self, *p) -> 'Image':
        '''
        Will show palettes in order (from p) left to right, up to down.
        '''
        assert len(p) != 0
        cols = math.ceil(len(p)**.5)
        rows = math.ceil(len(p)/cols)
        new_image = Image([[]])
        for row in range(rows):
            new_img2 = Image([[]])
            for col in range(cols):
                index = row*cols + col
                if index >= len(p): break
                i = self.apply_palette(p[index])
                new_img2 = new_img2.add_right(i)
            new_image = new_image.add_down(new_img2)
        return new_image

    def __getitem__(self, index):
        return self._colors[index]


#Just some testing
if __name__ == '__main__':
    image = Image.load(_EXAMPLE_IMG)
    r1 = [(50,200),
          (100,100),
          (200,50),
          (250,150)]
    r2 = [(1000,500),
          (500,200),
          (500,1100),
          (1000,800)]
    image2 = image.transform(r1,alias_amount=4)
    #image2 = image.scale_to_dimension(64,64)
    #image2 = image.scale(2)
    pil_img = image2.convert(the_type = PIL)
    #pil_img.show()
    pil_img.save(_EXAMPLE_SAVE)
    