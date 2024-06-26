import heapq
import sys
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgi
from numpy.random import binomial, choice, exponential

from helpers import count_prog_nonprog, grab, plot_group_heatmap, plot_quartet


# def τ(n, p, α, β, b=0.9): # group benefits
#     return np.exp(-α + β*(1 - c(n, p, b=b)))

def c(n, p, a=3, b=0.9): # cost function
    return b if n == p == 0 else b * np.exp(-a*p / n) 

# def sigmoid(p,n, N, K=25, mu=0.1):
#     return mu*(p+n+1) * (1-(p+n+1)/K) / N


# def τ_old(n,p, alpha, beta, b=.9):
#     return -alpha + beta(1 - c(n,p, b=b))

def τ(n,p,α,β,b=.9):
    return (-(n+1)**α/2) * (p+1)**β/2 + (1-c(n,p))*n**α/2 * (p+2)**β/2 + c(n,p)*n**α/2 * (p+1)**β/2

sns.set_style("whitegrid")

alpha, beta = 0.01, 0.5

def plot_non_prog(p):
    N_tot=40
    N=N_tot-p
    plt.plot(range(1,N), [τ(n, p, alpha, beta) for n in range(1,N)], label=f"p={p}")
    plt.xlabel("# non-programmers")
    plt.legend()

plot_non_prog(1)
plot_non_prog(5)
plot_non_prog(10)
plot_non_prog(20)

def plot_prog(n):
    N=40
    P=N-n
    plt.plot(range(P), [τ(n, p, alpha, beta) for p in range(P)], label=f"n={n}")
    plt.xlabel("# programmers")
    plt.legend()

plot_prog(1)
plot_prog(5)
plot_prog(10)
plot_prog(20)

def init_hypergraph(nb_groups=1000, max_group_size=40):
    current_node = 0
    hyperedge_dict = {}
    for group in range(nb_groups):
        group_size = binomial(max_group_size, 0.1)
        
        while group_size == 0: # make sure group size > 0
            group_size = binomial(max_group_size, 0.1)
        
        group_members = []
        for node in range(current_node, current_node+group_size):
            group_members.append(node)
        hyperedge_dict.update({group: group_members})
        current_node += group_size

    return xgi.Hypergraph(hyperedge_dict)

def adding_new_non_prog(H, group, tot_nodes):
    """
    B/c we allow group of size zero, we need to create 
    a new edge when the previous one is depleted.
    
    NOTE: IF ever we use edge size to calculate the number
          of groups, this will give the current number of 
          alive groups.
    """
    new_node =  tot_nodes + 1
    if H.edges.get(group) is None:
        # print(f"group {group} came back to life.")
        H.add_edge([new_node], id=group)
    else:
        H.add_node_to_edge(group, new_node)

    H.nodes[new_node]['state'] = 'non-prog'

def wrangle_Ig(Ig_norm, only_prog=True):
    """
    Extract the fraction of group size or the fraction of programmers
    by groups from I_g.
    """
    # only_prog=True
    # Ig_norm=history_group
    
    # If we only look at programmer, we only consider the bottom left corner
    # of the matrix. Given that we want the fraction of programmers by groups,
    # and that we bound the total number of programmers by having a square matrix (P x N),
    # any group size > P will show a diminish fraction of programmers as the max 
    # number of programmers has been reached.
    P, N = Ig_norm[0].shape
    max_group = P if only_prog else (P+N-1)
    Ig_norm_wrangled = np.zeros((len(Ig_norm), max_group)) # (t, gsize)
    for t in range(len(Ig_norm)):
        # t=10
        num = np.zeros(max_group)
        denum = np.zeros(max_group)

        for gsize in range(max_group): 
            # When only prog, this will be range(0,21)
            # gsize=22
            min_range = (gsize - P + 1) if gsize >= P else 0
            for p in range(min_range, np.min([P, gsize+1])):
                n = gsize-p
                # print(p, n, gsize)
                if only_prog: # we only do numerator
                    num[gsize] += 0 if p==gsize==0 else (p / gsize) * Ig_norm[t][p, n]
                
                denum[gsize] += Ig_norm[t][p, n]
        
        if only_prog == True:
            weighted_sum = np.array([0 if n==d==0 else n/d for n, d in zip(num, denum)])
            Ig_norm_wrangled[t,:] = weighted_sum / np.sum(weighted_sum)
        else: # fraction of group is just the denum
            Ig_norm_wrangled[t,:] = denum 

    return Ig_norm_wrangled
        
