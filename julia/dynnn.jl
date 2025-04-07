using Pkg; Pkg.activate(".")
using OrdinaryDiffEq, DuckDB, DataFrames, DiffEqCallbacks, LinearAlgebra
using Plots, Plots.Measures

include("./helpers.jl")

SRC_DIR = joinpath(pwd(), "julia")
RES_DIR = joinpath(SRC_DIR, "experiments", "results")

model_version = "v1"
include(joinpath(SRC_DIR, "experiments", "models", "bistability_model_$(model_version).jl")) # we version control the models

# ---------------------
# Parameters & Setup
# ---------------------

tmax = 500
tspan    = (0.0, tmax)

nb_of_states = 10
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  

# Model parameters
α, νn, νp = 0.9, 0.2, 0.2 # trad birth-death params
# α, νn, νp = 1.5, 0.25, 0.25 # trad birth-death params
# α, νn, νp = 100, 10, 10 # trad birth-death params

# Note
# K is the research group (PIs) carrying capacity. 
# If K > nb_of_states, the non-programmer population can grow indefinitely.
# So a K = 30 with nb_of_states=15, mass can saturate on the sides of the plots
# but reduced on the bottom right (when 15progs and 15 non-progs). We use the full 
# matrix when we do so.
# else if K = nb_of_states, the diagonal is the hard cutoff. Cannot go beyond that.
# else K < nb_of_states, right now it leaks again, for some reasons.
K = 14

ktau =  25.0
a = 7.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5

# other params defined at the top
p = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)

# viz functions from helpers
full_plot(p)

# --------------------
# Solve and plot the ODE
# ---------------------

cb_save, Rvals = make_saving_callback(τ, C);
cbset = CallbackSet(cb_save);

prob = ODEProblem(J!, x0, tspan, p);
sol  = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8, saveat = 0.01)  

sum(sol[end])
@assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"

# plot(tracker.diffs, yscale=:log10, label="Convergence")
# hline!([1e-6], color=:red, linestyle=:dash, label="Convergence threshold")

# At the end, you can retrieve the time series:
times                = Rvals.t
death_cost_series    = [v.R for v in Rvals.saveval]
avg_num_programmers  = [v.avg_num_programmers for v in Rvals.saveval]
avg_frac_programmers = [v.avg_frac_programmers for v in Rvals.saveval]
cumulative_loss = [v.cumulative_loss for v in Rvals.saveval]


println("final time Rvals: $(times[end])")
println("final average number of programmers: $(avg_num_programmers[end])")

# ---------------------
#
# Selected params plotting
#
# ---------------------


l = @layout [a{0.7h}  ; b c]

p1 = heatmap(
    parse_like_python(sol[end]),               
    xlabel = "Number of programmer",
    ylabel = "Number of non-programmer",
    colorbar_title = "log10(Occupation)",
    yflip = true,  # if you want the (0,0) coordinate in the top-left corner like imshow
    title = "χ=$(round(1/a, digits=2)), ktau=$ktau, kc=$kc, x0c=$x0c, bl=$bl, r=$r, tau_rescaling=7", titlefontsize=10
);

p2 = plot(
    times[2:end], 
    cumsum(death_cost_series[2:end]), xlabel="time to finish transition", ylabel="CumulativeDeaths", lw=3, legend=false,
    # yscale=:log10, 
    # xscale=:log10, minorgrid=true
);

p3 = plot(
    times[2:end], color="orange", lw=3,
    avg_num_programmers[2:end], 
    # xscale=:log10, 
    xlabel="time to finish transition", ylabel="Avg #progs", legend=false,
    # minorgrid=true,
    # xlims = (Inf, 1e+5)
    );

plot(p1,p2,p3, layout=l, size=(600,600))
# savefig("figs/heatmap_never_ending.pdf")


# ---------------------
#
# Movie time
#
# ---------------------

time_points = 0:1:200  # adjust interval as desired for smoothness

anim = @animate for t in time_points
    heatmap(
        parse_like_python(sol(t)),
        xlabel = "Number of programmer",
        ylabel = "Number of non-programmer",
        colorbar_title = "log₁₀(Occupation)",
        clim=(-7,0),
        yflip = true,
        title = "Time = $(round(t, digits=1))",
        size=(600,500)
    )
end

gif(anim, "solution_deaths.gif", fps = 10)

# death movie

anim = @animate for t in time_points
    plot(times, cumsum(death_cost_series), 
        xlabel="time", ylabel="R(t)", title="Death Cost Rate over Time (steps=$t)")
