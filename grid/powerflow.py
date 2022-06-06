import numpy as np

from scipy.sparse import coo_array, csr_array, hstack # type: ignore
from scipy.sparse.linalg import splu, SuperLU # type: ignore

from collections.abc import Hashable, Mapping
from typing import NamedTuple
from numpy.typing import NDArray

from itertools import product

from ..topology.coords import Topology
from .data import Grid, PFIndex

# To do:
# - Per-unit scaling

N = Hashable
C = Hashable
L = Hashable
G = Hashable
B = Hashable

BIndex = tuple[B, ...]
SIndex = dict[B, float]
YIndex = dict[frozenset[B], float]

PList = Mapping[L | G, float]
QList = Mapping[L, float]
AngList = Mapping[B, float]
MagList = Mapping[B, float]
FlowList = Mapping[C, complex]

class GridData(NamedTuple):
    p_list: PList
    q_list: QList
    mag_list: MagList

class GridRes(NamedTuple):
    ang_list: AngList
    mag_list: MagList
    flow_list: FlowList

YMat = NDArray[np.complex64]

PVec = NDArray[np.float64]
QVec = NDArray[np.float64]

AngVec = NDArray[np.float64]
MagVec = NDArray[np.float64]

class PFInit(NamedTuple):
    y_mat: YMat
    bp_mat: SuperLU
    bpp_mat: SuperLU

class PFData(NamedTuple):
    p_vec: PVec
    q_vec: QVec
    ang_vec: AngVec
    mag_vec: MagVec

def initialize(grid: Grid,
               topo: Topology,
               grid_data: GridData) -> tuple[PFIndex, PFData]:
    pass

def pf_data(grid_data: GridData,
            grid_idx: PFIndex) -> PFData:
    pass

def pf_init(grid: Grid, grid_idx: PFIndex) -> PFInit:
    
    y = laplacian(grid_idx.pv_idx + grid_idx.pq_idx, grid_idx.y_idx)
    
    bp = bp_mat(grid_idx)
    
    bpp = bpp_mat(grid_idx)
    
    return PFInit(y_mat=y, bp_mat=splu(bp), bpp_mat=splu(bpp))

def a_mat(b_idx: BIndex, y_idx: YIndex) -> YMat:
    
    cs = ((f[0], t[0], y_idx[frozenset([f[1], t[1]])]) 
          for f, t in product(enumerate(b_idx), enumerate(b_idx)) 
          if frozenset([f[1], t[1]]) in y_idx)
    
    rows, cols, data = zip(*cs)
    
    return csr_array((data, (rows, cols)), shape=2*[len(b_idx)])

def laplacian(b_idx: BIndex, y_idx: YIndex) -> YMat:
    
    a = a_mat(b_idx, y_idx)
    idx = np.arange(a.shape[0])
    diag = csr_array((a.sum(axis=1), (idx, idx)), shape=a.shape)
    
    return diag - a

def slack_array(pv_idx: BIndex, s_idx: SIndex) -> NDArray[np.float64]:
    
    slack = [(b[0], -s_idx[b[1]]) for b in enumerate(pv_idx)
             if b[1] in s_idx]
    
    rows, data = zip(*slack)
    cols = np.zeros(len(slack))
    
    return csr_array((data, (rows, cols)), shape=[len(slack), 1])

def bp_mat(grid_idx: PFIndex) -> YMat:
    
    lap = laplacian(grid_idx.pv_idx + grid_idx.pq_idx, grid_idx.y_idx)
    
    slack = slack_array(grid_idx.pv_idx, grid_idx.s_idx)
    
    return csr_array(hstack([slack, np.imag(lap[:, 1:])]))

def bpp_mat(grid_idx: PFIndex) -> YMat:
    
    lap = laplacian(grid_idx.pv_idx + grid_idx.pq_idx, grid_idx.y_idx)
    
    pq_start = len(grid_idx.pv_idx)
    
    return np.imag(lap[pq_start:, pq_start:])

def p(ang_vec: AngVec, mag_vec: MagVec, y_mat: YMat) -> PVec:
    
    cs = coo_array(y_mat)
    
    ang_diffs = ang_vec[cs.row] - ang_vec[cs.col]
    mags = mag_vec[cs.col]
    
    bs = np.imag(cs.data)*np.sin(ang_diffs)
    gs = np.real(cs.data)*np.cos(ang_diffs)
    
    amps = csr_array((mags*(bs + gs), (cs.row, cs.col))).sum(axis=1)
    
    return mag_vec*amps

def q(ang_vec: AngVec, mag_vec: MagVec, y_mat: YMat) -> QVec:
    
    cs = coo_array(y_mat)
    
    ang_diffs = ang_vec[cs.row] - ang_vec[cs.col]
    mags = mag_vec[cs.col]
    
    bs = -np.imag(cs.data)*np.cos(ang_diffs)
    gs = np.real(cs.data)*np.sin(ang_diffs)
    
    amps = csr_array((mags*(bs + gs), (cs.row, cs.col))).sum(axis=1)
    
    return mag_vec*amps

def ang_step(ang_vec: AngVec, mag_vec: MagVec, p_diff: PVec, bp_mat: SuperLU):
    
    return ang_vec - bp_mat.solve(p_diff/mag_vec)

def mag_step(AngVec, mag_vec: MagVec, q_diff: QVec, bpp_mat: SuperLU):
    
    return mag_vec - bpp_mat.solve(q_diff/mag_vec)

def fdpf(pf_data: PFData, pf_init: PFInit):
    pass