from collections.abc import (Hashable, Iterable, Iterator, Collection, 
                             Mapping, Set)
from typing import Optional

from itertools import combinations, product, chain

from ..core.itertools import chainmap, splits

from .coords import ECoord, NCoord, ESpace, NSpace
from .graphs import ne_connections, ne_list, degree, degree_list

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
    
    ne = ne_list(a_list)
    exclude = set(exclude)
    
    at_min = {e for n in ne for e in ne[n] if d_list[n] == min_deg}
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
                a_list: AList,
                min_deg: int = 2,
                max_splits: int = 2) -> Iterator[NSplit]:
    
    deg = degree(a_list, node)
    
    if deg < min_deg:
        raise ValueError(f'minimum degree not satisfied at {node}')
    
    e_list = frozenset(e_list)
    
    e_connect = e_list & frozenset(ne_connections(a_list, node))
    
    if len(e_connect) < min_deg:
        return iter([])
    
    return iter([])

def make_root():
    pass
