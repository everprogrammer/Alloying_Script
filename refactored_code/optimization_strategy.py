
from abc import ABC, abstractmethod
from models import *
import numpy as np
from scipy.optimize import minimize
## Extract optimization from alloy_master_addition


class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize_alloy(self, *args, **kwargs)
        pass

class NonLinearOptimizationStrategy(OptimizationStrategy):
    def optimize_alloy(
        self,
        initial_composition: InitialComposition,
        target_spec: TargetCompositionRange,
        master_alloys: List[MasterAlloy],
        initial_mass: float = 100,
        solver_method: str = 'SLSQP',
        max_iter: int = 1000,
        tol: float = 1e-6
    ) -> Dict[str, float]:
        """Optimize master alloy additions to meet target composition."""
        if not master_alloys:
            raise ValueError("No master alloys provided")

        # Prepare variables
        alloy_keys = [alloy.name for alloy in master_alloys]
        num_alloys = len(alloy_keys)

        # Objective: Minimize total additions
        objective = lambda x: np.sum(x)

        # Constraints: Elements within target ranges
        def constraints(x):
            total_addition = np.sum(x)
            final_mass = initial_mass + total_addition
            element_masses = {
                el: (initial_composition.get_element(el) / 100) * initial_mass
                for el in target_spec.composition
            }

            # Add contributions from master alloys
            for i, alloy in enumerate(master_alloys):
                for el, pct in alloy.composition.items():
                    element_masses[el] = element_masses.get(el, 0) + (pct / 100) * x[i]

            # Check target ranges
            constraint_list = []
            for el, (low, high) in target_spec.composition.items():
                final_pct = (element_masses[el] / final_mass) * 100
                constraint_list.append(final_pct - low)  # >= 0
                constraint_list.append(high - final_pct)  # >= 0
            return np.array(constraint_list)

        # Bounds: No negative additions
        bounds = [(0, None)] * num_alloys

        # Constraints for scipy
        cons = [
            {'type': 'ineq', 'fun': lambda x, i=i: constraints(x)[i]}
            for i in range(len(target_spec.composition.values()) * 2)
        ]

        # Initial guess
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

        # Process results
        result_dict = {}
        if result.success:
            total_added = np.sum(result.x)
            final_mass = initial_mass + total_added
            print("\nOptimization successful!")
            print(f"Initial mass: {initial_mass:.2f} kg")
            print(f"Final mass: {final_mass:.2f} kg \n")
            for i, key in enumerate(alloy_keys):
                if result.x[i] > 1e-1:  # Only show additions > 0.1 kg
                    print(f"Add {result.x[i]:.2f} kg of {key}")
                    result_dict[key] = result.x[i]
        else:
            print("\nOptimization failed:", result.message)
            print("Try relaxing constraints or adding more master alloys.")

        return result_dict

            
            