def whats_happening(event_queue, H, group, params, t):
    mu, nu_n, nu_p, alpha, beta, b, pa, K = params
    p, n = count_prog_nonprog(H, group) # Not that we allow 0,0; But the next event we'll be a new non-prog.

    R_nonprog_grad = nu_n * n
    R_prog_grad = nu_p * p
    
    # R_new_nonprog = mu * (1+(p+n)*pa)
    # R_new_nonprog = mu * (1+p+n) #non-prog growth limited by PI carrying capacity.
    # (p+n+1) * (1-(p+n+1)/K)
    # (p+n+1) * (K-p+n)
    # R_new_nonprog = mu * (p+n+1) * (1-(p+n+1)/K) if pa==1 else mu

    # As you have more people having H.nodes + H.num_edges reduce the recruitment rate.
    # We need to say H.num_edges b/c of the `+1` that take into account the 
    # the possibility of having empty groups (as if we are counting the PI).
    R_new_nonprog = mu * (p+n+1) * (1-(p+n+1)/K) / (H.num_nodes + H.num_edges) if pa==1 else mu

    # R_new_nonprog = mu * (p+n+1) * (1-(p+n+1)/K) / (H.num_nodes + H.num_edges) if pa==1 else mu
    R_conversion_attempt = τ(n, p, alpha, beta, b=b) if n > 0 else 0.
    
    # draw time to next event and event type
    R = R_nonprog_grad + R_conversion_attempt + R_new_nonprog + R_prog_grad
    tau = exponential(scale=1/R)
    
    taulab = ["non-prog graduates", "programmer graduates", "conversion attempt", "new non-programmer"]
    tauR = [R_nonprog_grad/R, R_prog_grad/R, R_conversion_attempt/R, R_new_nonprog/R] 
    which_event = choice(taulab, p=tauR)
    
    # Ok, now the new tau is added to time
    next_event = (t+tau, group, which_event, p, n)
    
    if which_event == 'conversion attempt':
        if R_conversion_attempt/R < (1-c(n,p,b=b)):
            next_event = (t+tau, group, "new programmer", p, n)
        else:
            next_event = (t+tau, group, "non-prog leaves", p, n)

    heapq.heappush(event_queue, next_event)

    return event_queue

