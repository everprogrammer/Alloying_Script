import numpy as np
from scipy.optimize import minimize
from constants import *


def optimize_alloy(
    initial_composition,
    target_spec,
    master_alloys,
    initial_mass=100,
    solver_method='SLSQP',  # Optimization algorithm ('SLSQP', 'COBYLA', etc.)
    max_iter=1000,
    tol=1e-6
):
    """
    Optimize master alloy additions to meet target composition.
    
    Args:
        initial_composition: Dict of initial alloy composition (wt%).
        target_spec: Dict of target ranges (e.g., {'Si': (7.5, 9.5)}).
        master_alloys: Dict of master alloys (e.g., {'Al-Si': {'Si': 50}}).
        initial_mass: Initial mass of metal (kg).
        solver_method: Optimization method ('SLSQP', 'COBYLA', etc.).
        max_iter: Maximum solver iterations.
        tol: Tolerance for convergence.
    
    Returns:
        result: Optimization result with `x` (additions in kg) and
        prints total mass after additions.
    """
    # Convert master_alloys to a list of keys (order matters for variables)
    alloy_keys = list(master_alloys.keys())
    num_alloys = len(alloy_keys)
    
    # Objective: Minimize total additions (sum of x)
    objective = lambda x: np.sum(x)
    
    # Constraints: All elements must be within target ranges
    def constraints(x):
        total_addition = np.sum(x)
        final_mass = initial_mass + total_addition
        
        # Initialize element masses from initial composition
        element_masses = {
            el: (initial_composition.get(el, 0) / 100) * initial_mass 
            for el in target_spec
        }
        
        # Add contributions from master alloys
        for i, key in enumerate(alloy_keys):
            for el, pct in master_alloys[key].items():
                element_masses[el] = element_masses.get(el, 0) + (pct / 100) * x[i]
        
        # Check if elements are within target ranges
        constraint_list = []
        for el, (low, high) in target_spec.items():
            final_pct = (element_masses[el] / final_mass) * 100
            constraint_list.append(final_pct - low)   # >= 0
            constraint_list.append(high - final_pct)  # >= 0
        
        return np.array(constraint_list)
    
    # Bounds: No negative additions
    bounds = [(0, None)] * num_alloys
    
    # Constraints for scipy (each >= 0)
    cons = [
        {'type': 'ineq', 'fun': lambda x, i=i: constraints(x)[i]} 
        for i in range(len(target_spec) * 2)
    ]
    
    # Initial guess: Small positive value (avoid zeros)
    x0 = np.ones(num_alloys) * 0.1
    
    # Solve
    result = minimize(
        objective,
        x0,
        method=solver_method,
        bounds=bounds,
        constraints=cons,
        options={'maxiter': max_iter, 'disp': False},
        tol=tol
    )

    if result.success:
        print("\nOptimization successful!")
        total_added = np.sum(result.x)
        final_mass = initial_mass + total_added
        print(f"Initial mass: {initial_mass:.2f} kg")
        print(f"Final mass: {final_mass:.2f} kg \n")
        for i, key in enumerate(master_alloys.keys()):
            if result.x[i] > 1e-1:  # Only show additions > 1 gram
                print(f"Add {result.x[i]:.2f} kg of {key}")
    else:
        print("\nOptimization failed:", result.message)
        print("Try relaxing constraints or adding more master alloys.")
    
    return result

# Example Usage
if __name__ == "__main__":

    initial_comp = INITIAL_COMP_AL91
    target_spec = A380_SPEC
    initial_mass = 100 #kg

    # Optimize for A356 (requires Mg addition)
    result = optimize_alloy(
        initial_composition=initial_comp,
        target_spec=target_spec,
        master_alloys=MASTER_ALLOYS,
        initial_mass=initial_mass,
        solver_method='SLSQP'  # COBYLA Better for tight constraints + SLSQP
    )

