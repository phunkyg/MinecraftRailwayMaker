import pyglet
import random
from pyglet.gl import *
from pyglet.window import key

INCREMENT = 5
ZOOM = 2
INCREMENT_ZOOM = 0.05
BLOCK = 0.5
AIR = 'air'
HOL = 'hollow'
PLAYER = '@p'
MAX_LEVEL = 4
TP_Y = 125
BASE_Y = 8
SEALEVEL = 74

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
    def __init__(self, start_x=0, start_y=BASE_Y, start_z=0):
        self.dir_x = 1
        self.dir_z = 0
        self.components = []
        self.hub = Station(self, self, 0, start_x, start_y, start_z)
        self.index_ptr = 0
        self.collect_garbage()
        self.check_backward()

    def __str__(self):
        return str(self.hub)

    def draw(self):
        self.hub.draw()

    def output(self):
        with open('./generated_commands.txt', 'w') as f:
            f.write(str(self))
        print('Command file written!')

    def get_index(self):
        self.index_ptr += 1
        yield self.index_ptr

    def reg(self, component):
        self.components.append(component)

    def check_collision(self, component):
        ok = True
        for comp in self.components:
            ok = component.check_collision(comp)
            if not ok:
                break

        return ok

    def check_backward(self):
        for comp in self.components:
            if comp.xmin > comp.xmax or comp.ymin > comp.ymax or comp.zmin > comp.zmax:
                print(comp.dmp())

    def collect_garbage(self):
        count = 0
        of = 0

        for comp in self.components:
            of += 1
            if not isinstance(comp, Shaft):
                if not comp.status:
                    if hasattr(comp, "children"):
                        for child in comp.children:
                            self.components.remove(child)
                            del child
                            count += 1
                    self.components.remove(comp)
                    del comp
                    count += 1
        print('Garbage Collected {0:d} of {1:d} objects'.format(count, of))


class RailwayComponent():
    def __init__(self, railway, parent, level):
        self.railway = railway
        self.parent = parent
        self.index = self.railway.get_index()
        self.children = []
        self.commands = []
        self.level = level
        self.railway.reg(self)
        self.status = True
        self.xmin = None
        self.xmax = None
        self.zmin = None
        self.zmax = None
        self.ymin = None
        self.ymax = None
        self.dir_x = self.parent.dir_x
        self.dir_z = self.parent.dir_z
        self.clr = ((1.0, 1.0, 1.0), 1)

    def add_child(self, component):
        if component.status:
            self.children.append(component)
        else:
            del component
            print('component rejected')

    def add_command(self, command):
        self.commands.append(command)

    def __str__(self):
        mainstr = ''
        if self.status:
            for piece in self.commands:
                mainstr += str(piece) + '\n'
            for child in self.children:
                mainstr += str(child)
        return mainstr

    def dmp(self):
        msg = '{0},{1},{2:d},{3:d},{4:d},{5:d},{6:d},{7:d}'.format(
            self.__class__.__name__, str(self.status), self.xmin, self.ymin,
            self.zmin, self.xmax, self.ymax, self.zmax)
        return msg

    def draw(self):
        if self.status:
            draw_cuboid(self.xmin, self.ymin, self.zmin, self.xmax, self.ymax,
                        self.zmax, self.clr[0])
            for child in self.children:
                child.draw()

    def check_collision(self, comp):
        ok = True
        if self == comp:
            return ok
        if isinstance(comp, Shaft):
            return ok
        if comp == self.parent:
            return ok

        if self.xmin < comp.xmax and self.xmax > comp.xmin and self.zmin < comp.zmax and self.zmax > comp.zmin:
            ok = False

        msg = self.dmp() + ',' + comp.dmp()
        if not ok:
            print(msg)
        return ok

    def set_status(self):
        self.status = self.railway.check_collision(self)

    def flip(self):
        if self.xmin > self.xmax:
            xtmp = self.xmax
            self.xmax = self.xmin
            self.xmin = xtmp
        if self.ymin > self.ymax:
            ytmp = self.ymax
            self.ymax = self.ymin
            self.ymin = ytmp
        if self.zmin > self.zmax:
            ztmp = self.zmax
            self.zmax = self.zmin
            self.zmin = ztmp

    def do_dir(self, dir_x, dir_z):
        if not dir_x is None:
            self.dir_x = dir_x
        if not dir_z is None:
            self.dir_z = dir_z