end


gif(anim, "solution_deaths.gif", fps = 10)

# time evolution movie

anim = @animate for t in time_points
     plot(1:nb_of_states, vec(sum(sol(t), dims=1)), marker = :o, 
          linestyle = :dash, label="prog", title="t=$t", xlabel="# people", ylabel="fraction")
     plot!(1:nb_of_states, vec(sum(sol(t), dims=2)), marker = :o, 
          linestyle = :dash, label="non-prog")
end

gif(anim, "solution_time_evo.gif", fps = 1)


# ---------------------
#
# Sweep
#
# ---------------------

tmax = 500
tspan    = (0.0, tmax)

ktau =  25.0
a = 3.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5

α, νn, νp = 0.9, 0.2, 0.2 # trad birth-death params
# α, νn, νp = 3, 1, 1 # trad birth-death params

# other params defined at the top
p = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)

χ_c_vals = reverse(0.06:0.01:0.33)

out = []
for x in χ_c_vals
    a_val = 1 / x
    cb_save, saved_vals = make_saving_callback(τ, C)
    cbset = CallbackSet(cb_save)

    p = (α, νn, νp, K, ktau, a_val, kc, x0c, bl, r)
    
    prob = ODEProblem(J!, x0, tspan, p)
    sol  = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8, saveat=0.01)  
    
    @assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"
    
    # At the end, you can retrieve the time series:
    
    last_time                = saved_vals.t
    last_death_cost_series    = [v.R for v in saved_vals.saveval]
    cumulative_loss = [v.cumulative_loss for v in saved_vals.saveval]
    last_avg_num_programmers  = [v.avg_num_programmers for v in saved_vals.saveval]
    last_avg_frac_programmers = [v.avg_frac_programmers for v in saved_vals.saveval]
    
    push!(out, (x, last_time, last_death_cost_series, last_avg_num_programmers, last_avg_frac_programmers, cumulative_loss))
end

final_as = [x[1] for x in out]
final_deaths = [x[3][end] for x in out]
final_avg_progs = [x[4][end] for x in out]
final_cumdeath = [x[6][end] for x in out]

# plot 1

scatter(final_deaths, final_avg_progs, line_z = final_as, 
        color=:viridis, 
        ylabel="final avg progs", xlabel="last R(t)", label=false)

# plot 1

# plot(
#     plot(final_as, final_times, marker=:circle,  ylabel="Final time (log10)", legend=false, 
#          title = "ktau=$ktau, kc=$kc, x0c=$x0c, bl=$bl, r=$r, tau_rescaling=5, K=$K", 
#          yscale=:log10, minorgrid=true,
#          titlefontsize=10),
#     plot(final_as, final_deaths, marker=:circle, 
#          color="orange", ylabel="costDeathsCum", legend=false), 
#     plot(final_as, final_avg_progs, marker=:circle, xlabel="χ", 
#          color="green", ylabel="avgProgs", legend=false), 
#     layout=(3,1), size=(700,800), sharey=true
# )

# savefig("figs/sweep_chi.pdf")

final_as = [x[1] for x in out]
final_times = [x[2] for x in out]
final_deaths = [x[3] for x in out]
final_avg_progs = [x[4] for x in out]
final_frac = [x[5] for x in out]
final_cum_loss = [x[6] for x in out]



# chosen_chi = 1:length(final_as)
chosen_chi = 10:4:length(final_as)-10
# chosen_chi = vcat(chosen_chi, [length(final_as)-1])
function make_plot_chi(xs, ys, scale, colorbar)
    p = plot(
        xscale = scale,
        minorgrid = true,
        size = (700, 500),
        legend = false,
        colorbar_title = "χ",  # for the line_z scale
        colorbar = colorbar,
    )
    
    # loop over each series and plot it
    for (x, y, a) in zip(xs, ys, final_as[chosen_chi])
        plot!(p,
            x, y,
            lw = 3,
            line_z = fill(a, length(x)),  # constant value along the line
            color = :viridis,
        )
    end
    return p
end

l = @layout [ [a ; b]  c]

p1=make_plot_chi(final_times[chosen_chi], final_avg_progs[chosen_chi], :log10, false)
xlabel!("time")
ylabel!("Avg #progs")

p2=make_plot_chi(final_times[chosen_chi], cumsum.(final_deaths[chosen_chi]), :identity, true)
xlabel!("time")
ylabel!("Deaths due to transition")


