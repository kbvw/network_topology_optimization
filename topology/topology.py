from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Hashable
from typing import TypeVar, Type, NoReturn

from itertools import product

from .abc import TopoData

# Type aliases

E = Hashable
N = Hashable
ECoord = frozenset[E]
NCoord = frozenset[N]
#NCoord = frozenset[tuple[N, tuple[frozenset[E], ...]]]
ESpace = frozenset[E]
NSpace = frozenset[N]
#NSpace = frozenset[tuple[N, frozenset[E]]]

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopo' with 'Self'
Topo = TypeVar('Topo', bound='Topology')

# Specific implementation of topology coordinate logic
# Direct subclass of tuple for better performance over many instances

class Topology(TopoData[ECoord, NCoord, ESpace, NSpace], ABC):
    
    __slots__ = ()
    
    @classmethod
    @abstractmethod
    def factory(cls: Type[Topo], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[Topo]:
        """Return iterable with cartesian product of coordinates."""
        
        raise NotImplementedError

class TopoTuple(tuple[ECoord, NCoord], Topology):
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
    
    @classmethod
    def factory(cls: Type[Topo], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[Topo]:
        """Return iterable with cartesian product of coordinates."""
        
        return map(cls, product(e_coords, n_coords))
    
    def __repr__(self) -> str:
        
        name = type(self).__name__
        
        return f'{name}(e_coord={self.e_coord!r}, n_coord={self.e_coord!r})'
    
    def __setattr__(self, key: str, value: object) -> NoReturn:
        
        name = type(self).__name__
        msg = f"'{name}' object does not support attribute assignment"
        
        raise TypeError(msg)
        
class EFull(Topology):
    
    __slots__ = ()
    
    def e_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the edge dimension."""
        
        unchanged = self.e_space - self.e_coord
        e_coords = (self.e_coord | {change} for change in unchanged)
        
        return self.factory(e_coords, [self.n_coord])
    
    def e_parents(self: Topo) -> Iterator[Topo]:
        """Return iterable containing parents in the edge dimension."""
        
        e_coords = (self.e_coord - {change} for change in self.e_coord)
        
        return self.factory(e_coords, [self.n_coord])

class NFull(Topology):
    
    __slots__ = ()
    
    def n_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the node dimension."""
        
        unchanged = self.n_space - self.n_coord
        n_coords = (self.n_coord | {change} for change in unchanged)
        
        return self.factory([self.e_coord], n_coords)
    
    def n_parents(self: Topo) -> Iterator[Topo]:
        """Return iterable containing parents in the node dimension."""
        
        n_coords = (self.n_coord - {change} for change in self.n_coord)
        
        return self.factory([self.e_coord], n_coords)