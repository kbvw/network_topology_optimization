from __future__ import annotations

from abc import ABC, abstractmethod

from itertools import chain, tee
from functools import reduce

from typing import Iterable, Optional, Callable, TypeVar

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TGCoords', 'TDGCoords, 'TDAGCoords', 'TTreeCoords' with 'Self'
TGCoords = TypeVar('TGCoords', bound='GCoords')
TDGCoords = TypeVar('TDGCoords', bound='DGCoords')
TDAGCoords = TypeVar('TDAGCoords', bound='DAGCoords')
TTreeCoords = TypeVar('TTreeCoords', bound='TreeCoords')

# Base coordinate classes to implement for using the library functions

class GCoords(ABC):
    """Base class for implicit definition of a graph."""
    __slots__ = ()
    
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Return True if self is equal to other."""
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return integer hash value of self."""
    
    @abstractmethod
    def adjacent(self: TGCoords) -> Iterable[TGCoords]:
        """Return iterable containing adjacent coordinates."""
    
    def isadjacent(self: TGCoords, other: TGCoords) -> bool:
        """Return True if self is a parent of other."""
        adjacent: Iterable[TGCoords] = self.adjacent()
        return any(coords == other for coords in adjacent)

class DGCoords(GCoords, ABC):
    """Base class for implicit definition of a directed graph."""
    __slots__ = ()
    
    @abstractmethod
    def children(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing children."""
    
    @abstractmethod
    def parents(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing parents."""
    
    def adjacent(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing adjacent coordinates."""
        return chain(self.children(), self.parents())
    
    def ischild(self: TDGCoords, other: TDGCoords) -> bool:
        """Return True if self is a child of other."""
        parents: Iterable[TDGCoords] = self.parents()
        return any(coords == other for coords in parents)
    
    def isparent(self: TDGCoords, other: TDGCoords) -> bool:
        """Return True if self is a parent of other."""
        children: Iterable[TDGCoords] = self.children()
        return any(coords == other for coords in children)

class DAGCoords(DGCoords, ABC):
    """Base class for implicit definition of a directed acyclic graph."""
    __slots__ = ()

class TreeCoords(DAGCoords, ABC):
    """Base class for implicit definition of a tree graph."""
    __slots__ = ()

# Generic types

T = TypeVar('T')
GC = TypeVar('GC', bound=GCoords)
DGC = TypeVar('DGC', bound=DGCoords)

# Type aliases

Guard = Callable[[GC], bool]
Enumerator = Callable[[GC, Optional[Guard[GC]]], Iterable[GC]]
GuardedDirection = Callable[[GC], Iterable[GC]]

# Main library functions

def adjacent(coords: GC,
             guard: Optional[Guard[GC]]=None) -> Iterable[GC]:
    
    return filter(guard, coords.adjacent())

def children(coords: DGC,
             guard: Optional[Guard[DGC]]=None) -> Iterable[DGC]:
    
    return filter(guard, coords.children())

def parents(coords: DGC,
            guard: Optional[Guard[DGC]]=None) -> Iterable[DGC]:
    
    return filter(guard, coords.parents())

def neighborhood(coords: GC, 
                 depth: int=1,
                 guard: Optional[Guard[GC]]=None) -> Iterable[GC]:
    
    return explore(coords, adjacent, depth, guard)

def descendants(coords: DGC, 
                depth: int=1,
                guard: Optional[Guard[DGC]]=None) -> Iterable[DGC]:
    
    return explore(coords, children, depth, guard)

def ancestors(coords: DGC, 
              depth: int=1,
              guard: Optional[Guard[DGC]]=None) -> Iterable[DGC]:
    
    return explore(coords, parents, depth, guard)

def traverse(coords: GC,
             direction: Enumerator[GC],
             depth: int=1,
             guard: Optional[Guard[GC]]=None) -> Iterable[GC]:
    
    # Additional runtime coercion to int for safe recursion
    if (depth := int(depth)) < 0:
        raise ValueError('depth must be a positive integer')
    
    if depth == 0:
        return (coords,)
    else:
        cs = direction(coords, guard)
        t = lambda c: traverse(c, direction, depth-1, guard)
        return chain.from_iterable(map(t, cs))

def explore(coords: GC,
            direction: Enumerator[GC],
            depth: int=1,
            guard: Optional[Guard[GC]]=None) -> Iterable[GC]:
    
    step = guarded(direction, guard)
    
    seen: set[GC] = {coords}
    queue: Iterable[GC] = (coords,)
    update: Iterable[GC] = ()
    
    for d in range(depth):
        seen.update(update)
        queue, update, results = tee(unique(chainmap(step, queue), seen), 3)
        yield from results
        
def chainmap(f: Callable[[T], Iterable[T]], 
             xs: Iterable[T]) -> Iterable[T]:
    
    return chain.from_iterable(map(f, xs))

def guarded(direction: Enumerator[GC],
            guard: Optional[Guard[GC]]) -> GuardedDirection[GC]:
    
    return lambda c: direction(c, guard)

def unique(xs: Iterable[T],
           exclude: Iterable[T]=()) -> Iterable[T]:
    
    seen: set[T] = set(exclude)
    for x in xs:
        if x not in seen:
            seen.add(x)
            yield x

# Specific implementation for topology search

from dataclasses import dataclass

from itertools import product, starmap

from typing import Type

# Generic type for all topology coordinates
TC = TypeVar('TC', bound='TopoCoords')

# Type aliases for topology coordinates
Node = int
Edge = int
NodeSplit = tuple[Node, frozenset[Edge], frozenset[Edge]]
EdgeSwitch = Edge
NodeCoord = frozenset[NodeSplit]
EdgeCoord = frozenset[EdgeSwitch]

@dataclass(frozen=True, slots=True)
class TopoDataMixin:
    """Mixin class for immutable topology search coordinates."""
    node_splits: frozenset[NodeSplit]
    edge_switches: frozenset[EdgeSwitch]
    
    @property
    def node_coord(self) -> frozenset[NodeSplit]:
        return self.node_splits
    
    @property
    def edge_coord(self) -> frozenset[EdgeSwitch]:
        return self.edge_switches

class TopoCoords(TopoDataMixin, DAGCoords, ABC):
    """Base coordinates for possible alterations to a graph topology."""
    __slots__ = ()
    
    @classmethod
    @property
    @abstractmethod
    def node_space(cls) -> frozenset[NodeSplit]:
        """Full space of possible node changes to the root topology."""
    
    @classmethod
    @property
    @abstractmethod
    def edge_space(cls) -> frozenset[EdgeSwitch]:
        """Full space of possible edge changes to the root topology."""
    
    @property
    def node_coord(self) -> NodeCoord:
        return super().node_coord
    
    @property
    def edge_coord(self) -> EdgeCoord:
        return super().edge_coord
    
    def node_children(self: TC) -> Iterable[TC]:
        """Return iterable containing children in the node dimension."""
        
        unchanged = self.node_space - self.node_coord
        node_coords = (self.node_coord | {change} 
                       for change in unchanged)
        
        return coord_factory(type(self), node_coords, (self.edge_coord,))
    
    def edge_children(self: TC) -> Iterable[TC]:
        """Return iterable containing children in the edge dimension."""
        
        unchanged = self.edge_space - self.edge_coord
        edge_coords = (self.edge_coord | {change} 
                       for change in unchanged)
        
        return coord_factory(type(self), (self.node_coord,), edge_coords)
    
    def node_parents(self: TC) -> Iterable[TC]:
        """Return iterable containing parents in the node dimension."""
        
        node_coords = (self.node_coord - {change} 
                       for change in self.node_coord)
        
        return coord_factory(type(self), node_coords, (self.edge_coord,))
    
    def edge_parents(self: TC) -> Iterable[TC]:
        """Return iterable containing parents in the edge dimension."""
        
        edge_coords = (self.edge_coord - {change} 
                       for change in self.edge_coord)
        
        return coord_factory(type(self), (self.node_coord,), edge_coords)
    
    def children(self: TC) -> Iterable[TC]:
        """Return iterable containing children."""
        
        return chain(self.node_children(), self.edge_children())
    
    def parents(self: TC) -> Iterable[TC]:
        """Return iterable containing parents."""
        
        return chain(self.node_parents(), self.edge_parents())

def coord_factory(coord_class: Type[TC],
                  node_coords: Iterable[NodeCoord],
                  edge_coords: Iterable[EdgeCoord]) -> Iterable[TC]:
    return starmap(coord_class, product(node_coords, edge_coords))