# scatter(
#     [cumsum(x)[end] for x in final_deaths[chosen_chi]], 
#     marker=:circle,
#     final_as[chosen_chi],
#     marker_z = final_as[chosen_chi],
#     color = :viridis,
#     label=false, 
#     xlabel="deaths due transition",
#     ylabel="χ",
# )

# plot(p1,p2, layout=(2,1), sharex=true, size=(500, 500))

p3=make_plot_chi(cumsum.(final_deaths[chosen_chi]), final_avg_progs[chosen_chi], :identity, true)
ylabel!("Avg #progs")
xlabel!("Final cumulative deaths")

plot(p1,p2,p3, layout=l, size=(800, 500))

savefig("figs/sweep_chi_deaths.png")




# ---------------------
#
# Parameter Sweep
#
# ---------------------


# # correspond to output in YAM:
# swept_par_fname = "sweep_a_ktau_v1"

# df = load_sweep_results(joinpath(RES_DIR, "sweeps.duckdb"), swept_par_fname)
    
# # we change by hand
# swept_params = ["a", "ktau"]
# # Sort unique param values
# unique_a     = sort(unique(df.a))
# unique_ktau  = sort(unique(df.ktau))
    
# # Create a 2D array to store final_fraction
# df_matrix = Matrix{Union{Missing,Float64}}(undef, length(unique_ktau), length(unique_a))
    
# # Fill in each cell
# for row in eachrow(df)
#         i = findfirst(==(row.ktau),  unique_ktau)
#         j = findfirst(==(row.a), unique_a)
#         df_matrix[i, j] = row.final_fraction
# end

# heatmap(
#     unique_a,          # x-axis
#     unique_ktau,       # y-axis
#     df_matrix,         # z-values
#     xlabel="a",
#     ylabel="ktau",
#     colorbar_title="Final Fraction of Programmers",
#     title="Phase Diagram"
# )


# ---------------------
#
# hysteresis
#
# ---------------------


function run_model_with_chi_c(chi_c_val, x_init)
    a_val = 1 / chi_c_val
    cb_save, saved_vals = make_saving_callback(τ, C)
    cbset = CallbackSet(cb_save, conv_cb)
    tmax = 1000
    tspan = (0.0, tmax)
    p = (α, νn, νp, K, ktau, a_val, kc, x0c, bl, r)
    prob = ODEProblem(J!, x_init, tspan, p)
    sol = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8, dt=0.01)  
    @assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"
    return sol, saved_vals
end



ktau = 25.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5
K = 30

function plot_hysteresis_loop()
    nb_of_states = 15
    x0 = zeros(nb_of_states, nb_of_states)

    # Upsweep
    chi_c_vals_up   = range(0.03, stop=0.20, length=40)
    prog_frac_up = Float64[]
    x0[nb_of_states, 1] = 1.0  
    x_init = x0
    
    for chi_c in chi_c_vals_up
        sol, saved_vals = run_model_with_chi_c(chi_c, x_init)
        last_avg_frac_programmers = [v.avg_frac_programmers for v in saved_vals.saveval][end]
        push!(prog_frac_up, last_avg_frac_programmers)
        x_init = sol[end]
    end
    
    # Downsweep
    chi_c_vals_down = reverse(chi_c_vals_up)
    prog_frac_down = Float64[]

    for chi_c in chi_c_vals_down
        sol, saved_vals = run_model_with_chi_c(chi_c, x_init)
        last_avg_frac_programmers = [v.avg_frac_programmers for v in saved_vals.saveval][end]
        push!(prog_frac_down, last_avg_frac_programmers)
        x_init = sol[end]
    end

    # Plot hysteresis loop
    plot(chi_c_vals_up, prog_frac_up, label="Up sweep", marker=:diamond)
    plot!(chi_c_vals_up, reverse(prog_frac_down), label="Down sweep", marker=:circle)
    xlabel!("χ_c (critical programmer fraction)")
    ylabel!("Final fraction of programmers")
    title!("ktau=$ktau, kc=$kc, x0c=$x0c, tau_rescaling=5", titlefontsize=10)
end

plot_hysteresis_loop()
savefig("figs/hysteresis_loop.pdf")

### CHATGPT implementation


