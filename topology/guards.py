from collections.abc import Hashable, Iterable, Mapping, Callable

from .coords import Topology
from .graphs import degree_list, en_connection_list, sub_connections

E = Hashable
N = Hashable

AList = Mapping[N, Mapping[N, Iterable[E]]]
DList = Mapping[N, int]

EList = Iterable[E]
NList = Iterable[tuple[N, Iterable[E]]]

ENList = Mapping[E, Iterable[N]]

Guard = Callable[[Topology], bool]

class GuardWrapper:
    """Container for composing multiple guard functions."""
    
    def __init__(self, guard_funcs: Iterable[Guard]) -> None:
        
        self.guard_funcs = guard_funcs
        
    def __call__(self, coords: Topology) -> bool:
        
        return all(func(coords) for func in self.guard_funcs)

def degree_guard(a_list: AList, 
                 min_deg: int = 2) -> Guard:
    """Function that returns true if minimum degree is satisfied."""
    
    d_list = degree_list(a_list)
    
    below_min = tuple(n for n in d_list if d_list[n] < min_deg)
    
    if len(below_min) > 0:
        raise ValueError(f'minimum degree not satisfied at {below_min}')
        
    en_list = en_connection_list(a_list)
    
    def degree_guard(coords: Topology) -> bool:
        
        return check_degree(coords, d_list, en_list, min_deg)
    
    return degree_guard

def check_degree(coords: Topology, 
                 d_list: DList, 
                 en_list: ENList,
                 min_deg: int = 2) -> bool:
    """True if smallest degree in topology is above minimum degree."""
    
    d_list = dict(d_list)
    
    for e in coords.e_coord:
        ds = [(n, d_list[n] - 1) for n in en_list[e]]
        if any(d < min_deg for _, d in ds):
            return False
        d_list.update(ds)
    
    for n in coords.n_coord:
        cs = sub_connections(n, en_list, coords)
        if any(len(es) < min_deg for es in cs):
            return False
           
    return True