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
    __slots__ = ()
    
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
    
    return unique(recursor(coords, children, depth, guard), (coords,))

def ancestors(coords: DAGCoords, 
              depth: int=1,
              guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    
    return unique(recursor(coords, parents, depth, guard), (coords,))

def neighborhood(coords: DAGCoords, 
                 depth: int=1,
                 guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    
    return unique(recursor(coords, adjacent, depth, guard), (coords,))

def recursor(coords: DAGCoords, 
             enumerator: Enumerator,
             depth: int,
             guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    
    # Additional runtime coercion to int for safe recursion
    if (depth := int(depth)) < 0:
        raise ValueError('depth must be a positive integer')
    
    if depth == 0:
        return (coords,)
    else:
        xs = enumerator(coords, guard)
        f = lambda x: recursor(x, enumerator, depth-1, guard)
        return chain((coords,), chain.from_iterable(map(f, xs)))

def unique(xs: Iterable[DAGCoords],
           exclude: Iterable[DAGCoords]=()) -> Iterable[DAGCoords]:
    
    seen: set[DAGCoords] = set(exclude)
    for x in xs:
        if x in seen:
            continue
        else:
            seen.add(x)
            yield x

def explorer(coords: DAGCoords, 
             enumerator: Enumerator,
             depth: int,
             guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    
    # Additional runtime coercion to int for safe recursion
    if (depth := int(depth)) < 0:
        raise ValueError('depth must be a positive integer')
    
    seen: set[DAGCoords] = set()
    
    # Impure inner recursor function that mutates a shared 'seen' cache
    def recursor(coords: DAGCoords, depth: int) -> Iterable[DAGCoords]:
        nonlocal seen
        if depth == 0:
            if coords in seen:
                return ()
            else:
                seen.add(coords)
                return (coords,)
        else:
            xs = enumerator(coords, guard)
            xs = filter(lambda x: x not in seen, xs)
            seen.update(xs)
            xss = map(lambda x: recursor(x, depth-1), xs)
            xs = chain.from_iterable(xss)
            return chain((coords,), xs)
    
    return recursor(coords, depth)

def crawler(coords: DAGCoords, 
            enumerator: Enumerator,
            depth: int,
            guard: Optional[Guard]=None) -> Iterable[DAGCoords]:
    
    # Runtime int coercion and value check for safe recursion
    if (depth := int(depth)) < 0:
        raise ValueError('depth must be a positive integer')
    
    # Starting node marked as seen
    seen: set[DAGCoords] = {coords}
    
    # Impure inner recursive generator that mutates 'seen'
    def recursor(coords: DAGCoords, depth: int) -> Iterable[DAGCoords]:
        nonlocal seen
        if depth == 0:
            if coords not in seen:
                seen.add(coords)
                yield coords
        else:
            for new_coords in enumerator(coords, guard):
                if new_coords not in seen:
                    seen.add(new_coords)
                    yield new_coords
                    yield from recursor(new_coords, depth-1)
    
    yield from recursor(coords, depth)

# Specific implementation for topology search

from dataclasses import dataclass

from itertools import product, starmap

from typing import Type

# Type variable for all types of topology coordinates
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