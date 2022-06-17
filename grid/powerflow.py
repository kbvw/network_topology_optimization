import numpy as np

from scipy.sparse import coo_array, csr_array, csc_array, hstack # type: ignore
from scipy.sparse.linalg import splu, SuperLU # type: ignore

from collections.abc import Hashable, Mapping
from typing import NamedTuple, Optional
from numpy.typing import NDArray

from itertools import product, chain
from functools import reduce

from ..topology.coords import Topology
from .data import Grid, GridParams, PFIndex

# To do:
# - Generator limits
# - Voltage determination for multiple generators on a bus
# - Initialization using previous results

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
AngList = Mapping[L | G, float]
MagList = Mapping[L | G, float]
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
SArray = NDArray[np.float64]

PVec = NDArray[np.float64]
QVec = NDArray[np.float64]

AngVec = NDArray[np.float64]
MagVec = NDArray[np.float64]

Slack = np.float64

class PFInit(NamedTuple):
    y_mat: YMat
    bp_mat: SuperLU
    bpp_mat: SuperLU
    s_array: SArray

class PFData(NamedTuple):
    p_vec: PVec
    q_vec: QVec
    ang_vec: AngVec
    mag_vec: MagVec
    p_slack: Slack

def initialize(grid: Grid,
               topo: Topology,
               grid_data: GridData) -> tuple[PFIndex, PFData]:
    pass

def p_vec(grid: Grid,
          grid_data: GridData,
          grid_params: GridParams,
          grid_idx: PFIndex,
          start_profile: Optional[PFData] = None) -> PVec:
    
    lgn_list = grid.gn_list | grid.ln_list
    
    ps: dict[N, float]
    ps = {p: 0. for p in chain(grid_idx.pv_idx, grid_idx.pq_idx)}
    
    r = lambda ps, p: ps | {lgn_list[p[0]]: ps[lgn_list[p[0]]] + p[1]}
    np_list = reduce(r, grid_data.p_list.items(), ps)
    
    p: PVec
    p = np.array([np_list[n] for n in chain(grid_idx.pv_idx, 
                                            grid_idx.pq_idx)])
    
    return p/grid_params.p_base

def q_vec(grid: Grid,
          grid_data: GridData,
          grid_params: GridParams,
          grid_idx: PFIndex,
          start_profile: Optional[PFData] = None) -> PVec:
    
    lgn_list = grid.gn_list | grid.ln_list
    
    qs: dict[N, float]
    qs = {q: 0. for q in chain(grid_idx.pv_idx, grid_idx.pq_idx)}
    
    r = lambda qs, q: qs | {lgn_list[q[0]]: qs[lgn_list[q[0]]] + q[1]}
    np_list = reduce(r, grid_data.q_list.items(), qs)
    
    q: QVec
    q = np.array([np_list[n] for n in chain(grid_idx.pv_idx, 
                                            grid_idx.pq_idx)])
    
    return q/grid_params.p_base

def ang_vec(grid: Grid,
            grid_data: GridData,
            grid_params: GridParams,
            grid_idx: PFIndex,
            start_profile: Optional[PFData] = None) -> AngVec:
    
    return np.zeros(len(grid_idx.pv_idx) + len(grid_idx.pq_idx))

def mag_vec(grid: Grid,
            grid_data: GridData,
            grid_params: GridParams,
            grid_idx: PFIndex,
            start_profile: Optional[PFData] = None) -> PVec:
    
    ms: dict[N, float]
    ms = {mag: 1. for mag in chain(grid_idx.pv_idx, grid_idx.pq_idx)}
    
    r = lambda ms, m: ms | {grid_data.mag_list[m[0]]: 
                            max(ms[m[0]], m[1]/grid_params.v_list[m[0]])}
    nm_list = reduce(r, grid_data.mag_list.items(), ms)
    
    m: MagVec
    m = np.array([nm_list[n] for n in chain(grid_idx.pv_idx, 
                                            grid_idx.pq_idx)])
    
    return m

def pf_data(grid: Grid,
            grid_data: GridData,
            grid_params: GridParams,
            grid_idx: PFIndex,
            start_profile: Optional[PFData] = None) -> PFData:
    
    #pq_start = len(grid_idx.pv_idx)
    
    p = p_vec(grid, grid_data, grid_params, grid_idx)
    q = q_vec(grid, grid_data, grid_params, grid_idx)
    
    ang = ang_vec(grid, grid_data, grid_params, grid_idx)
    mag = mag_vec(grid, grid_data, grid_params, grid_idx)
    
    slack = np.float64(0)
    
    return PFData(p_vec=p, q_vec=q, ang_vec=ang, mag_vec=mag, p_slack=slack)

