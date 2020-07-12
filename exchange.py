import heapq
import numpy as np
import copy

#If a bid is older than the maximum bid age, it is deleted from the exchange
MAX_BID_AGE = 1

class Bid:
    def __init__(self, agent_idx, contract_type, price, n_shares):
        self.id = agent_idx
        self.price = round(price, 3) #this defines a tick size of 0.001
        self.contract_type = contract_type
        self.n_shares = n_shares
        self.priority = price * -1 #for the purpose of sorting bids
        self.age = 0

    def __lt__(self, other):
        return self.priority < other.priority

    def get_cost(self):
        return self.price * self.n_shares

class Exchange:
    def __init__(self):
        self.active_bids = {}
        self.active_bids["FOR"] = []
        heapq.heapify(self.active_bids["FOR"])
        self.active_bids["AGAINST"] = []
        heapq.heapify(self.active_bids["AGAINST"])

    def head(self):
        highest_for_price = None
        if len(self.active_bids["FOR"]) > 0:
            highest_for_price = heapq.nsmallest(1, self.active_bids["FOR"])[0].price
        highest_against_price = None
        if len(self.active_bids["AGAINST"]) > 0:
            highest_against_price = heapq.nsmallest(1, self.active_bids["AGAINST"])[0].price
        return highest_for_price, highest_against_price

    def housekeeping(self, n_agents):
        #Age all bids
        for k in ["FOR", "AGAINST"]:
            for i in range(len(self.active_bids[k])):
                self.active_bids[k][i].age += 1

        #Remove old bids
        new_active_bids = {}
        new_active_bids["FOR"] = []
        heapq.heapify(new_active_bids["FOR"])
        new_active_bids["AGAINST"] = []
        heapq.heapify(new_active_bids["AGAINST"])
        for k in ["FOR", "AGAINST"]:
            while len(self.active_bids[k]) > 0:
                bid = heapq.heappop(self.active_bids[k])
                if not bid.age > MAX_BID_AGE:
                    heapq.heappush(new_active_bids[k], bid)
        self.active_bids = new_active_bids
        
        #Calculate how much cash each agent has pending on the exchange
        cash_on_exchange = np.zeros(n_agents)
        for k in ["FOR", "AGAINST"]:
            for i in range(len(self.active_bids[k])):
                bid = self.active_bids[k][i]
                cash_on_exchange[bid.id] += bid.get_cost()

        return cash_on_exchange

    def process_bid(self, bid):
        receipt = []
        if bid.contract_type == "FOR":
            if len(self.active_bids["AGAINST"]) > 0:
                opposite_bid = heapq.heappop(self.active_bids["AGAINST"])
            else:
                heapq.heappush(self.active_bids["FOR"], bid)
                return []
        else:
            if len(self.active_bids["FOR"]) > 0:
                opposite_bid = heapq.heappop(self.active_bids["FOR"])
            else:
                heapq.heappush(self.active_bids["AGAINST"], bid)
                return []

        if bid.price + opposite_bid.price >= 1:
            shares_to_trade = min(bid.n_shares, opposite_bid.n_shares)
            remaining_bid = None
            remaining_opposite_bid = None
            if bid.n_shares > shares_to_trade:
                remaining_bid = copy.deepcopy(bid)
                remaining_bid.n_shares = bid.n_shares - shares_to_trade
                bid.n_shares = shares_to_trade
            if opposite_bid.n_shares > shares_to_trade:
                remaining_opposite_bid = copy.deepcopy(opposite_bid)
                remaining_opposite_bid.n_shares = opposite_bid.n_shares - shares_to_trade
                opposite_bid.n_shares = shares_to_trade

            bid.price = 1 - opposite_bid.price #the clearing price defined the price of the older bid
            receipt.append(bid)
            receipt.append(opposite_bid)

            if not remaining_bid == None:
                receipt = receipt + self.process_bid(remaining_bid)
            if not remaining_opposite_bid == None:
                heapq.heappush(self.active_bids[opposite_bid.contract_type], remaining_opposite_bid)
        else:
            heapq.heappush(self.active_bids[bid.contract_type], bid)
            heapq.heappush(self.active_bids[opposite_bid.contract_type], opposite_bid)

        return receipt
        
