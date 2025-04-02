import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ------------------------------------------------
# 1) Global parameters
# ------------------------------------------------


# outflow: programmer (graduation) rate
nu_p   = 0.1 

# steepness in the benefit and cost logistic
k_ben  = k_cost = 3.0     

# midpoint for benefit and cost logistic
# when we increase midpoints together, we expand on the right.
# that is, the pitch of the logistic curve becomes steeper.
x0_ben = x0_cost = 0.5  

 # steepness of activation; almost a step function at this point
kphi = 20.0

# Creates hysteresis when negative kcost
# But stuck between 0.2 and 0.8

# nu_p   = 0.3      # outflow: programmer (graduation) rate
# k_ben  = 25.0     # steepness in the benefit logistic
# x0_ben = 0.50     # midpoint for benefit logistic
# k_cost = 10.0     # steepness in the cost logistic
# x0_cost= 0.5      # midpoint for cost logistic
# kphi = 10.0
# b = 0.26   # so that even at X=0 there's some small benefit

# Sweep over benefit strength alpha
alpha_values = np.linspace(0.0, 3.0, 80)
x_grid       = np.linspace(0., 1., 51)

# ------------------------------------------------
# 2) Define logistic-based functions
# ------------------------------------------------

def benefit(X, alpha):
    """
    A steep logistic 'benefit' function:
      s(X, alpha) = alpha * [1 / (1 + exp(-k_ben * (X - x0_ben)))]
    - alpha scales the overall magnitude
    - k_ben controls steepness
    - x0_ben is the midpoint
    """
    # return alpha * (1.0 / (1.0 + np.exp(-k_ben*(X - x0_ben))))
    return alpha * (1.0 / (1.0 + np.exp(-k_ben*(X - x0_ben))))

def cost(X):
    """
    A steep logistic 'cost':
      c(X) = 1.0 / (1 + exp( -k_cost * (X - x0_cost) ))
    By default, near X=0, cost ~ 1, and near X=1, cost ~ 0,
    but you can flip signs if you want the opposite.
    """
    # return 1.0 / (1.0 + np.exp(-k_cost*(X - x0_cost)))
    # flipped exponent so cost is near 0 at X=1
    # Creates a lower stable branch well below 0.2–0.3 for certain α.
    # An upper stable branch that can reach ≈0.9 or higher, depending on outflow vs. net benefit.
    return 1.0 / (1.0 + np.exp(k_cost*(X - x0_cost)))


def phi(z, steep=kphi):
    return 1.0 / (1.0 + np.exp(-steep*z))


# ------------------------------------------------
# 3) The ODE: dX/dt = Inflow - Outflow
# ------------------------------------------------

def dX_dt(X, alpha):
    """
    dX/dt = (1 - X)*Inflow - nu_p * X, where
      Inflow = phi( s_logistic(X, alpha) - c_logistic(X) )
    A standard 'mass-action' factor (1 - X) ensures we can't exceed 100% programmers.
    """
    net_benefit = benefit(X, alpha) - cost(X)  # can be + or -
    inflow = phi(net_benefit, steep=12.0)               # strongly saturating if net_benefit > 0
    return (1.0 - X)*inflow - nu_p*X

def dX_dt_derivative(X, alpha, eps=1e-8):
    """
    Numerically approximate partial derivative of dX_dt w.r.t X, used for stability check.
    """
    return (dX_dt(X+eps, alpha) - dX_dt(X-eps, alpha)) / (2.0*eps)

# ------------------------------------------------
# 4) Find equilibria by bracket search + check stability
# ------------------------------------------------
stable_alpha   = []
stable_X       = []
unstable_alpha = []
unstable_X     = []

for a in alpha_values:
    eq_solutions = []
    # bracket search
    for i in range(len(x_grid)-1):
        xlo = x_grid[i]
        xhi = x_grid[i+1]
        f_lo = dX_dt(xlo, a)
        f_hi = dX_dt(xhi, a)
        if f_lo * f_hi > 0:
            continue
        try:
            sol = root_scalar(lambda x: dX_dt(x, a), bracket=[xlo, xhi], method='brentq')
            if sol.converged:
                x_star = sol.root
                # Deduplicate solutions if they're too close
                if not any(abs(x_star - s) < 1e-4 for s in eq_solutions):
                    eq_solutions.append(x_star)
        except:
            pass
    
    # For each equilibrium, check stability
    for x_star in eq_solutions:
        df = dX_dt_derivative(x_star, a)
        if df < 0:
            # stable
            stable_alpha.append(a)
            stable_X.append(x_star)
        else:
            # unstable
            unstable_alpha.append(a)
            unstable_X.append(x_star)

# ------------------------------------------------
# 5) Plot the bifurcation diagram
# ------------------------------------------------
plt.figure(figsize=(7,5))
plt.scatter(stable_alpha,   stable_X,   color='blue',  s=25, label='Stable')
plt.scatter(unstable_alpha, unstable_X, facecolors='white',
            edgecolors='blue', s=60, label='Unstable')
plt.ylim(-0.05, 1.05)
plt.xlabel(r'$\alpha$ (strength of benefit)')
plt.ylabel(r'$X$ (fraction of programmers)')
plt.title("Bistability with All-Logistic Feedback")
plt.grid(True)
plt.legend()
# plt.savefig("hysteresis-mf.pdf")
plt.show()


# ------------------------------------------------
# BACK TO RATIO OF PROGRAMMERS 
# ------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ------------------------------
# Global parameters
# ------------------------------

