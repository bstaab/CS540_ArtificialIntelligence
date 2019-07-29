import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

filled = np.array([
    [[1, 0, 1], [0, 0, 1], [0, 1, 0]],
    [[0, 1, 1], [1, 0, 0], [1, 0, 1]],
    [[1, 1, 0], [1, 1, 1], [0, 0, 0]]
])

filled0= np.array([
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
])

filled1= np.array([
    [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
])

filled2= np.array([
    [[1, 1, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
])

filled3= np.array([
    [[1, 1, 1], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
])

def animate(i):
    ax.clear()
    if i % 4 == 0:
        ax.voxels(filled0, edgecolors='gray')
    if i % 4 == 1:
        ax.voxels(filled1, edgecolors='gray')
    if i % 4 == 2:
        ax.voxels(filled2, edgecolors='gray')
    if i % 4 == 3:
        ax.voxels(filled3, edgecolors='gray')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()