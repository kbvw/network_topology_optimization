from collections.abc import Hashable, Iterable, Iterator, Mapping

from itertools import chain

from ..core.core import unique

E = Hashable
N = Hashable

Adjacent = Mapping[N, Iterable[E]]
Connections = Iterable[E]
Degree = int

AList = Mapping[N, Adjacent]
CList = Mapping[N, Connections]
DList = Mapping[N, Degree]

def connections(adjacent: Adjacent) -> Iterator[E]:
    """Unique elements connecting node to adjacent nodes."""
    
    return unique(chain.from_iterable(adjacent.values()))

def connection_list(a_list: AList) -> dict[N, set[E]]:
    """Unique elements connected to each node."""
    
    return {n: set(connections(a_list[n])) for n in a_list.keys()}

def degree(adjacent: Adjacent) -> int:
    """Number of unique elements connecting node to adjacent nodes."""
    
    return len(tuple(connections(adjacent)))

def degree_list(a_list: AList) -> DList:
    """Number of unique elements connected to each node."""
    
    return {n: degree(neighbors) for n, neighbors in a_list.items()}