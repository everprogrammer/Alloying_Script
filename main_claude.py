from scipy.optimize import linprog
import numpy as np

class IndustrialAlloyOptimizer:
    def __init__(self):
        self.master_alloys = []
        self.pure_elements = []

    def add_master_alloy(self, name, composition, cost_per_kg):
        """
        Register master alloys (composition in %, cost in $/kg).
        
        Args:
            name (str): Name of the master alloy
            composition (dict): Dictionary with element symbols as keys and percentages as values
            cost_per_kg (float): Cost per kg in dollars
        """
        self.master_alloys.append({
            'name': name,
            'composition': {k: v/100 for k, v in composition.items()},  # Convert % to fraction
            'cost': cost_per_kg
        })
    
    def add_pure_element(self, element, cost_per_kg):
        """
        Add a pure element that can be used in the optimization.
        
        Args:
            element (str): Element symbol
            cost_per_kg (float): Cost per kg in dollars
        """
        self.pure_elements.append({
            'name': f"Pure {element}",
            'element': element,
            'cost': cost_per_kg
        })

    def optimize(self, initial_kg, target_ranges, max_total_addition=None, debug=False):
        """
        Optimizes additions to meet element ranges using linear programming with improved constraint formulation.
        
        Args:
            initial_kg (dict): Current composition in kg
            target_ranges (dict): Target composition ranges in % {element: (min_pct, max_pct)}
            max_total_addition (float, optional): Maximum allowed total addition in kg
            debug (bool): Whether to print debug information
            
        Returns:
            dict: Optimization results including success status, additions, cost, and final composition
        """
        if debug:
            print("Starting optimization...")
            print(f"Initial composition (kg): {initial_kg}")
            print(f"Target ranges (%): {target_ranges}")
        
        # Calculate initial total weight
        initial_weight = sum(initial_kg.values())
        if debug:
            print(f"Initial total weight: {initial_weight} kg")
        
        # Get list of all elements involved
        elements = set()
        elements.update(initial_kg.keys())
        elements.update(target_ranges.keys())
        
        for alloy in self.master_alloys:
            elements.update(alloy['composition'].keys())
        
        for elem in self.pure_elements:
            elements.add(elem['element'])
        
        if debug:
            print(f"Elements involved: {elements}")
        
        # Initialize variables for optimization
        num_alloys = len(self.master_alloys)
        num_pure_elements = len(self.pure_elements)
        total_vars = num_alloys + num_pure_elements
        
        if debug:
            print(f"Number of variables: {total_vars}")
            print(f"  - Master alloys: {num_alloys}")
            print(f"  - Pure elements: {num_pure_elements}")
        
        # Objective: Minimize cost
        costs = [m['cost'] for m in self.master_alloys] + [e['cost'] for e in self.pure_elements]
        
        # ======== IMPROVED CONSTRAINT FORMULATION ========
        # These constraints are formulated differently to ensure robustness
        
        # For each element E with range [min%, max%]:
        # Let T = initial_total_weight
        # Let W_E = initial_weight of element E
        # Let A_i = weight of addition i
        # Let f_Ei = fraction of element E in addition i
        
        # For each element, the final percentage must be in range [min%, max%]:
        # min% ≤ (W_E + Σ(A_i * f_Ei)) / (T + Σ(A_i)) ≤ max%
        
        # Rearranging for min constraint:
        # (W_E + Σ(A_i * f_Ei)) / (T + Σ(A_i)) ≥ min%
        # W_E + Σ(A_i * f_Ei) ≥ min% * (T + Σ(A_i))
        # W_E + Σ(A_i * f_Ei) ≥ min% * T + min% * Σ(A_i)
        # W_E + Σ(A_i * f_Ei) - min% * Σ(A_i) ≥ min% * T
        # Σ(A_i * (f_Ei - min%)) ≥ min% * T - W_E
        
        # Rearranging for max constraint:
        # (W_E + Σ(A_i * f_Ei)) / (T + Σ(A_i)) ≤ max%
        # W_E + Σ(A_i * f_Ei) ≤ max% * (T + Σ(A_i))
        # W_E + Σ(A_i * f_Ei) ≤ max% * T + max% * Σ(A_i)
        # W_E + Σ(A_i * f_Ei) - max% * Σ(A_i) ≤ max% * T
        # Σ(A_i * (f_Ei - max%)) ≤ max% * T - W_E
        
        A_ub = []
        b_ub = []
        
        # Constraints for element percentages
        for elem in elements:
            if elem in target_ranges:
                min_pct, max_pct = target_ranges[elem]
                min_fraction = min_pct / 100
                max_fraction = max_pct / 100
                
                # Current amount of element
                current_kg = initial_kg.get(elem, 0)
                
                # --- Min percentage constraint ---
                min_row = []
                
                # Coefficients for master alloys
                for alloy in self.master_alloys:
                    # How much this element the alloy contributes minus minimum required fraction
                    coefficient = alloy['composition'].get(elem, 0) - min_fraction
                    min_row.append(coefficient)
                
                # Coefficients for pure elements
                for pure in self.pure_elements:
                    if pure['element'] == elem:
                        coefficient = 1.0 - min_fraction  # Pure element is 100% of itself
                    else:
                        coefficient = 0 - min_fraction    # Other pure elements don't contain this element
                    min_row.append(coefficient)
                
                # Add constraint: Σ(A_i * (f_Ei - min%)) ≥ min% * T - W_E
                A_ub.append([-x for x in min_row])  # Negate for <= form
                b_ub.append(-(min_fraction * initial_weight - current_kg))  # Negate for <= form
                
                # --- Max percentage constraint ---
                max_row = []
                
                # Coefficients for master alloys
                for alloy in self.master_alloys:
                    coefficient = alloy['composition'].get(elem, 0) - max_fraction
                    max_row.append(coefficient)
                
                # Coefficients for pure elements
                for pure in self.pure_elements:
                    if pure['element'] == elem:
                        coefficient = 1.0 - max_fraction
                    else:
                        coefficient = 0 - max_fraction
                    max_row.append(coefficient)
                
                # Add constraint: Σ(A_i * (f_Ei - max%)) ≤ max% * T - W_E
                A_ub.append(max_row)
                b_ub.append(max_fraction * initial_weight - current_kg)
        
        # Add constraint for maximum total addition if specified
        if max_total_addition is not None:
            max_addition_row = [1.0] * total_vars  # Coefficient 1 for each variable
            A_ub.append(max_addition_row)
            b_ub.append(max_total_addition)
        
        # Set bounds for all variables (no negative additions)
        bounds = [(0, None) for _ in range(total_vars)]
        
        # Convert to numpy arrays
        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)
        
        if debug:
            print(f"Constraints matrix shape: {A_ub.shape}")
            print(f"Bounds vector length: {len(b_ub)}")
        
        # Solve the LP problem using the HiGHS solver
        try:
            res = linprog(
                c=costs,
                A_ub=A_ub,
                b_ub=b_ub,
                bounds=bounds,
                method='highs',
                options={'disp': debug}
            )
            
            if not res.success:
                if debug:
                    print("Optimization failed:", res.message)
                return {
                    'success': False,
                    'message': f"Optimization failed: {res.message}",
                    'status': res.status,
                    'details': res.message
                }
                
        except Exception as e:
            if debug:
                print(f"Error during optimization: {str(e)}")
            return {
                'success': False,
                'message': f"Error during optimization: {str(e)}",
                'details': str(e)
            }
        
        # Process results
        additions = {}
        total_cost = 0
        
        # Process master alloy additions
        for i, alloy in enumerate(self.master_alloys):
            if res.x[i] > 0.001:  # Ignore tiny additions
                addition_kg = round(res.x[i], 3)
                additions[alloy['name']] = addition_kg
                total_cost += addition_kg * alloy['cost']
        
        # Process pure element additions
        for i, element in enumerate(self.pure_elements):
            idx = i + num_alloys
            if res.x[idx] > 0.001:  # Ignore tiny additions
                addition_kg = round(res.x[idx], 3)
                additions[element['name']] = addition_kg
                total_cost += addition_kg * element['cost']
        
        # Calculate final weight and composition
        final_weight = initial_weight + sum(additions.values())
        
        # Calculate final composition
        final_comp = {elem: 0 for elem in elements}
        
        # Start with initial composition
        for elem, amount in initial_kg.items():
            final_comp[elem] = amount
        
        # Add contributions from alloy additions
        for i, alloy in enumerate(self.master_alloys):
            addition_kg = res.x[i]
            if addition_kg > 0.001:
                for elem, fraction in alloy['composition'].items():
                    final_comp[elem] = final_comp.get(elem, 0) + addition_kg * fraction
        
        # Add contributions from pure elements
        for i, element in enumerate(self.pure_elements):
            idx = i + num_alloys
            addition_kg = res.x[idx]
            if addition_kg > 0.001:
                elem = element['element']
                final_comp[elem] = final_comp.get(elem, 0) + addition_kg
        
        # Convert to percentages
        final_pct = {elem: round(amount / final_weight * 100, 2) for elem, amount in final_comp.items()}
        
        # Check if the final composition meets all target ranges
        in_spec = True
        out_of_spec = {}
        
        # Check each element against its target range
        for elem, (min_pct, max_pct) in target_ranges.items():
            if elem in final_pct:
                actual_pct = final_pct[elem]
                # Allow very small tolerance (0.01%) for numerical precision issues
                if actual_pct < min_pct - 0.01 or actual_pct > max_pct + 0.01:
                    in_spec = False
                    out_of_spec[elem] = {
                        'target': f"{min_pct}-{max_pct}%",
                        'actual': f"{actual_pct}%"
                    }
        
        # Return results
        return {
            'success': True,
            'additions': {name: round(kg, 3) for name, kg in additions.items()},
            'cost': round(total_cost, 2),
            'initial_weight': round(initial_weight, 2),
            'final_weight': round(final_weight, 2),
            'initial_composition': {elem: round(amount / initial_weight * 100, 2) for elem, amount in initial_kg.items()},
            'final_composition': final_pct,
            'in_specification': in_spec,
            'out_of_specification': out_of_spec if not in_spec else None,
            'optimization_status': {
                'status': res.status,
                'message': res.message,
                'fun': round(res.fun, 2),  # Objective function value (total cost)
                'iteration': res.nit,
            }
        }
    
    def analyze_problem(self, initial_kg, target_ranges):
        """
        Analyzes the problem to identify potential issues before optimization.
        
        Args:
            initial_kg (dict): Current composition in kg
            target_ranges (dict): Target composition ranges in % {element: (min_pct, max_pct)}
            
        Returns:
            dict: Analysis results including feasibility assessment
        """
        initial_weight = sum(initial_kg.values())
        initial_pct = {elem: amount/initial_weight*100 for elem, amount in initial_kg.items()}
        
        # Identify elements that need to be increased
        need_increase = {}
        for elem, (min_pct, _) in target_ranges.items():
            current = initial_pct.get(elem, 0)
            if current < min_pct:
                need_increase[elem] = {
                    'current': current,
                    'min_needed': min_pct,
                    'deficit': min_pct - current
                }
        
        # Identify elements that need to be decreased
        need_decrease = {}
        for elem, (_, max_pct) in target_ranges.items():
            current = initial_pct.get(elem, 0)
            if current > max_pct:
                need_decrease[elem] = {
                    'current': current,
                    'max_allowed': max_pct,
                    'excess': current - max_pct
                }
        
        # Check if we have master alloys or pure elements for elements that need increasing
        available_sources = {}
        for elem in need_increase:
            sources = []
            
            # Check master alloys
            for alloy in self.master_alloys:
                if elem in alloy['composition'] and alloy['composition'][elem] > 0:
                    sources.append({
                        'name': alloy['name'],
                        'content': alloy['composition'][elem] * 100,
                        'cost': alloy['cost']
                    })
            
            # Check pure elements
            for pure in self.pure_elements:
                if pure['element'] == elem:
                    sources.append({
                        'name': pure['name'],
                        'content': 100,
                        'cost': pure['cost']
                    })
            
            available_sources[elem] = sources
        
        # Identify potential issues
        issues = []
        
        # Issue 1: Elements that need increasing but have no available source
        for elem, info in need_increase.items():
            if elem not in available_sources or not available_sources[elem]:
                issues.append(f"No source available for {elem} which needs to be increased from {info['current']:.2f}% to at least {info['min_needed']:.2f}%")
        
        # Issue 2: Elements that need decreasing but can only be diluted
        for elem, info in need_decrease.items():
            # Can only decrease by dilution
            issues.append(f"{elem} needs to be decreased from {info['current']:.2f}% to max {info['max_allowed']:.2f}%, which requires dilution with other additions")
        
        # Issue 3: Check if the maximum allowed addition is too small
        total_min_addition = 0
        for elem, info in need_increase.items():
            # Simple estimate based on current deficit
            # This is a rough approximation assuming we can add pure elements
            element_mass_needed = (info['deficit'] / 100) * initial_weight
            
            # Find the most concentrated source
            max_concentration = 0
            for source in available_sources.get(elem, []):
                max_concentration = max(max_concentration, source['content'] / 100)
            
            if max_concentration > 0:
                min_addition = element_mass_needed / max_concentration
                total_min_addition += min_addition
        
        # Return analysis
        return {
            'initial_composition_pct': initial_pct,
            'elements_to_increase': need_increase,
            'elements_to_decrease': need_decrease,
            'available_sources': available_sources,
            'estimated_min_addition': round(total_min_addition, 2),
            'issues': issues,
            'has_critical_issues': len(issues) > 0
        }

