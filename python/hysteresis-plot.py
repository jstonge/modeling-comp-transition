import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

# Model parameters
gamma = 0.3   # outflow
n     = 3     # Hill exponent
# We'll vary alpha in the code below

def equilibrium_equation(X, alpha, gamma, n):
    """
    Returns F(X; alpha, gamma, n) = 0 for the equilibrium:
        alpha * (X^n / (1 + X^n)) * (1 - X) - gamma * X
    """
    return alpha * (X**n / (1 + X**n)) * (1 - X) - gamma * X

# We will sweep alpha between two extremes
alpha_vals = np.linspace(0, 10, 200)  # adjust range if needed

# --- Forward sweep (alpha up) ---
x_forward = []
x_guess = 0.  # start near X=0

for alpha in alpha_vals:
    sol = root(lambda X: equilibrium_equation(X, alpha, gamma, n), x_guess)
    X_sol = sol.x[0]
    # Clip solution to [0,1] if you like, but typically not necessary
    X_sol = np.clip(X_sol, 0, 1)
    x_forward.append(X_sol)
    x_guess = X_sol  # use this solution as the guess for next alpha

# --- Backward sweep (alpha down) ---
x_backward = []
x_guess = 1.0  # start near X=1

for alpha in alpha_vals[::-1]:
    sol = root(lambda X: equilibrium_equation(X, alpha, gamma, n), x_guess)
    X_sol = sol.x[0]
    X_sol = np.clip(X_sol, 0, 1)
    x_backward.append(X_sol)
    x_guess = X_sol

x_backward = x_backward[::-1]  # reverse to match the alpha_vals order

# Plotting
plt.figure(figsize=(6,4))
plt.plot(alpha_vals, x_forward, label='Forward sweep', lw=2)
plt.plot(alpha_vals, x_backward, label='Backward sweep', lw=2)
plt.xlabel(r'$\alpha$ (feedback strength)')
plt.ylabel(r'Fraction of Programmers, $X$')
plt.title(f'Hysteresis with Positive Feedback (gamma={gamma}, n={n})')
plt.grid(True)
plt.legend()
plt.show()



# ----





import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

# --- Model Parameters ---
gamma = 0.3
n = 3
alpha_vals = np.linspace(0, 5, 100)

def F(X, alpha, gamma, n):
    """
    The ODE's right-hand side:
        F(X; alpha) = alpha * (X^n / (1 + X^n)) * (1 - X) - gamma * X
    """
    return alpha * (X**n / (1 + X**n)) * (1 - X) - gamma * X

def dF_dX(X, alpha, gamma, n):
    """
    Derivative F'(X; alpha) for stability analysis.
    We'll manually differentiate.
    
    F(X) = alpha * (X^n/(1+X^n))*(1-X) - gamma*X
    
    Let's define A = X^n/(1+X^n).
    Then dA/dX = (n*X^(n-1)*(1+X^n) - X^n * n*X^(n-1)) / (1+X^n)^2
               = n*X^(n-1)/(1+X^n)^2.
    
    So derivative wrt X:
    dF/dX = alpha * [ dA/dX * (1 - X) + A * (-1) ] - gamma.
    """
    if X < 0 or X > 1:
        return None  # out of domain, just skip
    
    # A and derivative
    A = (X**n)/(1.0 + X**n)
    dA = n*X**(n-1)/(1.0 + X**n)**2
    
    # chain rule
    return alpha * ( dA*(1 - X) + A*(-1) ) - gamma

# We'll store solutions in lists, each alpha can have up to 3 solutions
stable_solutions = []
unstable_solutions = []

