#!/usr/bin/env python3

import pyglet
from pyglet.gl import *
import glooey
import autoprop

from line_clock import LineClock, HandGroup

CONFIG = Config(double_buffer=True, vsync=False) #sample_buffers=1, samples=8)
WINDOW = pyglet.window.Window(width=1024, height=768, config=CONFIG) #, resizable=True
WINDOW.set_minimum_size(1024, 768)
#WINDOW.set_maximum_size(1024, 768)
pyglet.clock.set_fps_limit(60)
GUI = glooey.Gui(WINDOW)

# Glooey classes to define style
class RwLabel(glooey.Label):
    custom_color = '#babdb6'
    custom_font_size = 10
    custom_alignment = 'center'


class RwTitle(glooey.Label):
    custom_color = '#eeeeec'
    custom_font_size = 12
    custom_alignment = 'left'
    custom_bold = True


class RwButton(glooey.Button):
    Label = RwLabel
    custom_alignment = 'fill'

    class Base(glooey.Background):
        custom_color = '#204a87'

    class Over(glooey.Background):
        custom_color = '#3465a4'

    class Down(glooey.Background):
        custom_color = '#729fcff'

    def __init__(self, text, callback):
        super().__init__(text)
        self.callback = callback

    def on_click(self, widget):
        self.callback()

# main canvas widget
class RwDiagram(glooey.Widget):
    custom_size = 10

    def __init__(self):
        super().__init__()

        # User-controlled attributes:
        self._property = self.custom_size

        # Internal attributes:
        self._axes = None

    def on_update(self, dt):
        self._draw()

    def do_attach(self):
        # Update the drawing 10 FPS
        pyglet.clock.schedule_interval(self.on_update, 1/10)

    def do_detach(self):
        pyglet.clock.unschedule(self.on_update)
    
    def do_claim(self):
        width = height = 2 * self.custom_size
        return width, height

    def do_regroup(self):
        if self._alive is not None:
            self.batch.migrate(
                    self._face, GL_TRIANGLE_STRIP, self.group, self.batch)

        for k in self._hands:
            self._hands[k].batch = self.batch
            self._hands[k].group = HandGroup(self)

    def do_draw(self):
        self.do_draw_axes()
        self.do_draw_diagram()

    def do_draw_axes(self):
        if self._axes is None:
            self._axes = self.batch.add(
                    num_vertices,
                    GL_TRIANGLE_STRIP,
                    self.group,
                    ('v2f', vertices),
                    ('c3B', colors),
            )
        else:
            self._face.vertices = vertices
            self._face.colors = colors

def on_resize(self):
    pass

# main application class
class RwApp():
    """ Main Application Class """
    menu_width = 100
    menu_height = 0

    def __init__(self, window, gui):
        self._menu_width = RwApp.menu_width
        self._menu_height = RwApp.menu_height
        self.window = window
        self.gui = gui
        self.setup()
        pyglet.app.run()

    def end(self):
        print("End")
        pyglet.app.exit()



    def setup(self):
        split = glooey.HBox()
        #split.set_alignment('top')
        
        # menu
        menubox = glooey.VBox()
        #menubox.set_alignment('top')
        menubox.set_width_hint(self._menu_width)
        menubox.cell_padding = 1
        #menubox.alignment = 'top'
        title = RwTitle("Controls")
        menubox.add(title, size = self.menu_height)
        buttons = [("Generate", self.generate), ("Exit", self.end)]
        for button in buttons:
            btn = RwButton(*button)
            menubox.add(btn, size = self.menu_height)
        
        #test - add line clock from external module
        lc = LineClock()
        menubox.add(lc, size = 300)

        split.pack(menubox)

        # canvas
        canvas = glooey.Placeholder()
        split.add(canvas)
        self.gui.add(split)

    def generate(self):
        print("Generate")

@WINDOW.event
def on_resize(width, height):
    print('The window was resized to %dx%d' % (width, height))
    GUI.do_resize()

# MAIN

if __name__ == '__main__':
    APP = RwApp(WINDOW, GUI)
