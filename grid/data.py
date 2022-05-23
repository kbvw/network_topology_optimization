from collections.abc import Hashable

from typing import NamedTuple
from itertools import chain
from functools import reduce

from ..core.itertools import unique

from ..topology.coords import Topology

N = Hashable
C = Hashable
L = Hashable
G = Hashable
B = Hashable

class Grid(NamedTuple):
    cn_list: dict[C, frozenset[N]]
    y_list: dict[C, complex]
    ln_list: dict[L, N]
    gn_list: dict[G, N]
    slack_list: dict[G, float]

class BusSplit(NamedTuple):
    cb_list: dict[C, frozenset[B]]
    lb_list: dict[L, B]
    gb_list: dict[G, B]

BIndex = tuple[B, ...]
SIndex = dict[B, float]
YIndex = dict[frozenset[B], float]

class GridIndex(NamedTuple):
    pv_idx: tuple[B, ...]
    pq_idx: tuple[B, ...]
    s_idx: dict[B, float]
    y_idx: dict[frozenset[B], float]

def slack_factors(grid: Grid, bus_split: BusSplit) -> SIndex:
    
    bs: dict[B, float]
    bs = {b: 0. for b in unique(bus_split.gb_list.values())}
    
    r = lambda bs, b: bs | {bs[b[0]] + grid.slack_list[b[1]]}
    return reduce(r, bus_split.gb_list.items(), bs)

def admittance(grid: Grid, bus_split: BusSplit) -> YIndex:
    
    bps: dict[frozenset[B], float]
    bps = {bp: 0. for bp in unique(bus_split.cb_list.values())}
    
    r = lambda bps, bp: bps | {bps[bp[0]] + grid.y_list[bp[1]]}
    return reduce(r, bus_split.cb_list.items(), bps)

def bus_types(grid: Grid, bus_split: BusSplit) -> tuple[BIndex, BIndex]:
    
    pv_idx = tuple(unique(n for n in bus_split.gb_list))
    pq_idx = tuple(unique(n for n in bus_split.lb_list))
    
    return (pv_idx, pq_idx)

def bus_split(grid: Grid, topo: Topology) -> BusSplit:
    
    splits = {(n, i): [e for e in es if not e in topo.e_coord]
              for n in topo.n_coord
              for i, es in enumerate(topo.n_coord[n][1])}
    
    l_splits = {e: b for b, es in splits.items()
                for e in es if e in grid.ln_list}
    g_splits = {e: b for b, es in splits.items()
                for e in es if e in grid.gn_list}
    
    bs = lambda e: ({b for b in splits if e in splits[b]}
                    | {b for b in grid.cn_list[e] if not b in topo.n_coord})
    c_splits = {e: frozenset(bs(e)) 
                for e in chain.from_iterable(splits.values())
                if e in grid.cn_list}
    
    return BusSplit(cb_list = grid.cn_list | c_splits,
                    lb_list = grid.ln_list | l_splits,
                    gb_list = grid.gn_list | g_splits)