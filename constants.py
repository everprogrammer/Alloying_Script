

initial_comp_1 = {
    'Al': 90.17,  # A356 requires higher purity Al vs A380
    'Si': 7.33,    # Narrower Si range than A380   
    'Fe': 0.855,    # Stricter than A380 (0.2% max)
    'Cu': 1.2,    # Much lower than A380
    'Pb': 0.218
}

initial_comp_2 = {
'Al' : 95.4, 'Si' : 2.96, 'Fe' : 0.653, 'Cu' : 0.528, 'Mn' : 0.0847, 
'Zn' : 0.613, 'Pb' : 0.157, 'Mg' : 0
}
target_ranges_a356 = {
    'Al': (90.0, 94.0),  # A356 requires higher purity Al vs A380
    'Si': (6.5, 7.5),    # Narrower Si range than A380
    'Mg': (0.2, 0.4),    # Critical for A356 (absent in initial melt)
    'Fe': (0.0, 0.2),    # Stricter than A380 (0.2% max)
    'Cu': (0.0, 0.1),    # Much lower than A380
    'Mn': (0.0, 0.1),
    'Zn': (0.0, 0.1),
    'Pb': (0.0, 0.05)    # Stricter than A380
}

target_ranges_a380 = {
    'Al': (80.0, 90.0),
    'Si': (7.5, 9.5),
    'Cu': (3.0, 4.0),
    'Fe': (0.0, 1.3),
    'Pb': (0.0, 0.2)
}
