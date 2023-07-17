import logging
import os

import matplotlib.pyplot as plt
from matplotlib import colors
import pandas as pd


basedir = os.path.join(os.path.dirname(__file__), "..")


def plot_locations(df, state):
    
    fig, ax = plt.subplots(1, 1)
    if state is not None:
        df.plot("x", "y", color="darkgray", s=1, alpha=0.2, kind="scatter", ax=ax)
        df[df.adm1_name==state].plot("x", "y", c="population", s=3, kind="scatter", norm=colors.LogNorm(), ax=ax)
    else:
        df.plot("x", "y", c="population", s=3, kind="scatter", norm=colors.LogNorm(), ax=ax)
    ax.set(aspect='equal')
    fig.set_tight_layout(True)

    os.makedirs(os.path.join(basedir, "figs"), exist_ok=True)
    fig_name = f"{state}_population_locations.png" if state is not None else "population_locations.png"
    fig.savefig(os.path.join(basedir, "figs", fig_name))


if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    state = "Jigawa"
    # state = None

    location_file = f"{state}_population_locations.csv" if state is not None else "population_locations.csv"

    df = pd.read_csv(os.path.join(basedir, "data", "parsed", location_file), index_col=0)
    logging.debug(df.head())

    plot_locations(df, state)
    plt.show()