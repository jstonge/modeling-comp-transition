using Pkg; Pkg.activate(".")
using OrdinaryDiffEq, Plots, Plots.PlotMeasures, DuckDB, DataFrames

include("./helpers.jl")

SRC_DIR = joinpath(pwd(), "src")
include(joinpath(SRC_DIR, "experiments", "models", "bistability_model_v1.jl")) # we version control the models

# ---------------------
# Parameters & Setup
# ---------------------
t_max = 200.0
tspan    = (0.0, t_max)

nb_of_states = 25
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  

ktau =  10.0
a = 6.0
kc = 30.0
x0c = 0.4
bl = 0.1
r = 5


# Model parameters
α, νn, νp = 0.9, 0.2, 0.2 # trad birth-death params

# Note
# K is the research group (PIs) carrying capacity. 
# If K > nb_of_states, the non-programmer population can grow indefinitely.
# else K < nb_of_states, the non-programmer population will saturate at K.
K = 25

# other params defined at the top
p = (α, νn, νp, K, ktau, a, kc, x0c, bl, r)

# viz functions from helpers
full_plot(p)

# ---------------------
# Solve the ODE
# ---------------------

prob = ODEProblem(J!, x0, tspan, p)
sol  = solve(prob)  

@assert is_prob_conserved(sol(t_max)) "Occupation number is not conserved"

# ---------------------
#
# Selected params plotting
#
# ---------------------

function plot_time_evo(sol)

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

plot_time_evo(sol)

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

heatmap(
    parse_like_python(sol[end]),                # check function for the little hacks
    xlabel = "Number of programmer",
    ylabel = "Number of non-programmer",
    colorbar_title = "log10(Occupation)",
    yflip = true,  # if you want the (0,0) coordinate in the top-left corner like imshow
    title ="size mat = $(size(x0)), Kmax = $K"
)

savefig("output.png")



# ---------------------
#
# Movie time
#
# ---------------------

time_points = 0:1:t_max  # adjust interval as desired for smoothness

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

gif(anim, "solution_evolution.gif", fps = 1)

# time evolution movie

time_points = 0:1:t_max

anim = @animate for t in time_points
     plot(1:nb_of_states, vec(sum(sol(1), dims=1)), marker = :o, 
          linestyle = :dash, label="prog", title="t=$t", xlabel="# people", ylabel="fraction")
     plot!(1:nb_of_states, vec(sum(sol(1), dims=2)), marker = :o, 
          linestyle = :dash, label="non-prog")
end

gif(anim, "solution_time_evo.gif", fps = 1)


round.(vec(sum(sol(1), dims=2)), digits=2)


# ---------------------
#
# Parameter Sweep
#
# ---------------------

function load_sweep_results(db_path::String, table_name::String)
    con = DBInterface.connect(DuckDB.DB, db_path)
    sql = "SELECT * FROM $(table_name)"
    df  = DataFrame(DBInterface.execute(con, sql))
    return df
end
    
df = load_sweep_results("experiments/results/sweeps.duckdb", "sweep_a_x0c_v1")
    
swept_params = ["a", "x0c"]
# Sort unique param values
unique_a     = sort(unique(df.a))
unique_ktau  = sort(unique(df.x0c))
    
# Create a 2D array to store final_fraction
df_matrix = Matrix{Union{Missing,Float64}}(undef, length(unique_ktau), length(unique_a))
    
# Fill in each cell
for row in eachrow(df)
        i = findfirst(==(row.x0c),  unique_ktau)
        j = findfirst(==(row.a), unique_a)
        df_matrix[i, j] = row.final_fraction
end

heatmap(
    unique_a,          # x-axis
    unique_ktau,       # y-axis
    df_matrix,         # z-values
    xlabel="a",
    ylabel="x0c",
    colorbar_title="Final Fraction of Programmers",
    title="Phase Diagram"
)



# ---------------------
#
# hysteresis
#
# ---------------------

function run_model_with_a(a_val, x_init)
    params = (α, νn, νp, K, ktau, a_val, kc, x0c, bl, r)
    prob = ODEProblem(J!, x_init, tspan, params)
    sol = solve(prob)
    return sol
end


# upsweep

a_vals = 1.0:0.5:10.0
prog_frac_up = Float64[]
nb_of_states = 25
x0 = zeros(nb_of_states, nb_of_states)
x0[nb_of_states, 1] = 1.0  
x_init = x0  # same starting point

for a in a_vals
    sol = run_model_with_a(a, x_init)
    push!(prog_frac_up, final_fraction_programmers(sol))
    x_init = sol[end]  # use this as next initial condition
end

# downsweep

a_vals_down = reverse(a_vals)
prog_frac_down = Float64[]
x0 = zeros(nb_of_states, nb_of_states)
x0[1, nb_of_states] = 1.0  

for a in a_vals_down
    sol = run_model_with_a(a, x_init)
    push!(prog_frac_down, final_fraction_programmers(sol))
    x_init = sol[end]
end

# hysteresis loop

plot(a_vals, prog_frac_up, label="Up sweep", marker=:circle)
plot!(a_vals, reverse(prog_frac_down), label="Down sweep", marker=:diamond)
xlabel!("a (group pressure strength)")
ylabel!("Final fraction of programmers")
title!("Hysteresis loop in programmer dynamics")



# 

# Sort unique param values
unique_a     = sort(unique(df.a))
unique_ktau  = sort(unique(df.ktau))

# Create a 2D array to store final_fraction
df_matrix = Matrix{Union{Missing,Float64}}(undef, length(unique_ktau), length(unique_a))

# Fill in each cell
for row in eachrow(df)
    i = findfirst(==(row.ktau),  unique_ktau)
    j = findfirst(==(row.a), unique_a)
    df_matrix[i, j] = row.final_fraction
end

heatmap(
    unique_a,          # x-axis
    unique_ktau,       # y-axis
    df_matrix,         # z-values
    xlabel="a",
    ylabel="ktau",
    colorbar_title="Final Fraction of Programmers",
    title="Phase Diagram"
)