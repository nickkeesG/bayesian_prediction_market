import numpy as np

from market import Market
from agents import Agent

def init_agents(n_agents, starting_cash):
    agents = []
    for i in range(n_agents):
        agents.append(Agent(i, starting_cash))
    return agents

def run_simulation(n_agents = 100, n_time_steps = 1000, time_per_evidence = 100, n_evidence = 10, starting_cash = 100000000, update_when_receiving = False):
    agents = init_agents(n_agents, starting_cash)
    market = Market(agents, update_when_receiving)
    price_log = np.zeros(n_time_steps)
    best_belief_log = np.zeros(n_time_steps)

    for i in range(n_time_steps):
        if i % time_per_evidence == 0 and n_evidence > 0:
            market.reveal_evidence()
            n_evidence -= 1
        market.trade()
        market.update_agents_belief()

        price_log[i] = market.get_market_price()
        best_belief_log[i] = market.get_best_belief()

    return price_log, best_belief_log
