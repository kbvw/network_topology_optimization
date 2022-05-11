from __future__ import annotations

from collections.abc import Iterable, Iterator, Hashable
from typing import TypeVar, Type, NoReturn

from itertools import product

from .abc import TopoData

# Type aliases

Edge = Hashable
Node = Hashable
ECoord = frozenset[Edge]
NCoord = frozenset[Node]
ESpace = frozenset[Edge]
NSpace = frozenset[Node]

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopoData', 'TTopology' with 'Self'
TTopology = TypeVar('TTopology', bound='Topology')

# Specific implementation of topology coordinate logic
# Direct subclass of tuple for better performance over many instances

class TopoTuple(tuple[ECoord, NCoord], 
                TopoData[ECoord, NCoord, ESpace, NSpace]):
    """Immutable implementation of topology alteration coordinates."""
    
    __slots__ = ()
    
    @property
    def e_coord(self) -> ECoord:
        """The set of edge changes to the topology."""
        
        return self[0]
    
    @property
    def n_coord(self) -> NCoord:
        """The set of node changes to the topology."""
        
        return self[1]
    
    def __repr__(self) -> str:
        
        name = type(self).__name__
        
        return f'{name}(e_coord={self.e_coord!r}, n_coord={self.e_coord!r})'
    
    def __setattr__(self, key: str, value: object) -> NoReturn:
        
        name = type(self).__name__
        msg = f"'{name}' object does not support attribute assignment"
        
        raise TypeError(msg)

class Topology(TopoTuple):
    """Basic implementation of topology alteration logic."""
    
    __slots__ = ()
    
    @classmethod
    def factory(cls: Type[TTopology], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[TTopology]:
        """Return iterable with cartesian product of coordinates."""
        
        return map(cls, product(e_coords, n_coords))
    
    def e_children(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing children in the edge dimension."""
        
        unchanged = self.e_space - self[0]
        e_coords = (self[0] | {change} for change in unchanged)
        
        return self.factory(e_coords, [self[1]])
    
    def n_children(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing children in the node dimension."""
        
        unchanged = self.n_space - self[1]
        n_coords = (self[1] | {change} for change in unchanged)
        
        return self.factory([self[0]], n_coords)
    
    def e_parents(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing parents in the edge dimension."""
        
        e_coords = (self[0] - {change} for change in self[0])
        
        return self.factory(e_coords, [self[1]])
    
    def n_parents(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing parents in the node dimension."""
        
        n_coords = (self[1] - {change} for change in self[1])
        
        return self.factory([self[0]], n_coords)