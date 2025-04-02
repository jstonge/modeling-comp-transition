
B(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                   # benefit
C(x, kc, x0c, bl, r) = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl    # cost
Π(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                         # group pressure to code
    
# combine all that into a sigmoid
tau_rescaling = 1
τ(x, ktau, a, kc, x0c, bl, r) = tau_rescaling*(1. / (1. + 5*exp(-ktau * (B(x, a, bl, r) - C(x, kc, x0c, bl, r) + Π(x, a, bl, r)))) )

is_prob_conserved(x) = 0.99 < sum(x) < 1.01


function full_plot(p)
    α, νn, νp, K, ktau, a, kc, x0c, bl, r  = p 
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

    myplot = plot(p1, p2, p3, layout=(1,3), size=(1200,400), margin = 5mm)
    # savefig(myplot, "new_hope.png")
    return myplot
end



function final_fraction_programmers(sol)
    occ = sol[end]
    total = sum(occ)
    if total < 1e-6
        return 0.0
    end
    N, P = size(occ)
    prog = 0:(P-1)
    mean_prog = sum(sum(occ, dims=1) .* prog') / total
    group_size = sum((i-1 + j-1 + 1) * occ[i,j] for i in 1:N, j in 1:P) / total
    return mean_prog / group_size
end




# Define the metric calculation function:
# function final_fraction_programmers(sol)
#     occ = sol[end]  # final state
#     total_prob = sum(occ)
#     if total_prob < 1e-6  # avoid division by tiny number
#         return 0.0
#     end

#     N, P = size(occ)
#     prog_numbers = 0:(P-1)
#     nonprog_numbers = 0:(N-1)

#     # Compute expected number of programmers
#     mean_prog = sum(sum(occ, dims=1) .* prog_numbers') / total_prob

#     # Compute expected group size
#     mean_group = 0.0
#     for i in 1:N, j in 1:P
#         n = i - 1
#         p = j - 1
#         mean_group += (n + p + 1) * occ[i, j]
#     end
#     mean_group /= total_prob

#     return mean_prog / mean_group
# end
