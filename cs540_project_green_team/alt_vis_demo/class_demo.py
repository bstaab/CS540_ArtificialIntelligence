import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import copy


class Animation3D:
    def __init__(self):
        self.color_list = ["yellow", "cyan", "green", "blue", "orange", "black", "gray", "sienna", "pink", "blue", "c"]
        self.fig = plt.figure(figsize=plt.figaspect(0.5))
        self.ax1 = self.fig.add_subplot(1, 1, 1, projection='3d')

        self.ax1.set_xticks(np.arange(0, 10, 1))
        self.ax1.set_yticks(np.arange(0, 10, 1))
        self.ax1.set_zticks(np.arange(0, 10, 1))

    def blocks_on_top(self, b1):
        c1 = self.coords[b1]
        blocks = []
        for b, c in self.coords.items():
            if c[0] == c1[0] and c[1] == c1[1] and c[2] > c1[2]:
                blocks.append(b)
        return blocks

    def plot_goal(self):

        #voxels = np.empty(self.x.shape, dtype=bool)
        #colors = np.empty(voxels.shape, dtype=object)
        voxels = np.zeros(self.x.shape, dtype=bool)
        colors = np.zeros(voxels.shape, dtype=object)
        j = 0
        first_ = True
        for block, coord in self.goal_coords.items():
            cube = (self.x == coord[0]) & (self.y == coord[1]) & (self.z == coord[2])
            colors[cube] = self.color_list[j]
            #if first_:
            #    first_ = False
            #    voxels = cube
            #else:
            #    voxels |= cube
            voxels |= cube
            j += 1

        self.ax1.voxels(voxels, facecolors=colors, edgecolors=colors)# edgecolor='k')

    def update(self, i):

        voxels = np.empty(self.x.shape, dtype=bool)
        colors = np.empty(voxels.shape, dtype=object)
        j = 0
        first = True

        for block, coord in self.coords.items():
            cube = (self.x == coord[0]) & (self.y == coord[1]) & (self.z == coord[2])
            colors[cube] = self.color_list[j]
            if first:
                first = False
                voxels = cube
            else:
                voxels |= cube
            j += 1

        try:
            block_, coord_ = self.paths[i]
            # move also blocks on top
            blocks_on_top = self.blocks_on_top(block_)
            self.coords[block_] = coord_
            for b in blocks_on_top:
                c_old = self.coords[b]
                c_new = [coord_[0], coord_[1], c_old[2]]
                self.coords[b] = c_new
        except:
            print("")

    def plot(self, goal_coords, paths, coords, speed=1000):

        self.paths = paths
        self.coords = coords
        self.goal_coords = goal_coords

        self.x, self.y, self.z = np.indices((10, 10, 10))
        self.plot_goal()
        self.ani = animation.FuncAnimation(self.fig, self.update, len(paths) + 10, interval=speed, blit=False,
                                           repeat=False)
        plt.show()


def cmds_to_paths(initial_coords, cmds):
    coords = copy.copy(initial_coords)
    paths = []
    for cmd in cmds:
        if 'grab' in cmd or 'release' in cmd:
            continue

        block = cmd[1]
        delta = cmd[2:]
        coord = coords[block]
        try:
            destination = [coord[0] + delta[0], coord[1] + delta[1], coord[2] + delta[2]]
        except:
            destination = [coord[0] + delta[0], coord[1] + delta[1], coord[2]]
        coords[block] = destination
        paths.append([block, destination])
    return paths


# Where goal_coordinates and start_coordinates are dictionaries in the form:

start_coordinates = {'block6': [2, 0, 0],
                     'block3': [0, 0, 0],
                     'block1': [0, 0, 1],
                     'block7': [2, 0, 1],
                     'block4': [0, 1, 0],
                     'block2': [0, 1, 1],
                     'block5': [2, 1, 0]}

goal_coordinates = {'block6': [2, 0, 0],
                    'block3': [0, 0, 0],
                    'block1': [0, 0, 1],
                    'block7': [2, 0, 1],
                    'block4': [0, 1, 0],
                    'block2': [0, 1, 1],
                    'block5': [2, 1, 0]}

cmds = [('grab', 'block2'),
        ('carry', 'block2', -1, -1, -1),
        ('carry', 'block2', 0, 0, -1),
        ('carry', 'block2', 0, 0, -1),
        ('carry', 'block2', 0, 0, -1),
        ('release', 'block2'),
        ('grab', 'block7'),
        ('carry', 'block7', 0, -1, -1),
        ('carry', 'block7', 0, -1, -1),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('carry', 'block7', 0, -1, 0),
        ('release', 'block7'),
        ('grab', 'block3'),
        ('carry', 'block3', 0, -1, -1),
        ('carry', 'block3', 0, 0, -1),
        ('release', 'block3'),
        ('grab', 'block5'),
        ('carry', 'block5', 1, -1, -1),
        ('release', 'block5'),
        ('grab', 'block2'),
        ('carry', 'block2', 1, 1, 1),
        ('release', 'block2'),
        ('slide', 'block3', -1, -1),
        ('slide', 'block3', -1, -1),
        ('slide', 'block3', 0, -1),
        ('slide', 'block3', 0, -1),
        ('slide', 'block3', 0, -1),
        ('slide', 'block3', 0, -1),
        ('slide', 'block3', 0, -1),
        ('grab', 'block1'),
        ('carry', 'block1', 0, 1, 1),
        ('release', 'block1')]

paths = cmds_to_paths(start_coordinates, cmds)
p = Animation3D()

p.plot(goal_coordinates, paths, start_coordinates, 10)
