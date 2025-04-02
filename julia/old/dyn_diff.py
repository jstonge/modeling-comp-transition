import numpy as np
import matplotlib.pyplot as plt
from numba import jit
plt.style.use(['ggplot'])

# We will use the odeint routine
from scipy.integrate import odeint
# With a wrapper to facilitate 2d arrays
from odeintw import odeintw

# Master Equations
@jit(nopython=True)
def J(x, t, alpha, gamma, beta):
    """
    Time derivative of the occupation numbers.

        * x is the state distribution (array like)
        * t is time (scalar)
        * alpha is the prey birth rate
        * gamma is the predator death rate
        * beta is the predation rate
        * NB: We use logistic growth for preys to limit the # of states
        * K will be the carrying capacity
    """
    
    K = x.shape[0]
    
    dx = 0*x
    for n1, n2 in np.ndindex(x.shape):
        dx[n1,n2] -= gamma*n2*x[n1,n2] #predator death output
        if n1<x.shape[0]-1: #prey birth output
            dx[n1,n2] -= alpha*n1*(K-n1)*x[n1,n2]/K
        if n2<x.shape[1]-1: #predation output
            dx[n1,n2] -= beta*n1*n2*x[n1,n2]
        if n1>0: #prey birth input
            dx[n1,n2] += alpha*(n1-1)*(K-n1+1)*x[n1-1,n2]/K
        if n2<x.shape[1]-1: #predator death input 
            dx[n1,n2] += gamma*(n2+1)*x[n1,n2+1]
        if n1<x.shape[0]-1 and n2>0: #predation input
            dx[n1,n2] += beta*(n1+1)*(n2-1)*x[n1+1,n2-1]

    return dx

# Time of observations
t_length = 20
t_steps = 80
t_vec = np.linspace(0, t_length, t_steps)

# Initial conditions
nb_of_states = 25
x_0 = np.zeros((nb_of_states,nb_of_states))
x_0[12,8] = 1

# Parameters
alpha = 0.9
gamma = 0.4
beta = 0.04

# Integration
G = lambda x, t: J(x, t, alpha, gamma, beta)
x_path = odeintw(G, x_0, t_vec)

# Plot
for t in np.arange(1,22,3):
    plt.plot(range(nb_of_states),np.sum(x_path[t],axis=0), marker="o", ls='--', label=fr"$t = {t_length*t/t_steps:.2f}$")
plt.legend()
plt.ylabel('Occupation number')
plt.xlabel('Number of predator')
plt.show()