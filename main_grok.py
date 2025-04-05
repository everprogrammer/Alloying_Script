from scipy.optimize import linprog
import numpy as np

class IndustrialAlloyOptimizer:
    def __init__(self):
        self.master_alloys = []
        self.scrap = None

    def add_master_alloy(self, name, composition, cost_per_kg):
        self.master_alloys.append({
            'name': name,
            'composition': {k: v/100 for k, v in composition.items()},
            'cost': cost_per_kg
        })

    def optimize(self, initial_composition_pct, target_ranges, max_increase=1.5, debug=False):
        initial_kg = {k: v/100 * 100 for k, v in initial_composition_pct.items()}
        if 'Al' not in target_ranges:
            target_ranges['Al'] = (80.0, 90.0)

        # Pre-check Pb dilution feasibility
        pb_initial = initial_kg.get('Pb', 0)
        max_pb = target_ranges['Pb'][1] / 100
        if pb_initial / 100 > max_pb and max_increase < pb_initial / (max_pb * 100):
            return {'success': False, 'message': "Pb dilution impossible within max_increase"}

        result = self._solve_lp(initial_kg, target_ranges, max_increase, debug=debug)

        if result['success']:
            final_comp = result['final_composition']
            final_weight = result['final_weight']
            out_of_range = []
            for elem, (min_pct, max_pct) in target_ranges.items():
                actual_pct = (final_comp.get(elem, 0) / final_weight) * 100
                if not (min_pct - 0.01 <= actual_pct <= max_pct + 0.01):  # Wider tolerance
                    out_of_range.append(f"{elem} ({actual_pct:.3f}%)")
            if out_of_range:
                result.update({
                    'success': False,
                    'message': f"Targets violated: {', '.join(out_of_range)}",
                    'diagnostics': {
                        'additions': result['additions'],
                        'final_composition': {k: v/final_weight*100 for k, v in final_comp.items()}
                    }
                })
            # Adjust Pb if slightly over
            elif final_comp.get('Pb', 0) / final_weight > max_pb + 0.0001:
                extra_al = (final_comp['Pb'] - max_pb * final_weight) / max_pb
                result['additions']['Pure Al'] = result['additions'].get('Pure Al', 0) + extra_al
                result['final_weight'] += extra_al
                result['final_composition']['Al'] += extra_al
                result['cost'] += extra_al * 1.5
        return result

    def _solve_lp(self, initial_kg, target_ranges, max_increase, debug=False):
        masters = self.master_alloys.copy()
        num_vars = len(masters) + 1
        elements = list(target_ranges.keys())

        costs = [m['cost'] for m in masters] + [1.5]
        A_ub = []
        b_ub = []

        for elem in elements:
            min_pct, max_pct = target_ranges[elem]
            # Max: (initial + sum(contrib * x)) <= max_pct/100 * (100 + sum(x))
            # Rearranged: sum((contrib - max_pct/100) * x) <= max_pct/100 * 100 - initial
            row_max = [m['composition'].get(elem, 0) - max_pct/100 for m in masters]
            row_max.append(1 if elem == 'Al' else 0 - max_pct/100)
            A_ub.append(row_max)
            b_ub.append(max_pct/100 * 100 - initial_kg.get(elem, 0))

            # Min: (initial + sum(contrib * x)) >= min_pct/100 * (100 + sum(x))
            # Rearranged: sum((min_pct/100 - contrib) * x) <= initial - min_pct/100 * 100
            row_min = [min_pct/100 - m['composition'].get(elem, 0) for m in masters]
            row_min.append(min_pct/100 - (1 if elem == 'Al' else 0))
            A_ub.append(row_min)
            b_ub.append(initial_kg.get(elem, 0) - min_pct/100 * 100)

        A_ub.append(np.ones(num_vars))
        b_ub.append((max_increase - 1) * 100)

        res = linprog(c=costs, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * num_vars, method='highs')

        if debug:
            print("Constraint Matrix:\n", np.array(A_ub))
            print("Constraint Bounds:\n", np.array(b_ub))
            print("Solution:\n", res.x)

        if res.success:
            additions = {}
            for i, m in enumerate(masters):
                if res.x[i] > 0.001:
                    additions[m['name']] = res.x[i]
            if res.x[-1] > 0.001:
                additions['Pure Al'] = res.x[-1]

            final_weight = 100 + sum(additions.values())
            final_comp = initial_kg.copy()
            for alloy, kg in additions.items():
                if alloy == 'Pure Al':
                    final_comp['Al'] = final_comp.get('Al', 0) + kg
                else:
                    master = next(m for m in self.master_alloys if m['name'] == alloy)
                    for elem, percent in master['composition'].items():
                        final_comp[elem] = final_comp.get(elem, 0) + kg * percent

            return {
                'success': True,
                'additions': additions,
                'cost': res.fun,
                'final_weight': final_weight,
                'final_composition': final_comp,
                'method': 'master_alloy'
            }
        return {
            'success': False,
            'message': "No feasible solution.",
            'diagnostics': res.message
        }

if __name__ == "__main__":
    optimizer = IndustrialAlloyOptimizer()
    optimizer.add_master_alloy('Al-Si', {'Si': 50, 'Al': 50}, cost_per_kg=3.0)
    optimizer.add_master_alloy('Al-Cu', {'Cu': 50, 'Al': 50}, cost_per_kg=5.0)

    initial_composition_pct = {
        'Al': 90.17, 'Si': 7.33, 'Fe': 0.855, 
        'Cu': 1.2, 'Pb': 0.218
    }

    target_ranges = {
        'Al': (80.0, 90.0),
        'Si': (7.5, 9.5),
        'Cu': (3.0, 4.0),
        'Fe': (0.0, 1.3),
        'Pb': (0.0, 0.2)
    }

    result = optimizer.optimize(
        initial_composition_pct=initial_composition_pct,
        target_ranges=target_ranges,
        max_increase=1.5,
        debug=True
    )

    print("Optimization Results:")
    for k, v in result.items():
        print(f"{k}: {v}")