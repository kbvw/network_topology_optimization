from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Hashable
from typing import TypeVar, Type, Generic, NoReturn

from dataclasses import dataclass

from itertools import chain, product, starmap

from network_topology_optimization.core import DAGCoords

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopologyCoords' with 'Self'
TTopologyCoords = TypeVar('TTopologyCoords', bound='TopoCoords')

class TopoCoords(DAGCoords, ABC):
    """Base class for possible alterations to a graph topology."""
    __slots__ = ()
    
    @abstractmethod
    def node_children(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing children in the node dimension."""
    
    @abstractmethod
    def edge_children(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing children in the edge dimension."""
    
    @abstractmethod
    def node_parents(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing parents in the node dimension."""
    
    @abstractmethod
    def edge_parents(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing parents in the edge dimension."""
    
    def children(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing children."""
        return chain(self.node_children(), self.edge_children())
    
    def parents(self: TTopologyCoords) -> Iterable[TTopologyCoords]:
        """Return iterable containing parents."""
        return chain(self.node_parents(), self.edge_parents())
    
    def is_node_child(self: TTopologyCoords, other: TTopologyCoords) -> bool:
        """Return True if self is a node-child of other."""
        node_parents: Iterable[TTopologyCoords] = self.node_parents()
        return any(coords == other for coords in node_parents)
    
    def is_node_parent(self: TTopologyCoords, other: TTopologyCoords) -> bool:
        """Return True if self is a node-parent of other."""
        node_children: Iterable[TTopologyCoords] = self.node_children()
        return any(coords == other for coords in node_children)
    
    def is_edge_child(self: TTopologyCoords, other: TTopologyCoords) -> bool:
        """Return True if self is a edge-child of other."""
        edge_parents: Iterable[TTopologyCoords] = self.edge_parents()
        return any(coords == other for coords in edge_parents)
    
    def is_edge_parent(self: TTopologyCoords, other: TTopologyCoords) -> bool:
        """Return True if self is a edge-parent of other."""
        edge_children: Iterable[TTopologyCoords] = self.edge_children()
        return any(coords == other for coords in edge_children)

# Generic types for topology coordinates
ECoord = TypeVar('ECoord', bound=Hashable)
NCoord = TypeVar('NCoord', bound=Hashable)
ESpace = TypeVar('ESpace', bound=Hashable)
NSpace = TypeVar('NSpace', bound=Hashable)

class TopoData(TopoCoords, Generic[ECoord, NCoord, ESpace, NSpace]): 
    """Base class for immutable topology search coordinates."""
    #__slots__ = ('e_coord', 'n_coord')
    __slots__ = ()
    
    @property
    @abstractmethod
    def e_coord(self) -> ESpace: 
        """The space of possible edge changes to the topology."""
        
        raise NotImplementedError
        
    @property
    @abstractmethod
    def n_coord(self) -> NSpace: 
        """The space of possible node changes to the topology."""
        
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
    
    def __setattr__(self, key: str, value: object) -> NoReturn:
        
        name = type(self).__name__
        msg = f"'{name}' object does not support attribute assignment"
        
        raise TypeError(msg)
    
    def __repr__(self) -> str:
        
        name = type(self).__name__
        
        return f'{name}(e_coord={self.e_coord!r}, n_coord={self.e_coord!r})'

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopoData', 'TTopology' with 'Self'
TTopology = TypeVar('TTopology', bound='Topology')

# Type aliasese
Edge = Hashable
Node = Hashable
ESwitch = frozenset[Edge]
NSplit = frozenset[Node]
ESwitchSpace = frozenset[Edge]
NSplitSpace = frozenset[Node]

class Topology(tuple, TopoData[ESwitch, NSplit, ESwitchSpace, NSplitSpace]):
    """Base coordinates for possible alterations to a graph topology."""
    __slots__ = ()
    
    @classmethod
    def factory(cls: Type[TTopology], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[TTopology]:
        """Return iterable with cartesian product of coordinates."""
        
        return map(cls, product(e_coords, n_coords))
    
    @property
    def e_coord(self) -> ESwitch:
        
        return self[0]
    
    @property
    def n_coord(self) -> NSplit:
        
        return self[1]
    
    def edge_children(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing children in the edge dimension."""
        
        unchanged = self.e_space - self.e_coord
        e_coords = (self.e_coord | {change} for change in unchanged)
        
        return self.factory(e_coords, (self.n_coord,))
    
    def node_children(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing children in the node dimension."""
        
        unchanged = self.n_space - self.n_coord
        n_coords = (self.n_coord | {change} for change in unchanged)
        
        return self.factory((self.e_coord,), n_coords)
    
    def edge_parents(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing parents in the edge dimension."""
        
        e_coords = (self.e_coord - {change} for change in self.e_coord)
        
        return self.factory(e_coords, (self.n_coord,))
    
    def node_parents(self: TTopology) -> Iterator[TTopology]:
        """Return iterable containing parents in the node dimension."""
        
        n_coords = (self.n_coord - {change} for change in self.n_coord)
        
        return self.factory((self.e_coord,), n_coords)
    
    def __repr__(self) -> str:
        
        return super(tuple, self).__repr__()