import numpy as np
import random
from scipy.ndimage import convolve
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import colors
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter

print("movie time")

plt.rcParams["animation.html"] = "jshtml"

#load data
data = np.genfromtxt("test.csv", delimiter=",")
dt = data[0,0]
max_t = np.max(data[:,0])
t = np.arange(dt,max_t+dt,dt)

x = 1+int(np.max(data[:,1]))
b = data[data[:, 0] == t[0]]
res = np.zeros((x,x))
fig, ax= plt.subplots(figsize=(6,6))
im = ax.imshow((res), cmap='RdYlGn', vmin=-6, vmax=0.0)
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("log(density) of groups")
plt.xlabel('number of programmers')
plt.ylabel('number of non-programmers')

#animation function
def animate(i):
    res = im.get_array()
    b = data[abs(data[:, 0]-t[i])<1e-2]
    for row in b:
      if row[3]>1e-6:
        res[int(row[1]),int(row[2])] = np.log10(row[3])
      else:
        res[int(row[1]),int(row[2])] = -7
    im.set_array((res))
    return [im]

#animation details
fps = 100
anim = FuncAnimation(fig,animate,frames=len(t),interval=1000/fps)
anim.save('movie2.gif', dpi=90)