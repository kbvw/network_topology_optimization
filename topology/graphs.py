from collections.abc import Hashable, Iterable, Iterator, Mapping

from itertools import chain

from .coords import Topology

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

SubNs = Iterator[tuple[N, int]]
SubCs = Iterator[frozenset[E]]

def e_list(a_list: AList) -> set[E]:
    """Unique elements in adjacency list."""
    
    return set(e for n in a_list for nb in a_list[n] for e in a_list[n][nb])

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

def en_from_ne(ne_list: NEList) -> ENList:
    """Element-node list from a node-element list."""
    
    return {e: set(n for n in ne_list if e in ne_list[n]) 
            for e in chain.from_iterable(ne_list.values())}

def sub_nodes(n: N, coords: Topology) -> SubNs:
    """Tuple of sub-nodes resulting from a node split."""
    
    return ((n, i) for i in range(len(coords.n_coord[n])))

def sub_connections(n: N, en_list: ENList, coords: Topology) -> SubCs:
    """Tuple of sets of elements resulting from a node split."""
    
    guard = lambda e: (e in en_list) and (e not in coords.e_coord)
    return (frozenset(filter(guard, es)) for es in coords.n_coord[n][1])

def topology_a_list(a_list: AList, coords: Topology) -> AList:
    """Adjacency list of topology."""
    
    ne = ne_connection_list(a_list)
    en = en_connection_list(a_list)
    
    splits = (zip(sub_nodes(n, coords), sub_connections(n, en, coords))
              for n in ne if n in coords.n_coord)
    
    split_ne = {n: es for n, es in chain.from_iterable(splits)}
    unsplit_ne = {n: es for n, es in ne.items() if n not in coords.n_coord}
    
    topo_ne = split_ne | unsplit_ne
    topo_en = en_from_ne(topo_ne)
    
    topo_a: dict[N, dict[N, set[E]]] = {}
    for n in topo_ne:
        topo_a[n] = {}
        for e in topo_ne[n]:
            nbs = (nb for nb in topo_en[e] if not nb == n)
            for nb in nbs:
                topo_a[n].setdefault(nb, set()).add(e)
    
    return topo_a