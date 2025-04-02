using Pkg; Pkg.activate(".")
using RecursiveArrayTools, OrdinaryDiffEq, Plots, Measures

# -----------------------------
#  Model helper functions 
# -----------------------------

# transition rate

# bl = baseline so that the cost of learning to code doesn't go to zero
#      and that the benefit and cost at first is not one.
#      we do the same for the group pressure to code


B(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                   # benefit
C(x, kc, x0c, bl, r) = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl    # cost
Π(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                         # group pressure to code

# combine all that into a sigmoid
tau_rescaling = 20
τ(x, ktau, a, kc, x0c, bl, r) = tau_rescaling*(1. / (1. + 5*exp(-ktau * (B(x, a, bl, r) - C(x, kc, x0c, bl, r) + Π(x, a, bl, r)))) )

# -----------------------------
# Visualizing helper functions
# -----------------------------


function full_plot()
    p1 = plot(x -> B(x, a, bl, r), 0, 1, label="Benefit(x) = $(1-r*bl)*exp(-$a*x) + $bl ", lw=2, c=:blue, legend=:outertop)
    plot!(x -> C(x, kc, x0c, bl, r), 0, 1, label="Cost(x) = $(1-r*bl)*(1 / (1 + exp($(kc) * (x - $(x0c)))) + $bl", lw=2, c=:red)
    plot!(x -> Π(x, a, bl, r), 0, 1, label="Π(x) = $(1 - r*bl)*exp(-$a*x) + $bl (group pressure to code)", lw=2, c=:aqua)
    xlabel!("#prog/gsize")
    ylims!(0, 1)

    p2 = plot(x -> (B(x, a, bl, r) - C(x, kc, x0c, bl, r)), 0, 1, label="B(x) - C(x)", lw=2, c=:grey, legend=:outertop)
    plot!(x -> (B(x, a, bl, r) - C(x, kc, x0c, bl, r) + Π(x, a, bl, r)), 0, 1, label="B(x) - C(x) + Π(x)", lw=2, c=:black, legend=:outertop)
    xlabel!("#prog/gsize")

    p3 = plot(x -> τ(x, ktau, a, kc, x0c, bl, r), 0, 1, label="τ(x) = 1 / ( 1 + 5*exp(-$ktau * (B(x) - C(x) + Π(x))) )", legend=:outertop)
    xlabel!("p/s")
    ylabel!("τ(x)")

    myplot = plot(p1, p2, p3, layout=(1,3), size=(1200,400), margin = 10mm)
    savefig(myplot, "new_hope.png")
    return myplot
end

# ktau, a, kc, x0c, bl, r =  5.0, 3.0, 5.0, 0.1, 0.1, 5 # F(X) params
ktau=10.0
a=1.5
bl=0.05
kc=30.0
x0c=0.3
r=3

full_plot()

# Just Tau

plot(x -> τ(x, ktau,  a, kc, x0c,  bl, r), 0, 1)
plot!(x -> τ(x, 1, -2, 5, 0,  bl, r), 0, 1)
ylabel!("τ(x)")
xlabel!("p/s")

# Just Cost

plot(x -> C(x, kc, x0c, bl, r), 0, 1)
plot!(x -> C(x, kc, 0, bl, r), 0, 1)
plot!(x -> C(x, 50, 0.3, bl, r), 0, 1)
ylabel!("c(x)")
ylims!(0, 1)
xlabel!("p/s")

# Just Benefit

plot(x -> B(x, a, bl, r) + Π(x, a, bl, r), 0, 1)
plot!(x -> B(x, 6, bl, r) + Π(x, 6, bl, r), 0, 1)
plot!(x -> B(x, 1, bl, r) + Π(x, 1, bl, r), 0, 1)
ylabel!("B(x)")
ylims!(0, 1)
xlabel!("p/s")




# ----------------
# The model
# ----------------


function comp_transition!(du, u, p, t)
    G = u 
    N, P = size(G) # Prob dist of groups, max N non-prog, max P prog
    μ, νn, νp, K, ktau, α, kc, x0c, bl, r  = p 

    for n=1:N, p=1:P

        nb_non_prog, nb_prog = n-1, p-1 # distinguish actual number of programmers from indices
        # gsize = nb_non_prog + nb_prog # varying group size
        
        nb_non_prog < N-1 && ( du[n,p] -= μ*(nb_non_prog + nb_prog)*(1 - (nb_non_prog + nb_prog)/K)*G[n,p] )  # Prey birth output
        nb_non_prog > 0 && ( du[n,p] += μ*(nb_non_prog + nb_prog - 1)*(1 - (nb_non_prog + nb_prog - 1)/K) *G[n-1,p] )  # Prey birth input
        
        du[n,p] -= νn*nb_non_prog*G[n,p]                                  # Prey deaths output (from graduation)
        nb_non_prog < N-1 && ( du[n,p] += νn*(nb_non_prog+1)*G[n+1,p] )   # Prey deaths input (from graduation) 
                
        du[n,p] -= νp*nb_prog*G[n,p]                                # predator death output
        nb_prog < P-1 && ( du[n,p] += νp*(nb_prog+1)*G[n,p+1] )   # Predator death input

        if gsize > 0
            nb_prog < P-1 && ( du.x[n][p] -= τ((nb_prog)/gsize, ktau, α, kc, x0c, bl, r) * (1. - C((nb_prog)/gsize,  kc, x0c, bl, r)) * (nb_non_prog) * G[n,p] )  # Predation input
            if (nb_non_prog < N-1 && nb_prog > 0 && nb_prog < P)
                du.x[n][p] += τ((nb_prog-1)/gsize, ktau, α, kc, x0c, bl, r) * (1. - C((nb_prog-1)/gsize, kc, x0c, bl, r)) * (nb_non_prog+1) * G.x[n+1][p-1]  # Predation input  
            end 
            # try and fails.
            du.x[n][p] -= τ(nb_prog/gsize, ktau, α, kc, x0c, bl, r) * C(nb_prog/gsize,  kc, x0c, bl, r) * nb_non_prog * G[n,p]  # Predation output
        end

        nb_non_prog < N-1 && ( du.x[n][p] += τ(nb_prog/(gsize+1), ktau, α, kc, x0c, bl, r) * C(nb_prog/(gsize+1),  kc, x0c, bl, r) * (nb_non_prog+1) * G.x[n+1][p] )  # Predation output
    end
end


# n,p = 10,10
# nb_prog, nb_non_prog = n-1, p-1
# gsize = nb_non_prog+nb_prog

# (
#     τ((nb_prog-1)/gsize, ktau, a, kc, x0c, bl, r)
#     * (1. - C((nb_prog-1)/gsize, kc, x0c, bl, r)) 
#     * (nb_non_prog+1) 
#     # * u₀.x[n+1][p-1]  
# )

# (
#     τ(nb_prog/gsize, ktau, a, kc, x0c, bl, r) 
#     * C(nb_prog/gsize,  kc, x0c, bl, r) 
#     * nb_non_prog 
#     # * u₀.x[n][p]
# ) 

# ----------------
# Simulate dynamics
# ----------------


# Initial conditions
N = P = 20
# u₀ = ArrayPartition(Tuple([zeros(N, P)[p,:] for p=1:P]))
u₀ = zeros(N,P)
# u₀.x[15][1] = 1.0
u₀[15,1] = 0.5
u₀[1,15] = 0.5
tmax = 2
tspan = (1.0,  tmax)

# Parameters
μ1, νn, νp, K = 20.0, 10.0, 10.0, 20.0 # trad birth-death params
# ktau, a, kc, x0c, bl, r =  5.0, 3.0, 5.0, 0.3, 0.1, 5 # F(X) params
params = ( μ1, νn, νp, K, ktau, a, kc, x0c, bl, r)

# Solve problem
prob = ODEProblem(comp_transition!, u₀, tspan, params)
sol = solve(prob, Tsit5())


# ----------------
# Explore
# ----------------

sum(sol)

sum(parse_sol(sol))

function parse_sol(sol)
    res = zeros(N,P)
    for n in 1:N
        for p in 1:P
            res[n,p] = sol.u[tmax].x[n][p]
        end
    end
    return res
end 


function parse_like_python(sol)
    raw_sol = parse_sol(sol)
    res_python = fill(-7.0, N, P)
    for d1 = 1:size(raw_sol,2)
        for d2 = 1:size(raw_sol,1)
            y_val = raw_sol[d1,d2]
            if y_val > 1e-6
                res_python[d1, d2] = log10(y_val)
            else
                res_python[d1, d2] = -7.0  # effectively "below detection"
            end
        end
    end
    return res_python
end

# 7) Plot
heatmap(
    parse_like_python(sol),
    color=:RdYlGn,  # Colormap
    xlabel="Number of programmers (d2)",
    ylabel="Number of non-programmers (d1)",
    title="Final Distribution at t=$tmax",
    clims=(-6, 0),  # Color scale range
    yflip=true  # Invert y-axis
)
