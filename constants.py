INITIAL_WEIGHT = 150 #kg
LOSS_FACTOR_SCRAP = 1 # 1.05 = 5 % loss after addition of scrap to molten metal(only for alloy_scrap addition not main alloy tool)
LOSS_FACTOR_MASTER_ALLOY = 1 # 5% loss for melting of master-alloys

# Define scrap composition (e.g., low-grade scrap with 5% Si, 0.1% Mg)
SCRAP_COMP = {'Al': 88, 'Si': 8, 'Cu': 7}


INITIAL_COMP_AL91 = {'Al': 90.17,'Si': 7.33 , 'Cu': 1.20, 'Fe': 0.855,
                            'Mn': 0.0577, 'Mg': 0, 'Cr': 0.0091, 'Ni': 0.0221,
                            'Zn': 0.0831, 'Sn': 0.0064, 'Ti': 0.0343, 'Pb': 0.15}

INITIAL_COMP_AL95 = {'Al': 95.49,'Si': 2.96 , 'Cu': 0.528, 'Fe': 0.653,
                            'Mn': 0.0847, 'Mg': 0, 'Cr': 0.0052, 'Ni': 0.012,
                            'Zn': 0.0613, 'Sn': 0.0065, 'Ti': 0.0263, 'Pb': 0.157}

INITIAL_COMP_RA3 = {'Al': 89.086,'Si': 7.6647 , 'Cu': 4.0972, 'Fe': 0.4279,
                            'Mn': 0.0289, 'Mg': 0, 'Cr': 0.0046, 'Ni': 0.0111,
                            'Zn': 0.0416, 'Sn': 0.0032, 'Ti':  0.0172, 'Pb': 0.0751}


INITIAL_COMP_A380_TEST = {'Al': 85,'Si': 8.5 , 'Cu': 3.5, 'Fe': 0.5,
                            'Mn': 0.0847, 'Mg': 0, 'Cr': 0.0052, 'Ni': 0.012,
                            'Zn': 0.0613, 'Pb': 0.10}

COMP_23FAR = alloy_composition = {
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
}

A356_SPEC = {
    'Al': (90.0, 94.0),  # A356 requires higher purity Al vs A380
    'Si': (6.5, 7.5),    # Narrower Si range than A380
    'Mg': (0.2, 0.4),    # Critical for A356 (absent in initial melt)
    'Fe': (0.0, 0.2),    # Stricter than A380 (0.2% max)
    'Cu': (0.0, 0.1),    # Much lower than A380
    'Mn': (0.0, 0.1),
    'Zn': (0.0, 0.1),
    'Pb': (0.0, 0.05)    # Stricter than A380
}

A380_SPEC = {
    "Al": (80, 90),          # Aluminum (base metal)
    "Si": (7.5, 9.5),          # Silicon
    "Cu": (3.0, 4.0),          # Cupper
    "Fe": (0.0, 1.3),          # Iron (max 1.3%)
    "Zn": (0.0, 3.0),          # Zinc
    "Mn": (0.0, 0.5),          # Manganese
    "Mg": (0.0, 0.1),          # Magnesium
    "Ni": (0.0, 0.5),          # Nickel
    "Sn": (0.0, 0.35),         # Tin
    "Pb": (0.0, 0.15),         # Lead
}
A413_SPEC = {
    "Al": (85.0, 90.0),     # Aluminum (base metal)
    "Si": (11.0, 13.0),     # Silicon (primary alloying element)
    "Fe": (0.0, 1.3),       # Iron (impurity, max limit)
    "Cu": (0.0, 1),       # Copper (impurity, max limit)
    "Mn": (0.0, 0.35),      # Manganese (impurity, max limit)
    "Mg": (0.0, 0.1),       # Magnesium (impurity, max limit)
    "Ni": (0.0, 0.5),       # Nickel (impurity, max limit)
    "Zn": (0.0, 0.5),       # Zinc (impurity, max limit)
    "Pb": (0.0, 0.15),      # Lead (impurity, max limit)
    "Sn": (0.0, 0.15),      # Tin (impurity, max limit)
    "Ti": (0.0, 0.2),       # Titanium (grain refiner, max limit)
    "Cr": (0.0, 0.15),      # Chromium (impurity, max limit)
    # "Other": (0.0, 0.25)    # Other impurities (combined max)
}

MASTER_ALLOYS = {
    'Pure_Al': {'Al': 100},
    'Al-Si': {'Si': 99, 'Al': 1},
    'Al-Cu': {'Cu': 100, 'Al': 0},
    # 'Al-Fe': {'Fe': 50, 'Al': 50},
    'Al-Mg': {'Mg': 50, 'Al': 50},  # Critical for A356!
    # 'Al-Mn': {'Mn': 50, 'Al': 50},
    # 'Al-Zn': {'Zn': 50, 'Al': 50},
    }

