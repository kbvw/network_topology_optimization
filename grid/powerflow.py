import numpy as np

from collections.abc import Hashable, Iterable, Mapping, Sequence, Set
from typing import NamedTuple
from numpy.typing import NDArray

from itertools import product

from ..topology.coords import Topology
from ..topology.graphs import topology_a_list

C = Hashable
N = Hashable

L = Hashable
G = Hashable

AList = Mapping[N, Mapping[N, Iterable[C]]]
NEList = Mapping[N, Iterable[L | G]]
YList = Mapping[C, complex]

class Grid(NamedTuple):
    a_list: AList
    ne_list: NEList
    y_list: YList

PList = Mapping[L | G, float]
QList = Mapping[L, float]
SlackList = Mapping[G, float]
AngList = Mapping[N, float]
MagList = Mapping[N, float]
FlowList = Mapping[C, complex]

class GridData(NamedTuple):
    p_list: PList
    q_list: QList
    mag_list: MagList
    slack_list: SlackList

class GridRes(NamedTuple):
    ang_list: AngList
    mag_list: MagList
    flow_list: FlowList

B = Hashable

BEList = Mapping[B, Iterable[L | G]]
BIndex = Sequence[B]
CIndex = Sequence[Set[C]]

class GridIndex(NamedTuple):
    be_list: BEList
    pv_idx: BIndex
    pq_idx: BIndex
    c_idx: CIndex

YMat = NDArray[np.float64]

PVec = NDArray[np.float64]
QVec = NDArray[np.float64]

AngVec = NDArray[np.float64]
MagVec = NDArray[np.float64]

class PFData(NamedTuple):
    b_mat: YMat
    g_mat: YMat
    bp_mat: YMat
    bpp_mat: YMat
    p_vec: PVec
    q_vec: QVec
    ang_vec: AngVec
    mag_vec: MagVec

def initialize(grid: Grid,
               topo: Topology,
               grid_data: GridData) -> tuple[GridIndex, PFData]:
    pass

def grid_index(grid: Grid,
               topo: Topology,
               grid_data: GridData) -> GridIndex:
    
    be_list = bus_split(grid.ne_list, topo)
    
    pv_idx, pq_idx = bus_types(be_list, grid_data)
    
    c_idx = connections(be_list, grid.y_list)
    
    return GridIndex(be_list, pv_idx, pq_idx, c_idx)

def connections(be_list: BEList, y_list: YList) -> CIndex:
    
    css = ({e for e in be_list[f] if e in be_list[t]}
           for f, t in product(be_list, be_list))
    
    return tuple(filter(lambda cs: len(cs) > 0, css))

def bus_types(be_list: BEList,
              grid_data: GridData) -> tuple[BIndex, BIndex]:
    
    pv_idx = tuple(n for n in be_list 
                     if any(e in grid_data.mag_list for e in be_list[n]))
    pq_idx = tuple(n for n in be_list
                     if all(e not in grid_data.mag_list for e in be_list[n]))
    
    return (pv_idx, pq_idx)

def bus_split(ne_list: NEList,
              topo: Topology) -> BEList:
    
    unsplit = {n: {e for e in es if e not in topo.e_coord}
               for n, es in ne_list.items() if n not in topo.n_coord}
    split = {(n, i): es for n in topo.n_coord 
             for i, es in enumerate(topo.n_coord[n][1])}
    
    return unsplit | split

def bp_mat(a_list: AList,
           y_list: YList,
           pv_idx: BIndex,
           topo: Topology) -> YMat:
    pass

def bpp_mat(a_list: AList,
            y_list: YList,
            pq_idx: BIndex,
            topo: Topology) -> YMat:
    pass

def p(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> PVec:
    pass

def q(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> QVec:
    pass