for alpha in alpha_vals:
    # A list to collect solutions for this alpha
    solutions_for_alpha = []

    # 1) Sample multiple initial guesses (maybe 15 guesses from 0..1)
    guesses = np.linspace(0, 1, 15)

    for guess in guesses:
        sol = root(lambda x: F(x, alpha, gamma, n), guess)
        x_star = sol.x[0]

        # 2) Round or clip to ensure it's in [0,1], discard if out of range
        if not (0 <= x_star <= 1):
            continue

        # 3) Check if we already have this solution in solutions_for_alpha
        # We'll consider two solutions the same if they're within 1e-3
        if any(abs(x_star - s) < 1e-3 for s in solutions_for_alpha):
            continue

        solutions_for_alpha.append(x_star)

    # 4) For each unique solution, check stability
    solutions_for_alpha.sort()
    stables = []
    unstables = []
    for x_star in solutions_for_alpha:
        deriv = dF_dX(x_star, alpha, gamma, n)
        if deriv < 0:  # stable
            stables.append(x_star)
        else:          # unstable
            unstables.append(x_star)

    # 5) Store the results so we can plot
    # We'll store pairs of (alpha, x)
    for s in stables:
        stable_solutions.append((alpha, s))
    for u in unstables:
        unstable_solutions.append((alpha, u))

# Convert to arrays for plotting
stable_solutions = np.array(stable_solutions)
unstable_solutions = np.array(unstable_solutions)

# Plot
plt.figure(figsize=(6,4))
if len(stable_solutions)>0:
    plt.plot(stable_solutions[:,0], stable_solutions[:,1], 'bo', label='Stable eq.')
if len(unstable_solutions)>0:
    plt.plot(unstable_solutions[:,0], unstable_solutions[:,1], 'ro', label='Unstable eq.')

plt.xlabel(r'$\alpha$')
plt.ylabel(r'$X$ (fraction of programmers)')
plt.title(f'Full Bifurcation Diagram (gamma={gamma}, n={n})')
plt.grid(True)
plt.legend()
plt.show()








# ----




import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ----------------------
# 1) Model Definition
# ----------------------
def F(X, alpha, gamma, n):
    """
    The ODE's right-hand side:
        F(X; alpha) = alpha * (X^n / (1 + X^n)) * (1 - X) - gamma * X.
    We set F(X; alpha) = 0 to find equilibria.
    """
    # For safety, allow X outside [0,1] if the solver drifts slightly.
    if X < 0:
        return alpha * 0 * (1 - 0) - gamma*X  # ~ -gamma*X
    if X > 1:
        return alpha * 1 * (0) - gamma*X     # ~ -gamma*X
    # Otherwise, compute the normal expression:
    A = X**n / (1 + X**n)  # Hill function
    return alpha * A * (1 - X) - gamma * X

def dF_dX(X, alpha, gamma, n):
    """
    Derivative dF/dX for stability analysis.
      F(X) = alpha*(X^n/(1+X^n))*(1 - X) - gamma*X
    
    Let A(X) = X^n/(1 + X^n).
    Then dA/dX = n*X^(n-1)/(1 + X^n)^2.
    => dF/dX = alpha * [ dA/dX*(1 - X) + A*( -1 ) ] - gamma
    """
    if X < 0 or X > 1:
        # derivative near boundary can be approximated if needed, 
        # but for simplicity just treat out-of-bounds as if there's no solution
        return 0
    
    # A and derivative
    A   = X**n / (1 + X**n)
    dA  = n * X**(n-1) / (1 + X**n)**2
    
    return alpha * ( dA*(1 - X) - A ) - gamma

# ----------------------
# 2) Parameter Choices
# ----------------------
gamma  = 0.3
n      = 3
alpha_vals = np.linspace(0.0, 5.0, 60)  # sweep alpha from 0 to 5
X_min, X_max = 0.0, 1.0                # fraction of programmers in [0,1]

# For storing solutions
stable_alpha   = []
stable_X       = []
unstable_alpha = []
unstable_X     = []

# ----------------------
# 3) Bracket & Solve for Each alpha
# ----------------------
N_brackets = 50
xs = np.linspace(X_min, X_max, N_brackets+1)

for alpha in alpha_vals:
    solutions_for_alpha = []

    # bracket search in [0,1]
    for i in range(N_brackets):
        xlo = xs[i]
        xhi = xs[i+1]
        f_lo = F(xlo, alpha, gamma, n)
        f_hi = F(xhi, alpha, gamma, n)

        # Check if a sign change occurs
        if f_lo * f_hi > 0:
            continue

        try:
            sol = root_scalar(lambda X: F(X, alpha, gamma, n),
                              bracket=[xlo, xhi],
                              method='brentq')
            if sol.converged:
                x_star = sol.root
                # Avoid duplicates if within a small tolerance
                if not any(abs(x_star - s) < 1e-3 for s in solutions_for_alpha):
                    solutions_for_alpha.append(x_star)
        except:
            pass

    # ----------------------
    # 4) Stability Check
    # ----------------------
    for x_star in solutions_for_alpha:
        df = dF_dX(x_star, alpha, gamma, n)
        if df < 0:
            stable_alpha.append(alpha)
            stable_X.append(x_star)
        else:
            unstable_alpha.append(alpha)
            unstable_X.append(x_star)

