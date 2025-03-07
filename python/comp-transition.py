import numpy as np
import matplotlib.pyplot as plt
from numba import jit
plt.style.use(['ggplot'])

# We will use the odeint routine
from scipy.integrate import odeint
# With a wrapper to facilitate 2d arrays
from odeintw import odeintw

import math

def cost(n: int, p: int, k: float, x0: float) -> float:
    if n > 0:
        value = 1 / (1 + math.exp(k * (p / n - x0)))
        if 0 < value < 1:
            return value
    return 0.0

def tau(a: float, b: float, n: int, p: int, k: float, x0: float) -> float:
    value = -a + b * (1 - cost(n, p, k, x0))
    if value > 0:
        return value
    return 0.0

def sigma(n: int, p: int, k: float, m: float) -> float:
    value = m * (n + p + 1) * (1.0 - (n + p + 1) / k)
    if value > 0:
        return value
    return 0.0


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
