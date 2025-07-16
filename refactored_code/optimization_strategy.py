
from abc import ABC, abstractmethod
from models import *
## Extract optimization from alloy_master_addition


class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize_alloy(
                        initial_composition: InitialComposition,
                        target_spec: TargetCompositionConstraint,
                        master_alloys: List[MasterAlloy],
                        scrap_composition=None,  # New: Composition of available scrap (e.g., {'Si': 5.0, 'Al': 95.0})
                        scrap_cost_ratio=0.5,    # New: Cost of scrap relative to master alloys (0.5 = half the cost)
                    ):
        """Returns amounts of master alloys to add(kg)"""
        pass

class NonLinearOptimizationStrategy(OptimizationStrategy):
    @abstractmethod
    def optimize_alloy(
                        initial_composition: InitialComposition,
                        target_spec: TargetCompositionConstraint,
                        master_alloys: List[MasterAlloy],
                        scrap_composition=None,  # New: Composition of available scrap (e.g., {'Si': 5.0, 'Al': 95.0})
                        scrap_cost_ratio=0.5,    # New: Cost of scrap relative to master alloys (0.5 = half the cost)
                        initial_mass=100,
                        solver_method='SLSQP',
                        max_iter=1000,
                        tol=1e-6
                    ):
        pass
        
        










