from models import *
from optimization_strategy import *
from constants import *


if __name__ == '__main__':
    # Create an initial metal with name, composition and weight
    initial_1 = InitialComposition('Initial', COMP_23FAR, weight=100)
    initial_2 = InitialComposition('Initial', COMP_2ORD, weight=100)


    # Create the target alloy instance
    target_1 = TargetCompositionRange('LM2', LM2_SPEC)
    target_2 = TargetCompositionRange('A413_1', A413_1_SPEC)

    registry = MasterAlloyRegistry()
    
    # add_from_name ## e.g. 'Al-Mn 40%' -> follow syntax:(Al 40%, Mn 60%)
    registry.add(MasterAlloy.add_from_name('Cu-Al 100%'))
    registry.add(MasterAlloy.add_from_name('Si-Al 100%'))
    registry.add(MasterAlloy.add_from_name('Al-Mg 50%'))
    registry.get_master_alloys_names

    optimizer = NonLinearOptimizationStrategy()

    result = optimizer.optimize_alloy(initial_composition=initial_2,
                                      target_spec=target_2,
                                      master_alloys=registry.master_alloys,
                                      initial_mass=initial_1.weight,
                                      solver_method='SLSQP'
                                      )
    print("Optimization result:", result)