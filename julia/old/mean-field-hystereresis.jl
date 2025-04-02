using Plots, Roots

# ------------------------------------------------
# 1) Global parameters
# ------------------------------------------------

# Outflow: programmer (graduation) rate
nu_p = 0.1 

# Steepness in the benefit and cost logistic
k_ben = k_cost = 3.0

# Midpoint for benefit and cost logistic
x0_ben = x0_cost = 0.5  

# Steepness of activation; almost a step function at this point
kphi = 12.0

# Sweep over benefit strength alpha
alpha_values = range(0.0, stop=3.0, length=80)
x_grid = range(0.0, stop=1.0, length=51)

# ------------------------------------------------
# 2) Define logistic-based functions
# ------------------------------------------------

benefit(X, alpha) = alpha / (1.0 + exp(-k_ben * (X - x0_ben)))
cost(X) = 1.0 / (1.0 + exp(k_cost * (X - x0_cost)))
phi(z; steep=kphi) = 1.0 / (1.0 + exp(-steep * z))

# ------------------------------------------------
# 3) The ODE: dX/dt = Inflow - Outflow
# ------------------------------------------------

dX_dt(X, alpha) = begin
    net_benefit = benefit(X, alpha) - cost(X)
    inflow = phi(net_benefit, steep=kphi)
    (1.0 - X) * inflow - nu_p * X
end

dX_dt_derivative(X, alpha, eps=1e-8) = 
    (dX_dt(X+eps, alpha) - dX_dt(X-eps, alpha)) / (2.0 * eps)

# ------------------------------------------------
# 4) Find equilibria by bracket search + check stability
# ------------------------------------------------

stable_alpha = Float64[]
stable_X = Float64[]
unstable_alpha = Float64[]
unstable_X = Float64[]

for a in alpha_values
    eq_solutions = Float64[]
    
    for i in 1:(length(x_grid)-1)
        xlo, xhi = x_grid[i], x_grid[i+1]
        f_lo, f_hi = dX_dt(xlo, a), dX_dt(xhi, a)
        
        if f_lo * f_hi > 0
            continue
        end
        
        sol = find_zero(x -> dX_dt(x, a), (xlo, xhi), Roots.Brent())
        
        if !any(abs(sol - s) < 1e-4 for s in eq_solutions)
            push!(eq_solutions, sol)
        end
    end
    
    for x_star in eq_solutions
        df = dX_dt_derivative(x_star, a)
        if df < 0
            push!(stable_alpha, a)
            push!(stable_X, x_star)
        else
            push!(unstable_alpha, a)
            push!(unstable_X, x_star)
        end
    end
end

# ------------------------------------------------
# 5) Plot the bifurcation diagram
# ------------------------------------------------
scatter(stable_alpha, stable_X, color=:blue, label="Stable")
scatter!(unstable_alpha, unstable_X, color=:white, markerstrokecolor=:blue, markersize=6, label="Unstable")
ylims!(-0.05, 1.05)
xlabel!("α (strength of benefit)")
ylabel!("X (fraction of programmers)")
title!("Bistability with All-Logistic Feedback")
