using  OrdinaryDiffEq, Plots

bn(n, p, K, μ) = μ*(p+n) * (1-(p+n)/K) # birth non-prog
τ(n, p, α, β, k, x0) = exp(-α + β*(1 - cost(n,p,k,x0))) # group benefits

function cost(n, p, k, x0)
  if n <= 0
      return 0.0
  end
  value = 1 / (1 + exp(k * (p / n - x0)))
  return (0 < value < 1) ? value : 0.0
end

function dynamics!(du, u, p, t)
  P, N = u
  μ, νₙ, νₚ, α, β, K, k, x₀ = p
  du[1] = dP = -P*νₚ + τ(N,P,α,β,k,x₀) * cost(N,P,k,x₀)
  du[2] = dN = bn(N,P,K,μ) - τ(N,P,α,β,k,x₀)*(1-cost(N,P,k,x₀)) - N*νₙ
end

#         μ,   νₙ,   νₚ,    α,    β,    K,   k,  x₀
params = [0.5, 0.01, 0.01, 0.01, 0.1, 40., 25.0, 0.25]
u₀ = [0, 10]
tspan = (0., 100)
prob = ODEProblem(dynamics!, u₀, tspan, params)
sol = solve(prob)
plot(sol)