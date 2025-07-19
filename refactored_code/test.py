from models import *
from optimization_strategy import *
from constants import *


if __name__ == '__main__':
    i1 = InitialComposition('initial', COMP_2ORD)
    t1 = TargetCompositionConstraint('LM2', LM2_SPEC)

    registry = MasterAlloyRegistry()
    for name, comp in MASTER_ALLOYS.items():
        alloy = MasterAlloy(name=name, composition=comp)
        alloy.validate()
        registry.add(alloy)
    

    master_alloys = registry.master_alloys
    print(master_alloys)

    optimizer = NonLinearOptimizationStrategy()
    result = optimizer.optimize_alloy(
            initial_composition=i1,
            target_spec=t1,
            master_alloys=master_alloys,
            initial_mass=498,
            solver_method='SLSQP'
        )
    print("Optimization result:", result)