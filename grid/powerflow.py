import numpy as np

from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import NamedTuple
from numpy.typing import NDArray

from ..topology.coords import Topology

C = Hashable
N = Hashable

L = Hashable
G = Hashable

AList = Mapping[N, Mapping[N, Iterable[C]]]
YList = Mapping[C, complex]
LoadList = Mapping[L, N]
GenList = Mapping[G, N]

PList = Mapping[L | G, float]
QList = Mapping[L, float]
SlackList = Mapping[G, float]
AngList = Mapping[N, float]
MagList = Mapping[N, float]
FlowList = Mapping[C, complex]

class Grid(NamedTuple):
    a_list: AList
    y_list: YList
    load_list: LoadList
    gen_list: GenList

class GridData(NamedTuple):
    p_list: PList
    q_list: QList
    mag_list: MagList
    slack_list: SlackList

class GridRes(NamedTuple):
    ang_list: AngList
    mag_list: MagList
    flow_list: FlowList

NIndex = Sequence[N]
CIndex = Sequence[C]

class GridIndex(NamedTuple):
    pv_index: NIndex
    pq_index: NIndex
    c_index: CIndex

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
    
    load_list, gen_list = bus_split(grid.load_list, grid.gen_list, topo)
    
    pass

def bus_split(load_list: LoadList, 
              gen_list: GenList, 
              topo: Topology) -> tuple[LoadList, GenList]:
    
    splits = {e: (n, k) for n in topo.n_coord 
              for k, es in enumerate(topo.n_coord[n][1])
              for e in es}
    
    ls = {l: (splits[l] if (l in splits) else load_list[l])
          for l in load_list}
    gs = {g: (splits[g] if (g in splits) else gen_list[g])
          for g in gen_list}
    
    return (ls, gs)

def bp_mat(a_list: AList,
           y_list: YList,
           n_index: NIndex,
           topo: Topology) -> YMat:
    pass

def bpp_mat(a_list: AList,
            y_list: YList,
            n_index: NIndex,
            topo: Topology) -> YMat:
    pass

def p(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> PVec:
    pass

def q(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> QVec:
    pass



