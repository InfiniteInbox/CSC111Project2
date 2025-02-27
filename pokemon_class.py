from typing import Any
from __future__ import annotations


class Type:
    """
    A Pokemon type.

    Instance Attributes:
        - name: name of the type
        - effectiveness: a dictionary mapping types to effectiveness
        (2.0 = super effective, 0.5 = not very effective, 0.0 = immune)
    """
    name: str
    effectiveness: dict[str, float]

    def __init__(self, name: str, effectiveness: dict[str, float]):
        self.name = name
        self.effectiveness = {}

    def set_effectiveness(self, effectiveness_dict: dict[str, float]) -> None:
        """Set the effectiveness of this type for other types."""
        self.effectiveness = effectiveness_dict


class Pokemon:
    """
    A class to represent a Pokemon.

    Instance Attributes:
        - pokemon_id: the unique Pokemon id
        - name: the name of the Pokemon
        - type1: the primary type of the Pokemon
        - type2: the secondary type of the Pokemon
        - stats: a tuple containing the stats of the Pokemon (HP, Attack, Defense, Special Attack, Special Defense, Speed)
        - bst: the base stat total of the Pokemon
    """
    pokemon_id: int
    name: str
    type1: Type
    type2: Type
    stats: tuple[int]
    bst: int

    def __init__(self, pokemon_id: int, name: str, type1: Type, type2: Type, stats: tuple[int], bst: int):
        """Initialize a new Pokemon instance."""
        self.pokemon_id = pokemon_id
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.stats = stats
        self.bst = bst

class TypeVertex:
    """
        A class to represent a vertex in a graph

        Instance Attributes:
            - item: The type of the pokemon
            - neighbors: a dictionary of neighbors where key represents the strength of connection
            (when the float is below  ) and the value is the vertex itself
        """
    item: Any
    neighbors: dict[float, set[TypeVertex]]
    def __init__(self, item: Any, neighbors: dict[float, set[TypeVertex]]) -> None:
        self.item = item
        self.neighbors = neighbors
class TypeGraph:
    """
        A class to represent the types and the interactions.

        Instance Attributes:
            - verticies: a dictionary representing the graphs verticies
        """

