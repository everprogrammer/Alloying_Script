from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from dataclasses import dataclass

class InitialComposition:
    def __init__(self, name: str, composition: Dict, weight=100):
        self._name = name
        if not isinstance(composition, Dict):
            raise ValueError('Composition must be a valid Dictionary object!')
        self._composition = composition
        self._weight = weight

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise ValueError('Name of the initial molten composition must be of type string...')
        self._name = value

    @property
    def composition(self):
        return self._composition
    
    @property
    def weight(self):
        return self._weight
    
    @weight.setter
    def weight(self, value):
        if not isinstance(value, float):
            raise ValueError(f'Weight must be of type float: {value}')
        self._weight = value

    def get_element(self, element: str) -> float:
        return self._composition.get(element, 0.0)
    
    def set_element(self, element:str, value: float) -> float:
        print(f'Setting new value for element {element}...')
        self._composition[element] = value
        return value
    
    def __repr__(self):
        return str(self._composition)
    
class TargetCompositionConstraint:
    def __init__(self, name: str, composition: Dict[str, tuple[float, float]]):
        self._name = name
        self._composition = composition

    @property
    def name(self):
        return self.name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise ValueError('Name of the alloy must be of type string...')
        self.name = value

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

@dataclass    
class MasterAlloy:
    name: str                     # e.g., "Al-Cu 30%"
    composition: Dict[str, float] # e.g., {"Al": 30, "Cu": 70}

    _predefined_alloys = {
    'Pure_Al': {'Al': 100},
    'Al-Si': {'Si': 99, 'Al': 1},
    'Al-Cu': {'Cu': 100, 'Al': 0},
    'Al-Fe': {'Fe': 50, 'Al': 50},
    'Al-Mg': {'Mg': 50, 'Al': 50},  # Critical for A356!
    'Al-Mn': {'Mn': 50, 'Al': 50},
    'Al-Zn': {'Zn': 50, 'Al': 50},
    }

    def validate(self):
        """Ensure composition percentage sum is 100%"""
        total = sum(self.composition.values())
        if not abs(100 - total) < 1e-6:
            raise ValueError(f"Composition for {self.name} must sum to 100%, got {total}%")
    
    @classmethod
    def add_from_name(cls, name: str) -> 'MasterAlloy':
        if name in cls._predefined_alloys:
            composition = cls._predefined_alloys[name]
        else:
            parts = name.split()
            if len(parts) != 2 or '%' not in parts[1]:
                raise ValueError(f'Invalid Master Alloy name: {name}!')
            elements = parts[0].split('-')
            if len(elements) < 2:
                raise ValueError(f'Expected at least two elements in {name}')
            percentage = float(parts[1].replace('%', ''))
            if not 0 <= percentage <= 100:
                raise ValueError(f'Percentage must be between 0 and 100: {percentage}')
            composition = {elements[0]: percentage, elements[1]: 100 - percentage}
            alloy = cls(name, composition)
            alloy.validate()
            return alloy


class MasterAlloyRegistry:

    def __init__(self):
        self._master_alloys : List[MasterAlloy] = []

    @property
    def master_alloys(self):
        return self._master_alloys

    def add(self, alloy: MasterAlloy):
        if not isinstance(alloy, MasterAlloy):
            raise ValueError('Only MasterAlloy objects can be added!')
        if alloy.name in [a.name for a in self._master_alloys]:
            raise ValueError(f"Alloy {alloy.name} already exists!")
        self._master_alloys.append(alloy)

    def add_many(self, alloys: List[MasterAlloy]):
        for alloy in alloys:
            self.add(alloy)
        
    def remove(self, master_alloy: MasterAlloy):
        if not isinstance(master_alloy, MasterAlloy):
            raise ValueError(f'{master_alloy} is not of type MasterAlloy')
        self._master_alloys.remove(master_alloy)

    def clear(self):
        self._master_alloys.clear()