# ----------------------
# 5) Plot
# ----------------------
plt.figure(figsize=(6,4))

# stable: filled black circles
plt.scatter(stable_alpha, stable_X, color='black', s=20, label='Stable eq.', zorder=3)

# unstable: open circles
plt.scatter(unstable_alpha, unstable_X, facecolors='white', edgecolors='black', 
            s=60, label='Unstable eq.', zorder=4)

plt.xlabel(r'$\alpha$ (feedback strength)')
plt.ylabel(r'$X$ (fraction of programmers)')
plt.title(f'Bifurcation Diagram: alpha vs. X  (gamma={gamma}, n={n})')
plt.grid(True)
plt.legend()
plt.ylim(-0.05, 1.05)
plt.show()



# --------

# back to cost benefits land

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ----------------------
# 1) Model Parameters
# ----------------------
gamma   = 0.3     # outflow (graduation rate)
n       = 3       # Hill exponent for benefit
k_b     = 10.0    # steepness of logistic in net payoff
C_min   = 0.1     # minimum possible cost
C_max   = 1.0     # maximum cost when X is near 0
k_c     = 6.0     # steepness of the cost logistic
x_c0    = 0.5     # midpoint for the cost logistic
NPTS    = 60      # number of alpha values to sweep

alpha_values = np.linspace(0.0, 3.0, NPTS)  # sweep alpha from 0 to 3
X_min, X_max = 0.0, 1.0                     # fraction of programmers in [0,1]
N_brackets   = 50                           # for bracket search in [0,1]

# ----------------------
# 2) Define Benefit, Cost, Net Payoff, Inflow
# ----------------------
def B(X, alpha):
    """Benefit function: Hill-type."""
    return alpha * (X**n / (1 + X**n))

def C(X):
    """
    Cost function: high at low X, low at high X.
    A decreasing logistic from C_max to C_min.
    """
    return (C_min 
            + (C_max - C_min)
            / (1.0 + np.exp(k_c*(X - x_c0))))

def Pi(X, alpha):
    """Net payoff = Benefit - Cost."""
    return B(X, alpha) - C(X)

def inflow(X, alpha):
    """
    Inflow = (1 - X) * sigmoid( net payoff ).
    Here we use a logistic in the net payoff Pi(X, alpha).
    """
    payoff = Pi(X, alpha)
    # logistic in payoff
    return (1 - X) * (1.0 / (1.0 + np.exp(-k_b * payoff)))

def F(X, alpha):
    """
    The ODE's right-hand side, dX/dt:
      F(X; alpha) = inflow(X, alpha) - gamma*X.
    We'll set F(X, alpha) = 0 to find equilibria.
    """
    return inflow(X, alpha) - gamma * X

def dF_dX(X, alpha, eps=1e-9):
    """
    Numerical derivative of F wrt X for stability check.
    We do a small finite difference for simplicity here.
    """
    return (F(X+eps, alpha) - F(X-eps, alpha)) / (2*eps)

# ----------------------
# 3) Solve for Equilibria Over alpha
# ----------------------
stable_alpha   = []
stable_X       = []
unstable_alpha = []
unstable_X     = []

xs = np.linspace(X_min, X_max, N_brackets + 1)

for alpha in alpha_values:
    solutions_for_alpha = []

    # bracket search in [0,1]
    for i in range(N_brackets):
        xlo = xs[i]
        xhi = xs[i+1]
        f_lo = F(xlo, alpha)
        f_hi = F(xhi, alpha)

        # Check sign change
        if f_lo * f_hi > 0:
            continue

        try:
            sol = root_scalar(lambda x: F(x, alpha),
                              bracket=[xlo, xhi],
                              method='brentq')
            if sol.converged:
                x_star = sol.root
                # Avoid duplicates if within a small tolerance
                if not any(abs(x_star - s) < 1e-3 for s in solutions_for_alpha):
                    solutions_for_alpha.append(x_star)
        except:
            pass

    # 4) Stability check
    for x_star in solutions_for_alpha:
        df = dF_dX(x_star, alpha)
        if df < 0:
            stable_alpha.append(alpha)
            stable_X.append(x_star)
        else:
            unstable_alpha.append(alpha)
            unstable_X.append(x_star)

