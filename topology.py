from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Hashable
from typing import TypeVar, Type, Generic, NoReturn

from itertools import chain, product

from network_topology_optimization.core import DAGCoords

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopoCoords' with 'Self'
TTopoCoords = TypeVar('TTopoCoords', bound='TopoCoords')

# Base topology coordinate class to implement for using topology functions

class TopoCoords(DAGCoords, ABC):
    """Base class for possible alterations to a graph topology."""
    
    __slots__ = ()
    
    @abstractmethod
    def e_children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children in the edge dimension."""
        
        raise NotImplementedError
    
    @abstractmethod
    def n_children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children in the node dimension."""
        
        raise NotImplementedError
    
    @abstractmethod
    def e_parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents in the edge dimension."""
        
        raise NotImplementedError
    
    @abstractmethod
    def n_parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents in the node dimension."""
        
        raise NotImplementedError
    
    def children(self: TTopoCoords) -> Iterator[TTopoCoords]:
        """Return iterable containing children."""
        
        return chain(self.e_children(), self.n_children())
    
    def parents(self: TTopoCoords) -> Iterator[TTopoCoords]:
        """Return iterable containing parents."""
        
        return chain(self.e_parents(), self.n_parents())
    
    def is_e_child(self: TTopoCoords, other: TTopoCoords) -> bool:
        """Return True if self is a edge-child of other."""
        
        e_parents: Iterable[TTopoCoords] = self.e_parents()
        return any(coords == other for coords in e_parents)
    
    def is_n_child(self: TTopoCoords, other: TTopoCoords) -> bool:
        """Return True if self is a node-child of other."""
        
        n_parents: Iterable[TTopoCoords] = self.n_parents()
        return any(coords == other for coords in n_parents)
    
    def is_e_parent(self: TTopoCoords, other: TTopoCoords) -> bool:
        """Return True if self is a edge-parent of other."""
        
        e_children: Iterable[TTopoCoords] = self.e_children()
        return any(coords == other for coords in e_children)
    
    def is_n_parent(self: TTopoCoords, other: TTopoCoords) -> bool:
        """Return True if self is a node-parent of other."""
        
        n_children: Iterable[TTopoCoords] = self.n_children()
        return any(coords == other for coords in n_children)

# Generic types for topology coordinates

ECoord = TypeVar('ECoord', bound=Hashable)
NCoord = TypeVar('NCoord', bound=Hashable)
ESpace = TypeVar('ESpace', bound=Hashable)
NSpace = TypeVar('NSpace', bound=Hashable)

# Base class for storing topology coordinate data

class TopoData(TopoCoords, Generic[ECoord, NCoord, ESpace, NSpace], ABC): 
    """Base class for data layout of topology alteration coordinates."""
    
    __slots__ = ()
    
    @property
    @abstractmethod
    def e_coord(self) -> ECoord: 
        """The set of edge changes to the topology."""
        
        raise NotImplementedError
        
    @property
    @abstractmethod
    def n_coord(self) -> NCoord: 
        """The set of node changes to the topology."""
        
        raise NotImplementedError
    
    @property
    @abstractmethod
    def e_space(self) -> ESpace: 
        """The space of possible edge changes to the topology."""
        
        raise NotImplementedError
    
    @property
    @abstractmethod
    def n_space(self) -> NSpace: 
        """The space of possible node changes to the topology."""
        
        raise NotImplementedError
    
    def __eq__(self, other: object) -> bool:
        
        if isinstance(other, type(self)):
            return (self.e_coord == other.e_coord
                    and self.n_coord == other.n_coord)
        else:
            return NotImplemented
    
    def __hash__(self) -> int:
        
        return hash(self.e_coord) ^ hash(self.n_coord)

# Type aliases

Edge = Hashable
Node = Hashable
ESwitch = frozenset[Edge]
NSplit = frozenset[Node]
ESwitchSpace = frozenset[Edge]
NSplitSpace = frozenset[Node]

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopoData', 'TTopology' with 'Self'
TTopology = TypeVar('TTopology', bound='Topology')

# Specific implementation of topology coordinate logic
# Direct subclass of tuple for better performance over many instances

class TopoTuple(tuple[ESwitch, NSplit], 
                TopoData[ESwitch, NSplit, ESwitchSpace, NSplitSpace]):
    """Immutable implementation of topology alteration coordinates."""
    
    __slots__ = ()
    
    @property
    def e_coord(self) -> ESwitch:
        """The set of edge changes to the topology."""
        
        return self[0]
    
    @property
    def n_coord(self) -> NSplit:
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