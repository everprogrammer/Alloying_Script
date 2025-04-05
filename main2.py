from scipy.optimize import linprog
import numpy as np
from pprint import pprint

class IndustrialAlloyOptimizer:
    def __init__(self):
        self.master_alloys = []
        self.scrap = None

    def add_master_alloy(self, name, composition, cost_per_kg):
        """Register master alloys (composition in %, cost in $/kg)."""
        self.master_alloys.append({
            'name': name,
            'composition': {k: v/100 for k, v in composition.items()},
            'cost': cost_per_kg
        })

    def set_scrap(self, composition):
        """Set scrap composition (in %) for impurity dilution."""
        self.scrap = {k: v/100 for k, v in composition.items()}

    def optimize(self, initial_percent, target_ranges, max_increase=1.5, buffer_pct=0, debug=False):
        """
        Optimizes additions to meet ALL element ranges (including Al).
        Args:
            initial_percent: {element: %} of initial composition
            target_ranges: {element: (min%, max%)} (MUST include 'Al')
            max_increase: Max allowed weight increase (default 1.5x)
            buffer_pct: Safety buffer for critical elements
            debug: Print diagnostic messages
        Returns:
            Dictionary with optimization results
        """
        # Convert initial percentages to kg in 100kg batch
        initial_kg = {k: v for k, v in initial_percent.items()}
        
        # Ensure Al is constrained
        if 'Al' not in target_ranges:
            target_ranges['Al'] = (80.0, 90.0)

        # Apply buffer to target ranges
        buffered_ranges = {}
        for elem, (min_pct, max_pct) in target_ranges.items():
            buffered_min = min_pct * (1 + buffer_pct/100) if elem in ['Si', 'Cu'] else min_pct
            buffered_ranges[elem] = (buffered_min, max_pct)

        # Solve using master alloys + pure Al
        result = self._solve_lp(initial_kg, buffered_ranges, max_increase, debug)

        # Verify results
        if result['success']:
            final_comp = result['final_composition']
            final_weight = result['final_weight']
            
            # Calculate final percentages
            final_percent = {k: (v / final_weight * 100) for k, v in final_comp.items()}
            
            # Check all targets
            violations = []
            for elem, (min_pct, max_pct) in target_ranges.items():
                actual = final_percent.get(elem, 0)
                if not (min_pct <= actual <= max_pct):
                    violations.append(f"{elem} ({actual:.2f}%)")
            
            if violations:
                return {
                    'success': False,
                    'message': f"Targets violated: {', '.join(violations)}",
                    'diagnostics': {
                        'initial': initial_percent,
                        'targets': target_ranges,
                        'additions': result['additions'],
                        'final': final_percent
                    }
                }
            
            # Convert to clean output
            clean_additions = {k: round(float(v), 2) for k, v in result['additions'].items()}
            clean_percent = {k: round(float(v), 2) for k, v in final_percent.items()}
            
            return {
                'success': True,
                'additions': clean_additions,
                'cost': round(float(result['cost']), 2),
                'final_weight': round(float(final_weight), 2),
                'final_composition': clean_percent
            }
        
        return result

    def _solve_lp(self, initial_kg, target_ranges, max_increase, debug=False):
        """Core LP solver with percentage-based constraints."""
        masters = self.master_alloys
        num_vars = len(masters) + 1  # [master1, ..., pure_Al]
        elements = list(target_ranges.keys())

        # Objective: minimize cost
        c = [m['cost'] for m in masters] + [1.5]  # Pure Al cost

        # Constraints: Ax <= b
        A = []
        b = []

        # 1. Element constraints (percentage-based)
        for elem in elements:
            min_pct, max_pct = target_ranges[elem]
            initial = initial_kg.get(elem, 0)
            
            # Max constraint: (initial + Σ additions) / (100 + Σ additions) ≤ max_pct
            # Rewritten as: initial + Σ additions ≤ max_pct*(100 + Σ additions)
            # → Σ additions*(1 - max_pct) ≤ max_pct*100 - initial
            row_max = np.zeros(num_vars)
            for i, m in enumerate(masters):
                row_max[i] = m['composition'].get(elem, 0) - max_pct/100
            row_max[-1] = (1 if elem == 'Al' else 0) - max_pct/100
            A.append(row_max)
            b.append(max_pct - initial/100)
            
            # Min constraint: (initial + Σ additions) / (100 + Σ additions) ≥ min_pct
            # Rewritten as: initial + Σ additions ≥ min_pct*(100 + Σ additions)
            # → Σ additions*(1 - min_pct) ≥ min_pct*100 - initial
            # → -Σ additions*(1 - min_pct) ≤ initial - min_pct*100
            row_min = np.zeros(num_vars)
            for i, m in enumerate(masters):
                row_min[i] = -m['composition'].get(elem, 0) + min_pct/100
            row_min[-1] = -(1 if elem == 'Al' else 0) + min_pct/100
            A.append(row_min)
            b.append(initial/100 - min_pct)

        # 2. Max weight constraint: Σ additions ≤ (max_increase - 1)*100
        A.append(np.ones(num_vars))
        b.append((max_increase - 1))

        # Solve
        res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)]*num_vars, method='highs')

        if debug:
            print("Constraint Matrix:\n", np.array(A))
            print("Constraint Bounds:\n", b)
            print("Solution:\n", res.x)

        if res.success:
            additions = {}
            for i, m in enumerate(masters):
                if res.x[i] > 0.001:  # Ignore tiny additions
                    additions[m['name']] = res.x[i]
            if res.x[-1] > 0.001:
                additions['Pure Al'] = res.x[-1]

            # Calculate final composition
            total_added = sum(additions.values())
            final_weight = 100 + total_added
            final_comp = initial_kg.copy()
            
            for alloy, kg in additions.items():
                if alloy == 'Pure Al':
                    final_comp['Al'] += kg
                else:
                    master = next(m for m in masters if m['name'] == alloy)
                    for elem, frac in master['composition'].items():
                        final_comp[elem] = final_comp.get(elem, 0) + kg * frac

            return {
                'success': True,
                'additions': additions,
                'cost': res.fun,
                'final_weight': final_weight,
                'final_composition': final_comp
            }
        
        return {
            'success': False,
            'message': "No feasible solution found",
            'diagnostics': {
                'target_ranges': target_ranges,
                'max_increase': max_increase
            }
        }

# Example Usage
if __name__ == "__main__":
    optimizer = IndustrialAlloyOptimizer()
    optimizer.add_master_alloy('Al-Si', {'Si': 50, 'Al': 50}, cost_per_kg=3.0)
    optimizer.add_master_alloy('Al-Cu', {'Cu': 50, 'Al': 50}, cost_per_kg=5.0)

    # Problem 1: Initial composition in percentages
    initial = {
        'Al': 90.17,
        'Si': 7.33,
        'Fe': 0.855,
        'Cu': 1.2,
        'Pb': 0.218
    }

    # A380 target ranges in percentages
    targets = {
        'Al': (80.0, 90.0),
        'Si': (7.5, 9.5),
        'Cu': (3.0, 4.0),
        'Fe': (0.0, 1.3),
        'Pb': (0.0, 0.2)
    }

    result = optimizer.optimize(
        initial_percent=initial,
        target_ranges=targets,
        max_increase=1.5,
        debug=False
    )

    print("Optimization Results:")
    pprint(result)