## Structure of the script

import numpy as np
from scipy.optimize import minimize
import constants as c

# Sample input data
M0 = 100  # kg of initial metal
initial_composition = c.INITIAL_COMP_AL91
target_spec = c.TARGET_RANGES_A356

master_alloys = {
    'Pure_Al': {'Al': 100},
    'Al-Cu': {'Al': 50, 'Cu': 50},
    'Al-Si': {'Al': 50, 'Si': 50},
    'Al-Fe': {'Al': 50, 'Fe': 50},
    'Al-Mn': {'Al': 50, 'Mn': 50},
    'Al-Pb': {'Al': 50, 'Pb': 50},
    'Al-Zn': {'Al': 50, 'Zn': 50},
    'Al-Ti': {'Al': 50, 'Ti': 50},
    'Al-Mg': {'Al': 50, 'Mg': 50},
    'Al-Ni': {'Al': 50, 'Ni': 50},
}

# Order matters: match the order of variables with master_alloys
alloy_keys = ['Pure_Al', 'Al-Cu', 'Al-Si', 'Al-Fe']

# Objective: Minimize total additions
def objective(x):
    return np.sum(x)

# Constraints: All elements within target ranges
def constraints(x):
    total_addition = np.sum(x)
    final_mass = M0 + total_addition

    # Initialize mass of each element
    element_masses = {el: (initial_composition.get(el, 0) / 100) * M0 for el in target_spec}

    # Add contributions from master alloys
    for i, key in enumerate(alloy_keys):
        for el, pct in master_alloys[key].items():
            element_masses[el] = element_masses.get(el, 0) + (pct / 100) * x[i]

    # Final percentages
    constraint_list = []
    for el, (low, high) in target_spec.items():
        final_pct = (element_masses[el] / final_mass) * 100
        constraint_list.append(final_pct - low)  # should be >= 0
        constraint_list.append(high - final_pct)  # should be >= 0

    return constraint_list

# Bounds: you cannot subtract alloy, so all >= 0
bounds = [(0, None)] * len(alloy_keys)

# Constraints formatted for scipy
cons = [{'type': 'ineq', 'fun': lambda x, i=i: constraints(x)[i]} for i in range(len(target_spec)*2)]

# Initial guess
x0 = np.zeros(len(alloy_keys))

# Solve
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)

# Output
if result.success:
    print("Solution found!")
    for i, key in enumerate(alloy_keys):
        print(f"Add {result.x[i]:.3f} kg of {key}")
else:
    print("Optimization failed:", result.message)
