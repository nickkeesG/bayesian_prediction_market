from bayes import *
from exchange import Bid
import math

MAX_BET = 100000

class Agent:
    def __init__(self, idx = -1, cash = 0):
        self.idx = idx
        self.belief = 0.5
        self.cash = cash            #money the agent has not spent
        self.available_cash = cash  #money the agent has not offered to spend on bids
        self.shares = {}
        self.shares["FOR"] = 0
        self.shares["AGAINST"] = 0

    def cash_in_pairs(self):
        pairs = min(self.shares["FOR"], self.shares["AGAINST"])
        self.shares["FOR"] -= pairs
        self.shares["AGAINST"] -= pairs
        self.cash += pairs
        self.available_cash += pairs

#This function defines the behavior of the agent
    def place_bid(self, highest_price_for, highest_price_against):
        if highest_price_for == None:
            highest_price_for = 0
        if highest_price_against == None:
            highest_price_against = 0
        
        bid_for = None
        bid_against = None
        if self.belief > (1 - highest_price_against):
            bid_for = Bid(self.idx, "FOR", (1 - highest_price_against), 0)
        elif self.belief > highest_price_for:
            bid_for = Bid(self.idx, "FOR", (self.belief + highest_price_for)/2, 0)
        if (1 - self.belief) > (1 - highest_price_for):
            bid_against = Bid(self.idx, "AGAINST", (1 - highest_price_for), 0)
        elif (1 - self.belief) > highest_price_against:
            bid_against = Bid(self.idx, "AGAINST", ((1 - self.belief) + highest_price_against)/2, 0)
        
        if not bid_for == None:
            bid_for.n_shares = min(math.floor(self.available_cash / bid_for.price), min(MAX_BET, round(1000*(self.belief - bid_for.price)/bid_for.price, 0)))
            if bid_for.n_shares == 0:
                bid_for = None
        if not bid_against == None:
            bid_against.n_shares = min(math.floor(self.available_cash / bid_against.price), min(MAX_BET, round(1000*((1-self.belief) - bid_against.price)/bid_against.price, 0)))
            if bid_against.n_shares == 0:
                bid_against = None

        if bid_for == None:
            return bid_against
        if bid_against == None:
            return bid_for

        if bid_for.n_shares > bid_against.n_shares:
            return bid_for
        else:
            return bid_against

    def update_belief(self, new_evidence):
        current_evidence = prob_to_evidence(self.belief)
        self.belief = evidence_to_prob(current_evidence + new_evidence)

    