# Function for running multiple tests with different scenarios
def run_test_scenario(name, initial_kg, target_ranges, optimizer, max_addition=None):
    print(f"\n{'='*80}")
    print(f"TESTING SCENARIO: {name}")
    print(f"{'='*80}")
    
    # First analyze the problem
    analysis = optimizer.analyze_problem(initial_kg, target_ranges)
    
    print(f"Initial composition: {analysis['initial_composition_pct']}")
    
    if analysis['elements_to_increase']:
        print("\nElements that need to be increased:")
        for elem, info in analysis['elements_to_increase'].items():
            print(f"  {elem}: {info['current']:.2f}% → {info['min_needed']:.2f}% (deficit: {info['deficit']:.2f}%)")
            
            # Show available sources
            if elem in analysis['available_sources'] and analysis['available_sources'][elem]:
                print("    Available sources:")
                for source in analysis['available_sources'][elem]:
                    print(f"      {source['name']}: {source['content']:.1f}%, cost: ${source['cost']}/kg")
            else:
                print("    No sources available for this element!")
    
    if analysis['elements_to_decrease']:
        print("\nElements that need to be decreased:")
        for elem, info in analysis['elements_to_decrease'].items():
            print(f"  {elem}: {info['current']:.2f}% → {info['max_allowed']:.2f}% (excess: {info['excess']:.2f}%)")
    
    if analysis['issues']:
        print("\nPotential issues:")
        for issue in analysis['issues']:
            print(f"  - {issue}")
        
        if analysis['has_critical_issues']:
            print("\nWARNING: Critical issues found - optimization may not succeed!")
    
    print(f"\nEstimated minimum addition needed: {analysis['estimated_min_addition']} kg")
    
    # Run the optimization
    print("\nRunning optimization...")
    result = optimizer.optimize(
        initial_kg=initial_kg,
        target_ranges=target_ranges,
        max_total_addition=max_addition,
        debug=True
    )
    
    # Display results
    print("\nOptimization Result:")
    if result['success']:
        print("  Status: SUCCESS")
        print(f"  Additions needed:")
        for alloy, amount in result['additions'].items():
            print(f"    {alloy}: {amount:.3f} kg")
        
        print(f"\n  Total Cost: ${result['cost']:.2f}")
        print(f"  Final Weight: {result['final_weight']:.2f} kg")
        
        print("\n  Final Composition:")
        for element, percentage in result['final_composition'].items():
            target = target_ranges.get(element, ("N/A", "N/A"))
            target_str = f"{target[0]}-{target[1]}%" if target[0] != "N/A" else "N/A"
            in_range = "" if target[0] == "N/A" else "✓" if target[0] <= percentage <= target[1] else "❌"
            print(f"    {element}: {percentage:.2f}% (Target: {target_str}) {in_range}")
        
        if not result['in_specification']:
            print("\n  WARNING: Some elements are out of specification:")
            for elem, details in result['out_of_specification'].items():
                print(f"    {elem}: {details['actual']} (Target: {details['target']})")
    else:
        print("  Status: FAILED")
        print(f"  Reason: {result['message']}")
    
    return result


