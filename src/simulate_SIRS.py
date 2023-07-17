import os

import epipack as epk
from epipack.vis import visualize
import netwulf as nw


def run_SIRS(network):

    N = len(network['nodes'])
    links = [ (l['source'], l['target'], 1.0) for l in network['links'] ]

    eta = 10.0
    rho = 1.0
    omega = 0.2

    I_0 = 50
    R_0 = int(0.2 * N)

    S, I, R = list("SIR")
    model = epk.StochasticEpiModel([S, I, R], N, links)\
                .set_link_transmission_processes([ 
                    (I, S, eta, I, I) 
                ])\
                .set_node_transition_processes([
                    (I, rho, R),
                    (R, omega, S) 
                ])\
                .set_random_initial_conditions({
                    S: N - I_0 - R_0,
                    I: I_0,
                    R: R_0
                })

    visualize(model, network, sampling_dt=0.1)


if __name__ == "__main__":

    basedir = os.path.join(os.path.dirname(__file__), "..")

    # network, _, __ = nw.load(os.path.join(basedir, 'data', 'configured', 'knn_graph.json'))
    network, _, __ = nw.load(os.path.join(basedir, 'data', 'configured', 'Jigawa_knn_graph.json'))

    run_SIRS(network)