function run_model_with_chi_c(chi_c_val, x_init)
    a_val = 1 / chi_c_val
    cb_save, saved_vals = make_saving_callback(τ, C)
    cbset = CallbackSet(cb_save, conv_cb)
    tmax = 1000
    tspan = (0.0, tmax)
    p = (α, νn, νp, K, ktau, a_val, kc, x0c, bl, r)
    prob = ODEProblem(J!, x_init, tspan, p)
    sol = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8, dt=0.01)  
    @assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"
    last_avg_frac_programmers = [v.avg_frac_programmers for v in saved_vals.saveval][end]
    return last_avg_frac_programmers
end


function plot_bifurcation()
    nb = 15
    chi_c_vals = range(0.01, stop=0.18, length=100)
    
    prog_frac_low_init = Float64[]
    prog_frac_high_init = Float64[]

    for chi_c in chi_c_vals
        # Low-programmer init (just one non-programmer)
        x0_low = zeros(nb, nb)
        x0_low[nb, 1] = 1.0
        push!(prog_frac_low_init, run_model_with_chi_c(chi_c, x0_low))

        # High-programmer init (just one programmer)
        x0_high = zeros(nb, nb)
        x0_high[nb, nb] = 1.0
        push!(prog_frac_high_init, run_model_with_chi_c(chi_c, x0_high))
    end

    plot(chi_c_vals, prog_frac_low_init, label="prog_frac_up", marker=:circle)
    plot!(chi_c_vals, prog_frac_high_init, label="prog_frac_down", marker=:diamond)
    xlabel!("χ_c (critical programmer fraction)")
    ylabel!("Final average programmer fraction")
    title!("Bifurcation diagram — low vs. high initial conditions")
    vline!([0.125, 0.165], linestyle=:dash, color=:gray, label="")
end

plot_bifurcation()


# ---------------------
#
# Density plot
#
# ---------------------


using CairoMakie


K = 30
α, νn, νp = 0.9, 0.2, 0.2 # trad birth-death params
ktau =  25.0
a = 3.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5
tmax = 1000.0
tspan    = (0.0, tmax)
nb_of_states = 15
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  

chi_c_vals = range(0.03, stop=0.20, length=9)
chi_c_vals_labs   = ["χ=$(round(c, digits=3))" for c in chi_c_vals]

tracker = ConvergenceTracker(copy(x0))
conv_cb = make_convergence_callback(tracker, 1e-6)

f = Figure(size=(500,700))
ax = Axis(f[1, 1], yticks = (1:9, reverse(chi_c_vals_labs)), xlabel="# programmers")

for (i,chi) in enumerate(reverse(chi_c_vals))
    a = 1/chi
    println("i = $i, a = $a")    
    p    = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)
    prob = ODEProblem(J!, x0, tspan, p)
    sol  = solve(prob, callback=conv_cb, abstol=1e-6, reltol=1e-8, dt=0.01)

    # sum_num_progs = round.(vec(sum(sol[end], dims=1)), digits=4)
    sum_num_progs = vec(sum(sol[end], dims=1))

    d = barplot!(
        1:length(sum_num_progs),
        sum_num_progs,
        offset      = i,   # integer offsets
        gap = 0,
        color = sum_num_progs,
        strokewidth = 1,
        strokecolor = :black,
    )

    translate!(d, 0, 0, -0.1i)
end

f
save("bimodality.png", f)





# ---------------------
#
# Sweep - PHASE DIAGRAM
#
# ---------------------

tmax = 10_000.0
tspan    = (0.0, tmax)

ktau =  25.0
a = 3.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5
K=30

α, νn, νp = 1.5, 0.25, 0.25 # trad birth-death params

# other params defined at the top
p = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)

using Base.Threads
Threads.nthreads() = 8
nb_of_states = 15
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  
tracker = ConvergenceTracker(copy(x0), Inf, Float64[]);
conv_cb = make_convergence_callback(tracker, 1e-6);

χ_c_vals = collect(range(0.06, stop=0.25, length=25))
ktau_vals = collect(1:25)
a_vals = 1 ./ χ_c_vals

# Prepare index map and output array
Nχ, Nk = length(χ_c_vals), length(ktau_vals)
out = Vector{NTuple{6, Float64}}(undef, Nχ * Nk)

# Generate Cartesian product of parameters with flat indexing
params_list = [(i, j, a_vals[i], ktau_vals[j]) for i in 1:Nχ, j in 1:Nk]

