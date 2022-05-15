from collections.abc import Hashable, Iterable, Iterator, Mapping, Set

from ..core.itertools import splits, unique

from .coords import ESpace, NSpace, ECoord, NCoord, Topology
from .coords import TopoTuple, EC, EP, NC, NP

from .graphs import ne_connections, ne_connection_list, degree, degree_list

E = Hashable
N = Hashable

AList = Mapping[N, Mapping[N, Iterable[E]]]

EList = Iterable[E]
NList = Iterable[tuple[N, Iterable[E]]]

Split = Iterable[frozenset[E]]
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
    
    if not isinstance(max_splits, Iterable):
        max_splits = (max_splits for n in a_list)
    
    return NSpace({n: tuple(node_splits(n[0], n[1], a_list, min_deg, s))
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
    
    e_list = frozenset(e_list)
    
    e_connect = e_list & frozenset(ne_connections(a_list, node))
    
    n_splits = ((node, s) for s in splits(e_connect, min_deg, max_splits))
    
    if ordered:
        return n_splits
    else:
        return unique(n_splits)

def make_root(e_space: ESpace, n_space: NSpace) -> Topology:
    """Root of coordinate system defined by e-space and n-space."""
    
    class Coords(TopoTuple, EC, EP, NC, NP):
        e_space = e_space
        n_space = n_space
    
    return Coords([ECoord(), NCoord()])
