from scipy.optimize import linprog
import numpy as np
import constants

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

    def optimize(self, initial_kg, target_ranges, max_increase=1.5, buffer_pct=5, debug=False):
        """
        Optimizes additions to meet ALL element ranges (including Al).
        Args:
            initial_kg: {element: kg} per 100kg melt.
            target_ranges: {element: (min%, max%)} (MUST include 'Al').
            max_increase: Max allowed weight increase (default 1.5x).
            buffer_pct: Safety buffer for critical elements (e.g., Si, Cu).
            debug: Print diagnostic messages.
        Returns:
            {success, additions, cost, final_weight, final_composition, message, diagnostics}
        """
        # Ensure Al is constrained
        if 'Al' not in target_ranges:
            target_ranges['Al'] = (80.0, 90.0)  # Default range

        # Apply buffer to target ranges (e.g., Si min 7.5% -> 7.5 * 1.05)
        buffered_ranges = {}
        for elem, (min_pct, max_pct) in target_ranges.items():
            buffered_min = min_pct * (1 + buffer_pct/100) if elem in ['Si', 'Cu'] else min_pct
            buffered_ranges[elem] = (buffered_min, max_pct)

        # Pre-check feasibility of dilution
        required_dilution_factors = {}
        for elem, (_, max_pct) in target_ranges.items():
            if max_pct > 0 and elem in initial_kg:
                required_dilution_factors[elem] = initial_kg[elem] / (max_pct / 100)
        
        max_required_dilution = max(required_dilution_factors.values()) if required_dilution_factors else 0
        if max_required_dilution > max_increase * 100:
            impossible_elements = {
                elem: f"Must reduce from {initial_kg[elem]/100:.3f}% to ≤{max_pct}% (needs {required_dilution_factors[elem] - 100:.1f}kg additions)"
                for elem, (_, max_pct) in target_ranges.items()
                if elem in required_dilution_factors and required_dilution_factors[elem] > max_increase * 100
            }
            return {
                'success': False,
                'message': "Cannot dilute impurities to targets with current max_increase.",
                'diagnostics': impossible_elements,
                'suggestions': [
                    "Increase max_increase parameter.",
                    "Pre-treat melt to remove impurities before optimization."
                ]
            }

        # Solve using master alloys + pure Al
        result = self._solve_lp(initial_kg, buffered_ranges, max_increase, use_scrap=False, debug=debug)

        # Verify against original (non-buffered) ranges
        if result['success']:
            final_comp = result['final_composition']
            out_of_range = self._check_ranges(final_comp, target_ranges, result['final_weight'])
            if out_of_range:
                result.update({
                    'success': False,
                    'message': f"Buffered solution violated: {', '.join(out_of_range)}",
                    'diagnostics': {
                        elem: f"Initial: {initial_kg[elem]/100:.3f}% → Final: {final_comp[elem]/result['final_weight']*100:.3f}% (Target: {min_pct}-{max_pct}%)"
                        for elem, (min_pct, max_pct) in target_ranges.items()
                    }
                })

        return result

    def _solve_lp(self, initial_kg, target_ranges, max_increase, use_scrap=False, debug=False):
        """Core LP solver with simultaneous constraints."""
        masters = self.master_alloys.copy()
        if use_scrap and self.scrap:
            masters.append({'name': 'Scrap', 'composition': self.scrap, 'cost': 0.8})

        # Decision variables: [master1, master2, ..., pure_Al]
        num_vars = len(masters) + 1
        elements = list(target_ranges.keys())
            
        # Min Al constraint (Al% >= al_min)
        row_al_min = np.zeros(num_vars)
        for i, m in enumerate(masters):
            row_al_min[i] = -(m['composition'].get('Al', 0)) + al_min/100
        row_al_min[-1] = -1 + al_min/100  # Pure Al coefficient
        A_ub.append(row_al_min)
        b_ub.append(-(al_min/100 * 100 - initial_kg.get('Al', 0)))
        # Objective: minimize cost
        costs = [m['cost'] for m in masters] + [1.5]  # Pure Al cost

        # Constraints: Ax <= b
        A_ub = []
        b_ub = []
        if 'Al' in target_ranges:
            al_min, al_max = target_ranges['Al']
            # Max Al constraint (Al% <= al_max)
            row_al_max = np.zeros(num_vars)
            for i, m in enumerate(masters):
                row_al_max[i] = m['composition'].get('Al', 0) - al_max/100
            row_al_max[-1] = 1 - al_max/100  # Pure Al coefficient
            A_ub.append(row_al_max)
            b_ub.append(al_max/100 * 100 - initial_kg.get('Al', 0))

        # 1. Element % constraints (min <= elem% <= max)
        for elem in elements:
            min_pct, max_pct = target_ranges[elem]
            
            # Max constraint: elem% <= max_pct
            row_max = np.zeros(num_vars)
            for i, m in enumerate(masters):
                row_max[i] = m['composition'].get(elem, 0) - max_pct/100
            row_max[-1] = (1 if elem == 'Al' else 0) - max_pct/100
            A_ub.append(row_max)
            b_ub.append(max_pct/100 * 100 - initial_kg.get(elem, 0))
            
            # Min constraint: elem% >= min_pct (rewritten as -elem% <= -min_pct)
            row_min = np.zeros(num_vars)
            for i, m in enumerate(masters):
                row_min[i] = -(m['composition'].get(elem, 0)) + min_pct/100
            row_min[-1] = -(1 if elem == 'Al' else 0) + min_pct/100
            A_ub.append(row_min)
            b_ub.append(-(min_pct/100 * 100 - initial_kg.get(elem, 0)))

        # 2. Max weight constraint (sum additions <= (max_increase-1)*100)
        row_weight = np.ones(num_vars)
        A_ub.append(row_weight)
        b_ub.append((max_increase - 1) * 100)

        # Solve
        res = linprog(
            c=costs,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=[(0, None)] * num_vars,
            method='highs'
        )

        if debug:
            print(f"LP status: {res.message}")
            print(f"Additions: {res.x}")

        if res.success:
            additions = {}
            for i, m in enumerate(masters):
                if res.x[i] > 0.001:
                    additions[m['name']] = res.x[i]
            if res.x[-1] > 0.001:
                additions['Pure Al'] = res.x[-1]

            # Calculate final composition
            final_weight = 100 + sum(additions.values())
            final_comp = self._calculate_final_composition(initial_kg, additions)
            
            return {
                'success': True,
                'additions': additions,
                'cost': res.fun,
                'final_weight': final_weight,
                'final_composition': final_comp,
                'method': 'scrap_blending' if use_scrap else 'master_alloy'
            }
        return {
            'success': False,
            'message': "LP solver found no feasible solution.",
            'diagnostics': {
                'target_ranges': target_ranges,
                'max_increase': max_increase
            }
        }

    def _calculate_final_composition(self, initial_kg, additions):
        """Calculate final composition after additions."""
        final_comp = initial_kg.copy()
        for alloy, kg in additions.items():
            if alloy == 'Pure Al':
                final_comp['Al'] = final_comp.get('Al', 0) + kg
            elif alloy == 'Scrap':
                for elem, percent in self.scrap.items():
                    final_comp[elem] = final_comp.get(elem, 0) + kg * percent
            else:
                master = next(m for m in self.master_alloys if m['name'] == alloy)
                for elem, percent in master['composition'].items():
                    final_comp[elem] = final_comp.get(elem, 0) + kg * percent
        return final_comp

    def _check_ranges(self, final_comp, target_ranges, final_weight):
        """Strict check if all elements are within target ranges after dilution."""
        out_of_range = []
        for elem, (min_pct, max_pct) in target_ranges.items():
            actual_pct = (final_comp.get(elem, 0) / final_weight) * 100
            if not (min_pct <= actual_pct <= max_pct):
                out_of_range.append(f"{elem} ({actual_pct:.3f}%)")
        return out_of_range
    
    ## ==============================================
    # how to use
optimizer = IndustrialAlloyOptimizer()
optimizer.add_master_alloy('Al-Si', {'Si': 50, 'Al': 50}, cost_per_kg=3.0)
optimizer.add_master_alloy('Al-Cu', {'Cu': 50, 'Al': 50}, cost_per_kg=5.0)

result = optimizer.optimize(
    initial_kg=constants.initial_comp_1,
    target_ranges=constants.target_ranges_a380,
    max_increase=1.5,
    debug=True  # Enable for diagnostics
)

print(result)