nu_p   = 0.1      # outflow rate
k_ben  = 3.0
k_cost = 3.0
x0_ben = 0.5
x0_cost= 0.5
k_phi  = 20.0     # activation steepness

# We'll sweep over alpha
alpha_values = np.linspace(0, 3, 100)

# Domain for x in bracket searching:
# ratio x = p/n can in principle go from 0..∞
# We'll bracket search from near zero to some large number (like 5).
x_search = np.linspace(0, 5, 200)

def benefit(x, alpha):
    """Benefit = alpha * logistic( x - x0_ben )"""
    return alpha / (1.0 + np.exp(-k_ben*(x - x0_ben)))

def cost(x):
    """Cost = logistic( x - x0_cost ), but 'flipped' so cost is near 1 if x<<x0"""
    return 1.0 / (1.0 + np.exp(k_cost*(x - x0_cost)))

def phi(z, slope=k_phi):
    """Activation from net benefit"""
    return 1.0 / (1.0 + np.exp(-slope*z))

def dX_dt(x, alpha):
    """
    dx/dt = (1 + x)*phi( benefit(x) - cost(x) ) - nu_p*x
    If x=0 => no programmers => ratio can't grow unless net benefit>0
    If x is huge => nearly all programmers => might saturate
    """
    net = benefit(x, alpha) - cost(x)
    inflow = phi(net, slope=k_phi)
    return (1 + x)*inflow - nu_p*x

def stability(x, alpha, eps=1e-6):
    """Check the sign of derivative of dX_dt wrt x."""
    val1 = dX_dt(x+eps, alpha)
    val2 = dX_dt(x-eps, alpha)
    return (val1 - val2)/(2*eps)

stable_branches   = []
unstable_branches = []

for a in alpha_values:
    eq_points = []
    # bracket search in x in [0..5]
    for i in range(len(x_search)-1):
        xlo = x_search[i]
        xhi = x_search[i+1]
        f_lo, f_hi = dX_dt(xlo,a), dX_dt(xhi,a)
        if f_lo*f_hi>0: 
            continue
        sol = root_scalar(lambda xx: dX_dt(xx,a),
                          bracket=[xlo,xhi], method='brentq')
        if sol.converged:
            x_star = sol.root
            # deduplicate
            if not any(abs(x_star - s)<1e-3 for s in eq_points):
                eq_points.append(x_star)
    # classify stability
    for x_star in eq_points:
        dF = stability(x_star, a)
        if dF<0:
            stable_branches.append( (a, x_star) )
        else:
            unstable_branches.append( (a, x_star) )

# Plot
stable_alpha   = [pt[0] for pt in stable_branches]
stable_x       = [pt[1] for pt in stable_branches]
unstable_alpha = [pt[0] for pt in unstable_branches]
unstable_x     = [pt[1] for pt in unstable_branches]

plt.figure(figsize=(7,5))
plt.scatter(stable_alpha, stable_x, color='blue', s=25, label='Stable')
plt.scatter(unstable_alpha, unstable_x, facecolors='white', edgecolors='blue',
            s=60, label='Unstable')
plt.xlabel(r'$\alpha$')
plt.ylabel(r'$x = p/n$')
plt.ylim(-0.1,1)
plt.title("Ratio-based logistic model: x = p/n")
plt.grid(True)
plt.legend()
plt.show()






# ------------------------------------------------
# WITH NON-PROGS COMING IN 
# ------------------------------------------------





# import numpy as np
# import matplotlib.pyplot as plt
# from math import exp
# from scipy.integrate import solve_ivp

# # ------------------------------
# # 1) Parameter definitions
# # ------------------------------


# nu_p  = 0.1   # outflow of programmers
# mu    = 0.02   # birth/turnover rate => inflow of non-progs
# alpha = 5.0   # overall strength of benefit
# k     = 3.0  # slope for logistic
# x0    = 0.5   # midpoint of logistic
# kphi  = 20.0  # slope for netBenefit->inflow

# # ------------------------------
# # 2) Cost & benefit
# # ------------------------------
# def cost(X):
#     # logistic, near 1 at X=0, near 0 at X=1
#     return 1.0 / (1.0 + exp(+k*(X - x0)))

# def benefit(X, alpha):
#     # logistic, near 0 at X=0, near alpha at X=1
#     return alpha / (1.0 + exp(-k*(X - x0)))

# def phi(netB):
#     # map netBenefit -> [0..1]
#     return 1.0/(1.0 + exp(-kphi*netB))

# # ------------------------------
# # 3) The ODE: dX/dt
# # ------------------------------
# def dX_dt(t, X):
#     # net benefit
#     netB = benefit(X, alpha) - cost(X)
#     # fraction who adopt
#     adopt_rate = phi(netB)
    
#     # dX/dt = inflow - outflow - turnover
#     return (1 - X)*adopt_rate - nu_p*X - mu*X

# # ------------------------------
# # 4) Solve for a single alpha
# # ------------------------------
# t_span = (0, 200)
# X0 = 0.3   # initial fraction of programmers
# sol = solve_ivp(dX_dt, t_span, [X0], max_step=0.1, dense_output=True)

# t_vals = np.linspace(t_span[0], t_span[1], 25)
# X_vals = sol.sol(t_vals)[0]

# plt.plot(t_vals, X_vals, label="X(t)")
# plt.title("ODE with inflow of non-progs (mu={})".format(mu))
# plt.xlabel("Time")
# plt.ylabel("Programmer fraction, X")
# plt.grid(True)
# plt.ylim(-0.05,1.05)
# plt.legend()
# plt.show()
