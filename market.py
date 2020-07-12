import numpy as np
from agents import Agent
from bayes import *
from exchange import Exchange

class Market:
    def __init__(self, agents, update_when_receiving = False):
        self.agents = agents
        self.last_market_price = 0.5
        self.market_price = 0.5
        self.best_belief = 0.5
        self.idx_agent_receiving_evidence = -1 #This is always set to the last agent to receive evidence
        self.god = Agent()
        self.exchange = Exchange()
        self.update_when_receiving = update_when_receiving #Whlie receiving evidence, does the agent update belief based on change in market price?

    def get_best_belief(self):
        return self.god.belief

    def get_market_price(self):
        return self.market_price
    
    def reveal_evidence(self, size_evidence = 1):
        size_evidence = 1
        evidence = 0
        if np.random.uniform() > 0.5:
            evidence = size_evidence
        else:
            evidence = size_evidence * -1
        
        #Show new evidence to one of the agents
        self.idx_agent_receiving_evidence += 1
        self.agents[self.idx_agent_receiving_evidence].update_belief(evidence)

        #Show new evidence to God
        self.god.update_belief(evidence)

    def trade(self):
        order = [i for i in range(len(self.agents))]
        np.random.shuffle(order)
        for idx in order:
            highest_price_for, highest_price_against = self.exchange.head()
            bid = self.agents[idx].place_bid(highest_price_for, highest_price_against)
            if not bid == None:
                receipt = self.exchange.process_bid(bid)
                self.transact_shares(receipt)
        cash_on_exchange = self.exchange.housekeeping(len(self.agents))
        self.update_available_cash(cash_on_exchange)

    def transact_shares(self, receipt):
        for bid in receipt:
            self.agents[bid.id].cash -= bid.get_cost()
            self.agents[bid.id].shares[bid.contract_type] += bid.n_shares
            
            #if an agent holds both a 'for' and an 'against' contract, they may cash them in for a guarranteed 1 cash
            self.agents[bid.id].cash_in_pairs()

            if bid.contract_type == "FOR":
                self.market_price = bid.price
            else:
                self.market_price = 1 - bid.price

    def update_agents_belief(self):
        last_evidence = prob_to_evidence(self.last_market_price)
        current_evidence = prob_to_evidence(self.market_price)
        evidence = current_evidence - last_evidence

        for i in range(len(self.agents)):
            if self.update_when_receiving or not i==self.idx_agent_receiving_evidence:
                self.agents[i].update_belief(evidence)

        self.last_market_price = self.market_price

    def update_available_cash(self, cash_on_exchange):
        for i in range(len(self.agents)):
            self.agents[i].available_cash = self.agents[i].cash - cash_on_exchange[i]