def main():
    """
    params
    ======
     - K: carrying capapacity of the PI. It should bound the total number of
          students by group. This means that the total number of students
          should never exceed K*nb_groups.
    """
    #         mu, nu_n, nu_p, alpha, beta, b, pa, K 
    params = (0.5, 0.01, 0.01, 0.01, 0.1, .5, 1, 40)
    I0 = 0.1

    #initial conditions
    event_queue = []
    max_group_size = params[-1]
    H = init_hypergraph(max_group_size=max_group_size)
    I = 0
    Ig = np.zeros((max_group_size+1, max_group_size+1))
    t = 0
    # total nodes dead or alive to have unique node identifier.
    tot_nodes = H.num_nodes
    # we start out we a hypergraph where hyperedges == groups
    # they are non-overlapping at the moment. all_gsize > 0.
    for group, members in enumerate(H.edges.members()): #loop over groups
        gsize = len(members)
        states_binary = binomial(1, I0, size=gsize)
        p = np.sum(states_binary)
        n = gsize - p
        states = np.where(states_binary == 0, 'non-prog', 'prog')
        for node, state in zip(members, states):
            H.nodes[node]['state'] = state
        event_queue = whats_happening(event_queue, H, group, params, t)
        Ig[p, n] += 1
        I += p

    assert all([Ig[q[-2], q[-1]] != 0 for q in event_queue]), "Ig should never be zero when there are non-prog/prog"

    # what's in the event queue?
    # Counter(e[2] for e in event_queue)
    
    history = []
    history_group = []
    tot_pop = []
    history.append(I/H.num_nodes)
    history_group.append(Ig / np.sum(Ig))
    tot_pop.append(H.num_nodes)
    times = np.zeros(1)

    #for each generation
    t_max = 500
    next_int = 1

    #for each generation
    while t <= t_max:
        
        # draw from event queue
        # here is use time_tau because in whats_happening I always
        # add time + tau. So this is not just tau, this is current time.
        (time, group, event, p, n) = heapq.heappop(event_queue)  

        t=time

        # assert H.edges.get(group) is not None, "We should not have None group anymore"
        #     (time, group, event, p, n) = heapq.heappop(event_queue)
        # Ig[p, n]  -= 1

        if event == 'non-programmer graduates' or event == "non-prog leaves":           
            leaving_node = grab(H, group, 'non-prog')
            # Not ideal.
            assert leaving_node is not None, "node is None"
            if leaving_node:
                H.remove_node(leaving_node)
                assert n > 0
                Ig[p, n]   -= 1
                Ig[p, n-1] += 1
                
        if event == 'programmer graduates':
            leaving_node = grab(H, group, 'prog')
            assert leaving_node is not None, "node is None"
            # Not ideal.
            if leaving_node:
                H.remove_node(leaving_node)
                I -= 1
                assert p > 0
                Ig[p, n]   -= 1
                Ig[p-1, n] += 1
    
        if event == 'new non-programmer':
            adding_new_non_prog(H, group, tot_nodes)
            tot_nodes += 1
            # assert n < max_group_size, f"We currently have {p} prog and {n} non progs in group {group}"
            Ig[p, n]  -= 1
            Ig[p, n+1] += 1
        
        if event == 'new programmer':
            converting_node = grab(H, group, 'non-prog')
            assert converting_node is not None, "node is None"
            # Not ideal.
            if converting_node:
                H.nodes[converting_node]['state'] = 'prog'
                I += 1
                # assert p < max_group_size and n > 0
                Ig[p, n]     -= 1
                Ig[p+1, n-1] += 1

        event_queue = whats_happening(event_queue, H, group, params, t)

        # update history every integer

        assert np.sum(Ig) == 1000, "Our number of groups is fixed"        
        
        if t >= next_int: 
            tot_pop.append(H.num_nodes)
            history = np.append(history, I / H.num_nodes)
            history_group.append(Ig / np.sum(Ig))
            times = np.append(times, time)
            
            next_int += 1

    # Plotting

    sns.set_style('whitegrid')
    
    ig_wrangled = wrangle_Ig(history_group, only_prog=True)
    ig_wrangled_group = wrangle_Ig(history_group, only_prog=False)

    assert (np.sum(ig_wrangled[t_max]) > .998) & (np.sum(ig_wrangled[t_max]) < 1.001), "Should always be normalized"
    assert (np.sum(ig_wrangled_group[t_max]) > .998) & (np.sum(ig_wrangled_group[t_max]) < 1.001) == 1.0, "Should always be normalized"

    # Quartet
    plot_quartet(history, tot_pop, params, history_group, times)


    # Timeseries 
    ss = np.array([_ for _ in ig_wrangled[t_max,:]])
    top_ind = ss.argsort()[-5:][::-1]
    fig, ax = plt.subplots(1,1, figsize=(10,8))
    for i in range(ig_wrangled.shape[1]):
        if i in top_ind:
            plt.plot(times, [ig_wrangled[t, i] for t in range(len(history_group))], label=f"gsize={i}", marker="o")
        plt.plot(times, [ig_wrangled[t, i] for t in range(len(history_group))], color="grey", alpha=0.1, label=f"", marker="o")
    plt.plot(times[-1], ig_wrangled[t_max, top_ind[0]], label="")
    plt.legend()
    plt.ylabel("frac programmers")
    plt.xlabel("time")

    ss = np.array([_ for _ in ig_wrangled_group[t_max,:]])
    top_ind = ss.argsort()[-5:][::-1]
    fig, ax = plt.subplots(1,1, figsize=(10,8))
    for i in range(ig_wrangled_group.shape[1]):
        if i in top_ind:
            plt.plot(times, [ig_wrangled_group[t, i] for t in range(len(history_group))], label=f"gsize={i}", marker="o")
        plt.plot(times, [ig_wrangled_group[t, i] for t in range(len(history_group))], color="grey", alpha=0.1, label=f"", marker="o")
    plt.plot(times[-1], ig_wrangled_group[t_max, top_ind[0]], label="")
    plt.legend()
    plt.ylabel("frac programmers")
    plt.xlabel("time")

    
    # JULIA 

    julia_output = pd.read_csv("../test.csv").to_numpy()
    
    fig, ax = plt.subplots(1,1, figsize=(10,8))

    ss = np.array([_ for _ in ig_wrangled_group[50,:]])
    top_ind = ss.argsort()[-5:][::-1]
    for i in range(ig_wrangled_group.shape[1]):
        if i in top_ind:
            ax.plot(times[:50], [ig_wrangled_group[t, i] for t in range(len(history_group[:50]))], label=f"gsize={i}")    
        ax.plot(times[:50], [ig_wrangled_group[t, i] for t in range(len(history_group[:50]))], color="grey", alpha=0.3, label=f"")
    ax.plot(times[:50][-1], ig_wrangled_group[59, top_ind[0]], label="")
    plt.legend()
    

    ss = np.array([_ for _ in julia_output[50,:]])
    top_ind = ss.argsort()[-5:][::-1]
    # fig, ax = plt.subplots(1,1, figsize=(10,8))
    for i in range(julia_output.shape[1]):
        if i in top_ind:
            ax.scatter(times[:50], [julia_output[t, i] for t in range(len(history_group[:50]))], marker="*", label=f"gsize={i}")    
        ax.scatter(times[:50], [julia_output[t, i] for t in range(len(history_group[:50]))], marker="*", color="grey", alpha=0.3, label=f"")
    ax.scatter(times[:50][-1], julia_output[50, top_ind[0]], marker="*", label="")
    plt.ylabel("frac group size")
    plt.xlabel("time")
    
    plt.savefig("../figs/python_sos_julia.pdf")
    
    # Individual plots
    
    # fig, ax = plt.subplots(1,1,figsize=(15,12))
    # gsizes = [6, 8, 11, 13, 15]
    # plot_group_size(history_group, times, ax=ax, gsizes=gsizes)
    
    fig, (ax1, ax2) = plt.subplots(2,1,figsize=(15,10))
    plot_group_heatmap(ig_wrangled, only_prog=True, ax=ax1)
    plot_group_heatmap(ig_wrangled_group, only_prog=False, ax=ax2)
    # plt.savefig("update_frac_group.png")

    
    # plt.savefig(f"../figs/summary_pa{params[-1]}.png")




