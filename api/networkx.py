import networkx as nx # type: ignore
import networkx.algorithms.connectivity as nxc # type: ignore

from collections.abc import Hashable, Iterable, Mapping, Callable
from typing import Optional

from itertools import chain

from ..topology.coords import Topology, ECoord, NCoord
from ..topology.graphs import en_connection_list

E = Hashable
N = Hashable

ENList = Mapping[E, Iterable[N]]

AList = Mapping[N, Mapping[N, Iterable[E]]]

Guard = Callable[[Topology], bool]

def make_graph(a_list: AList,
               topo: Optional[Topology] = None,
               en_list: Optional[ENList] = None,
               store_edge_data: bool = True) -> nx.Graph:
    """NetworkX graph from adjacency list."""
    
    if topo is None:
        e_coord, n_coord = ECoord(), NCoord()
    else:
        e_coord, n_coord = topo.e_coord, topo.n_coord
    
    if en_list is None:
        en_list = en_connection_list(a_list)
    
    en_sub_list: dict[E, list[tuple[N, int]]] = {}
        
    graph = nx.Graph()
    
    for n in a_list:
        if n not in n_coord:
            graph.add_node(n)
        else:
            subs = (((n, i), es) for i, es in enumerate(n_coord[n][1]))
            for sn, es in subs:
                graph.add_node(sn)
                for e in es:
                    en_sub_list.setdefault(e, []).append(sn)
    
    for e in en_list:
        if e not in e_coord:
            t, f = en_list[e]
            match (t in n_coord, f in n_coord):
                case (False, False):
                    st, sf = t, f
                case (False, True):
                    st, sf = t, en_sub_list[e][0]
                case (True, False):
                    st, sf = en_sub_list[e][0], f
                case (True, True):
                    st, sf = en_sub_list[e][0], en_sub_list[e][1]
            
            if store_edge_data:
                graph.add_edge(st, sf, e=e)
            else:
                graph.add_edge(st, sf)
            
    return graph

def k_edge_guard(a_list: AList, 
                 k: int = 2) -> Guard:
    """Function that returns true if graph is k-edge connected."""
    
    en_list = en_connection_list(a_list)
    
    g = make_graph(a_list, en_list=en_list, store_edge_data=False)
    
    if not nxc.is_k_edge_connected(g, k):
        raise ValueError(f'not {k}-edge connected')
    
    def k_edge_guard(coords: Topology) -> bool:
        
        return check_k_edge_connected(coords, a_list, en_list, k)
    
    return k_edge_guard

def check_k_edge_connected(coords: Topology,
                           a_list: AList, 
                           en_list: ENList,
                           k: int = 2) -> bool:
    """True if topology is k-edge connected."""
    
    g = make_graph(a_list, coords, en_list=en_list, store_edge_data=False)
    
    return nxc.is_k_edge_connected(g, k)