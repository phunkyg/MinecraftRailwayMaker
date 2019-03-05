import pyglet
from pyglet.gl import *
from pyglet.window import key

INCREMENT = 5
ZOOM = 2
INCREMENT_ZOOM = 0.05
BLOCK = 0.5
AIR = 'air'
HOL = 'hollow'
PLAYER = '@p'
MAX_LEVEL = 2

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
        self.hub = Station(start_x, start_y, start_z, 1, 0, 0)
        #Output the whole tree to the terminal
        self.output()

    def __str__(self):
        return str(self.hub)

    def draw(self):
        self.hub.draw()
    
    def output(self):
        print(self)


class Station():
    block_base = 'concrete'
    block_ceiling = 'sealantern'
    start_size = 20
    decrease_size = 2
    inner_height = 3
    clrs = [
        ((1.0, 0.0, 1.0), 10),
        ((0.0, 1.0, 1.0), 11),
        ((1.0, 1.0, 0.0), 12),
        ((1.0, 0.4, 1.0), 13),
        ((0.4, 1.0, 1.0), 14),
        ((1.0, 1.0, 0.4), 15),
    ]

    def __init__(self, start_x, base_y, start_z, dir_x, dir_z, level):

        # Set the level and size of this station
        # Decrease slightly each time
        self.level = level
        self.size = Station.start_size - (self.level * Station.decrease_size)
        self.half_size = self.size // 2  # use integer divison so no half blocks!

        # Set the station main colour from the list according to level
        # cycles around what is in the list
        # and the MC block type with its colour value
        clrind = level % len(Station.clrs)
        self.clr = Station.clrs[clrind]
        self.block_base = Station.block_base
        self.block_ceiling = Station.block_ceiling

        # Calculate outer dimensions of station cuboid
        if dir_x != 0:
            self.xmin = start_x
            self.zmin = start_z - self.half_size
            self.xmax = self.xmin + (dir_x * self.size)
            self.zmax = start_z + self.half_size
            self.centre_x = start_x + (dir_x * self.half_size)
            self.centre_z = start_z
        elif dir_z != 0:
            self.zmin = start_z
            self.xmin = start_x - self.half_size
            self.zmax = self.zmin + (dir_z * self.size)
            self.xmax = start_x + self.half_size
            self.centre_z = start_z + (dir_z * self.half_size)
            self.centre_x = start_x

        self.ymin = base_y
        self.ymax = base_y + Station.inner_height + 2

        # Set the mc commands for the outer and ceiling
        self.commands = [
            Cheat(None, self.xmin + 1, self.ymin + 1, self.zmin + 1, othercommand='tp'),
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL),
            Cheat(self.block_ceiling, self.xmin, self.ymax - 1, self.zmin,
                  self.xmax, self.ymax - 1, self.zmax)
        ]

        # Spawn children
        self.children = [
            Shaft(self.xmax, self.ymin, self.zmax)
        ]
        if self.level < MAX_LEVEL:
            if dir_x != -1 or level == 0:
                self.children.append(Tunnel(self.xmax, self.ymin, self.centre_z, +1, 0, self.level + 1))
            if dir_x != 1 or level == 0:
                self.children.append(Tunnel(self.xmin, self.ymin, self.centre_z, -1, 0, self.level + 1))
            if dir_z != -1 or level == 0:
                self.children.append(Tunnel(self.centre_x, self.ymin, self.zmax, 0, +1, self.level + 1))
            if dir_z != 1 or level == 0:
                self.children.append(Tunnel(self.centre_x, self.ymin, self.zmin, 0, -1, self.level + 1))
            

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
    clrs = [((0.96, 0.625, 0.26), 2)]  #orange

    def __init__(self, corner_x, base_y, corner_z):

        # Shaft builds slightly inside the outer corner of the station, then sticking out
        # materials and colour stay the same for now, but support change for future
        self.clr = Shaft.clrs[0]
        self.block_base = Shaft.block_base
        self.block_inside = Shaft.block_inside
        self.block_landing = Shaft.block_landing

        # Calculate outer dimensions of shaft cuboid
        self.xmin = corner_x
        self.zmin = corner_z - 1
        self.xmax = corner_x + Shaft.inner_x + 1
        self.zmax = corner_z - Shaft.inner_z - 2

        # Calculate the inside structure fill
        self.ix = self.xmin + 1
        self.iz = self.zmin - 1
        self.iy = base_y + 1

        self.ymin = base_y
        self.ymax = Shaft.sea_level

        # Door cutout
        # door x = xmin
        self.dz = self.zmax + 1
        self.dy = base_y + 2

        self.tz = self.zmin - 1

        # Set the mc commands for the shaft
        self.commands = [
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL),
            Cheat(self.block_inside, self.ix, self.iy, self.iz, self.ix,
                  self.ymax, self.iz),
            Cheat(AIR, self.xmin, self.iy, self.zmin - 1, self.xmin, self.dy,
                  self.dz),
            Cheat(AIR, self.ix, self.ymax, self.dz),
            Cheat(self.block_landing, self.ix, self.ymin, self.dz)
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


