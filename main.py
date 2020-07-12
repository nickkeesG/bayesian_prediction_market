import matplotlib.pyplot as plt
from simulator import run_simulation

p, b = run_simulation(n_agents = 100, n_time_steps = 100, time_per_evidence = 100, n_evidence = 1, starting_cash = 1000, update_when_receiving = False)

plt.figure(figsize=(12,4))
plt.plot(p)
plt.plot(b)
plt.legend(['Price', 'Total evidence as belief'])
plt.xlabel("Time (market cycles)")
plt.grid()
plt.show()