main()







def plot_group_heatmap(Ig_norm_wrangled, only_prog=False, ax=None):
    """return gsize x time heatmap with z=fraction of programmers""" 
    # Ig_norm_wrangled=ig_wrangled
    # only_prog=True
    max_group = len(Ig_norm_wrangled[0,:])-1
    if ax is None:
        fig, ax = plt.subplots(1,1,figsize=(18,8))
    sns.heatmap(pd.DataFrame(Ig_norm_wrangled).transpose()[:max_group], 
                cmap= "Blues" if only_prog else "Greens", 
                cbar_kws={"label": "frac programmers" if only_prog else "frac gsize"}, ax=ax)
    # labels = [int(item.get_text())+1 for item in ax.get_yticklabels()]
    ax.set_xlabel("Time →")
    ax.set_ylabel("Group size")
    ax.set_xticklabels([]);


def plot_quartet(history, tot_pop, params, history_group, times):
    fig, axes = plt.subplots(2, 2, figsize=(15,10))
    
    ig_wrangled = wrangle_Ig(history_group, only_prog=True)
    ig_wrangled_group = wrangle_Ig(history_group, only_prog=False)
    
    plot_group_heatmap(ig_wrangled, only_prog=True, ax=axes[0,0])
    axes[0,0].set_xlabel("")
    
    plot_group_heatmap(ig_wrangled_group, only_prog=False, ax=axes[0,1])
    axes[0,1].set_xlabel("")
    
    sns.lineplot(x=times, y=history, color='black', ax=axes[1,0])
    axes[1,0].set_xlabel('Time')
    axes[1,0].set_ylabel('Frac Programmers')
    axes[1,0].set_ylim(0, np.max(history)+0.2)
    
    sns.lineplot(x=times, y=tot_pop, color='midnightblue', alpha=1., ax=axes[1,1])
    axes[1,1].set_ylabel('Total Population')
    axes[1,1].set_xlabel('Time')
    param_lab = ['mu', 'nu_n', 'nu_p', 'alpha', 'beta', 'b']
    title=';'.join([f'{lab}={val}' for lab, val in zip(param_lab, params)])
    title += f"\nPI carrying capacity={params[-1]}"
    fig.suptitle(title, fontsize=16)