class Tunnel():
    block_base = 'concrete'
    block_ceiling = 'quartz_block'
    block_ceiling_data = 3
    block_lamp = 'sealantern'
    block_rail = 'rail'
    block_power = 'redstone_block'
    block_poweredrail = 'golden_rail'
    lamp_spacing = 10
    inner_width = 3
    inner_height = 3
    length_longest = 200
    length_reduceby = 60
    clrs = [((1.0, 0.0, 0.0), 3), ((1.0, 0.4, 0.4), 4), ((0.0, 1.0, 0.0), 5),
            ((0.4, 1.0, 0.4), 6), ((0.0, 0.0, 1.0), 7), ((0.4, 0.4, 1.0), 8)]

    def __init__(self, start_x, base_y, start_z, dir_x, dir_z, level):

        # Tunnel starts slightly inside the outer wall of the station, then sticking out
        # in the direction stated by dir_x and dir_z
        # color by direction for now
        self.level = level
        self.block_base = Shaft.block_base
        self.length = Tunnel.length_longest - (Tunnel.length_reduceby * level)
        self.half_width = Tunnel.inner_width // 2

        # load in other prefs
        self.lamp_spacing = Tunnel.lamp_spacing
        self.block_lamp = Tunnel.block_lamp

        # Calculate outer dimensions of shaft cuboid
        # going z + or - then x is width , z is length
        if dir_z != 0:
            assert dir_x == 0, "Tunnel Can only go X or Z not both!"
            clrind = dir_z + 1
            self.xmin = start_x - self.half_width - 1
            self.xmax = start_x + self.half_width + 1
            self.zmin = start_z
            self.zmax = start_z + (self.length * dir_z)

        elif dir_x != 0:
            assert dir_z == 0, "Tunnel Can only go X or Z not both!"
            clrind = dir_x + 2
            self.zmin = start_z - self.half_width - 1
            self.zmax = start_z + self.half_width + 1
            self.xmin = start_x
            self.xmax = start_x + (self.length * dir_x)
            self.rail_data = 1
        
        self.clr = Tunnel.clrs[clrind]
        self.ymin = base_y
        self.ymax = self.ymin + Tunnel.inner_height + 2
        self.yrail = self.ymin + 1
        self.ylamp = self.ymin + 2
        self.ygap = self.ymax - 2

        # Set the mc commands for the tunnel
        self.commands = [
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL),
            Cheat(self.block_ceiling, self.xmin, self.ymax - 1, self.zmin,
                  self.xmax, self.ymax - 1, self.zmax,
                  self.block_ceiling_data),
        ]
        # Place rail, lamp blocks and powered rail segments
        if dir_z != 0:
            # knock out entrance and exit
            self.commands.append(
                Cheat(AIR, self.xmin + 1, self.yrail, self.zmin, self.xmax - 1,
                      self.ygap, self.zmin))
            self.commands.append(
                Cheat(AIR, self.xmin + 1, self.yrail, self.zmax, self.xmax - 1,
                      self.ygap, self.zmax))
            self.rail_data = 0
            self.commands.append(
                Cheat(self.block_rail, start_x, self.yrail, self.zmin, start_x,
                      self.yrail, self.zmax, self.rail_data))
            for zlamp in range(self.zmin, self.zmax, self.lamp_spacing * dir_z):
                # lamp either side
                self.commands.append(
                    Cheat(self.block_lamp, self.xmin, self.ylamp, zlamp))
                self.commands.append(
                    Cheat(self.block_lamp, self.xmax, self.ylamp, zlamp))
                # redstone under rail
                self.commands.append(
                    Cheat(self.block_power, start_x, self.ymin, zlamp))
                # powered rail
                self.commands.append(
                    Cheat(self.block_poweredrail, start_x, self.yrail, zlamp, self.rail_data & 8))
            # Spawn child station
            self.children = [
                Station(start_x, base_y, self.zmax, dir_x, dir_z, self.level)
            ]
        elif dir_x != 0:
            # knock out entrance and exit
            self.commands.append(
                Cheat(AIR, self.xmin, self.yrail, self.zmin + 1, self.xmin,
                      self.ygap, self.zmax - 1))
            self.commands.append(
                Cheat(AIR, self.xmax, self.yrail, self.zmin + 1, self.xmax,
                      self.ygap, self.zmax - 1))
            self.rail_data = 1
            self.commands.append(
                Cheat(self.block_rail, self.xmin, self.yrail, start_z,
                      self.xmax, self.yrail, start_z, self.rail_data))
            for xlamp in range(self.xmin, self.xmax, self.lamp_spacing * dir_x):
                # lamp either side
                self.commands.append(
                    Cheat(self.block_lamp, xlamp, self.ylamp, self.zmin))
                self.commands.append(
                    Cheat(self.block_lamp, xlamp, self.ylamp, self.zmax))
                # redstone under rail
                self.commands.append(
                    Cheat(self.block_power, xlamp, self.ymin, start_z))
                # powered rail
                self.commands.append(
                    Cheat(self.block_poweredrail, xlamp, self.yrail, start_z, self.rail_data & 8))
            # Spawn child station
            self.children = [
                Station(self.xmax, base_y, start_z, dir_x, dir_z, self.level)
            ]


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