@threads for idx in eachindex(params_list)
    i, j, a_val, ktau = params_list[idx]

    # Define callbacks inside the thread to avoid shared mutable state
    cb_save, saved_vals = make_saving_callback(τ, C)
    cbset = CallbackSet(cb_save, conv_cb)

    p = (α, νn, νp, K, ktau, a_val, kc, x0c, bl, r)
    prob = ODEProblem(J!, x0, tspan, p)

    sol = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8)

    @assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"

    last_time                = saved_vals.t[end]
    last_death_cost_series    = sum([v.R for v in saved_vals.saveval])
    last_avg_num_programmers  = saved_vals.saveval[end].avg_num_programmers
    last_avg_frac_programmers = saved_vals.saveval[end].avg_frac_programmers

    # Store result
    out[idx] = (χ_c_vals[i], ktau, last_time, last_death_cost_series,
                last_avg_num_programmers, last_avg_frac_programmers)
end

# Build zmat and plot
zmat = reshape([x[6] for x in out], Nk, Nχ)'

contour(
    ktau_vals, χ_c_vals, zmat;
    xlabel="ktau",
    ylabel="χ_c",
    color=:plasma,
    fill=true,
    levels=20,
    lw=0.4,
    colorbar_title="Final Fraction of Programmers",
    title = "ktau=$ktau, kc=$kc, x0c=$x0c, bl=$bl, r=$r, tau_rescaling=7, K=$K", 
    titlefontsize=10
)

savefig("figs/phase_diagram.png")

zmat = reshape([sum(x[4]) for x in out], Nk, Nχ)'

contour(
    ktau_vals, χ_c_vals, round.(zmat);
    xlabel="ktau",
    ylabel="χ_c",
    color=:plasma,
    fill=true,
    levels=5,
    lw=0,
    colorbar_title="Cumulative deaths",
    title = "ktau=$ktau, kc=$kc, x0c=$x0c, bl=$bl, r=$r, tau_rescaling=7, K=$K", 
    titlefontsize=10
)

savefig("figs/phase_diagram2.png")


# ---------------------
#
# Sweep - PHASE DIAGRAM - Birth-Death
#
# ---------------------

using Base.Threads

tmax = 10_000.0
tspan    = (0.0, tmax)

ktau =  25.0
a = 3.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5
K=30

α, νn, νp = 1.5, 0.25, 0.25 # trad birth-death params

# other params defined at the top
p = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)

Threads.nthreads() = 8
nb_of_states = 15
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  
tracker = ConvergenceTracker(copy(x0), Inf, Float64[]);
conv_cb = make_convergence_callback(tracker, 1e-6);

α_vals = collect(range(0.08, stop=3, length=20))
ν_vals = collect(range(0.02, stop=1.25, length=20))

# Prepare index map and output array
Nχ, Nk = length(α_vals), length(ν_vals)
out = Vector{NTuple{6, Float64}}(undef, Nχ * Nk)

# Generate Cartesian product of parameters with flat indexing
params_list = [(i, j, α_vals[i], ν_vals[j]) for i in 1:Nχ, j in 1:Nk]

@threads for idx in eachindex(params_list)
    i, j, αval, νval = params_list[idx]

    # Define callbacks inside the thread to avoid shared mutable state
    cb_save, saved_vals = make_saving_callback(τ, C)
    cbset = CallbackSet(cb_save, conv_cb)

    p = (αval, νval, νval, K, ktau, a, kc, x0c, bl, r)
    prob = ODEProblem(J!, x0, tspan, p)

    sol = solve(prob, callback=cbset, abstol=1e-6, reltol=1e-8)

    @assert is_prob_conserved(sol(tmax)) "Occupation number is not conserved"

    last_time                = saved_vals.t[end]
    last_death_cost_series    = sum([v.R for v in saved_vals.saveval])
    last_avg_num_programmers  = saved_vals.saveval[end].avg_num_programmers
    last_avg_frac_programmers = saved_vals.saveval[end].avg_frac_programmers

    # Store result
    out[idx] = (αval, νval, last_time, last_death_cost_series,
                last_avg_num_programmers, last_avg_frac_programmers)
end

# Build zmat and plot
zmat = reshape([x[6] for x in out], Nk, Nχ)'

contour(
    α_vals, ν_vals, zmat;
    xlabel="α",
    ylabel="ν",
    color=:plasma,
    fill=true,
    levels=20,
    lw=0.1,
    colorbar_title="Time finish transition",
    title = "χ=$(round(1/a, digits=2)), ktau=$ktau, kc=$kc, x0c=$x0c, bl=$bl, r=$r, tau_rescaling=7, K=$K", 
    titlefontsize=10
)

savefig("figs/phase_diagram_bd.png")