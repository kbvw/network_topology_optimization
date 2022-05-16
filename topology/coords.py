from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Hashable, Set
from typing import TypeVar, Type

from itertools import product, chain, repeat
from functools import reduce

from ..core.itertools import chainmap
from .abc import TopoData
from ..core.collections import NamedFrozenSet, NamedFrozenDict

# Type aliases

E = Hashable
N = Hashable
Split = tuple[frozenset[E], ...] | frozenset[frozenset[E]]
NSplit = tuple[N, Split]

class ECoord(NamedFrozenSet[E]):
    """Elements that are switched."""
    
    __slots__ = ()

class NCoord(NamedFrozenDict[N, NSplit]):
    """Nodes that are split."""
    
    __slots__ = ()

class ESpace(NamedFrozenSet[E]):
    """Space of all possible element switches."""
    
    __slots__ = ()

class NSpace(NamedFrozenDict[N, frozenset[NSplit]]):
    """Space of all possible node splits."""
    
    __slots__ = ()

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TTopo' with 'Self'
Topo = TypeVar('Topo', bound='Topology')

class Topology(TopoData[ECoord, NCoord], ABC):
    """Base class for all topology object mixins."""
    
    __slots__ = ()
    
    @property
    @abstractmethod
    def e_space(self) -> ESpace:
        """The space of possible edge changes to the topology."""
        
        raise NotImplementedError
    
    @property
    @abstractmethod
    def n_space(self) -> NSpace:
        """The space of possible node changes to the topology."""
        
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def factory(cls: Type[Topo], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[Topo]:
        """Return iterable with cartesian product of coordinates."""
        
        raise NotImplementedError

# Direct subclass of tuple for better performance over many instances

class TopoTuple(tuple[ECoord, NCoord], Topology):
    """Immutable implementation of topology alteration coordinates."""
    
    __slots__ = ()
    
    @property
    def e_coord(self) -> ECoord:
        """The set of edge changes to the topology."""
        
        return self[0]
    
    @property
    def n_coord(self) -> NCoord:
        """The set of node changes to the topology."""
        
        return self[1]
    
    @classmethod
    def factory(cls: Type[Topo], 
                e_coords: Iterable[ECoord], 
                n_coords: Iterable[NCoord]) -> Iterator[Topo]:
        """Return iterable with cartesian product of coordinates."""
        
        return map(cls, product(e_coords, n_coords))
    
    def __repr__(self) -> str:
        
        name = type(self).__name__
        
        return f'{name}({super().__repr__()})'

class ECSimple(Topology):
    
    __slots__ = ()
    
    def e_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the edge dimension."""
        
        unswitched = (e for e in self.e_space if e not in self.e_coord)
        
        e_coords = (ECoord(self.e_coord | {switch})
                    for switch in unswitched)
        
        return self.factory(e_coords, [self.n_coord])

class EPSimple(Topology):
    
    __slots__ = ()
    
    def e_parents(self: Topo) -> Iterator[Topo]:
        """Return iterable containing parents in the edge dimension."""
        
        e_coords = (ECoord(e for e in self.e_coord if not e == switch)
                    for switch in self.e_coord)
        
        return self.factory(e_coords, [self.n_coord])

class NCSimple(Topology):
    
    __slots__ = ()
    
    def n_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the node dimension."""
        
        unsplit = (n for n in self.n_space if n not in self.n_coord)
        splits = chain(split for n in unsplit 
                       for split in self.n_space[n])
        
        n_coords = (NCoord(self.n_coord | {split[0]: split}) 
                    for split in splits)
        
        return self.factory([self.e_coord], n_coords)

class ECCoupled(Topology):
    
    __slots__ = ()
    
    def e_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the edge dimension."""
        
        unswitched = (e for e in self.e_space if e not in self.e_coord)
        
        e_coords = (ECoord(self.e_coord | {switch})
                    for switch in unswitched)
        
        en = ((e, n_filter(self.n_coord, e)) for e in e_coords)
        f = lambda en: self.factory([en[0]], [en[1]])
        
        return chainmap(f, en)

class EPCoupled(Topology):
    
    __slots__ = ()
    
    def e_parents(self: Topo) -> Iterator[Topo]:
        """Return iterable containing parents in the edge dimension."""
        
        en_coords = ((ECoord(e for e in self.e_coord if not e == switch),
                      n_branch(self.n_coord, self.n_space, switch))
                     for switch in self.e_coord)
        
        en = (zip(repeat(cs[0]), cs[1]) for cs in en_coords)
        
        f = lambda en: self.factory([en[0]], [en[1]])
        
        return chainmap(f, en)

class NCCoupled(Topology):
    
    __slots__ = ()
    
    def n_children(self: Topo) -> Iterator[Topo]:
        """Return iterable containing children in the node dimension."""
        
        unsplit = (n for n in self.n_space if n not in self.n_coord)
        splits = chain(split_filter(split, self.e_coord) for n in unsplit 
                       for split in self.n_space[n])
        
        n_coords = (NCoord(self.n_coord | {split[0]: split}) 
                    for split in splits)
        
        return self.factory([self.e_coord], n_coords)

class NP(Topology):
    
    __slots__ = ()
    
    def n_parents(self: Topo) -> Iterator[Topo]:
        """Return iterable containing parents in the node dimension."""
        
        n_coords = (NCoord((n, self.n_coord[n]) 
                           for n in self.n_coord 
                           if not n == split)
                    for split in self.n_coord)
        
        return self.factory([self.e_coord], n_coords)

def split_filter(split: NSplit, switches: Set[E]) -> NSplit:
    """Remove switched elements from node split."""
    
    n, ess = split
    filtered = type(ess)(frozenset(e for e in es if not e in switches)
                         for es in ess)
    return (n, filtered)

def n_filter(n_coord: NCoord, es: Set[E]) -> NCoord:
    """Remove switched elements from node N-coordinate."""
    
    return NCoord({n: split_filter(s, es) for n, s in n_coord.items()})

def n_branch(n_coord: NCoord, n_space: NSpace, e: E) -> Iterable[NCoord]:
    """Enumerate possible N-coordinates with switch added back."""
    
    union = lambda x, y: x | y
    return (NCoord({n: split}) for n in n_coord for split in n_space[n]
            if e in reduce(union, split[1]))

