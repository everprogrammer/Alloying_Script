import numpy as np
from scipy.optimize import linprog

def convert_molten_metal_to_alloy(initial_mass, initial_comp, target_ranges, master_alloys, 
                                 scrap_mass_max=None, scrap_comp=None, 
                                 trace_elements=None, trace_limits=None, 
                                 crucible_capacity=None, melting_loss_factor=1.02, round_to=0.1):
    """
    Convert molten metal to a target aluminum alloy using linear programming, with optional scrap metal addition.
    
    Parameters:
    - initial_mass (float): Initial mass of the molten metal (kg).
    - initial_comp (dict): Initial composition of molten metal as percentages (e.g., {'Si': 7.33, 'Cu': 1.20, ...}).
    - target_ranges (dict): Target alloy composition ranges (e.g., {'Si': (7.5, 9.5), 'Cu': (3.0, 4.0), ...}).
    - master_alloys (list): List of master alloys available (e.g., ['Si', 'Cu', 'Mn', 'Mg', 'Zn']).
    - scrap_mass_max (float, optional): Maximum amount of scrap metal available to add (kg). Set to None if no scrap.
    - scrap_comp (dict, optional): Composition of scrap metal as percentages (e.g., {'Si': 5.0, 'Cu': 0.5, ...}).
    - trace_elements (dict, optional): Trace elements to track (e.g., {'Pb': 0.157}).
    - trace_limits (dict, optional): Upper limits for trace elements (e.g., {'Pb': 0.1}).
    - crucible_capacity (float, optional): Maximum crucible capacity (kg). Set to None if no limit.
    - melting_loss_factor (float): Factor to account for melting losses (e.g., 1.02 for 2% loss).
    - round_to (float): Round additions to this increment (e.g., 0.1 for nearest 0.1 kg).
    
    Returns:
    - Dictionary with results (additions, final mass, final composition).
    """
    # Calculate initial mass of each element (kg) for molten metal
    initial_mass_elements = {k: initial_mass * (v / 100) for k, v in initial_comp.items()}
    initial_other = sum(trace_elements.values()) if trace_elements else 0
    initial_mass_elements['Al'] = initial_mass * (1 - (sum(initial_comp.values()) + initial_other) / 100)
    if trace_elements:
        for k, v in trace_elements.items():
            initial_mass_elements[k] = v
    
    # Define variables: [pure_al, scrap, al_si, al_cu, al_mn, ...] or [pure_al, al_si, al_cu, ...]
    use_scrap = scrap_mass_max is not None and scrap_mass_max > 0
    
    # Objective: Minimize total additions (coefficients are all 1)
    c = np.ones(1 + (1 if use_scrap else 0) + len(master_alloys))
    
    # Define A_eq and b_eq for each element to ensure it meets target ranges
    # Create arrays for the linear constraints
    num_constraints = 2 * len(target_ranges)  # Min and max for each element
    if trace_elements and trace_limits:
        num_constraints += len(trace_limits)  # Upper limits for trace elements
    
    num_vars = 1 + (1 if use_scrap else 0) + len(master_alloys)
    
    A_ub = np.zeros((num_constraints, num_vars))
    b_ub = np.zeros(num_constraints)
    
    constraint_idx = 0
    
    # Process each element in target_ranges
    for elem, (min_val, max_val) in target_ranges.items():
        initial_elem_kg = initial_mass_elements.get(elem, 0)
        
        # Min constraint: ensure final composition has at least min_val% of element
        # (initial_elem_kg + additions of elem) / (initial_mass + all_additions) >= min_val/100
        # Rearranging: (initial_elem_kg + additions of elem) - (min_val/100) * (initial_mass + all_additions) >= 0
        # Further: additions of elem - (min_val/100) * all_additions >= (min_val/100) * initial_mass - initial_elem_kg
        
        # Setup row for minimum constraint
        row_min = np.zeros(num_vars)
        row_min[0] = -min_val / 100  # Pure Al contribution (dilutes the element)
        
        col_idx = 1
        if use_scrap:
            row_min[col_idx] = scrap_comp.get(elem, 0) / 100 - min_val / 100  # Scrap contribution
            col_idx += 1
            
        for i, master in enumerate(master_alloys):
            if master == elem:
                row_min[col_idx + i] = 0.5 - min_val / 100  # Master alloy adds 50% of the element
            else:
                row_min[col_idx + i] = -min_val / 100  # Other master alloys dilute the element
        
        # Right-hand side: min requirement minus what we already have
        b_ub_min = initial_elem_kg - (min_val / 100) * initial_mass
        
        # Add to constraints
        A_ub[constraint_idx] = -row_min  # Flip signs for >= constraint
        b_ub[constraint_idx] = -b_ub_min  # Flip signs for >= constraint
        constraint_idx += 1
        
        # Max constraint: ensure final composition has at most max_val% of element
        # (initial_elem_kg + additions of elem) / (initial_mass + all_additions) <= max_val/100
        
        # Setup row for maximum constraint
        row_max = np.zeros(num_vars)
        row_max[0] = -max_val / 100  # Pure Al contribution (dilutes the element)
        
        col_idx = 1
        if use_scrap:
            row_max[col_idx] = scrap_comp.get(elem, 0) / 100 - max_val / 100  # Scrap contribution
            col_idx += 1
            
        for i, master in enumerate(master_alloys):
            if master == elem:
                row_max[col_idx + i] = 0.5 - max_val / 100  # Master alloy adds 50% of the element
            else:
                row_max[col_idx + i] = -max_val / 100  # Other master alloys dilute the element
        
        # Right-hand side: max requirement minus what we already have
        b_ub_max = initial_elem_kg - (max_val / 100) * initial_mass
        
        # Add to constraints
        A_ub[constraint_idx] = row_max
        b_ub[constraint_idx] = b_ub_max
        constraint_idx += 1
    
    # Add trace element constraints if specified
    if trace_elements and trace_limits:
        for elem, limit in trace_limits.items():
            trace_mass = initial_mass_elements.get(elem, 0)
            
            row = np.zeros(num_vars)
            row[0] = -limit / 100  # Pure Al dilutes the trace element
            
            col_idx = 1
            if use_scrap:
                row[col_idx] = scrap_comp.get(elem, 0) / 100 - limit / 100
                col_idx += 1
                
            for i in range(len(master_alloys)):
                row[col_idx + i] = -limit / 100  # All master alloys dilute the trace element
            
            # Right-hand side: limit minus what we already have
            b_trace = trace_mass - (limit / 100) * initial_mass
            
            # Add to constraints
            A_ub[constraint_idx] = row
            b_ub[constraint_idx] = b_trace
            constraint_idx += 1
    
    # Add crucible capacity constraint if specified
    if crucible_capacity is not None:
        row_capacity = np.ones(num_vars)  # All variables represent mass additions
        A_ub = np.vstack([A_ub, row_capacity])
        b_ub = np.append(b_ub, crucible_capacity - initial_mass)
    
    # Set bounds for variables
    bounds = [(0, None)] * num_vars  # All additions must be non-negative
    if use_scrap:
        bounds[1] = (0, scrap_mass_max)  # Limit on scrap addition
    
    # Run linear programming optimization
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    # Process results
    if result.success:
        # Extract results
        additions = result.x * melting_loss_factor
        
        # Round additions to practical amounts
        additions_rounded = np.round(additions / round_to) * round_to
        
        # Parse results into a structured dictionary
        pure_al = additions_rounded[0]
        
        idx = 1
        scrap_added = 0
        if use_scrap:
            scrap_added = additions_rounded[idx]
            idx += 1
        
        master_adds = {elem: additions_rounded[idx + i] for i, elem in enumerate(master_alloys)}
        
        # Calculate final mass and composition
        final_mass = initial_mass_elements.copy()
        final_mass['Al'] += pure_al
        
        if scrap_added > 0 and scrap_comp:
            for elem, comp in scrap_comp.items():
                if elem not in final_mass:
                    final_mass[elem] = 0
                final_mass[elem] += (comp / 100) * scrap_added
            
            # Calculate aluminum in scrap
            scrap_al = 1 - sum(comp / 100 for comp in scrap_comp.values())
            final_mass['Al'] += scrap_al * scrap_added
        
        # Add master alloy contributions
        for elem, mass in master_adds.items():
            if mass > 0:
                final_mass['Al'] += 0.5 * mass  # 50% Al in master alloy
                if elem not in final_mass:
                    final_mass[elem] = 0
                final_mass[elem] += 0.5 * mass  # 50% element in master alloy
        
        # Calculate total mass and final composition percentages
        total_mass = sum(final_mass.values())
        final_comp = {k: (v / total_mass) * 100 for k, v in final_mass.items()}
        
        # Only include master alloys with non-zero additions in results
        master_alloy_additions = {f"Al-{elem} (50%)": mass for elem, mass in master_adds.items() if mass > 0}
        
        # Prepare results dictionary
        results = {
            'initial_mass': initial_mass,
            'initial_composition_kg': initial_mass_elements,
            'additions': {
                'Pure Aluminum': pure_al,
                **({"Scrap Metal": scrap_added} if use_scrap else {}),
                **master_alloy_additions
            },
            'total_added_mass': sum([pure_al, scrap_added] + list(master_adds.values())),
            'final_total_mass': total_mass,
            'final_mass_kg': final_mass,
            'final_composition_percent': final_comp
        }
        
        return results
    else:
        raise Exception("Optimization failed: " + result.message)

