using RecursiveArrayTools, OrdinaryDiffEq, Plots, Measures


# -----------------------------
#  Model helper functions 
# -----------------------------

# transition rate

# bl = baseline so that the cost of learning to code doesn't go to zero
#      and that the benefit and cost at first is not one.
#      we do the same for the group pressure to code

B(x, α, bl, r) = (1. - r*bl)*exp(-α*x) + bl                   # benefit
C(x, kc, x0c, bl, r) = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl     # cost
Π(x, α, bl, r) = (1. - r*bl)*exp(-α*x) + bl                         # group pressure to code

# combine all that into a sigmoid
τ(x, ktau, α, kc, x0c, bl, r) = 1. / (1. + 5*exp(-ktau * (B(x, α, bl, r) - C(x, kc, x0c, bl, r) + Π(x, α, bl, r))))


# -----------------------------
# Visualizing helper functions
# -----------------------------

ktau, α, kc, x0c, bl, r =  5.0, 3.0, 20.0, 0.3, 0.1, 5

p1 = plot(x -> B(x, α, bl, r), 0, 1, label="Benefit(x) = $(1-r*bl)*exp(-$α*x) + $bl ", lw=2, c=:blue, legend=:outertop)
plot!(x -> C(x, kc, x0c, bl, r), 0, 1, label="Cost(x) = $(1-r*bl)*(1 / (1 + exp($kc * (x - $x0c))) + $bl", lw=2, c=:red)
plot!(x -> Π(x, α, bl, r), 0, 1, label="Π(x) = $(1 - r*bl)*exp(-$α*x) + $bl (group pressure to code)", lw=2, c=:aqua)
xlabel!("#prog/gsize")
ylims!(0, 1)

p2 = plot(x -> (B(x, α, bl, r) - C(x, kc, x0c, bl, r)), 0, 1, label="B(x) - C(x)", lw=2, c=:grey, legend=:outertop)
plot!(x -> (B(x, α, bl, r) - C(x, kc, x0c, bl, r) + Π(x, α, bl, r)), 0, 1, label="B(x) - C(x) + Π(x)", lw=2, c=:black, legend=:outertop)
xlabel!("#prog/gsize")

p3 = plot(x -> τ(x, ktau, α, kc, x0c, bl, r), 0, 1, label="τ(x) = 1 / ( 1 + 5*exp(-$ktau * (B(x) - C(x) + Π(x))) )", legend=:outertop)
xlabel!("p/s")
ylabel!("τ(x)")

myplot = plot(p1, p2, p3, layout=(1,3), size=(1200,400), margin = 10mm)
savefig(myplot, "new_hope.png")

# ----------------
# The model
# ----------------


function comp_transition!(du, u, p, t)
    G, N, P = u, length(u.x[1]), length(u.x[1]) # Prob dist of groups, max N non-prog, max P prog
    μ, νn, νp, K, ktau, α, kc, x0c, bl, r   = p 

    for n=1:N, p=1:P
        nb_non_prog, nb_prog = n-1, p-1 # distinguish actual number of programmers from indices
        gsize = nb_non_prog + nb_prog # varying group size
        
        nb_non_prog < N-1 && ( du.x[n][p] -= μ*gsize*(1. - gsize/K)*G.x[n][p] )  # Prey birth output
        nb_non_prog > 0 && ( du.x[n][p] += μ*(gsize-1)*(1. - (gsize-1)/K)*G.x[n-1][p] )  # Prey birth input
    
        du.x[n][p] -= νn*nb_non_prog*G.x[n][p]                                  # Prey deaths output (from graduation)
        nb_non_prog < N-1 && ( du.x[n][p] += νn*(nb_non_prog+1)*G.x[n+1][p] )   # Prey deaths input (from graduation) 
        
        du.x[n][p] -= νp*nb_prog*G.x[n][p]                                # predator death output
        nb_prog < P-1 && ( du.x[n][p] += νp*(nb_prog+1)*G.x[n][p+1] )   # Predator death input

        if gsize > 0
            nb_prog < P-1 && ( du.x[n][p] -= τ((nb_prog)/gsize, ktau, α, kc, x0c, bl, r) * (1. - C((nb_prog)/gsize,  kc, x0c, bl, r)) * (nb_non_prog) * G.x[n][p] )  # Predation input
            if (nb_non_prog < N-1 && nb_prog > 0 && nb_prog < P)
                du.x[n][p] += τ((nb_prog-1)/gsize, ktau, α, kc, x0c, bl, r) * (1. - C((nb_prog-1)/gsize, kc, x0c, bl, r)) * (nb_non_prog+1) * G.x[n+1][p-1]  # Predation input  
            end 

            du.x[n][p] -= τ(nb_prog/gsize, ktau, α, kc, x0c, bl, r) * C(nb_prog/gsize,  kc, x0c, bl, r) * nb_non_prog * G.x[n][p]  # Predation output
        end

        nb_non_prog < N-1 && ( du.x[n][p] += τ(nb_prog/(gsize+1), ktau, α, kc, x0c, bl, r) * C(nb_prog/(gsize+1),  kc, x0c, bl, r) * (nb_non_prog+1) * G.x[n+1][p] )  # Predation output
    end
end


# ----------------
# Simulate dynamics
# ----------------


# Initial conditions
N = P = 20

u₀ = ArrayPartition(
    Tuple([zeros(N, P)[p,:] for p=1:P])
    )

u₀.x[1][16] = 1.0

tmax = 5.0
tspan = (1.0,  tmax)

# Parameters
μ, νn, νp, K = 0.1, 0.1, 0.1, 40.0 # trad birth-death params
ktau, α, kc, x0c, bl, r =  5.0, 3.0, 20.0, 0.3, 0.1, 5
params = ( μ, νn, νp, K, ktau, α, kc, x0c, bl, r )

# Solve problem
prob = ODEProblem(comp_transition!, u₀, tspan, params)
sol = solve(prob, Tsit5())


# ----------------
# Explore
# ----------------


sol_mat = []
for n=1:N, p=1:P
    push!(sol_mat, sol(tmax).x[n][p])
end

sum(sol_mat)