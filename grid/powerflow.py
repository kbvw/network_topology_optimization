import numpy as np
from scipy.sparse import csr_matrix, hstack, vstack # type: ignore
from scipy.sparse.linalg import splu # type: ignore

from collections.abc import Hashable, Iterable, Mapping, Sequence, Set
from typing import NamedTuple
from numpy.typing import NDArray

from itertools import product, chain

from ..topology.coords import Topology

C = Hashable
N = Hashable

L = Hashable
G = Hashable

AList = Mapping[N, Mapping[N, Iterable[C]]]
NEList = Mapping[N, Iterable[L | G]]
YList = Mapping[C, complex]
SlackList = Mapping[G, float]

class Grid(NamedTuple):
    a_list: AList
    ne_list: NEList
    y_list: YList
    slack_list: SlackList

PList = Mapping[L | G, float]
QList = Mapping[L, float]
AngList = Mapping[N, float]
MagList = Mapping[N, float]
FlowList = Mapping[C, complex]

class GridData(NamedTuple):
    p_list: PList
    q_list: QList
    mag_list: MagList

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

def pf_data(grid_data: GridData,
            grid_idx: GridIndex) -> PFData:
    pass

def a_mat(b_idx: BIndex, be_list: BEList, y_list: YList) -> YMat:
    
    cs = ((f, t, sum(y_list[e] for e in be_list[t] if e in be_list[t]))
          for f, t in product(b_idx, b_idx))
    
    rows, cols, data = zip(*filter(lambda c: c[2] != 0, cs))
    
    return csr_matrix((data, (rows, cols)), shape=2*[len(be_list)])

def laplacian(b_idx: BIndex, be_list: BEList, y_list: YList) -> YMat:
    
    a = a_mat(b_idx, be_list, y_list)
    
    return csr_matrix(a.sum(axis=0) - a)

def bp_mat(pv_idx: BIndex, 
           pq_idx: BIndex,
           be_list: BEList, 
           y_list: YList, 
           slack_list: SlackList) -> YMat:
    
    grounded_lap = laplacian([pv_idx] + [pq_idx], be_list, y_list)[1:, 1:]
    padded_lap = csr_matrix([np.zeros(len(pv_idx)-1), *grounded_lap])
    slack = np.array(sum(slack_list[e] for e in be_list[b]) 
                     for b in pv_idx)
    
    return np.imag(csr_matrix([slack, *padded_lap.T]).T)

def bpp_mat(pv_idx: BIndex,
            pq_idx: BIndex, 
            be_list: BEList, 
            y_list: YList) -> YMat:
    
    lap = laplacian([pv_idx] + [pq_idx], be_list, y_list)
    
    return np.imag(lap[len(pv_idx):, len(pv_idx):])

def p(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> PVec:
    pass

def q(ang_vec: AngVec, mag_vec: MagVec, b_mat: YMat, g_mat: YMat) -> QVec:
    pass