class Station(RailwayComponent):
    block_base = 'concrete'
    block_ceiling = 'sealantern'
    start_size = 24
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

    def __init__(self,
                 railway,
                 parent,
                 level,
                 start_x,
                 base_y,
                 start_z,
                 dir_x=None,
                 dir_z=None):
        super().__init__(railway, parent, level)
        self.do_dir(dir_x, dir_z)

        # Set the level and size of this station
        # Decrease slightly each time
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
        if self.dir_x != 0:
            self.xmin = start_x
            self.zmin = start_z - self.half_size
            self.xmax = self.xmin + (self.dir_x * self.size)
            self.zmax = start_z + self.half_size
            self.centre_x = start_x + (self.dir_x * self.half_size)
            self.centre_z = start_z
        elif self.dir_z != 0:
            self.zmin = start_z
            self.xmin = start_x - self.half_size
            self.zmax = self.zmin + (self.dir_z * self.size)
            self.xmax = start_x + self.half_size
            self.centre_z = start_z + (self.dir_z * self.half_size)
            self.centre_x = start_x

        self.ymin = base_y
        self.ymax = base_y + Station.inner_height + 2

        # Set status
        self.flip()
        self.set_status()
        if not self.status:
            return

        # Set the mc commands for the outer and ceiling
        self.add_command(
            Cheat(AIR, self.centre_x, self.ymin + 1, self.centre_z,
                  self.centre_x, self.ymin + 2, self.centre_z))
        self.add_command(
            Cheat(
                None,
                self.centre_x,
                TP_Y,
                self.centre_z,
                othercommand='tp'))
        self.add_command(
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL))
        self.add_command(
            Cheat(self.block_ceiling, self.xmin, self.ymax - 1, self.zmin,
                  self.xmax, self.ymax - 1, self.zmax))
        # punch out entrance if a child
        if level > 0:
            half = Tunnel.inner_width // 2
            ytun = self.ymin + Tunnel.inner_height
            if dir_z != 0:
                self.add_command(
                    Cheat(AIR, start_x - half, self.ymin + 1, start_z, start_x + half,
                        ytun, start_z))
            else:
                self.add_command(
                    Cheat(AIR, start_x, self.ymin + 1, start_z - half, start_x,
                        ytun, start_z + half))                

        # Spawn children
        even = self.level % 2 == 0

        if even or self.level == MAX_LEVEL:
            self.add_child(Shaft(self.railway, self))

        if self.level < MAX_LEVEL:
            if self.dir_x == 1 or level == 0 or (self.dir_z != 0 and even):
                self.add_child(
                    Tunnel(self.railway, self, self.level + 1, self.xmax,
                           self.ymin, self.centre_z, +1, 0))
            if self.dir_x == -1 or level == 0 or (self.dir_z != 0 and even):
                self.add_child(
                    Tunnel(self.railway, self, self.level + 1, self.xmin,
                           self.ymin, self.centre_z, -1, 0))
            if self.dir_z == 1 or level == 0 or (self.dir_x != 0 and even):
                self.add_child(
                    Tunnel(self.railway, self, self.level + 1, self.centre_x,
                           self.ymin, self.zmax, 0, +1))
            if self.dir_z == -1 or level == 0 or (self.dir_x != 0 and even):
                self.add_child(
                    Tunnel(self.railway, self, self.level + 1, self.centre_x,
                           self.ymin, self.zmin, 0, -1))


