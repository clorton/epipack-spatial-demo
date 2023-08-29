import os
from typing import Dict

import epipack as epk
from epipack.vis import visualize
import netwulf as nw
import yaml


def run_SIRS(network, params):

    """Run SIRS model on a network."""

    N = len(network['nodes'])
    links = [ (l['source'], l['target'], 1.0) for l in network['links'] ]

    eta = params["eta"]
    rho = params["rho"]
    omega = params["omega"]

    I_0 = params["I_initial"]
    R_0 = int(params["R_initial_fraction"] * N)

    S, I, R = list("SIR")
    model = epk.StochasticEpiModel([S, I, R], N, links)\
        .set_link_transmission_processes(
        [
            (I, S, eta, I, I)
        ])\
        .set_node_transition_processes(
        [
            (I, rho, R),
            (R, omega, S)
        ])\
        .set_random_initial_conditions(
        {
            S: N - I_0 - R_0,
            I: I_0,
            R: R_0
        })

    visualize(model, network, sampling_dt=0.1)


def run_SEIRS(network, params):

    """Run SEIRS model on a network."""

    N = len(network['nodes'])
    links = [(link['source'], link['target'], 1.0) for link in network['links']]

    eta = params["eta"]
    kappa = params["kappa"]
    rho = params["rho"]
    omega = params["omega"]

    E_0 = 0
    I_0 = params["I_initial"]
    R_0 = int(params["R_initial_fraction"] * N)

    S, E, I, R = list("SEIR")
    model = epk.StochasticEpiModel([S, E, I, R], N, links)\
        .set_link_transmission_processes(
        [
            (I, S, eta, I, E)
        ])\
        .set_node_transition_processes(
        [
            (E, kappa, I),
            (I, rho, R),
            (R, omega, S)
        ])\
        .set_random_initial_conditions(
        {
            S: N - I_0 - R_0,
            E: E_0,
            I: I_0,
            R: R_0
        })

    visualize(model, network, sampling_dt=0.1)


if __name__ == "__main__":

    basedir = os.path.join(os.path.dirname(__file__), "..")

    params = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["simulate"]
    
    # state = "Jigawa"
    # state = "Nigeria"
    state = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["state"]

    network, _, __ = nw.load(os.path.join(basedir, 'data', 'configured', f"{state}_knn_graph.json"))
    # run_SIRS(network, params)
    run_SEIRS(network, params)