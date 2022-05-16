from collections.abc import Hashable

from itertools import chain

E = Hashable
N = Hashable

AList = dict[N, dict[N, list[E]]]

EList = list[E]
NList = dict[N, list[E]]

def infer_a_list(net, 
                 edge_elements=('line', 'trafo')) -> AList:
    
    a_list: AList = {}
    
    for n in net['bus'].index:
        a_list[n] = {}
        
    for e_type in edge_elements:
        for e in net[e_type].index:
            f = net[e_type]['from_bus'][e]
            t = net[e_type]['to_bus'][e]
            a_list[f].setdefault(t, []).append((e_type, e))
            a_list[t].setdefault(f, []).append((e_type, e))
    
    return a_list

def infer_e_list(net, 
                 edge_elements=('line', 'trafo'),
                 other_elements=()) -> EList:
    
    e_list: EList = []
    
    for e_type in chain(edge_elements, other_elements):
        for e in net[e_type].index:
            e_list.append((e_type, e))
    
    return e_list

def infer_n_list(net, 
                 edge_elements=('line', 'trafo'),
                 other_elements=('load', 'gen', 'ext_grid')) -> NList:
    
    n_list: NList = {}
    
    for n in net['bus'].index:
        n_list[n] = []
        
    for e_type in edge_elements:
        for e in net[e_type].index:
            f = net[e_type]['from_bus'][e]
            t = net[e_type]['to_bus'][e]
            n_list[f].append((e_type, e))
            n_list[t].append((e_type, e))
    
    for e_type in other_elements:
        for e in net[e_type].index:
            n = net[e_type]['bus'][e]
            n_list[n].append((e_type, e))
    
    return n_list