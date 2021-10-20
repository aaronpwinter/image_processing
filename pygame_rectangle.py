#pygame_rectangle.py
#
#Pygame Rectangle
#   This is very literally only for testing purposes.
#
#Edit History:
#   [001]   aw  12/21/20    Initial Creation

import pygame
from rectangles import *
import images

_FPS = 30
_HEIGHT = 800
_WIDTH = 1500
_COLORS = [pygame.Color(255,0,0),
           pygame.Color(0,255,0),
           pygame.Color(0,0,255),
           pygame.Color(200,200,60)]
_BG = pygame.Color(100,100,100)
_POINT = pygame.Color(255,255,255)
_IMAGE = 'pusheen.png'
_ALIAS = 4

class RectangleApp:
    def __init__(self):
        self._running = True
        self._rect1 = None
        self._rect2 = None
        self._mouse = (0,0)
        self._surface = None
        self._base_image = None
        self._image = None
        self._base_surface = None
        self._img_surface = None

    def run(self) -> None:

        self._pygame_init()
        
        try:
            clock = pygame.time.Clock()

            self._initialize()

            while self._running:
                clock.tick(_FPS)

                self._update_world()

                self._redraw()
        finally:
            pygame.quit()

    def _pygame_init(self) -> None:
        '''
        Runs everything it needs to before pygame starts. and stuff
        '''
        self._rect1 = Rectangle([Coordinate(450,600),
                                 Coordinate(500,500),
                                 Coordinate(600,450),
                                 Coordinate(650,550)])

        self._base_image = images.Image.load(_IMAGE)
        self._rect2 = Rectangle(width = self._base_image.width(), 
                                height = self._base_image.height())

        self._image = self._base_image.transform(rect = self._rect1, alias_amount=_ALIAS)

        pygame.init()

    def _initialize(self) -> None:
        '''
        Runs everything right before the main loop.
        '''

        self._resize_display((_WIDTH,_HEIGHT))        

        self._base_surface = self._base_image.convert()
        self._img_surface = self._image.convert()


    def _update_world(self) -> None:
        '''
        Updates the world once per frame, by checking events and whatever
        else needs handling.
        '''
        for event in pygame.event.get():
            self._handle_event(event)
        
        self._mouse = pygame.mouse.get_pos()

    def _handle_event(self, event) -> None:
        '''
        Handles specific events in the pygame.
        '''
        if event.type == pygame.QUIT:
            self._stop_running()
        elif event.type == pygame.VIDEORESIZE:
            self._resize_display(event.size)

    def _stop_running(self) -> None:
        '''
        Everything which happens when the game is closed.
        '''
        self._running = False

    def _resize_display(self, size:(int, int)) -> None:
        '''
        Resizes the display.
        '''
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    def _redraw(self) -> None:
        '''
        Draws everything.
        '''
        pygame.draw.rect(self._surface, _BG,
                                pygame.Rect(0, 0, self._surface.get_width(),
                                            self._surface.get_height()))

        
        self._surface.blit(self._base_surface, (0,0))
        self._surface.blit(self._img_surface, (self._rect1.min_x(),self._rect1.min_y()))
        self._draw_rect(self._rect1)
        self._draw_rect(self._rect2)

        newpoint = self._rect1.transform(Coordinate(tuple_coord=self._mouse), self._rect2)
        if newpoint != None:
            pygame.draw.circle(self._surface, _POINT, newpoint.to_tuple(), 5)

        newpoint2 = self._rect2.transform(Coordinate(tuple_coord=self._mouse), self._rect1)
        if newpoint2 != None:
            pygame.draw.circle(self._surface, _POINT, newpoint2.to_tuple(), 5)
        
        pygame.display.flip()

    def _draw_rect(self, r: Rectangle) -> None:
        '''
        Draws a rectangle thing that from the rectangle class
        '''
        for line in range(len(r._lines)):
            color = _COLORS[line%len(_COLORS)]
            p1 = r._lines[line].point().to_tuple()
            p2 = r._lines[(line+1)%len(r._lines)].point().to_tuple()

            pygame.draw.aaline(self._surface, color, p1, p2)
    
if __name__ == '__main__':
    RectangleApp().run()