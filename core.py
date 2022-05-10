from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Callable, Generator, Set
from typing import Optional, TypeVar, TypeAlias

from itertools import chain

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
        
        raise NotImplementedError
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return integer hash value of self."""
        
        raise NotImplementedError
    
    @abstractmethod
    def adjacent(self: TGCoords) -> Iterable[TGCoords]:
        """Return iterable containing adjacent coordinates."""
        
        raise NotImplementedError
    
    def is_adjacent(self: TGCoords, other: TGCoords) -> bool:
        """Return True if self is a parent of other."""
        
        adjacent: Iterable[TGCoords] = self.adjacent()
        return any(coords == other for coords in adjacent)

class DGCoords(GCoords, ABC):
    """Base class for implicit definition of a directed graph."""
    
    __slots__ = ()
    
    @abstractmethod
    def children(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing children."""
        
        raise NotImplementedError
    
    @abstractmethod
    def parents(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing parents."""
        
        raise NotImplementedError
    
    def adjacent(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing adjacent coordinates."""
        
        return chain(self.children(), self.parents())
    
    def is_child(self: TDGCoords, other: TDGCoords) -> bool:
        """Return True if self is a child of other."""
        
        parents: Iterable[TDGCoords] = self.parents()
        return any(coords == other for coords in parents)
    
    def is_parent(self: TDGCoords, other: TDGCoords) -> bool:
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

# Generic type aliases

Guard: TypeAlias = Callable[[GC], bool]
Direction: TypeAlias = Callable[[GC, Optional[Guard[GC]]], Iterable[GC]]

# Main library functions

def adjacent(coords: GC,
             guard: Optional[Guard[GC]] = None) -> Iterator[GC]:
    
    return filter(guard, coords.adjacent())

def children(coords: DGC,
             guard: Optional[Guard[DGC]] = None) -> Iterator[DGC]:
    
    return filter(guard, coords.children())

def parents(coords: DGC,
            guard: Optional[Guard[DGC]] = None) -> Iterator[DGC]:
    
    return filter(guard, coords.parents())

def neighborhood(coords: GC, 
                 depth: int = 1,
                 guard: Optional[Guard[GC]] = None) -> Iterable[GC]:
    
    return explore(coords, adjacent, depth, guard)

def descendants(coords: DGC, 
                depth: int = 1,
                guard: Optional[Guard[DGC]] = None) -> Iterator[DGC]:
    
    return explore(coords, children, depth, guard)

def ancestors(coords: DGC, 
              depth: int = 1,
              guard: Optional[Guard[DGC]] = None) -> Iterator[DGC]:
    
    return explore(coords, parents, depth, guard)

def explore(coords: GC,
            direction: Direction[GC],
            depth: int = 1,
            guard: Optional[Guard[GC]] = None) -> Generator[GC, None, None]:
    
    step = lambda c: direction(c, guard)
    
    seen: set[GC] = {coords}
    queue: set[GC] = {coords}
    
    for d in range(depth):
        seen = seen | queue
        queue = yield from unique(chainmap(step, queue), seen)

def reach(queue: Iterable[GC],
          direction: Direction[GC],
          depth: int = 1,
          exclude: Set[GC] = frozenset(),
          guard: Optional[Guard[GC]] = None) -> Generator[GC, None, None]:
        
    if depth > 0:
        qs = set(chainmap(lambda c: direction(c, guard), queue))
        yield from reach(qs, direction, depth-1, exclude | qs, guard)

def area(queue: Iterable[GC],
         direction: Direction[GC],
         depth: int = 1,
         exclude: Set[GC] = frozenset(),
         guard: Optional[Guard[GC]] = None) -> Generator[GC, None, None]:
        
    if depth > 0:
        cs = chainmap(lambda c: direction(c, guard), queue)
        qs = yield from unique(cs, exclude)
        yield from area(qs, direction, depth-1, exclude | qs, guard)

def chainmap(f: Callable[[T], Iterable[T]], xs: Iterable[T]) -> Iterator[T]:
    
    return chain.from_iterable(map(f, xs))

def unique(xs: Iterable[T],
           exclude: Set[T] = frozenset()) -> Generator[T, None, set[T]]:
    
    seen: set[T] = set()
    for x in xs:
        if (x not in exclude) and (x not in seen):
            seen.add(x)
            yield x
    return seen