import pyglet
import glooey
import autoprop
import datetime
from pyglet.gl import *
from vecrec import Vector, Rect


@autoprop
class DrawingWidget(glooey.Widget):
    custom_zoom = 1


    def __init__(self):
        super().__init__()

        # User-controlled attributes:
        self._zoom = self.custom_zoom

        # Internal attributes:
        self._main_gfx = None
        self._axes = {
                'x': glooey.drawing.Rectangle(),
                'z': glooey.drawing.Rectangle()
        }

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, zoom):
        self._zoom = zoom
        self._repack()
        #self._draw()

    def on_update(self, dt):
        self._draw()

    def do_attach(self):
        # Update the clock ten times a second.  
        pyglet.clock.schedule_interval(self.on_update, 1/10)

    def do_detach(self):
        pyglet.clock.unschedule(self.on_update)
    
    def do_claim(self):
        width = height = 0
        return width, height

    def do_regroup(self):
        if self._axes is not None:
            self.batch.migrate(
                    self._axes, GL_TRIANGLE_STRIP, self.group, self.batch)

        for k in self._axes:
            self._axes[k].batch = self.batch
            self._axes[k].group = self.group
            #self._axes[k].group = HandGroup(self)

    def do_draw(self):
        self.do_draw_axes()
        #self.do_draw_hands()

    def do_draw_axes(self):
        rects = {
            'hour': Rect.from_size(self.custom_hour_hand_width, self.zoom/2),
            'min': Rect.from_size(self.custom_minute_hand_width, self.zoom),
            'sec': Rect.from_size(self.custom_second_hand_width, self.zoom),
        }

        # The clock hands all start pointing towards 12:00, and the rotations 
        # are clockwise, so 90° is 3:00, 180° is 6:00, 270° is 9:00, etc.

        now = datetime.datetime.now()
        angles = {
            'hour': 360 * now.hour / 12,
            'min': 360 * now.minute / 60,
            'sec': 360 * now.second / 60,
        }

        for k in self._hands:
            rects[k].bottom = 0
            rects[k].center_x = 0

            self._hands[k].rect = rects[k]
            self._hands[k].group.angle = angles[k]
            self._hands[k].color = self._color
            self._hands[k].show()

    def do_undraw(self):
        if self._face is not None:
            self._face.delete()
            self._face = None

        for k in self._hands:
            self._hands[k].hide()


class HandGroup(pyglet.graphics.Group):

    def __init__(self, clock):
        super().__init__(parent=clock.group)
        self.clock = clock
        self.angle = 0

    def set_state(self):
        x, y = self.clock.rect.center
        clockwise = -1

        glPushMatrix()
        glLoadIdentity()
        glTranslatef(x, y, 0)
        glRotatef(self.angle, 0, 0, clockwise)

    def unset_state(self):
        glPopMatrix()

# MAIN

if __name__ == '__main__':
    window = pyglet.window.Window()
    gui = glooey.Gui(window)
    gui.add(LineClock())
    pyglet.app.run()