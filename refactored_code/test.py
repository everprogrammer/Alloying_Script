from models import *
from optimization_strategy import *


if __name__ == '__main__':
    i1 = InitialComposition('test1', {
    'Al': 95.40,    # Aluminum
    'Si': 3.22,     # Silicon
    'Fe': 0.49,     # Iron
    'Cu': 0.54,     # Copper
    'Zn': 0.07,     # Zinc
    'Pb': 0.14,     # Lead
    'Mn': 0.05,     # Manganese
    'Ti': 0.029,    # Titanium
    'Ni': 0.01,     # Nickel
    'Ga': 0.01,     # Gallium
    'Co': 0.01,     # Cobalt
    'V': 0.007,     # Vanadium
    'Bi': 0.007,    # Bismuth
    'Na': 0.002,    # Sodium
    'Mg': 0.006,    # Magnesium
    'Cr': 0.004,    # Chromium
    'Sn': 0.005,    # Tin (reported as <0.005)
    'B': 0.001,     # Boron (reported as <0.001)
}, weight=100)
    
    print(i1.composition)
    print('\n')
    print(i1.get_element('Cu'))
    print('\n')
    print(i1.set_element('Cu', 5))
    print('\n')
    print(i1.get_element('Cu'))

    t1 = TargetCompositionConstraint('A380', {
    "Al": (80, 90),          # Aluminum (base metal)
    "Si": (8.5, 9.5),          # Silicon
    "Cu": (3.3, 4.0),          # Cupper
    "Fe": (0.0, 1.3),          # Iron (max 1.3%)
    "Zn": (0.0, 3.0),          # Zinc
    "Mn": (0.0, 0.5),          # Manganese
    "Mg": (0.0, 0.1),          # Magnesium
    "Ni": (0.0, 0.5),          # Nickel
    "Sn": (0.0, 0.35),         # Tin
    "Pb": (0.0, 0.15),         # Lead
})
    print(t1.get_range('Cu'))
    print('\n')
    t1.set_range('Cu', (5,6))
    print('\n')
    print(t1.get_range('Cu'))
    print('\n')
    print(t1.composition)
    print('\n')
    print(t1.get_range('Ft'))
    print(t1)

registry = MasterAlloyRegistry()
MA1 = MasterAlloy.add_from_name('Al-Cu 50%')
MA2 = MasterAlloy.add_from_name('Al-Si 1%')
MA3 = MasterAlloy.add_from_name('Cu-Al 100%')
registry.add_many([MA1, MA2, MA3])
print(registry.master_alloys)
registry.remove(MA1)
print(registry.master_alloys)

master_alloys = registry.master_alloys
optimizer = NonLinearOptimizationStrategy()
result = optimizer.optimize_alloy(
        initial_composition=i1.composition,
        target_spec=t1.composition,
        master_alloys=master_alloys,
        initial_mass=100,
        solver_method='SLSQP'
    )
print("Optimization result:", result)