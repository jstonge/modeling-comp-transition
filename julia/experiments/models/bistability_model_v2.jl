B(x, a, bl; M=5) =  bl + (M - bl) * exp(-a * x)
C(x, kc, x0c, bl, r) = (1 - r*bl)*(1. / (1. + exp(kc * (x - x0c)))) + bl    # cost


# combine all that into a sigmoid
tau_rescaling = 10
τ(x, ktau, a, kc, x0c, bl, r) = tau_rescaling*(1. / (1. + exp(-ktau * ( B(x, a, bl) - C(x, kc, x0c, bl, r) ))) )


function J!(du, u, p, t)
    α, νn, νp, K, ktau, a, kc, x0c, bl, r = p
    N, P = size(u)         
    # Reset du to zero at each call
    @. du = 0.0
    for i=1:N, j=1:P
        # Occupant numbers:
        n1 = i - 1 
        n2 = j - 1
        
        gsize = n1+n2+1 # 0..(N+P-2), e.g. N=15, P=15 -> 0..28. 
        du[i, j] -= νp * n2 * u[i, j]                                         # programmer death (outflow)
        du[i, j] -= νn * n1 * u[i, j]
        n1 < N-1 && (du[i, j] -= α * gsize * (1 - gsize/K) * u[i, j] )                 # non-programmer birth (outflow)
        n1 > 0   && (du[i, j] += α * (gsize - 1) * (1 - (gsize - 1)/K) * u[i-1, j])  # non-programmer birth (inflow)
        n2 < P-1 && (du[i, j] += νp * (n2 + 1) * u[i, j+1])                            # programmer death (inflow)
        n1 < N-1 && (du[i, j] += νn * (n1+1) * u[i+1, j])

        if gsize > 0
            n2 < P-1 && (  # Predation output
                du[i,j] -= τ(n2/gsize, ktau, a, kc, x0c, bl, r) 
                                        * (1. - C(n2/gsize,  kc, x0c, bl, r)) 
                                        * n1 
                                        * u[i,j]
                                        ) 
            
            (n1 < N-1 && n2 > 0 && n2 < P) && ( # Predation input  
                du[i,j] += τ((n2-1)/gsize, ktau, a, kc, x0c, bl, r) 
                                * (1. - C((n2-1)/gsize, kc, x0c, bl, r)) 
                                * (n1+1) 
                                * u[i+1,j-1]
                            )

            (
                du[i,j] -= τ(n2/gsize, ktau, a, kc, x0c, bl, r)   # Predation output
                            * C(n2/gsize,  kc, x0c, bl, r) 
                            * n1 
                            * u[i,j] 
            ) 
        end

        n1 < N-1 && ( du[i,j] += τ(n2/(gsize+1), ktau, a, kc, x0c, bl, r) 
                                    * C(n2/(gsize+1),  kc, x0c, bl, r) 
                                    * (n1+1) 
                                    * u[i+1,j] )  # Predation output
   
    end
end
