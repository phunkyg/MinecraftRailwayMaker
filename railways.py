import pyglet
from pyglet.gl import *
from pyglet.window import key

INCREMENT = 5
BLOCK = 3
AIR = 'air'

# GL drawing helpers


def draw_cuboid(xmin, ymin, zmin, xmax, ymax, zmax, clr):
    xmin = xmin * BLOCK
    xmax = xmax * BLOCK
    ymin = ymin * BLOCK
    ymax = ymax * BLOCK
    zmin = zmin * BLOCK
    zmax = zmax * BLOCK

    # BACK
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmax, ymin, zmax)
    glVertex3f(xmax, ymax, zmax)
    glVertex3f(xmin, ymax, zmax)
    glVertex3f(xmin, ymin, zmax)
    glEnd()

    # FRONT
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmax, ymin, zmin)
    glVertex3f(xmax, ymax, zmin)
    glVertex3f(xmin, ymax, zmin)
    glVertex3f(xmin, ymin, zmin)
    glEnd()

    # RIGHT
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmax, ymin, zmin)
    glVertex3f(xmax, ymax, zmin)
    glVertex3f(xmax, ymax, zmax)
    glVertex3f(xmax, ymin, zmax)
    glEnd()

    #  LEFT
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmin, ymin, zmax)
    glVertex3f(xmin, ymax, zmax)
    glVertex3f(xmin, ymax, zmin)
    glVertex3f(xmin, ymin, zmin)
    glEnd()

    # TOP
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmax, ymax, zmax)
    glVertex3f(xmax, ymax, zmin)
    glVertex3f(xmin, ymax, zmin)
    glVertex3f(xmin, ymax, zmax)
    glEnd()

    # BOTTOM
    glBegin(GL_POLYGON)
    glColor3f(*clr)
    glVertex3f(xmax, ymin, zmin)
    glVertex3f(xmax, ymin, zmax)
    glVertex3f(xmin, ymin, zmax)
    glVertex3f(xmin, ymin, zmin)
    glEnd()


class Railway():
    def __init__(self, start_x=0, start_y=4, start_z=0):
        self.hub = Station(start_x, start_y, start_z, 0)
        #Output the whole tree to the terminal
        print(self)

    def __str__(self):
        return str(self.hub)

    def draw(self):
        self.hub.draw()


class Station():
    block_base = 'concrete'
    block_ceiling = 'sealantern'
    start_size = 40
    decrease_size = 3
    inner_height = 3
    clrs = [((1.0, 0.0, 1.0), 10)]

    def __init__(self, centre_x, base_y, centre_z, level):

        # Set the level and size of this station
        # Decrease slightly each time
        self.level = level
        self.size = Station.start_size - (self.level * Station.decrease_size)
        self.half_size = self.size // 2  # use integer divison so no half blocks!

        # Set the station main colour from the list according to level
        # and the MC block type with its colour value
        self.clr = Station.clrs[level]
        self.block_base = '{} {}'.format(Station.block_base, self.clr[1])
        self.block_ceiling = Station.block_ceiling

        # Calculate outer dimensions of station cuboid
        self.xmin = centre_x - self.half_size
        self.zmin = centre_z - self.half_size
        self.xmax = centre_x + self.half_size
        self.zmax = centre_z + self.half_size

        self.ymin = base_y
        self.ymax = base_y + Station.inner_height + 2

        # Set the mc commands for the outer and ceiling
        self.commands = [
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax),
            Cheat(self.block_ceiling, self.xmin, self.ymax - 1, self.zmin,
                  self.xmax, self.ymax - 1, self.zmax)
        ]

        # Spawn children
        self.children = [Shaft(self.xmax, self.ymin, self.zmax)]

    def __str__(self):
        mainstr = ''
        for piece in self.commands:
            mainstr += str(piece) + '\n'
        for child in self.children:
            mainstr += str(child)
        return mainstr

    def draw(self):
        draw_cuboid(self.xmin, self.ymin, self.zmin, self.xmax, self.ymax,
                    self.zmax, self.clr[0])
        for child in self.children:
            child.draw()


class Shaft():
    block_base = 'concrete'
    block_inside = 'scaffolding'
    block_landing = 'slime'
    sea_level = 64
    inner_x = 1
    inner_z = 2
    clrs = [((244, 161, 66), 2)]  #orange

    def __init__(self, corner_x, base_y, corner_z):

        # Shaft builds slightly inside the outer corner of the station
        # materials and colour stay the same for now, but support change for future
        self.clr = Shaft.clrs[0]
        self.block_base = '{} {}'.format(Shaft.block_base, self.clr[1])
        self.block_inside = Shaft.block_inside
        self.block_landing = Shaft.block_landing

        # Calculate outer dimensions of shaft cuboid
        self.xmin = corner_x - Shaft.inner_x - 1
        self.zmin = corner_z - Shaft.inner_z - 1
        self.xmax = corner_x
        self.zmax = corner_z

        # Calculate the inside structure fill
        self.ix = self.xmin + 1
        self.iz = self.zmin + 1
        self.iy = base_y + 1

        self.ymin = base_y
        self.ymax = Shaft.sea_level

        # Set the mc commands for the shaft
        self.commands = [
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax),
            Cheat(self.block_inside, self.ix, self.iy, self.iz, self.ix,
                  self.ymax, self.iz)
        ]

        # Spawn children
        self.children = []

    def __str__(self):
        mainstr = ''
        for piece in self.commands:
            mainstr += str(piece) + '\n'
        for child in self.children:
            mainstr += str(child)
        return mainstr

    def draw(self):
        draw_cuboid(self.xmin, self.ymin, self.zmin, self.xmax, self.ymax,
                    self.zmax, self.clr[0])


