from collections.abc import (Hashable, Iterable, Iterator, Collection, 
                             Mapping, Set)
from typing import Optional

from ..core.core import chainmap

from itertools import combinations, product

from .coords import ECoord, NCoord, ESpace, NSpace
from .graphs import connections, connection_list, degree, degree_list

E = Hashable
N = Hashable

EList = Iterable[E]
NList = Iterable[tuple[N, EList]]

Adjacent = Mapping[N, Iterable[E]]
Connections = Iterable[E]
Degree = int

AList = Mapping[N, Adjacent]
CList = Mapping[N, Connections]
DList = Mapping[N, Degree]

Split = Iterable[frozenset[E]]
NSplit = tuple[N, Split]

def make_e_space(e_list: EList,
                 a_list: AList,
                 min_deg: int = 2,
                 exclude: Set[E] = frozenset()) -> ESpace:
    """E-coordinate space from iterable of elements."""
    
    d_list = degree_list(a_list)
    
    below_min = tuple(n for n in d_list if d_list[n] < min_deg)
    
    if len(below_min) > 0:
        raise ValueError(f'minimum degree not satisfied at {below_min}')
    
    c_list = connection_list(a_list)
    exclude = set(exclude)
    
    at_min = {e for n in c_list for e in c_list[n] if d_list[n] == min_deg}
    exclude.update(at_min)
    
    return ESpace(e for e in e_list if not e in exclude)

def make_n_space(n_list: NList,
                 a_list: AList,
                 min_deg: int = 2,
                 max_splits: int = 2) -> NSpace:
    """N-coordinate space from iterable (node, elements) tuples."""
    
    d_list = degree_list(a_list)
    
    below_min = tuple(n for n in d_list if d_list[n] < min_deg)
    
    if len(below_min) > 0:
        raise ValueError(f'minimum degree not satisfied at {below_min}')
    
    return NSpace()

def node_splits(node: N,
                e_list: EList,
                adjacent: Adjacent,
                min_deg: int = 2,
                max_splits: int = 2) -> Iterator[NSplit]:
    
    deg = degree(adjacent)
    
    if deg < min_deg:
        raise ValueError(f'minimum degree not satisfied at {node}')
    
    e_list = frozenset(e_list)
    
    e_connect = e_list & frozenset(connections(adjacent))
    
    if len(e_connect) < min_deg:
        return iter([])
    
    return iter([])

def split(es: frozenset[E],
          min_deg: int,
          max_splits: int) -> Iterable[Hashable]:
    
    if (len(es) < 2 * min_deg) or (max_splits < 2):
        return tuple([es])
    else:
        f = lambda r: (frozenset(c) for c in combinations(es, r))
        ss = chainmap(f, range(min_deg, len(es) - min_deg + 1))
        return ((s, *split(es - s, min_deg, max_splits - 1)) for s in ss)


def make_root():
    pass