class Cheat():
    """class to compose and output minecraft cheat commands"""

    def __init__(self,
                 block,
                 xmin,
                 ymin,
                 zmin,
                 xmax=None,
                 ymax=None,
                 zmax=None,
                 bdata=None,
                 modes=None,
                 othercommand=None):
        self.xmin = xmin
        self.ymin = ymin
        self.zmin = zmin
        self.xmax = xmax
        self.ymax = ymax
        self.zmax = zmax
        self.block = block
        self.bdata = bdata or 0
        self.modes = modes or ''

        if not othercommand is None:
            self.command = othercommand
        else:
            if (any([xmax is None, ymax is None, zmax is None])) or (all([
                    self.xmin == self.xmax, self.ymin == self.ymax,
                    self.zmin == self.zmax
            ])):
                self.command = 'setblock'
            else:
                self.command = 'fill'

    def __str__(self):
        mainstr = ''
        if self.command == 'fill':
            mainstr = '{0} {1:d} {2:d} {3:d} {4:d} {5:d} {6:d} {7} {8:d} {9}'.format(
                self.command, self.xmin, self.ymin, self.zmin, self.xmax,
                self.ymax, self.zmax, self.block, self.bdata, self.modes)
        elif self.command == 'setblock':
            mainstr = '{0} {1:d} {2:d} {3:d} {4} {5:d} {6}'.format(
                self.command, self.xmin, self.ymin, self.zmin, self.block,
                self.bdata, self.modes)
        elif self.command == 'tp':
            mainstr = '{0} {1} {2:d} {3:d} {4:d}'.format(
                self.command, PLAYER, self.xmin, self.ymin, self.zmin)        
        else:
            raise ValueError("commands known are fill, setblock and tp")

        return mainstr


class Window(pyglet.window.Window):

    init_rotation = (90, 0, 0)
    alt_rotation = (50, -45, 0)
    init_zoom = ZOOM
    clr_red = (1.0, 0.0, 0.0)
    clr_red_light = (1.0, 0.4, 0.4)
    clr_green = (0.0, 1.0, 0.0)
    clr_green_light = (0.4, 1.0, 0.4)
    clr_blue = (0.0, 0.0, 1.0)
    clr_blue_light = (0.4, 0.4, 1.0)

    def __init__(self, width, height, title=''):
        self.reset_rotation()
        self.reset_zoom()
        self.uwidth = width
        self.uheight = height
        super(Window, self).__init__(
            self.uwidth, self.uheight, title, resizable=True)
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

    def reset_rotation(self, alt=False):
        if not alt:
            rot = Window.init_rotation
        else:  
            rot = Window.alt_rotation  
        (self.xRotation, self.yRotation, self.zRotation) = rot

    def reset_zoom(self):
        self.zoom = Window.init_zoom

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

    def set_zoom(self):
        # hacky - more research!
        self.on_resize(self.uwidth, self.uheight)
        #print(self.zoom)

    def on_resize(self, width, height):
        self.uwidth = width
        self.uheight = height
        hw = width / 2
        hh = height / 2

        # set the Viewport
        glViewport(0, 0, width * 2, height * 2)

        self.do_rotate()

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(35 * self.zoom, aspectRatio, 1, 10000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #gluOrtho2D(-hw,hw,-hh,hh)
        glTranslatef(0, 0, -hw)

    def on_key_release(self, symbol, modifiers):
        #print(key.symbol_string(symbol))
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
        elif symbol == key.Z:
            self.zoom -= INCREMENT_ZOOM
            self.set_zoom()
        elif symbol == key.X:
            self.zoom += INCREMENT_ZOOM
            self.set_zoom()
        elif symbol == key.R:
            self.reset_rotation()
            self.reset_zoom()
        elif symbol == key.F:
            self.reset_rotation(True)
            self.reset_zoom()
        elif symbol == key.P:
            self.railway.output()


if __name__ == '__main__':
    Window(1024, 768, 'Minecraft Railway Builder')
    pyglet.app.run()