class Cheat():
    """class to compose and output minecraft cheat commands"""

    def __init__(self,
                 block,
                 xmin,
                 ymin,
                 zmin,
                 xmax=None,
                 ymax=None,
                 zmax=None):
        self.xmin = xmin
        self.ymin = ymin
        self.zmin = zmin
        self.xmax = xmax
        self.ymax = ymax
        self.zmax = zmax
        self.block = block

        if (any([xmax is None, ymax is None, zmax is None])) or (all([
                self.xmin == self.xmax, self.ymin == self.ymax,
                self.zmin == self.zmax
        ])):
            self.command = 'setblock'
        else:
            self.command = 'fill'

    def __str__(self):
        mainstr = ''
        if (self.command == 'fill'):
            mainstr = '{0} {1:d} {2:d} {3:d} {4:d} {5:d} {6:d} {7}'.format(
                self.command, self.xmin, self.ymin, self.zmin, self.xmax,
                self.ymax, self.zmax, self.block)
        elif (self.command == 'setblock'):
            mainstr = '{0} {1:d} {2:d} {3:d} {4}'.format(
                self.command, self.xmin, self.ymin, self.zmin, self.block)
        else:
            Raise(ValueError, "commands knows are fill and setblock")
        return mainstr


class Window(pyglet.window.Window):

    init_rotation = (90, 0, 0)
    zoom = 1
    clr_red = (1.0, 0.0, 0.0)
    clr_red_light = (1.0, 0.4, 0.4)
    clr_green = (0.0, 1.0, 0.0)
    clr_green_light = (0.4, 1.0, 0.4)
    clr_blue = (0.0, 0.0, 1.0)
    clr_blue_light = (0.4, 0.4, 1.0)

    def __init__(self, width, height, title=''):
        self.reset_rotation()
        super(Window, self).__init__(width, height, title, resizable=True)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.railway = Railway()

    def on_draw(self):
        # Clear the current GL Window
        self.clear()

        # Push Matrix onto stack
        glPushMatrix()

        self.do_rotate()

        self.draw_axes()
        #self.draw_cube(30)
        self.railway.draw()

        # Pop Matrix off stack
        glPopMatrix()

    def reset_rotation(self):
        (self.xRotation, self.yRotation, self.zRotation) = Window.init_rotation

    def do_rotate(self):
        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)
        glRotatef(self.zRotation, 0, 0, 1)

    def draw_cube(self, size=3.0):

        # White side - BACK
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_blue)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, -size, size)
        glEnd()

        # White side - BACK
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_blue_light)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(-size, -size, -size)
        glEnd()

        # Purple side - RIGHT
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_red)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)
        glEnd()

        # Green side - LEFT
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_red_light)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)
        glVertex3f(-size, -size, -size)
        glEnd()

        # Blue side - TOP
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_green)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glEnd()

        # Red side - BOTTOM
        glBegin(GL_POLYGON)
        glColor3f(*self.clr_green_light)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, -size, -size)
        glEnd()

    def draw_axes(self):
        glBegin(GL_LINES)

        # x +
        glColor3f(*self.clr_red)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(1.0, 0.0, 0.0, 0.0)

        # x -
        glColor3f(*self.clr_red_light)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(-1.0, 0.0, 0.0, 0.0)

        # y +
        glColor3f(*self.clr_green)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(0.0, 1.0, 0.0, 0.0)

        # y -
        glColor3f(*self.clr_green_light)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(0.0, -1.0, 0.0, 0.0)

        # z +
        glColor3f(*self.clr_blue)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(0.0, 0.0, 1.0, 0.0)

        # z -
        glColor3f(*self.clr_blue_light)
        glVertex4f(0.0, 0.0, 0.0, 1.0)
        glVertex4f(0.0, 0.0, -1.0, 0.0)

        glEnd()

    def on_resize(self, width, height):
        hw = width / 2
        hh = height / 2

        # set the Viewport
        glViewport(0, 0, width * 2, height * 2)

        self.do_rotate()

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(35, aspectRatio, 1, 10000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #gluOrtho2D(-hw,hw,-hh,hh)
        glTranslatef(0, 0, -hw)

    def on_key_release(self, symbol, modifiers):
        print(key.symbol_string(symbol))
        if symbol == key.W:
            self.xRotation -= INCREMENT
        elif symbol == key.S:
            self.xRotation += INCREMENT
        elif symbol == key.A:
            self.yRotation -= INCREMENT
        elif symbol == key.D:
            self.yRotation += INCREMENT
        elif symbol == key.Q:
            self.zRotation -= INCREMENT
        elif symbol == key.E:
            self.zRotation += INCREMENT
        elif symbol == key.R:
            self.reset_rotation()


if __name__ == '__main__':
    Window(1024, 768, 'Minecraft Railway Builder')
    pyglet.app.run()
