from __future__ import annotations

from collections.abc import Iterable, Iterator, Callable, Generator, Set
from typing import Optional, TypeVar, TypeAlias

from .abc import GCoords, DGCoords
from .itertools import chainmap, unique

# Generic types

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