def print_results(results, target_ranges, trace_elements=None, trace_limits=None):
    print(f"\nInitial mass: {results['initial_mass']:.2f} kg")
    print("Initial composition (kg):")
    for elem, mass in results['initial_composition_kg'].items():
        print(f"  {elem}: {mass:.4f} kg")
    
    print("\nAdditions (rounded for practicality):")
    for elem, mass in results['additions'].items():
        if mass > 0:  # Only print non-zero additions
            print(f"  {elem}: {mass:.2f} kg")
    
    print(f"Total added mass: {results['total_added_mass']:.2f} kg")
    print(f"Final total mass: {results['final_total_mass']:.2f} kg")
    
    print("\nFinal composition (%):")
    for elem, (min_val, max_val) in target_ranges.items():
        print(f"  {elem}: {results['final_composition_percent'][elem]:.2f}% (Target: {min_val}–{max_val})")
    print(f"  Al: {results['final_composition_percent']['Al']:.2f}% (Balance)")
    print(f"  Other (trace elements): {results['final_composition_percent'].get('Other', 0):.4f}%")
    if trace_elements and trace_limits:
        for elem, limit in trace_limits.items():
            print(f"  {elem}: {results['final_composition_percent'][elem]:.4f}% (Target: <= {limit})")

# Example usage for industrial application
if __name__ == "__main__":
    # Define target alloy (e.g., A380, A356, etc.)
    target_alloy = {
        'Si': (7.5, 9.5),  # A380 example
        'Cu': (3.0, 4.0),
        'Fe': (0.0, 1.3),
        'Mn': (0.0, 0.5),
        'Mg': (0.0, 0.1),
        'Zn': (0.0, 3.0)
    }
    
    # Initial composition of molten metal (modify as needed)
    initial_mass = 100  # kg
    initial_comp = {
        'Si': 7.33,
        'Cu': 1.20,
        'Fe': 0.855,
        'Mn': 0.0577,
        'Mg': 0.0,
        'Zn': 0.0831
    }
    
    # Scrap metal details (optional, set to None if not using scrap)
    scrap_mass_max = 0  # Maximum amount of scrap available (kg)
    scrap_comp = {
        'Si': 8.0,  # Scrap composition in percentages
        'Cu': 0.5,
        'Fe': 0.3,
        'Mn': 0.02,
        'Mg': 0.1,
        'Zn': 0.05,
        'Pb': 0.02  # Adding Pb to scrap for testing
    }
    
    # Trace elements and limits
    trace_elements = None
    trace_limits = None
    master_alloys = ['Si', 'Cu', 'Mn', 'Mg', 'Zn']

    # Run the conversion
    results = convert_molten_metal_to_alloy(
        initial_mass=initial_mass,
        initial_comp=initial_comp,
        target_ranges=target_alloy,
        master_alloys=master_alloys,
        scrap_mass_max=None,
        scrap_comp=None,
        trace_elements=trace_elements,
        trace_limits=trace_limits,
        crucible_capacity=None,  # No crucible capacity constraint
        melting_loss_factor=1.02,  # 2% safety margin for melting losses
        round_to=0.1  # Round to nearest 0.1 kg
    )

    # Print results
    print_results(results, target_alloy, trace_elements, trace_limits)