# Example Usage
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = IndustrialAlloyOptimizer()
    
    # Add master alloys
    optimizer.add_master_alloy('Al-Si', {'Si': 50, 'Al': 50}, cost_per_kg=3.0)
    optimizer.add_master_alloy('Al-Cu', {'Cu': 50, 'Al': 50}, cost_per_kg=5.0)
    optimizer.add_master_alloy('Al-Mg', {'Mg': 50, 'Al': 50}, cost_per_kg=4.5)
    optimizer.add_master_alloy('Al-Mn', {'Mn': 25, 'Al': 75}, cost_per_kg=3.8)
    
    # Add only aluminum as pure element
    optimizer.add_pure_element('Al', cost_per_kg=2.2)
    
    # Test Case 1: A380 Aluminum Alloy
    initial_kg_1 = {
        'Al': 90.17,
        'Si': 7.33,
        'Fe': 0.855,
        'Cu': 1.2,
        'Pb': 0.218,
        'Mn': 0.227
    }
    
    target_ranges_1 = {
        'Al': (80.0, 89.5),  # Balance
        'Si': (7.5, 9.5),
        'Cu': (3.0, 4.0),
        'Fe': (0.0, 1.3),
        'Pb': (0.0, 0.35),
        'Mn': (0.1, 0.5)
    }
    
    # Test Case 2: Another alloy specification - with tighter constraints
    initial_kg_2 = {
        'Al': 95.49,
        'Si': 2.96,
        'Cu': 0.528,
        'Mg': 0,
        'Mn': 0.0847,
        'pb': 0.157
    }
    
    target_ranges_2 = {
        'Al': (90.0, 93.0),
        'Si': (6.5, 7.5),
        'Cu': (1.5, 2.0),
        'Mg': (0.45, 0.9),
        'Mn': (0.1, 0.3)
    }
    
    # Run test scenarios
    print("\nTESTING THE IMPROVED INDUSTRIAL ALLOY OPTIMIZER\n")
    
    # Run A380 test
    result_1 = run_test_scenario(
        name="A380 Aluminum Alloy",
        initial_kg=initial_kg_1,
        target_ranges=target_ranges_1,
        optimizer=optimizer,
        max_addition=10.0
    )
    
    # Run second test
    result_2 = run_test_scenario(
        name="Custom Alloy Specification",
        initial_kg=initial_kg_2,
        target_ranges=target_ranges_1,
        optimizer=optimizer,
        max_addition=10.0
    )