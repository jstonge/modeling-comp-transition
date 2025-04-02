using Pkg; Pkg.activate(".")
using YAML, DuckDB, DataFrames, OrdinaryDiffEq, StatsBase, IterTools
using Base.Threads

include("./helpers.jl")

SRC_DIR = joinpath(pwd(), "julia")
DIR_EXPERIMENT = joinpath(SRC_DIR, "experiments")
DIR_RES = joinpath(SRC_DIR, "results")

################################################################################
# 1) Parse config
################################################################################
# config       = YAML.load_file(joinpath(DIR_EXPERIMENT, "sweeps", "sweep_a_ktau.yaml"))
config       = YAML.load_file(ARGS[1])
model_version= config["model_version"]
output_dir   = config["output_dir"]

# setup paths
include(joinpath(DIR_EXPERIMENT, "models", "bistability_model_" * model_version * ".jl"))

# Parameter sweeps
sweep_keys   = collect(keys(config["sweep"]))
sweep_ranges = Dict(
    k => config["sweep"][k]["start"] : config["sweep"][k]["step"] : config["sweep"][k]["stop"]
    for k in sweep_keys
)

# Fixed
fixed = config["fixed_parameters"]

# Time & initial condition
tspan = Tuple(config["tspan"])
nb    = config["grid_size"]
x0    = zeros(nb, nb)
x0[end, 1] = 1.0


################################################################################
# 3) Generate full combos & run solver
################################################################################
sweep_values = collect(values(sweep_ranges))  # array of ranges
sweep_grid   = collect(product(sweep_values...))

# unify param names: sweep_keys + fixed
all_param_names = union(sweep_keys, keys(fixed))  # e.g. ["a","ktau","r","α","νn",...]

# We'll store final_fraction as well
all_columns = sort(collect(all_param_names))
if !in("final_fraction", all_columns)
    push!(all_columns, "final_fraction")
end

# Suppose we already constructed `sweep_grid` & have `all_param_names`
N = length(sweep_grid)
results_storage = Vector{Dict{String, Any}}(undef, N)

# Pre-declare columns in results DF: all as Any[] to allow missing/float
results = DataFrame()
# for combo in sweep_grid
@threads for idx in 1:N
    combo = sweep_grid[idx]
    
    # 1) build a partial dict of param => value from the sweep
    sweep_dict = Dict(sweep_keys[i] => combo[i] for i in 1:length(sweep_keys))

    # Build a dictionary of parameters for this combo
    param_map = Dict{String,Any}()
    
    for pname in setdiff(all_columns, ["final_fraction"])
        if haskey(sweep_dict, pname)
            param_map[pname] = sweep_dict[pname]
        elseif haskey(fixed, pname)
            param_map[pname] = fixed[pname]
        else
            param_map[pname] = missing
        end
    end

    # 3) Extract or skip if missing
    α_  = get(param_map, "α",   missing)
    νn_ = get(param_map, "νn",  missing)
    νp_ = get(param_map, "νp",  missing)
    K_  = get(param_map, "K",   missing)
    kt_ = get(param_map, "ktau",missing)
    a_  = get(param_map, "a",   missing)
    kc_ = get(param_map, "kc",  missing)
    x0_ = get(param_map, "x0c", missing)
    b_  = get(param_map, "bl",  missing)
    r_  = get(param_map, "r",   missing)

    if any(x -> x === missing, (α_, νn_, νp_, K_, kt_, a_, kc_, x0_, b_, r_))
        @warn "Skipping combo due to missing param"
        continue
    end

    # 4) Solve
    p = (α_, νn_, νp_, K_, kt_, a_, kc_, x0_, b_, r_)
    prob = ODEProblem(J!, x0, tspan, p)
    sol  = solve(prob)
    fval = final_fraction_programmers(sol)

    # 5) Build a NamedTuple row for push!(results)
    param_map["final_fraction"] = fval
    param_map["skip"] = false

    # Store in the vector
    results_storage[idx] = param_map

end

# Now convert to DataFrame, filtering out the `skip` combos

valid_results = filter(!=(true) ∘ r -> r["skip"], results_storage)
df = DataFrame(valid_results)

################################################################################
# 4) Save results to DuckDB (Simplified)
################################################################################

con = DBInterface.connect(DuckDB.DB, joinpath(DIR_RES, "sweeps.duckdb"))

# (A) optionally drop old table
try
    DBInterface.execute(con, "DROP TABLE $(output_dir)")
catch e
    @warn "No existing table to drop" exception=(e, catch_backtrace())
end

if ncol(df) == 0
    @warn "No columns in df. Sweep might have been skipped entirely!"
else
    DuckDB.register_table(con, df, "temp_results")
    DBInterface.execute(con, "CREATE TABLE $(output_dir) AS SELECT * FROM temp_results")
    DBInterface.execute(con, "DROP VIEW temp_results")
end

DBInterface.execute(con, "CREATE TABLE IF NOT EXISTS sweep_configs (sweep_name TEXT, config TEXT)")
conf_insert = "INSERT INTO sweep_configs VALUES ('$(output_dir)', '$(YAML.dump(config))')"
DBInterface.execute(con, conf_insert)
