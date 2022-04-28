class TopologyDAG:
    """Directed acyclic graph of possible topologies.
    
    Combination of a coordinate system and a map of coordinates 
    to topology data.
    """
    
    # Subclass Dict / UserDict / another type of map?
    
    def __init__(self, coord_sys):
        
        self.coord_sys = coord_sys
        self.map = {}
        
class CoordinateSystem:
    
    # Logic for defining moves on the topology DAG
    
    pass
    
class Topology:
    """Topology object that stores topology coordinates and data."""
    
    # Subclass Dict / UserDict / another type of map?
    
    def __init__(self, coords):
        
        self.map = {'coords': coords}
