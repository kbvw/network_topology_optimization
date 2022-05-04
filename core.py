from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Callable, TypeVar
from dataclasses import dataclass
from operator import sub
from itertools import chain

# Becomes unnecessary with PEP 673:
# -> replace 'TDAGCoords' and 'TTopoCoords' with 'Self' as of Python 3.11
TDAGCoords = TypeVar('TDAGCoords', bound='DAGCoords')
TTopoCoords = TypeVar('TTopoCoords', bound='TopoCoords')

class DAGCoords(ABC):
    """Base class for implicit definition of a directed acyclic graph."""
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Return True if self is equal to other."""
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return integer hash value of self."""
    
    @abstractmethod
    def children(self: TDAGCoords) -> Iterable[TDAGCoords]:
        """Return iterable containing children."""
    
    @abstractmethod
    def parents(self: TDAGCoords) -> Iterable[TDAGCoords]:
        """Return iterable containing parents."""
    
    def ischild(self: TDAGCoords, other: TDAGCoords) -> bool:
        """Return True if self is a child of other."""
        parents: Iterable[TDAGCoords] = self.parents()
        return any(parent == other for parent in parents)
    
    def isparent(self: TDAGCoords, other: TDAGCoords) -> bool:
        """Return True if self is a parent of other."""
        children: Iterable[TDAGCoords] = self.children()
        return any(child == other for child in children)
    
@dataclass(frozen=True, slots=True)
class FrozenCoordsMixin:
    """Mixin class for immutable and space-efficient coordinate types."""
    coords: tuple[frozenset]
    
class TopoCoords(FrozenCoordsMixin, DAGCoords, ABC):
    """Base coordinates for possible alterations to a graph topology."""
    
    @classmethod
    @property
    @abstractmethod
    def space(cls) -> tuple[frozenset]:
        """The full space of possible changes to the root topology."""
    
    def children(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing children."""
        raise NotImplementedError
    
    def parents(self: TTopoCoords) -> Iterable[TTopoCoords]:
        """Return iterable containing parents."""
        raise NotImplementedError

T = TypeVar('T')
def dimension_map(xs, ys) -> Callable[[T], frozenset[T]]:
    pass

def children(coords):
    return coords.children()

def parents(coords):
    return coords.parents()