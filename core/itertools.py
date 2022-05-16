from collections.abc import (Hashable, Iterable, Iterator, 
                             Callable, Generator, Set)
from itertools import chain, combinations, product
from typing import TypeVar

A = TypeVar('A', bound=Hashable)
B = TypeVar('B', bound=Hashable)

C = TypeVar('C')

Split = tuple[frozenset[A], ...]

def chainmap(f: Callable[[A], Iterable[B]], xs: Iterable[A]) -> Iterator[B]:
    """Chain of iterables from a map of f over xs."""
    
    return chain.from_iterable(map(f, xs))

def unique(xs: Iterable[A],
           exclude: Set[A] = frozenset()) -> Generator[A, None, set[A]]:
    """Unique elements from xs."""
    
    seen: set[A] = set()
    for x in xs:
        if (x not in exclude) and (x not in seen):
            seen.add(x)
            yield x
    return seen

def splits(xs: Set[A],
           min_size: int,
           max_splits: int) -> Iterator[Split[A]]:
    """All possible ordered splits of xs into disjoint subsets."""
    
    if (len(xs) >= 2 * min_size) and (max_splits > 1):
        
        sizes = range(min_size, len(xs) - min_size + 1)
        yss = (frozenset(c) for n in sizes for c in combinations(xs, n))
        
        prod = (product([ys], splits(xs - ys, min_size, max_splits - 1))
                for ys in yss)
        
        yield from ((split, *subsplits) for p in prod 
                    for split, subsplits in p)
    
    else:
        yield tuple([frozenset(xs)])

def distribute(ys: Iterable[A], 
               xsss: Iterable[Split[A]]) -> Iterator[Split[A]]:
    """All possible distributions of ys over xss for all xss in xsss."""
    
    ys = iter(ys)
    try:
        y = next(ys)
        zsss = chain.from_iterable(supplement(xss, y) for xss in xsss)
        yield from distribute(ys, zsss)
    except StopIteration:
        yield from xsss

def supplement(xss: Split[A], y: A) -> Iterator[Split[A]]:
    """All possible ways to add y to one xs in xss."""
    
    return ((*xss[:n], xss[n] | {y}, *xss[n + 1:]) for n in range(len(xss)))