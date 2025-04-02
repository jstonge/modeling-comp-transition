import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ------------------------------------------------
# 1) Global Parameters (Refined)
# ------------------------------------------------
mu      = 10.0   # Stronger initial group growth
nu_n    = 0.02  # Low researcher dropout rate
nu_p    = 0.02  # Low leader dropout rate
k       = 40    # Carrying capacity of research groups

# Initial benefit-cost parameters (Now tuned dynamically)
k_BC    = .5    # Stronger steepness to push equilibrium beyond 20
x0_BC   = 0.05   # Benefit kicks in earlier
kphi    = 30.0   # Sharper activation function for bistability

# Adaptive step sizes for tuning
x0_adapt_rate = 0.05  # How fast we adapt x0_BC
kBC_adapt_rate = 0.2  # Faster adaptation of benefit steepness
mu_adapt_rate = 0.15  # Allow group formation rate to adjust dynamically

# Sweep over benefit strength alpha
alpha_values = np.linspace(0.0, 3.0, 80)
N_grid       = np.linspace(0., 40., 51)

# ------------------------------------------------
# 2) Define logistic-based functions
# ------------------------------------------------

def B(N, P, alpha, x0_BC):
    """ Benefit function using logistic shape. """
    return alpha / (1.0 + np.exp(-k_BC * (P / (N + 1e-6) - x0_BC)))

def C(N, P, x0_BC):
    """ Cost function using logistic shape. """
    return 1.0 / (1.0 + np.exp(k_BC * (P / (N + 1e-6) - x0_BC)))

def F(N, P, alpha, x0_BC):
    """ Difference in benefit and cost activation. """
    return (1.0 / (1.0 + np.exp(-kphi * (B(N+1, P-1, alpha, x0_BC) - C(N+1, P-1, x0_BC))))) - \
           (1.0 / (1.0 + np.exp(-kphi * (B(N, P, alpha, x0_BC) - C(N, P, x0_BC)))))

def dN_dt(N, P, alpha, x0_BC):
    """ Mean-field equation for N with dynamic parameters. """
    return mu * N * (1 - (N + P) / k) - nu_n * N + F(N, P, alpha, x0_BC)

def dN_dt_derivative(N, P, alpha, x0_BC, eps=1e-8):
    """ Numerical derivative for stability analysis. """
    return (dN_dt(N+eps, P, alpha, x0_BC) - dN_dt(N-eps, P, alpha, x0_BC)) / (2.0 * eps)

# ------------------------------------------------
# 3) Find equilibria and dynamically adjust parameters
# ------------------------------------------------

stable_alpha   = []
stable_N       = []
unstable_alpha = []
unstable_N     = []

for a in alpha_values:
    eq_solutions = []
    
    # Bracket search for equilibria
    for i in range(len(N_grid)-1):
        Nlo = N_grid[i]
        Nhi = N_grid[i+1]
        f_lo = dN_dt(Nlo, Nlo, a, x0_BC)
        f_hi = dN_dt(Nhi, Nhi, a, x0_BC)
        if f_lo * f_hi > 0:
            continue  # No root in this bracket
        try:
            sol = root_scalar(lambda N: dN_dt(N, N, a, x0_BC), bracket=[Nlo, Nhi], method='brentq')
            if sol.converged:
                N_star = sol.root
                # Avoid duplicate solutions
                if not any(abs(N_star - s) < 1e-4 for s in eq_solutions):
                    eq_solutions.append(N_star)
        except:
            pass
    
    # Stability check & dynamic parameter tuning
    avg_N = np.mean(eq_solutions) if eq_solutions else 0
    for N_star in eq_solutions:
        df = dN_dt_derivative(N_star, N_star, a, x0_BC)
        if df < 0:
            stable_alpha.append(a)
            stable_N.append(N_star)
        else:
            unstable_alpha.append(a)
            unstable_N.append(N_star)

    # ----------------
    # Dynamic Parameter Updates
    # ----------------
    if avg_N < 15:  # If groups are too small, encourage larger groups
        x0_BC -= x0_adapt_rate  # Make benefit kick in sooner
        k_BC -= kBC_adapt_rate  # Smooth out benefit-cost transition
        mu += mu_adapt_rate     # Boost recruitment for larger groups

    elif avg_N > 30:  # If groups are too large, slow growth
        x0_BC += x0_adapt_rate  # Delay benefit onset slightly
        k_BC += kBC_adapt_rate  # Sharpen transitions to slow growth
        mu -= mu_adapt_rate     # Reduce recruitment

    # Keep values within reasonable bounds
    x0_BC = np.clip(x0_BC, 0.05, 0.5)
    k_BC = np.clip(k_BC, 1.0, 10.0)
    mu = np.clip(mu, 1.0, 10.0)

# ------------------------------------------------
# 4) Plot the Bifurcation Diagram
# ------------------------------------------------

plt.figure(figsize=(7,5))
plt.scatter(stable_alpha, stable_N, color='blue', s=25, label='Stable')
plt.scatter(unstable_alpha, unstable_N, facecolors='white',
            edgecolors='blue', s=60, label='Unstable')
plt.ylim(-0.05, max(N_grid) + 1)
plt.xlabel(r'$\alpha$ (strength of benefit)')
plt.ylabel(r'$N$ (prey population / group size)')
plt.title("Bifurcation Diagram with Adaptive Feedback")
plt.grid(True)
plt.legend()
plt.show()
