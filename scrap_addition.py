import numpy as np
from scipy.optimize import minimize
from constants import INITIAL_WEIGHT
# Calculate the optimal amount of scrap to add to molten metal to approach target composition

def calculate_scrap_addition(initial_comp, scrap_comp, target_ranges, initial_weight=INITIAL_WEIGHT):
    """
    Calculate the optimal amount of scrap to add to molten metal to approach target composition.
    
    Args:
        initial_comp: Dict of initial composition (% by weight)
        scrap_comp: Dict of scrap composition (% by weight)
        target_ranges: Dict of target ranges (min, max) for each element
        initial_weight: Initial weight of molten metal (kg)
        
    Returns:
        Dict containing:
            - optimal_scrap_weight: Recommended scrap weight to add (kg)
            - final_composition: Predicted final composition (%)
            - status: Optimization status
            - message: Explanation of results
    """
    
    # Prepare data - ensure all elements are accounted for
    all_elements = set(initial_comp.keys()).union(scrap_comp.keys()).union(target_ranges.keys())
    
    # Normalize compositions (fill missing elements with 0)
    initial_comp_normalized = {el: initial_comp.get(el, 0) for el in all_elements}
    scrap_comp_normalized = {el: scrap_comp.get(el, 0) for el in all_elements}
    
    # Get target midpoints (our optimization target)
    target_midpoints = {el: np.mean(bounds) for el, bounds in target_ranges.items() 
                       if el in all_elements}
    
    # Objective function to minimize
    def objective(scrap_weight):
        total_weight = initial_weight + scrap_weight
        final_comp = {}
        
        # Calculate final composition for each element
        for el in all_elements:
            initial_amt = initial_comp_normalized[el] * initial_weight / 100
            scrap_amt = scrap_comp_normalized[el] * scrap_weight / 100
            final_comp[el] = (initial_amt + scrap_amt) / total_weight * 100
        
        # Calculate penalty based on deviation from target and exceeding max bounds
        penalty = 0
        for el, target in target_midpoints.items():
            if el in final_comp:
                # Penalize deviation from target midpoint
                penalty += (final_comp[el] - target)**2
                
                # Heavily penalize exceeding upper bounds
                if el in target_ranges:
                    upper_bound = target_ranges[el][1]
                    if final_comp[el] > upper_bound:
                        penalty += 10 * (final_comp[el] - upper_bound)**2
        
        return penalty
    
    # Constraints: scrap weight must be positive
    constraints = ({'type': 'ineq', 'fun': lambda x: x})
    
    # Initial guess (10% of initial weight)
    x0 = initial_weight * 0.1
    
    # Optimize
    result = minimize(objective, x0, method='SLSQP', constraints=constraints)
    
    # Calculate final composition at optimal scrap weight
    optimal_scrap_weight = result.x[0]
    total_weight = initial_weight + optimal_scrap_weight
    final_composition = {}
    
    for el in all_elements:
        initial_amt = initial_comp_normalized[el] * initial_weight / 100
        scrap_amt = scrap_comp_normalized[el] * optimal_scrap_weight / 100
        final_composition[el] = (initial_amt + scrap_amt) / total_weight * 100
    
    # Prepare result message
    message = "Optimization successful." if result.success else f"Optimization ended with: {result.message}"
    
    return {
        'optimal_scrap_weight': optimal_scrap_weight,
        'final_composition': final_composition,
        'status': result.success,
        'message': message,
        'target_ranges': target_ranges
    }


def print_results(result):
    """Print the optimization results in a readable format.
    
    Args:
        result: Dictionary containing the optimization results (including target_ranges)
    """
    print(f"Optimal scrap weight to add: {result['optimal_scrap_weight'] * LOSS_FACTOR_SCRAP:.2f} kg")
    print("\nFinal composition:")
    for el, val in result['final_composition'].items():
        if el in result['target_ranges']:
            target_min, target_max = result['target_ranges'][el]
            status = "✅ Within target" if target_min <= val <= target_max else "⚠️ Outside target"
            print(f"{el}: {val:.4f}% (Target: {target_min}-{target_max}%) {status}")
        else:
            print(f"{el}: {val:.4f}% (No target specified)")
    
    print(f"\nStatus: {result['message']}")

# Example usage
if __name__ == "__main__":
    from constants import *
    
    result = calculate_scrap_addition(
        initial_comp=INITIAL_COMP_AL91,
        scrap_comp=SCRAP_COMP,
        target_ranges=TARGET_RANGES_A380,
        initial_weight=INITIAL_WEIGHT  
    )

    print_results(result)