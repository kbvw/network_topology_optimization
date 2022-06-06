from collections.abc import Hashable, Callable

from typing import NamedTuple
from itertools import chain
from functools import reduce

from ..core.itertools import unique

from ..topology.coords import Topology

# To do:
# - Maintain ordering in line endings: important for transformers

N = Hashable
C = Hashable
L = Hashable
G = Hashable
B = Hashable

CNList = dict[C, frozenset[N]]
LNList = dict[L, N]
GNList = dict[G, N]

Admittances = dict[C, complex]
SlackFactors = dict[G, float]
VoltageLevels = dict[N | C, float]
PowerBase = float

class Grid(NamedTuple):
    cn_list: CNList
    ln_list: LNList
    gn_list: GNList

class GridParams(NamedTuple):
    y_list: Admittances
    s_list: SlackFactors
    v_list: VoltageLevels
    p_base: PowerBase

BIndex = tuple[B, ...]
SIndex = dict[B, float]
YIndex = dict[frozenset[B], float]

class PFIndex(NamedTuple):
    pv_idx: BIndex
    pq_idx: BIndex
    s_idx: SIndex
    y_idx: YIndex

def apply_topology(grid: Grid, topo: Topology) -> Grid:
    pass

def pf_index(grid: Grid, grid_params: GridParams) -> PFIndex:
    pass

def slack_factors(grid: Grid, grid_params: GridParams) -> SIndex:
    
    bs: dict[B, float]
    bs = {b: 0. for b in unique(grid.gn_list.values())}
    
    r = lambda bs, b: bs | {bs[b[0]] + grid_params.s_list[b[1]]}
    return reduce(r, grid.gn_list.items(), bs)

def admittances(grid: Grid, grid_params: GridParams) -> YIndex:
    
    pu_y_list = {c: y*grid_params.p_base/(grid_params.v_list[c]**2)
                 for c, y in grid_params.y_list.items()}
    
    bps: dict[frozenset[B], float]
    bps = {bp: 0. for bp in unique(grid.cn_list.values())}
    
    r = lambda bps, bp: bps | {bps[bp[0]] + pu_y_list[bp[1]]}
    return reduce(r, grid.cn_list.items(), bps)

def bus_types(grid: Grid, grid_params: GridParams) -> tuple[BIndex, BIndex]:
    
    pv_idx = tuple(unique(n for n in grid.gn_list))
    pq_idx = tuple(unique(n for n in grid.ln_list))
    
    return (pv_idx, pq_idx)

def bus_split(grid: Grid, topo: Topology) -> Grid:
    
    splits = {(n, i): [e for e in es if not e in topo.e_coord]
              for n in topo.n_coord
              for i, es in enumerate(topo.n_coord[n][1])}
    
    l_splits = {e: b for b, es in splits.items()
                for e in es if e in grid.ln_list}
    g_splits = {e: b for b, es in splits.items()
                for e in es if e in grid.gn_list}
    
    bs: Callable[[C], set[N]]
    bs = lambda e: ({b for b in splits if e in splits[b]}
                    | {b for b in grid.cn_list[e] if not b in topo.n_coord})
    c_splits = {e: frozenset(bs(e))
                for e in chain.from_iterable(splits.values())
                if e in grid.cn_list}
    
    return Grid(cn_list = grid.cn_list | c_splits,
                ln_list = grid.ln_list | l_splits,
                gn_list = grid.gn_list | g_splits)