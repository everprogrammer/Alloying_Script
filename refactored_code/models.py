from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class InitialComposition:
    def __init__(self, name: str, composition: Dict):
        self.name = name
        self.composition = composition

    def get_element(self, element: str) -> float:
        return self.composition.get(element, 0.0)
    
    def __repr__(self):
        return str(self.composition)
    
class TargetCompositionConstrain:
    def __init__(self, name: str, composition: Dict):
        self.name = name
        self._composition = composition

    @property
    def composition(self):
        return self._composition

    def get_range(self, element:str) -> tuple:
        print(f'Getting range for element "{element}" ...')
        element_range = self._composition.get(element, (0,0))
        print(f'Retrieved range for "{element}": {element_range}')
        return element_range
    
    def set_range(self, element:str, value: tuple) -> Dict:
        print(f'Setting range for element "{element}" ...')
        if element not in self._composition:
            raise ValueError(f'Element "{element}" does not exist in the composition!')
        
        self._composition[element] = value
        print(f'Range of the element {element} is now: {value}')
        return self._composition
    
    def __repr__(self):
        return str(self._composition)
    

if __name__ == '__main__':
    t1 = TargetCompositionConstrain('A380', {
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
