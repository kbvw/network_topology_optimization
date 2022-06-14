from collections.abc import Hashable, Callable

from typing import NamedTuple
from itertools import chain
from functools import reduce

from ..core.itertools import unique

from ..topology.coords import Topology

# To do:
# - Update nodes in voltage levels

N = Hashable
C = Hashable
L = Hashable
G = Hashable

#E = C | L | G

CNList = dict[C, frozenset[N]]
LNList = dict[L, N]
GNList = dict[G, N]
#NEList = dict[N, frozenset[E]]

Admittances = dict[C, complex]
SlackFactors = dict[G, float]
VoltageLevels = dict[L | G | C, float]
PowerBase = float

class Grid(NamedTuple):
    cn_list: CNList
    ln_list: LNList
    gn_list: GNList
    
    #ne_list: NEList

class GridParams(NamedTuple):
    y_list: Admittances
    s_list: SlackFactors
    v_list: VoltageLevels
    p_base: PowerBase

BIndex = tuple[N, ...]
SIndex = dict[N, float]
YIndex = dict[frozenset[N], float]

class PFIndex(NamedTuple):
    pv_idx: BIndex
    pq_idx: BIndex
    s_idx: SIndex
    y_idx: YIndex

def pf_index(grid: Grid, grid_params: GridParams) -> PFIndex:
    """Ordered buses and mappings to admittances and slack factors."""
    
    pv_idx = pv_buses(grid, grid_params)
    pq_idx = pq_buses(grid, grid_params)
    s_idx = slack_factors(grid, grid_params)
    y_idx = admittances(grid, grid_params)
    
    return PFIndex(pv_idx, pq_idx, s_idx, y_idx)

def slack_factors(grid: Grid, grid_params: GridParams) -> SIndex:
    """Mapping from buses to sums of slack participation factors."""
    
    bs: dict[N, float]
    bs = {b: 0. for b in unique(grid.gn_list.values())}
    
    r = lambda bs, b: bs | {b[0]: bs[b[1]] + grid_params.s_list[b[0]]}
    return reduce(r, grid.gn_list.items(), bs)

def admittances(grid: Grid, grid_params: GridParams) -> YIndex:
    """Mapping from connections to sums of parallel admittances."""
    
    pu_y_list = {c: y*grid_params.p_base/(grid_params.v_list[c]**2)
                 for c, y in grid_params.y_list.items()}
    
    bps: dict[frozenset[N], float]
    bps = {bp: 0. for bp in unique(grid.cn_list.values())}
    
    r = lambda bps, bp: bps | {bp[0]: bps[bp[1]] + pu_y_list[bp[0]]}
    return reduce(r, grid.cn_list.items(), bps)

def pv_buses(grid: Grid, grid_params: GridParams) -> BIndex:
    """Tuple of buses with at least one generator."""
    
    return tuple(unique(grid.gn_list.values()))

def pq_buses(grid: Grid, grid_params: GridParams) -> BIndex:
    """Tuple of buses without any generator."""
    
    return tuple(unique(chain.from_iterable(grid.cn_list.values()),
                        exclude=set(grid.gn_list.values())))

def apply_topology(grid: Grid, topo: Topology) -> Grid:
    """Apply topology to a grid, redefining nodes and removing edges."""
    
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