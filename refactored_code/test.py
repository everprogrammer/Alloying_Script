from models import *
from optimization_strategy import *
from constants import *


if __name__ == '__main__':
    # Create an initial metal with name, composition and weight
    i1 = InitialComposition('initial', COMP_2ORD, weight=498)

    # Create the target alloy instance
    t1 = TargetCompositionConstraint('LM2', LM2_SPEC)

    registry = MasterAlloyRegistry()
    registry.add(MasterAlloy.add_from_name('Cu-Al 100%'))
    registry.add(MasterAlloy.add_from_name('Si-Al 99%'))
    registry.add(MasterAlloy.add_from_name('Al-Mg 50%'))
    registry.get_master_alloys_names
    registry.remove('Al-Mg 50%')
    registry.get_master_alloys_names


    optimizer = NonLinearOptimizationStrategy()

    result = optimizer.optimize_alloy(
            initial_composition=i1,
            target_spec=t1,
            master_alloys=registry.master_alloys,
            initial_mass=i1.weight,
            solver_method='SLSQP'
        )
    print("Optimization result:", result)