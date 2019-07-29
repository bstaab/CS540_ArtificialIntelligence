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
        self.x = 0
        self.y = 0
        self.z = 0

    def blocks_on_top(self, b1):
        c1 = self.coords[b1]
        blocks = []
        for b, c in self.coords.items():
            if c[0] == c1[0] and c[1] == c1[1] and c[2] > c1[2]:
                blocks.append(b)
        return blocks

    def plot_goal(self):

        voxels = np.empty(self.x.shape, dtype=bool)
        colors = np.empty(voxels.shape, dtype=object)
        j = 0
        first_ = True
        for block, coord in self.goal_coords.items():
            cube = (self.x == coord[0]) & (self.y == coord[1]) & (self.z == coord[2])
            colors[cube] = self.color_list[j]
            if first_:
                first_ = False
                voxels = cube
            else:
                voxels |= cube
            j += 1

        self.ax1.voxels(voxels, facecolors=colors, edgecolor='k')

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

    def plot(self, coords, speed=1000):
        self.coords = coords
        self.x, self.y, self.z = np.indices((10, 10, 10))
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=speed, blit=False, repeat=False)
        plt.show()

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

p = Animation3D()
p.plot(start_coordinates, 10)