# ----------------------
# 5) Plot Bifurcation Diagram
# ----------------------
plt.figure(figsize=(7,5))
plt.scatter(stable_alpha, stable_X, 
            color='blue', s=20, label='Stable eq.')
plt.scatter(unstable_alpha, unstable_X, 
            facecolors='white', edgecolors='blue', s=50, label='Unstable eq.')

plt.xlabel(r'$\alpha$ (Benefit strength)')
plt.ylabel(r'$X$ (fraction of programmers)')
plt.title('Cost-Benefit Public Good with Potential Bistability')
plt.grid(True)
plt.ylim(-0.05, 1.05)
plt.legend()
plt.show()



# -----

# same but simpler


import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ------------------------
# 1) Fixed parameters
# ------------------------
νp = 0.3     # outflow: programmer (graduation) rate
n_brackets = 50
k = 10.0
x0 = 0.5

# We'll sweep alpha
alpha_values = np.linspace(0, 3, 60)

# ------------------------
# 2) Define the functions
# ------------------------
def cost(X):
    # Logistic decreasing from ~1 at X=0 to ~0 at X=1
    # more fancy than model 3
    return 1.0 / (1.0 + np.exp(k*(X - x0)))

def s(X, alpha):
    # Benefit function
    # Hill function with exponent = 2, scaled by alpha
    return alpha * (X**2 / (1 + X**2))

def f(z, a1=5):
    # A logistic function for the inflow switch
    # same than model 3 but here it is
    # to model the non-prog to prog transitions
    return 1.0 / (1.0 + np.exp(-a1*z))

def F(X, alpha):
    """
    The ODE right-hand side: dX/dt = inflow - outflow.
    inflow = (1 - X)*f( s(X, alpha) - cost(X) )
    outflow = νp*X
    """
    return (1 - X)*f(s(X, alpha) - cost(X)) - gamma*X

def dF_dX(X, alpha, eps=1e-8):
    # numerical derivative for stability check
    return (F(X+eps, alpha) - F(X-eps, alpha)) / (2*eps)


# ------------------------
# 3) Find Equilibria
# ------------------------
stable_alpha   = []
stable_X       = []
unstable_alpha = []
unstable_X     = []

xs = np.linspace(0.0, 1.0, n_brackets+1)

for a in alpha_values:
    eq_solutions = []

    # bracket search over [0,1]
    for i in range(n_brackets):
        xlo = xs[i]
        xhi = xs[i+1]
        f_lo = F(xlo, a)
        f_hi = F(xhi, a)
        if f_lo * f_hi > 0:
            continue
        try:
            sol = root_scalar(lambda X: F(X, a), bracket=[xlo, xhi], method='brentq')
            if sol.converged:
                x_star = sol.root
                # avoid duplicates within tolerance
                if not any(abs(x_star - s) < 1e-3 for s in eq_solutions):
                    eq_solutions.append(x_star)
        except:
            pass

    # check stability
    for x_star in eq_solutions:
        df = dF_dX(x_star, a)
        if df < 0:
            stable_alpha.append(a)
            stable_X.append(x_star)
        else:
            unstable_alpha.append(a)
            unstable_X.append(x_star)


# ------------------------
# 4) Plot
# ------------------------
plt.figure(figsize=(7,5))
plt.scatter(stable_alpha, stable_X, color='blue', s=25, label='Stable eq.')
plt.scatter(unstable_alpha, unstable_X, facecolors='white', edgecolors='blue',
            s=50, label='Unstable eq.')

plt.grid(True)
plt.xlabel(r'$\alpha$ (benefit strength)')
plt.ylabel(r'$X$ (fraction of programmers)')
plt.title('Minimal Public Good Model (Cost-Benefit) with Potential Bistability')
plt.ylim(-0.05, 1.05)
plt.legend()
plt.show()
