MASTER_ALLOYS = {
    # 'Pure_Al': {'Al': 100},
    'Al-Si': {'Si': 99, 'Al': 1},
    'Al-Cu': {'Cu': 100, 'Al': 0},
    # 'Al-Fe': {'Fe': 50, 'Al': 50},
    # 'Al-Mg': {'Mg': 50, 'Al': 50},  # Critical for A356!
    # 'Al-Mn': {'Mn': 50, 'Al': 50},
    # 'Al-Zn': {'Zn': 50, 'Al': 50},
    }

A380_SPEC = {
    "Al": (80, 90),          # Aluminum (base metal)
    "Si": (7.5, 9.5),          # Silicon
    "Cu": (3.3, 4.0),          # Cupper
    "Fe": (0.0, 1.3),          # Iron (max 1.3%)
    "Zn": (0.0, 3.0),          # Zinc
    "Mn": (0.0, 0.5),          # Manganese
    "Mg": (0.0, 0.1),          # Magnesium
    "Ni": (0.0, 0.5),          # Nickel
    "Sn": (0.0, 0.35),         # Tin
    "Pb": (0.0, 0.15),         # Lead
}

LM2_SPEC = {
    "Al": (82.0, 89.3),
    "Si": (9.5, 11.5),
    "Cu": (0.7, 2.5),
    "Zn": (0.0, 2.0),
    "Fe": (0.0, 1.0),
    "Mn": (0.0, 0.5),
    "Ni": (0.0, 0.5),
    "Mg": (0.0, 0.3),
    "Pb": (0.0, 0.3),
    "Sn": (0.0, 0.2),
    "Ti": (0.0, 0.2)
}

COMP_23FAR = {
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

COMP_2ORD = {
    'Si': 3.84,
    'Fe': 0.49,
    'Cu': 0.64,
    'Mn': 0.06,
    'Mg': 0.004,
    'Cr': 0.005,
    'Ni': 0.01,
    'Zn': 0.07,
    'Ti': 0.016,
    'Pb': 0.13,
    'Sn': 0.006,
    'V': 0.01,
    'Na': 0.002,
    'Co': 0.01,
    'Ga': 0.01,
    'Al': 94.70
}
