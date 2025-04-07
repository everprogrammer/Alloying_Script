
INITIAL_COMP_AL91 = {'Al': 90.17,'Si': 7.33 , 'Cu': 1.20, 'Fe': 0.855,
                            'Mn': 0.0577, 'Mg': 0, 'Cr': 0.0091, 'Ni': 0.0221,
                            'Zn': 0.0831, 'Sn': 0.0064, 'Ti': 0.0343, 'Pb': 0.15}


INITIAL_COMP_AL95 = {'Al': 95.49,'Si': 2.96 , 'Cu': 0.528, 'Fe': 0.653,
                            'Mn': 0.0847, 'Mg': 0, 'Cr': 0.0052, 'Ni': 0.012,
                            'Zn': 0.0613, 'Sn': 0.0065, 'Ti': 0.0263, 'Pb': 0.157}

TARGET_RANGES_A356 = {
    'Al': (90.0, 94.0),  # A356 requires higher purity Al vs A380
    'Si': (6.5, 7.5),    # Narrower Si range than A380
    'Mg': (0.2, 0.4),    # Critical for A356 (absent in initial melt)
    'Fe': (0.0, 0.2),    # Stricter than A380 (0.2% max)
    'Cu': (0.0, 0.1),    # Much lower than A380
    'Mn': (0.0, 0.1),
    'Zn': (0.0, 0.1),
    'Pb': (0.0, 0.05)    # Stricter than A380
}

INITIAL_COMP_A380_TEST = {'Al': 85,'Si': 8.5 , 'Cu': 3.5, 'Fe': 0.5,
                            'Mn': 0.0847, 'Mg': 0, 'Cr': 0.0052, 'Ni': 0.012,
                            'Zn': 0.0613, 'Pb': 0.10}
TARGET_RANGES_A380 = {
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

MASTER_ALLOYS = {
    'Pure_Al': {'Al': 100},
    'Al-Si': {'Si': 50, 'Al': 50},
    'Al-Cu': {'Cu': 50, 'Al': 50},
    'Al-Fe': {'Fe': 50, 'Al': 50},
    'Al-Mg': {'Mg': 50, 'Al': 50},  # Critical for A356!
    'Al-Mn': {'Mn': 50, 'Al': 50},
    'Al-Zn': {'Zn': 50, 'Al': 50},
    }

# Define scrap composition (e.g., low-grade scrap with 5% Si, 0.1% Mg)
SCRAP_COMP = {'Al':88, 'Si': 8, 'Cu': 7}