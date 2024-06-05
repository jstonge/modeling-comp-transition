import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd

def read_experiment_dat(i): 
    # Pour chaque paire de beta et de conditions initiales, tu enregistres la fraction 
    #  moyenne de programmeurs dans les groupes de taille > 0 dans la limite des 
    #  grands temps. Ensuite tu fais un graphique avec trois courbes 
    # (1 par condition initiales) de cette fraction là sur l'axe vertical en 
    # fonction de beta sur l'axe horizontal.
    fnames=list(Path(f"beta_experiment_ic{i}").glob('*.csv'))
    fnames=sorted(fnames, key=lambda x: float(x.stem))
    data = [np.genfromtxt(_, delimiter=",") for _ in fnames]
    betas=[_[1] for _ in data]
    avg_group_density_eq=[_[3] for _ in data]
    return betas, avg_group_density_eq

def check_last_step(fname):
    data = np.genfromtxt(fname, delimiter=",")
    if len(data) == 4:
        df = pd.DataFrame([data], columns=["t", "beta", "ic", "density"])
    else:
        df = pd.DataFrame(data, columns=["t", "beta", "ic", "density"])\
               .assign(density = lambda x: np.round(x.density,3)).query('density > 0')
    last_step = df.t.max()
    return df[(df.t == last_step )]

check_last_step("test_eq_ic0.csv")
check_last_step("test_eq_ic1.csv")
check_last_step("test_eq_ic3.csv")


plt.rcParams['text.usetex'] = False

fnames=list(Path(f"test").glob('*.csv'))
fnames=sorted(fnames, key=lambda x: float(x.stem))
data = [np.genfromtxt(_, delimiter=",") for _ in fnames]
betas=[_[1] for _ in data]
avg_group_density_eq=[_[3] for _ in data]
plt.scatter(betas, avg_group_density_eq)
plt.title("IC0 (c=0.95)")
plt.xlabel(r"\\beta")
plt.ylabel(r"final group density")

list_cols = [ "mu", "nu_n", " nu_p", "alpha", "beta", "b", "K", "c0", "IC", "avg"]

fnames=list(Path(f"test").glob('*.csv'))
fnames=sorted(fnames, key=lambda x: float(x.stem))
data = [np.genfromtxt(_, delimiter=",") for _ in fnames]
betas=[_[1] for _ in data]
avg_group_density_eq=[_[3] for _ in data]
plt.title("IC0; beta=0.47")
plt.xlabel(r"c0")
plt.ylabel(r"final group density")
plt.scatter(betas, avg_group_density_eq)

fnames=list(Path(f"test").glob('*.csv'))
fnames=sorted(fnames, key=lambda x: float(x.stem))
data = [np.genfromtxt(_, delimiter=",") for _ in fnames]
betas=[_[8] for _ in data]
avg_group_density_eq=[_[-1] for _ in data]

plt.title("IC1; beta=0.47")
plt.xlabel(r"c0")
plt.ylabel(r"final group density")
plt.scatter(betas, avg_group_density_eq)

