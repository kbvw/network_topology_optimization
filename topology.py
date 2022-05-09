from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Hashable, TypeVar, Type, NamedTuple, ClassVar

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

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopology' with 'Self'
TTopology = TypeVar('TTopology', bound='Topology')

# Type aliases for topology coordinates
Node = Hashable
Edge = Hashable
NodeSplit = Node
EdgeSwitch = Edge
NodeCoord = frozenset[NodeSplit]
EdgeCoord = frozenset[EdgeSwitch]

@dataclass(frozen=True, slots=True)
class TopologyData:
    """Mixin class for immutable topology search coordinates."""
    
    node_splits: frozenset[NodeSplit]
    edge_switches: frozenset[EdgeSwitch]
    
    node_split_space: ClassVar[frozenset[NodeSplit]]
    edge_switch_space: ClassVar[frozenset[EdgeSwitch]]
    
class Topology(TopologyData, TopoCoords):
    """Base coordinates for possible alterations to a graph topology."""
    __slots__ = ()
    
    @classmethod
    def factory(cls: Type[TTopology], 
                n_coords: Iterable[NodeCoord], 
                e_coords: Iterable[EdgeCoord]) -> Iterable[TTopology]:
        """Return iterable with cartesian product of coordinates."""
        
        return starmap(cls, product(n_coords, e_coords))
    
    def node_children(self: TTopology) -> Iterable[TTopology]:
        """Return iterable containing children in the node dimension."""
        
        unchanged = self.node_split_space - self.node_splits
        changes = (self.node_splits | {change} for change in unchanged)
        
        return self.factory(changes, (self.edge_switches,))
    
    def edge_children(self: TTopology) -> Iterable[TTopology]:
        """Return iterable containing children in the edge dimension."""
        
        unchanged = self.edge_switch_space - self.edge_switches
        changes = (self.edge_switches | {change} for change in unchanged)
        
        return self.factory((self.node_splits,), changes)
    
    def node_parents(self: TTopology) -> Iterable[TTopology]:
        """Return iterable containing parents in the node dimension."""
        
        changes = (self.node_splits - {change} 
                   for change in self.node_splits)
        
        return self.factory(changes, (self.edge_switches,))
    
    def edge_parents(self: TTopology) -> Iterable[TTopology]:
        """Return iterable containing parents in the edge dimension."""
        
        changes = (self.edge_switches - {change} 
                   for change in self.edge_switches)
        
        return self.factory((self.node_splits,), changes)