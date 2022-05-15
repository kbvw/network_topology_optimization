from collections.abc import Hashable, Iterable, Mapping

from itertools import chain

E = Hashable
N = Hashable

ENConnections = Iterable[N]
NEConnections = Iterable[E]

ENList = Mapping[E, ENConnections]
NEList = Mapping[N, NEConnections]

Adjacent = Mapping[N, Iterable[E]]
Degree = int

AList = Mapping[N, Adjacent]
DList = Mapping[N, Degree]

def e_list(a_list: AList) -> set[E]:
    """Unique elements in adjacency list."""
    
    return set(e for n in a_list for e in a_list[n])

def en_connections(a_list: AList, e: E) -> set[N]:
    """Nodes connected to element e in the adjacency list."""
    
    return set(n for n in a_list if e in ne_connections(a_list, n))

def en_connection_list(a_list: AList) -> dict[E, set[N]]:
    """Nodes connected to each element in the adjacency list."""
    
    return {e: set(en_connections(a_list, e)) for e in e_list(a_list)}

def n_list(a_list: AList) -> set[N]:
    """Unique nodes in adjacency list."""
    
    return set(a_list.keys())

def ne_connections(a_list: AList, n: N) -> set[E]:
    """Elements connected to node n in the adjacency list."""
    
    return set(chain.from_iterable(a_list[n].values()))

def ne_connection_list(a_list: AList) -> dict[N, set[E]]:
    """Elements connected to each node in the adjacency list."""
    
    return {n: set(ne_connections(a_list, n)) for n in n_list(a_list)}

def degree(a_list: AList, n: N) -> int:
    """Number of elements connected to node n in the adjacency list."""
    
    return len(tuple(ne_connections(a_list, n)))

def degree_list(a_list: AList) -> DList:
    """Number of elements connected to each node in the adjacency list."""
    
    return {n: degree(a_list, n) for n in a_list}