class Shaft(RailwayComponent):
    block_base = 'concrete'
    block_inside = 'scaffolding'
    block_landing = 'slime'
    block_beacon = 'glowstone'
    sea_level = SEALEVEL
    sky_level = 255
    inner_x = 1
    inner_z = 2
    clrs = [((0.96, 0.625, 0.26), 3)]  #orange
    beacon = True

    def __init__(self, railway, parent):
        super().__init__(railway, parent, parent.level)
        # Shaft builds slightly inside the outer corner of the station, then sticking out
        # materials and colour stay the same for now, but support change for future
        self.clr = Shaft.clrs[0]
        self.block_base = Shaft.block_base
        self.block_inside = Shaft.block_inside
        self.block_landing = Shaft.block_landing

        # Calculate outer dimensions of shaft cuboid
        self.xmin = parent.centre_x - 1
        self.xmax = parent.centre_x + Shaft.inner_x
        self.zmin = parent.centre_z - 1
        self.zmax = parent.centre_z + Shaft.inner_z
        self.ymin = parent.ymin
        self.ymax = Shaft.sea_level
        # Door cutout
        self.dz = self.zmax - 1
        self.dy = self.ymin + 2

        # Calculate the inside structure fill
        self.ix = parent.centre_x
        self.iz = parent.centre_z
        self.iy = self.ymin + 1

        self.tz = self.zmin - 1

        # Set the mc commands for the shaft
        self.add_command(
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL))
        self.add_command(
            Cheat(self.block_inside, self.ix, self.iy, self.iz, self.ix,
                  self.ymax, self.iz))
        self.add_command(
            Cheat(AIR, self.xmin, self.iy, self.zmin + 1, self.xmin, self.dy,
                  self.dz))
        self.add_command(Cheat(AIR, self.ix, self.ymax, self.dz))
        self.add_command(
            Cheat(self.block_landing, self.ix, self.ymin, self.dz))

        # Place a beacon on top
        self.add_command(
            Cheat(Shaft.block_beacon, self.xmin, self.ymax + 1, self.zmin, self.xmin, Shaft.sky_level,
                  self.zmin)) 


