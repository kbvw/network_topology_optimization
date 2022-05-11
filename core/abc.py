from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TypeVar

from itertools import chain

# Becomes unnecessary with PEP 673 as of Python 3.11:
# -> replace 'TGCoords', 'TDGCoords, 'TDAGCoords', 'TTreeCoords' with 'Self'
TGCoords = TypeVar('TGCoords', bound='GCoords')
TDGCoords = TypeVar('TDGCoords', bound='DGCoords')
TDAGCoords = TypeVar('TDAGCoords', bound='DAGCoords')
TTreeCoords = TypeVar('TTreeCoords', bound='TreeCoords')

# Base coordinate classes to implement for using the library functions

class GCoords(ABC):
    """Base class for implicit definition of a graph."""
    
    __slots__ = ()
    
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Return True if self is equal to other."""
        
        raise NotImplementedError
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return integer hash value of self."""
        
        raise NotImplementedError
    
    @abstractmethod
    def adjacent(self: TGCoords) -> Iterable[TGCoords]:
        """Return iterable containing adjacent coordinates."""
        
        raise NotImplementedError
    
    def is_adjacent(self: TGCoords, other: TGCoords) -> bool:
        """Return True if self is a parent of other."""
        
        adjacent: Iterable[TGCoords] = self.adjacent()
        return any(coords == other for coords in adjacent)

class DGCoords(GCoords, ABC):
    """Base class for implicit definition of a directed graph."""
    
    __slots__ = ()
    
    @abstractmethod
    def children(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing children."""
        
        raise NotImplementedError
    
    @abstractmethod
    def parents(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing parents."""
        
        raise NotImplementedError
    
    def adjacent(self: TDGCoords) -> Iterable[TDGCoords]:
        """Return iterable containing adjacent coordinates."""
        
        return chain(self.children(), self.parents())
    
    def is_child(self: TDGCoords, other: TDGCoords) -> bool:
        """Return True if self is a child of other."""
        
        parents: Iterable[TDGCoords] = self.parents()
        return any(coords == other for coords in parents)
    
    def is_parent(self: TDGCoords, other: TDGCoords) -> bool:
        """Return True if self is a parent of other."""
        
        children: Iterable[TDGCoords] = self.children()
        return any(coords == other for coords in children)

class DAGCoords(DGCoords, ABC):
    """Base class for implicit definition of a directed acyclic graph."""
    
    __slots__ = ()

class TreeCoords(DAGCoords, ABC):
    """Base class for implicit definition of a tree graph."""
    
    __slots__ = ()