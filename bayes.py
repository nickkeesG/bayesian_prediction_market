import math

def prob_to_evidence(p):
    return math.log(p, 2) - math.log((1-p), 2)

def evidence_to_prob(w):
    update_factor = 2**w
    return update_factor / (update_factor + 1)
