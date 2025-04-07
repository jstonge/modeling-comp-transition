using OrdinaryDiffEq, DiffEqCallbacks


B(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                   # benefit
C(x, kc, x0c, bl, r) = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl    # cost
Π(x, a, bl, r) = (1. - r*bl)*exp(-a*x) + bl                         # group pressure to code
tau_rescaling = 5
τ(x, ktau, a, kc, x0c, bl, r) = tau_rescaling*(1. / (1. + 5*exp(-ktau * (B(x, a, bl, r) - C(x, kc, x0c, bl, r) + Π(x, a, bl, r)))) )

# alternate version of τ
B2(x, a, bl; M=5) =  bl + (M - bl) * exp(-a * x)
τ2(x, ktau, a, kc, x0c, bl, r) = tau_rescaling*(1. / (1. + exp(-ktau * ( B2(x, a, bl) - C(x, kc, x0c, bl, r) ))) )

is_prob_conserved(x) = 0.99 < sum(x) < 1.01

# --- Define helper for convergence callback ---

# Make a global variable to store previous state (will be updated inside callback)
mutable struct ConvergenceTracker
    last_u::Matrix{Float64}
    last_diff::Float64
    diffs::Vector{Float64}
end

const MetricTuple = NamedTuple{
    (:R, :avg_num_programmers, :avg_frac_programmers), 
    Tuple{Float64, Float64, Float64}
}


function make_convergence_callback(tracker::ConvergenceTracker, ϵ::Float64)
    
    function condition(u, t, integrator)
        diff = norm(u .- tracker.last_u)
        push!(tracker.diffs, diff)
        tracker.last_diff = diff
        tracker.last_u .= u
        return diff <= ϵ
    end


    function affect!(integrator)
        # println("Terminating at t = $(integrator.t), diff = $(tracker.last_diff)")
        terminate!(integrator)
    end

    return DiscreteCallback(condition, affect!)
end

function make_saving_callback(τ, C)
    # Mutable containers for cumulative loss and previous time
    cumulative_loss = Ref(0.0)
    last_time = Ref(0.0)

    function death_cost_and_stats(u, t, integrator)
        # Unpack parameters
        α, νn, νp, K, ktau, a, kc, x0c, bl, r = integrator.p

        N, P = size(u)
        R = 0.0
        total_p = 0.0
        total_frac_prog = 0.0
        total_pop_mass = 0.0

        for i in 1:N, j in 1:P
            n1 = i - 1
            n2 = j - 1
            pop = u[i, j]
            gsize = n1 + n2 + 1
            frac = n2 / gsize

            R += τ(frac, ktau, a, kc, x0c, bl, r) * n1 * C(frac, kc, x0c, bl, r) * pop
            total_p += n2 * pop
            total_frac_prog += frac * pop
            total_pop_mass += pop
        end

        denom = total_pop_mass + 1e-12
        avg_num_programmers = total_p / denom
        avg_frac_programmers = total_frac_prog / denom

        # Compute time delta and update cumulative loss
        dt = t - last_time[]
        cumulative_loss[] += R * dt
        last_time[] = t

        return (
            R = R,
            avg_num_programmers = avg_num_programmers,
            avg_frac_programmers = avg_frac_programmers,
            cumulative_loss = cumulative_loss[]
        )
    end

    saved_vals = SavedValues(Float64, NamedTuple{(:R, :avg_num_programmers, :avg_frac_programmers, :cumulative_loss), Tuple{Float64, Float64, Float64, Float64}})
    cb_save = SavingCallback(death_cost_and_stats, saved_vals)
    return cb_save, saved_vals
end



function parse_like_python(sol)
    N, P = size(sol)
    res_python = fill(-7.0, N, P)
    for d1 = 1:size(sol,2)
        for d2 = 1:size(sol,1)
            y_val = sol[d1,d2]
            if y_val > 1e-6
                res_python[d1, d2] = log10(y_val)
            else
                res_python[d1, d2] = -7.0  # effectively "below detection"
            end
        end
    end
    return res_python
end

function load_sweep_results(db_path::String, table_name::String)
    con = DBInterface.connect(DuckDB.DB, db_path)
    sql = "SELECT * FROM $(table_name)"
    df  = DataFrame(DBInterface.execute(con, sql))
    return df
end

function plot_time_evo(sol)
    nb_of_states = size(sol[end], 1)
    t_max = maximum(sol.t)

    p = plot(1:nb_of_states, vec(sum(sol(t_max), dims=1)), marker = :o, linestyle = :dash, label="t=1", xlabel="Number of programmer")

    # for t in 4.0:(t_max/5):t_max
    for t in [3.0, 5.0, 10.]
        p = plot!(1:nb_of_states, vec(sum(sol(t), dims=1)), marker = :o, linestyle = :dash, label="t=$t")
    end

    occupation = vec(sum(sol(t_max), dims=1))
    plot!(1:nb_of_states, occupation, marker = :o, linestyle = :dash, label="t=$t_max")

    xlabel!("Number of programmer")
    ylabel!("Occupation number")
    title!("Master Equation Evolution")
    # savefig("time_evo.png")
end

function full_plot(p)
    α, νn, νp, K, ktau, a, kc, x0c, bl, r  = p 
    ar = round(a, digits=2)
    p1 = plot(x -> B(x, a, bl, r), 0, 1, label="Benefit(x) = $(1-r*bl)*exp(-$ar*x) + $bl ", lw=2, c=:blue, legend=:outertop)
    plot!(x -> C(x, kc, x0c, bl, r), 0, 1, label="Cost(x) = $(1-r*bl)*(1 / (1 + exp($(kc) * (x - $(x0c)))) + $bl", lw=2, c=:red)
    plot!(x -> Π(x, a, bl, r), 0, 1, label="Π(x) = $(1 - r*bl)*exp(-$ar*x) + $bl (group pressure to code)", lw=2, c=:aqua)
    xlabel!("#prog/gsize")
    ylims!(0, 1)

    p2 = plot(x -> (B(x, a, bl, r) - C(x, kc, x0c, bl, r)), 0, 1, label="B(x) - C(x)", lw=2, c=:grey, legend=:outertop)
    plot!(x -> (B(x, a, bl, r) - C(x, kc, x0c, bl, r) + Π(x, a, bl, r)), 0, 1, label="B(x) - C(x) + Π(x)", lw=2, c=:black, legend=:outertop)
    xlabel!("#prog/gsize")

    p3 = plot(x -> τ(x, ktau, a, kc, x0c, bl, r), 0, 1, label="τ(x) = 1 / ( 1 + 5*exp(-$ktau * (B(x) - C(x) + Π(x))) )", legend=:outertop)
    xlabel!("p/s")
    ylabel!("τ(x)")
    
    p4 = plot(x -> τ(x, ktau, a, kc, x0c, bl, r)*(1-C(x, kc, x0c, bl, r)), 0, 1, label=false)
    xlabel!("p/s")
    ylabel!("τ(x)*(1-C(x))")

    myplot = plot(p1, p2, p3, p4, layout=(2,2), size=(800,800), margin = 5mm)
    # savefig(myplot, "new_hope.png")
    return myplot
end

function compare_p4()
    plot(x -> τ(x, ktau, a, kc, x0c, bl, r)*(1-C(x, kc, x0c, bl, r)), 0, 1)

    
    plot!(x -> τ2(x, ktau, a, kc, x0c, bl, r)*(1-C(x, kc, x0c, bl, r)), 0, 1)
    
    xlabel!("p/s")
    ylabel!("τ(x)*(1-C(x))")

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