def pf_init(grid: Grid, grid_idx: PFIndex) -> PFInit:
    
    y = laplacian(grid_idx.pv_idx + grid_idx.pq_idx, grid_idx.y_idx)
    
    s = slack_array(grid_idx.pv_idx, grid_idx.s_idx)
    
    bp = bp_mat(grid_idx.pv_idx, grid_idx.pq_idx, grid_idx.y_idx, s)
    
    bpp = bpp_mat(grid_idx.pv_idx, grid_idx.pq_idx, grid_idx.y_idx)
    
    return PFInit(y_mat=y, 
                  bp_mat=splu(bp), 
                  bpp_mat=splu(bpp), 
                  s_array=s)

def a_mat(b_idx: BIndex, y_idx: YIndex) -> YMat:
    
    cs = ((f[0], t[0], y_idx[frozenset([f[1], t[1]])]) 
          for f, t in product(enumerate(b_idx), enumerate(b_idx)) 
          if frozenset([f[1], t[1]]) in y_idx)
    
    rows, cols, data = zip(*cs)
    
    return csc_array((data, (rows, cols)), shape=2*[len(b_idx)])

def laplacian(b_idx: BIndex, y_idx: YIndex) -> YMat:
    
    a = a_mat(b_idx, y_idx)
    idx = np.arange(a.shape[0])
    diag = csc_array((a.sum(axis=1), (idx, idx)), shape=a.shape)
    
    return diag - a

def slack_array(pv_idx: BIndex, s_idx: SIndex) -> NDArray[np.float64]:
    
    slack = [-s_idx[b] for b in pv_idx if b in s_idx]
    
    return np.array(slack)

def bp_mat(pv_idx: BIndex,
           pq_idx: BIndex,
           y_idx: YIndex,
           s_array: SArray) -> YMat:
    
    lap = laplacian(pv_idx + pq_idx, y_idx)
    slack = csc_array(np.reshape(s_array, (len(s_array), 1)))
    
    return csc_array(hstack([slack, np.imag(lap[:, 1:])]))

def bpp_mat(pv_idx: BIndex,
            pq_idx: BIndex,
            y_idx: YIndex) -> YMat:
    
    lap = laplacian(pv_idx + pq_idx, y_idx)
    
    pq_start = len(pv_idx)
    
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

def ang_step(p_diff: PVec,
             ang_vec: AngVec,
             mag_vec: MagVec,
             pf_init: PFInit) -> tuple[AngVec, Slack]:
    
    step = pf_init.bp_mat.solve(p_diff/mag_vec)
    
    ang_new: AngVec
    ang_new = ang_vec + np.concatenate(([0], step[1:]))
    
    slack_new: Slack
    slack_new = step[0]
    
    return ang_new, slack_new

def mag_step(q_diff: PVec,
             mag_vec: MagVec,
             q_vec: QVec,
             q_current: QVec,
             pf_init: PFInit) -> tuple[MagVec, QVec]:
    
    pq_start = len(pf_init.s_array)
    
    step = pf_init.bpp_mat.solve(q_diff/mag_vec[pq_start:])
    
    mag_new: MagVec
    mag_new = np.concatenate([mag_vec[:pq_start],
                              mag_vec[pq_start:] + step])
    
    q_new: QVec
    q_new = np.concatenate([q_current[:pq_start], q_vec[pq_start:]])
    
    return mag_new, q_new

def fdpf(pf_data: PFData,
         pf_init: PFInit,
         max_iter: int = 10,
         min_error: float = 0.001) -> PFData:
    
    pq_start = pf_init.s_array.shape[0]
    
    p_current = p(pf_data.ang_vec, pf_data.mag_vec, pf_init.y_mat)
    q_current = q(pf_data.ang_vec, pf_data.mag_vec, pf_init.y_mat)
    
    p_diff = pf_data.p_vec + pf_init.s_array*pf_data.p_slack - p_current
    q_diff = pf_data.q_vec[pq_start:] - q_current[pq_start:]
    
    if all(p_diff < min_error) and all(q_diff < min_error) or max_iter <= 0:
        
        return PFData(p_vec=p_current, q_vec=q_current, 
                      ang_vec=pf_data.ang_vec, mag_vec=pf_data.mag_vec,
                      p_slack=pf_data.p_slack)
    
    else:
        
        ang_new, slack_new = ang_step(p_diff=p_diff, 
                                      ang_vec=pf_data.ang_vec, 
                                      mag_vec=pf_data.mag_vec, 
                                      pf_init=pf_init)
        
        mag_new, q_new = mag_step(q_diff=q_diff,
                                  mag_vec=pf_data.mag_vec,
                                  q_vec=pf_data.q_vec,
                                  q_current=q_current,
                                  pf_init=pf_init)
        
        pf_data_new = PFData(p_vec=pf_data.p_vec, q_vec=q_new,
                             ang_vec=ang_new, mag_vec=mag_new,
                             p_slack=slack_new)
        
        return fdpf(pf_data_new, pf_init, max_iter - 1, min_error)