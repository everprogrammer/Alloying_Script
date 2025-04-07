import numpy as np
from scipy.optimize import minimize

def optimize_alloy(
    initial_composition,
    target_spec,
    master_alloys,
    scrap_composition=None,  # New: Composition of available scrap (e.g., {'Si': 5.0, 'Al': 95.0})
    scrap_cost_ratio=0.5,    # New: Cost of scrap relative to master alloys (0.5 = half the cost)
    initial_mass=100,
    solver_method='SLSQP',
    max_iter=1000,
    tol=1e-6
):
    """
    Optimizes master alloy AND scrap additions to meet target composition.
    scrap_cost_ratio: 0.5 means scrap is 50% the cost of master alloys.
    """
    # --- Step 1: Prepare Variables ---
    alloy_keys = list(master_alloys.keys())
    if scrap_composition:
        alloy_keys.append('Scrap')  # Add scrap as an optional addition
    num_alloys = len(alloy_keys)
    
    # Objective: Minimize total cost (scrap is cheaper)
    def objective(x):
        total_cost = np.sum(x[:-1]) if scrap_composition else np.sum(x)  # Master alloys cost = 1x
        if scrap_composition:
            total_cost += scrap_cost_ratio * x[-1]  # Scrap cost = scrap_cost_ratio x
        return total_cost
    
    # --- Step 2: Constraints ---
    def constraints(x):
        total_addition = np.sum(x)
        final_mass = initial_mass + total_addition
        
        # Initialize element masses
        element_masses = {
            el: (initial_composition.get(el, 0) / 100) * initial_mass 
            for el in target_spec
        }
        
        # Add contributions from master alloys
        for i, key in enumerate(alloy_keys[:-1] if scrap_composition else alloy_keys):
            for el, pct in master_alloys[key].items():
                element_masses[el] = element_masses.get(el, 0) + (pct / 100) * x[i]
        
        # Add contributions from scrap (if used)
        if scrap_composition:
            for el, pct in scrap_composition.items():
                element_masses[el] = element_masses.get(el, 0) + (pct / 100) * x[-1]
        
        # Check target ranges
        constraint_list = []
        for el, (low, high) in target_spec.items():
            final_pct = (element_masses[el] / final_mass) * 100
            constraint_list.append(final_pct - low)   # >= 0
            constraint_list.append(high - final_pct)  # >= 0
        return np.array(constraint_list)
    
    # --- Step 3: Solver Setup ---
    bounds = [(0, None)] * num_alloys
    cons = [{'type': 'ineq', 'fun': lambda x, i=i: constraints(x)[i]} 
            for i in range(len(target_spec) * 2)]
    x0 = np.ones(num_alloys) * 0.1  # Start with 0.1 kg for each
    
    # --- Step 4: Run Optimization ---
    result = minimize(
        objective,
        x0,
        method=solver_method,
        bounds=bounds,
        constraints=cons,
        options={'maxiter': max_iter, 'disp': True},
        tol=tol
    )
    
    # --- Step 5: Print Results ---
    if result.success:
        print("\nOptimization successful!")
        total_added = np.sum(result.x)
        final_mass = initial_mass + total_added
        print(f"Initial mass: {initial_mass:.2f} kg")
        print(f"Total additions: {total_added:.2f} kg")
        print(f"Final mass: {final_mass:.2f} kg")
        print(f"Total cost (relative): {objective(result.x):.2f}\n")
        
        for i, key in enumerate(alloy_keys):
            if result.x[i] > 1e-3:
                cost = scrap_cost_ratio if key == 'Scrap' else 1.0
                print(f"Add {result.x[i]:.3f} kg of {key} (cost: {cost}x)")
    else:
        print("\nOptimization failed:", result.message)
    
    return result

# Example Usage
if __name__ == "__main__":
    from constants import (INITIAL_COMP_AL91, INITIAL_COMP_AL95, 
                           TARGET_RANGES_A356, INITIAL_COMP_A380_TEST,
                           TARGET_RANGES_A380, MASTER_ALLOYS, SCRAP_COMP)


    result = optimize_alloy(
        initial_composition=INITIAL_COMP_AL95,
        target_spec=TARGET_RANGES_A356,
        master_alloys=MASTER_ALLOYS,
        scrap_composition=SCRAP_COMP,
        scrap_cost_ratio=0.1  # Scrap is 50% the cost of master alloys
    )