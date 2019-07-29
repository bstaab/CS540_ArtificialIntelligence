'''Our pyglet-based blocks world visualization system.
'''

from math import pi, sin, cos

import pyglet
from pyglet.gl import *
from . import obj_batch
import copy


def color(r, g, b, a=1):
    return (GLfloat * 5)(r, g, b, a)

COLORS = {
    'blue':color(0.2, 0.2, 1),
    'red':color(1, 0.2, 0.2),
    'green':color(0.2, 1, 0.2),
    'yellow':color(0.9, 0.9, 0),
    'purple':color(0.7, 0, 0.7),
    'cyan':color(0, 0.8, 0.8),
    'orange':color(1, 0.5, 0)
    }

class window(pyglet.window.Window):

    def __init__ (self, config):
        super(window, self).__init__(800, 600, fullscreen=False,resizable=True, config=config)
        pyglet.clock.schedule(self.update)

    def on_resize(self, width, height):
        # Override the default on_resize handler to create a 3D projection
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def update(self, dt):
        pass   # here is our periodic update function

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for obj in scene:
            obj.draw()


# Define a simple function to create ctypes arrays of floats:
def farray(*args):
    return (GLfloat * len(args))(*args)
    
def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)
    glColor3f(1, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always 
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightfv(GL_LIGHT0, GL_POSITION, farray(.5, .5, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, color(.5, .5, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, color(1, 1, 1))
    
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, farray(1, 0, .5))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, color(.5, .5, .5))
    glLightfv(GL_LIGHT1, GL_SPECULAR, color(1, 1, 1))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color(0.5, 0, 0.3))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, color(1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

class Material(object):
    def __init__(self, diffuse_color=None, shininess=50):
        self.diffuse_color = diffuse_color or color(0.9, 0.9, 0.9)
        self.specular_color = color(1,1,1)
        self.shininess = 50
    
    def apply(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.diffuse_color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular_color)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
    

def applyCamera():
    glTranslatef(-4.5, -3, -6.5)
    glRotatef(30, 1, 0, 0)

class Object3D(object):
    def __init__(self):
        # position and rotation
        self.rotation = [0, 0, 0]   # (Euler angles)
        self.position = [0, 0, 0]
        
        # material
        self.material = Material()

        # triangle batch
        self.batch = pyglet.graphics.Batch()
   
    def rotate(self, x=0, y=0, z=0):
        self.rotation[0] = (self.rotation[0] + x) % 360
        self.rotation[1] = (self.rotation[1] + y) % 360
        self.rotation[2] = (self.rotation[2] + z) % 360
        
    
    def draw(self):
        self.material.apply()
        glLoadIdentity()
        applyCamera()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[2], 0, 0, 1)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[0], 1, 0, 0)
        self.batch.draw()
        
    def delete(self):
        self.vertex_list.delete()
    
    def clone(self):
        "Create a clone of this object that can be positioned independently."
        result = copy.copy(self)
        result.rotation = copy.copy(self.rotation)
        result.position = copy.copy(self.position)
        return result
    
class Cube(Object3D):
    def __init__(self, size=1):
        super(Cube, self).__init__()

        h = size * 0.5
        vertices = []
        normals = []
        indices = []
        
        # Coordinate system: +X right, +Y up, +Z towards the viewer.
        # Triangles should be specified in counter-clockwise order.

        # bottom
        i = len(vertices)//3
        vertices += [ h,-h,h,   -h,-h,h,   -h,-h,-h,   h,-h,-h ]
        normals += [ 0,-1,0,   0,-1,0,   0,-1,0,   0,-1,0 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        # top
        i = len(vertices)//3
        vertices += [ h,h,-h,   -h,h,-h,   -h,h,h,   h,h,h ]
        normals += [ 0,1,0,   0,1,0,   0,1,0,   0,1,0 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        # front
        i = len(vertices)//3
        vertices += [ h,h,h,   -h,h,h,   -h,-h,h,   h,-h,h ]
        normals += [ 0,0,1,   0,0,1,   0,0,1,   0,0,1 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        # back
        i = len(vertices)//3
        vertices += [ -h,h,-h,   h,h,-h,   h,-h,-h,   -h,-h,-h ]
        normals += [ 0,0,-1,   0,0,-1,   0,0,-1,   0,0,-1 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        # left
        i = len(vertices)//3
        vertices += [ -h,h,h,   -h,h,-h,   -h,-h,-h,   -h,-h,h ]
        normals += [ -1,0,0,   -1,0,0,   -1,0,0,   -1,0,0 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        # right
        i = len(vertices)//3
        vertices += [ h,h,-h,   h,h,h,   h,-h,h,   h,-h,-h ]
        normals += [ 1,0,0,   1,0,0,   1,0,0,   1,0,0 ]
        indices += [ i+0,i+1,i+2,   i+2,i+3,i+0 ]

        self.vertex_list = self.batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             None,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))

class Torus(Object3D):
    def __init__(self, radius, inner_radius, slices, inner_slices):
        super(Torus, self).__init__()
        
        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])

        self.vertex_list = self.batch.add_indexed(len(vertices)//3, 
                                             GL_TRIANGLES,
                                             None,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))

class ObjFile(Object3D):
    def __init__(self, modelPath):
        super(ObjFile, self).__init__()
        
        obj = obj_batch.OBJ(modelPath)
        obj.add_to(self.batch)

def add_cube(color, row, col, height=0):
    global scene
    cube = Cube(0.95)
    cube.material.diffuse_color = color
    cube.position = [col, height, -row]
    scene += [cube]

def add_block(blockObj):
    c = color(0.8, 0.8, 0.8)
    if 'color' in blockObj.properties:
        colorName = blockObj.properties['color']
        if colorName in COLORS:
            c = COLORS[colorName]
    add_cube(c, blockObj.y, blockObj.x, blockObj.z)

def show_state(state, command=None):
    # For now, we're going to just clear out our old blocks and add new
    # ones according to the given state.
    # In the future, if we want to get fancy, we can check for old blocks
    # with the same ID, and do a little animation to the new positions.
    # NOTE: command is used to keep api with plot.show_state() function the same
    global scene
    scene = list(filter(lambda o:not isinstance(o, Cube), scene))
    for blockId in state.blocks:
        add_block(state.blocks[blockId])


def blocksMainThread():
	return True

def present(state=None):
    global scene, window
    # set up
    try:
        # Try and create a window with multisampling (antialiasing)
        config = Config(sample_buffers=1, samples=4, 
                        depth_size=16, double_buffer=True,)
        window = window(config)
    except pyglet.window.NoSuchConfigException:
        # Fall back to no multisampling for old hardware
        window = pyglet.window.Window(None)

    setup()
    scene = []
    
    if state:
        show_state(state)

    # Don't add these blocks so we start with an empty grid
    # else:
        # create some cubes
        # add_cube(color(0.2, 0.2, 1), 4, 3)
        # add_cube(color(1, 0.2, 0.2), 2, 7)
        # add_cube(color(0.2, 1, 0.2), 2, 7, 1)

    # create the floor/table
    tile = ObjFile("vis/models/tile.obj")
    for row in range(0,10):
        for col in range(0,10):
            clone = tile.clone()
            clone.position = [col, -0.5, -row]
            scene += [clone]


    # start the main loop
    pyglet.app.run()


def stop():
    pyglet.app.exit()


if __name__ == "__main__":
    present()
