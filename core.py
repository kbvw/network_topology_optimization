from __future__ import annotations

from abc import ABC, abstractmethod

from itertools import chain

from typing import Iterable, Optional, Callable, TypeVar

# Becomes unnecessary with PEP 673:
# -> replace 'TDAGCoords' with 'Self' as of Python 3.11
TDAGCoords = TypeVar('TDAGCoords', bound='DAGCoords')

# Base coordinate class to implement for using the library functions

class DAGCoords(ABC):
    """Base class for implicit definition of a directed acyclic graph."""
    
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Return True if self is equal to other."""
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return integer hash value of self."""
    
    @abstractmethod
    def children(self: TDAGCoords) -> Iterable[TDAGCoords]:
        """Return iterable containing children."""
    
    @abstractmethod
    def parents(self: TDAGCoords) -> Iterable[TDAGCoords]:
        """Return iterable containing parents."""
    
    def ischild(self: TDAGCoords, other: TDAGCoords) -> bool:
        """Return True if self is a child of other."""
        parents: Iterable[TDAGCoords] = self.parents()
        return any(parent == other for parent in parents)
    
    def isparent(self: TDAGCoords, other: TDAGCoords) -> bool:
        """Return True if self is a parent of other."""
        children: Iterable[TDAGCoords] = self.children()
        return any(child == other for child in children)

# Type aliases followed by main library functions
Guard = Callable[[DAGCoords], bool]
Enumerator = Callable[[DAGCoords, Optional[Guard]], Iterable[DAGCoords]]

def children(coords: DAGCoords,
             guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    if guard is None:
        return coords.children()
    else:
        return filter(guard, coords.children())

def parents(coords: DAGCoords,
            guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    if guard is None:
        return coords.parents()
    else:
        return filter(guard, coords.parents())

def adjacent(coords: DAGCoords,
             guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    return chain(children(coords, guard), parents(coords, guard))

def descendants(coords: DAGCoords, 
                depth: int=1,
                guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    return unique(recursor(coords, children, depth, guard))

def ancestors(coords: DAGCoords, 
              depth: int=1,
              guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    return unique(recursor(coords, parents, depth, guard))

def neighborhood(coords: DAGCoords, 
                 depth: int=1,
                 guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    return unique(recursor(coords, adjacent, depth, guard))

def recursor(coords: DAGCoords, 
             enumerator: Enumerator,
             depth: int,
             guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    if depth < 0:
        raise ValueError('depth must be a positive integer')
    elif depth == 0:
        return (coords,)
    else:
        xs = enumerator(coords, guard)
        f = lambda x: recursor(x, enumerator, depth-1, guard)
        return chain.from_iterable(map(f, xs))

def unique(xs: Iterable[DAGCoords]) -> Iterable[DAGCoords]:
    cache: set[DAGCoords] = set()
    for x in xs:
        if x in cache:
            continue
        else:
            cache.add(x)
            yield x

# Specific implementation for topology search

from dataclasses import dataclass

# Becomes unnecessary with PEP 673:
# -> replace 'TTopoCoords' with 'Self' as of Python 3.11
TTopoCoords = TypeVar('TTopoCoords', bound='TopoCoords')

@dataclass(frozen=True, slots=True)
class TopoDataMixin:
    """Mixin class for immutable topology search coordinates."""
    nodes: frozenset[int]
    edges: frozenset[int]

class TopoCoords(TopoDataMixin, DAGCoords, ABC):
    """Base coordinates for possible alterations to a graph topology."""
    
    @classmethod
    @property
    @abstractmethod
    def node_space(cls) -> frozenset[int]:
        """Full space of possible node changes to the root topology."""
    
    @classmethod
    @property
    @abstractmethod
    def edge_space(cls) -> frozenset[int]:
        """Full space of possible edge changes to the root topology."""
    
    def node_children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children in the node dimension."""
        unchanged = self.node_space - self.nodes
        node_coords = (self.nodes | {change} for change in unchanged)
        factory = lambda node_coord: type(self)(node_coord, self.edges)
        return map(factory, node_coords)
    
    def edge_children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children in the edge dimension."""
        unchanged = self.edge_space - self.edges
        edge_coords = (self.edges | {change} for change in unchanged)
        factory = lambda edge_coord: type(self)(self.nodes, edge_coord)
        return map(factory, edge_coords)
    
    def node_parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents in the node dimension."""
        node_coords = (self.nodes - {change} for change in self.nodes)
        factory = lambda node_coord: type(self)(node_coord, self.edges)
        return map(factory, node_coords)
    
    def edge_parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents in the edge dimension."""
        edge_coords = (self.edges - {change} for change in self.edges)
        factory = lambda edge_coord: type(self)(self.nodes, edge_coord)
        return map(factory, edge_coords)
    
    def children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children."""
        return chain(self.node_children(), self.edge_children())
    
    def parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents."""
        return chain(self.node_parents(), self.edge_parents())