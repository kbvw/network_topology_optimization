from collections.abc import (Hashable, Iterable, Iterator, 
                             Callable, Generator, Set)
from itertools import chain, combinations, product
from typing import TypeVar

A = TypeVar('A', bound=Hashable)
B = TypeVar('B', bound=Hashable)

def chainmap(f: Callable[[A], Iterable[B]], xs: Iterable[A]) -> Iterator[B]:
    """Chain of iterables from a map."""
    
    return chain.from_iterable(map(f, xs))

def unique(xs: Iterable[A],
           exclude: Set[A] = frozenset()) -> Generator[A, None, set[A]]:
    """Unique elements from an iterable."""
    
    seen: set[A] = set()
    for x in xs:
        if (x not in exclude) and (x not in seen):
            seen.add(x)
            yield x
    return seen

def splits(xs: Set[A],
           min_size: int,
           max_splits: int) -> Iterator[Iterable[frozenset[A]]]:
    """All possible ordered splits of an iterable into disjoint subsets."""
    
    if (len(xs) >= 2 * min_size) and (max_splits > 1):
        
        sizes = range(min_size, len(xs) - min_size + 1)
        yss = (frozenset(c) for n in sizes for c in combinations(xs, n))
        
        prod = (product([ys], splits(xs - ys, min_size, max_splits - 1))
                for ys in yss)
        
        return ((split, *subsplits) for p in prod for split, subsplits in p)
    
    else:
        return iter([tuple([frozenset(xs)])])