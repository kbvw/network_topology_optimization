from collections.abc import (Hashable, Iterable, Iterator,
                             Mapping, Set, Collection)

from itertools import repeat

from ..core.itertools import splits, unique, distribute

from .coords import ESpace, NSpace, ECoord, NCoord, Topology
from .coords import TopoTuple, EC, EP, NC, NP

from .graphs import ne_connections, ne_connection_list, degree, degree_list

# To do: non-connection elements in node splits

E = Hashable
N = Hashable

AList = Mapping[N, Mapping[N, Iterable[E]]]

EList = Iterable[E]
NList = Mapping[N, Iterable[E]]

Split = Collection[frozenset[E]]
NSplit = tuple[N, Split]

def make_e_space(e_list: EList,
                 a_list: AList,
                 min_deg: int = 2,
                 exclude: Set[E] = frozenset()) -> ESpace:
    """E-coordinate space from iterable of elements."""
    
    d = degree_list(a_list)
    
    below_min = tuple(n for n in d if d[n] < min_deg)
    
    if len(below_min) > 0:
        raise ValueError(f'minimum degree not satisfied at {below_min}')
    
    ne = ne_connection_list(a_list)
    exclude = set(exclude)
    
    at_min = {e for n in ne for e in ne[n] if d[n] == min_deg}
    exclude.update(at_min)
    
    return ESpace({e for e in e_list if not e in exclude})

def make_n_space(n_list: NList,
                 a_list: AList,
                 min_deg: int = 2,
                 max_splits: int | Iterable[int] = 2) -> NSpace:
    """N-coordinate space from iterable of (node, elements) tuples."""
    
    d = degree_list(a_list)
    
    below_min = tuple(n for n in d if d[n] < min_deg)
    
    if len(below_min) > 0:
        raise ValueError(f'minimum degree not satisfied at {below_min}')
    
    if isinstance(max_splits, int):
        max_splits = repeat(max_splits)
    
    return NSpace({n: frozenset(node_splits(n, n_list[n], a_list, min_deg, s))
                   for n, s in zip(n_list, max_splits)})

def node_splits(node: N,
                e_list: Iterable[E],
                a_list: AList,
                min_deg: int = 2,
                max_splits: int = 2,
                ordered: bool = False) -> Iterator[NSplit]:
    """All possible node satisfying minimum degree in adjacency list."""
    
    deg = degree(a_list, node)
    
    if deg < min_deg:
        raise ValueError(f'minimum degree not satisfied at {node}')
    
    e_list = set(e_list)
    e_connect = set(ne_connections(a_list, node))
    
    ec_flex = e_list & e_connect
    ec_fix = e_connect - e_list
    e_other = e_list - e_connect
    
    base_splits = splits(ec_flex, min_deg, max_splits, ec_fix)
    full_splits = distribute(e_other, base_splits)
    
    if ordered:
        return ((node, tuple(s)) for s in full_splits)
    else:
        return unique((node, frozenset(s)) for s in full_splits)

def make_root(es: ESpace, ns: NSpace) -> Topology:
    """Root of coordinate system defined by e-space and n-space."""
    
    class Coords(TopoTuple, EC, EP, NC, NP):
        e_space = es
        n_space = ns
    
    return Coords([ECoord(), NCoord()])