class Tunnel(RailwayComponent):
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
    length_longest = 256
    length_random = 32
    clrs = [((1.0, 0.0, 0.0), 3), ((1.0, 0.4, 0.4), 4), ((0.0, 1.0, 0.0), 5),
            ((0.4, 1.0, 0.4), 6), ((0.0, 0.0, 1.0), 7), ((0.4, 0.4, 1.0), 8)]

    def __init__(self,
                 railway,
                 parent,
                 level,
                 start_x,
                 base_y,
                 start_z,
                 dir_x=None,
                 dir_z=None):
        super().__init__(railway, parent, level)
        self.do_dir(dir_x, dir_z)

        # Tunnel starts slightly inside the outer wall of the station, then sticking out
        # in the direction stated by dir_x and dir_z
        # color by direction for now
        self.block_base = Shaft.block_base
        self.length = (Tunnel.length_longest // (
            (self.level + 1) // 2)) + random.randint(-Tunnel.length_random,
                                                     Tunnel.length_random)
        #self.length = Tunnel.length_longest + random.randint(
        #    -Tunnel.length_random, Tunnel.length_random)
        #(Tunnel.length_reduceby * level)
        self.half_width = Tunnel.inner_width // 2

        # load in other prefs
        self.lamp_spacing = Tunnel.lamp_spacing
        self.block_lamp = Tunnel.block_lamp

        # Calculate outer dimensions of shaft cuboid
        # going z + or - then x is width , z is length
        if self.dir_z != 0:
            assert self.dir_x == 0, "Tunnel Can only go X or Z not both!"
            clrind = self.dir_z + 1
            self.xmin = start_x - self.half_width - 1
            self.xmax = start_x + self.half_width + 1
            self.zmin = start_z
            self.zmax = start_z + (self.length * self.dir_z)

        elif self.dir_x != 0:
            assert self.dir_z == 0, "Tunnel Can only go X or Z not both!"
            clrind = self.dir_x + 2
            self.zmin = start_z - self.half_width - 1
            self.zmax = start_z + self.half_width + 1
            self.xmin = start_x
            self.xmax = start_x + (self.length * self.dir_x)
            self.rail_data = 1

        self.clr = Tunnel.clrs[clrind]
        self.ymin = base_y
        self.ymax = self.ymin + Tunnel.inner_height + 2
        self.yrail = self.ymin + 1
        self.ylamp = self.ymin + 2
        self.ygap = self.ymax - 2

        # set status
        self.flip()
        self.set_status()
        if not self.status:
            return

        # Set the mc commands for the tunnel
        self.add_command(
            Cheat(AIR, self.xmax - self.dir_x, self.yrail,
                  self.zmax - self.dir_z, self.xmax - self.dir_x,
                  self.yrail + 1, self.zmax - self.dir_z))
        self.add_command(
            Cheat(
                None,
                self.xmax - self.dir_x,
                TP_Y,
                self.zmax - self.dir_z,
                othercommand='tp'))
        self.add_command(
            Cheat(AIR, self.xmin - self.dir_x, self.yrail,
                  self.zmin - self.dir_z, self.xmin - self.dir_x,
                  self.yrail + 1, self.zmin - self.dir_z))
        self.add_command(
            Cheat(
                None,
                self.xmin - self.dir_x,
                TP_Y,
                self.zmin - self.dir_z,
                othercommand='tp'))
        self.add_command(
            Cheat(self.block_base, self.xmin, self.ymin, self.zmin, self.xmax,
                  self.ymax, self.zmax, self.clr[1], HOL))
        self.add_command(
            Cheat(self.block_ceiling, self.xmin, self.ymax - 1, self.zmin,
                  self.xmax, self.ymax - 1, self.zmax,
                  self.block_ceiling_data))
        # Place rail, lamp blocks and powered rail segments
        if self.dir_z != 0:
            # knock out entrance and exit
            self.add_command(
                Cheat(AIR, self.xmin + 1, self.yrail, self.zmin, self.xmax - 1,
                      self.ygap, self.zmin))
            self.add_command(
                Cheat(AIR, self.xmin + 1, self.yrail, self.zmax, self.xmax - 1,
                      self.ygap, self.zmax))
            self.rail_data = 0
            self.add_command(
                Cheat(self.block_rail, start_x, self.yrail, self.zmin, start_x,
                      self.yrail, self.zmax, self.rail_data))
            for zlamp in range(self.zmin, self.zmax, self.lamp_spacing):
                # lamp either side
                self.add_command(
                    Cheat(self.block_lamp, self.xmin, self.ylamp, zlamp))
                self.add_command(
                    Cheat(self.block_lamp, self.xmax, self.ylamp, zlamp))
                # redstone under rail
                self.add_command(
                    Cheat(self.block_power, start_x, self.ymin, zlamp))
                # powered rail
                self.add_command(
                    Cheat(self.block_poweredrail, start_x, self.yrail, zlamp,
                          self.rail_data & 8))
            # Spawn child station
            if self.dir_z == 1:
                self.add_child(
                    Station(self.railway, self, self.level, start_x, base_y,
                            self.zmax, self.dir_x, self.dir_z))
            else:
                self.add_child(
                    Station(self.railway, self, self.level, start_x, base_y,
                            self.zmin, self.dir_x, self.dir_z))

        elif self.dir_x != 0:
            # knock out entrance and exit
            self.add_command(
                Cheat(AIR, self.xmin, self.yrail, self.zmin + 1, self.xmin,
                      self.ygap, self.zmax - 1))
            self.add_command(
                Cheat(AIR, self.xmax, self.yrail, self.zmin + 1, self.xmax,
                      self.ygap, self.zmax - 1))
            self.rail_data = 1
            self.add_command(
                Cheat(self.block_rail, self.xmin, self.yrail, start_z,
                      self.xmax, self.yrail, start_z, self.rail_data))
            for xlamp in range(self.xmin, self.xmax, self.lamp_spacing):
                # lamp either side
                self.add_command(
                    Cheat(self.block_lamp, xlamp, self.ylamp, self.zmin))
                self.add_command(
                    Cheat(self.block_lamp, xlamp, self.ylamp, self.zmax))
                # redstone under rail
                self.add_command(
                    Cheat(self.block_power, xlamp, self.ymin, start_z))
                # powered rail
                self.add_command(
                    Cheat(self.block_poweredrail, xlamp, self.yrail, start_z,
                          self.rail_data & 8))
            # Spawn child station
            if self.dir_x == 1:
                self.add_child(
                    Station(self.railway, self, self.level, self.xmax, base_y,
                            start_z, self.dir_x, self.dir_z))
            else:
                self.add_child(
                    Station(self.railway, self, self.level, self.xmin, base_y,
                            start_z, self.dir_x, self.dir_z))


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
            mainstr = '{0} {1} {2:d} {3:d} {4:d} 0 90'.format(
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
        self.railway = None
        self.generate()

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
        draw_cuboid(-size, -size, -size, size, size, size, (1.0, 1.0, 1.0))

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

    def generate(self):
        if not self.railway is None:
            del self.railway
        self.railway = Railway()

    def on_key_release(self, symbol, modifiers):
        global MAX_LEVEL
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
        elif symbol == key.C:
            self.railway.collect_garbage()
        elif symbol == key.G:
            self.generate()
        elif symbol == key.P:
            self.railway.output()
        elif symbol == key.PLUS:
            MAX_LEVEL += 1
            self.generate()
        elif symbol == key.MINUS:
            MAX_LEVEL -= 1
            self.generate()


if __name__ == '__main__':
    Window(1024, 768, 'Minecraft Railway Builder')
    pyglet.app.run()
