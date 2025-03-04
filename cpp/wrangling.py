import numpy as np

data = np.genfromtxt("test.csv", delimiter=",")

dt = data[0,0]
max_t = np.max(data[:,0])
t = np.arange(dt,max_t+dt,dt)

x = 1+int(np.max(data[:,1]))
b = data[data[:, 0] == t[0]]
res = np.zeros((x,x))

for i in range(len(t)):
    # i=0
    b = data[abs(data[:, 0]-t[i])<1e-2]
    for row in b:
      if row[3]>1e-6:
        res[int(row[1]),int(row[2])] = np.log10(row[3])
      else:
        res[int(row[1]),int(row[2])] = -7


    