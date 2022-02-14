import pandas as pd
import pandapower as pp
import networkx as nx

class FlexibleGrid():
    def __init__(self, pp_net, 
                 connected_subnet=None,
                 splittable_nodes=None,
                 switchable_edges=None):
        pass
        
class Topology(nx.Graph):
    
    @property
    def splittable_nodes(self):
        
        return self._splittable_nodes
    
    @splittable_nodes.setter
    def splittable_nodes(self, value):
        
        self._splittable_nodes = value
    
    @property
    def switchable_edges(self):
        
        return self._switchable_edges
    
    @switchable_edges.setter
    def switchable_edges(self, value):
        
        self.switchable_edges = value
        
def split_flexible_nodes(pp_net, flexible_nodes):
    
    # Add split busses in main tables with index 'a', 'b'
    pass
        
def topology_from_pp(pp_net):
    
    # Extract nodes from bus table
    bus_list = list(pp_net.bus.index)
    
    # Extract edges from line table, with line index stored as edge attribute
    line_list = list(zip(pp_net.line['from_bus'], 
                          pp_net.line['to_bus'],
                          [{'line':idx} for idx in pp_net.line.index]))
    
    # Extract attributes from load and generator tables
    load_list = list(zip(pp_net.load['bus'], pp_net.load.index))
    gen_list = list(zip(pp_net.gen['bus'], pp_net.gen.index))
    
    # Build the graph
    topology = Topology()
    topology.add_nodes_from(bus_list)
    topology.add_edges_from(line_list)
    
    # Add node attributes
    for bus, load in load_list:
        topology.nodes[bus]['load'] = load  
    for bus, gen, in gen_list:
        topology.nodes[bus]['gen'] = gen
    
    return topology

def apply_topology(pp_net, topology):
    
    # Switches lines in pandapower net object, without making a copy
    
    # Should be applied to connected subnet only
    # Set all buses and lines to out of service
    pp_net.bus['in_service'] = False
    pp_net.line['in_service'] = False
    
    # Extract bus index and bus elements by iterating over nodes in topology
    for bus, elements in topology.nodes.data():
        
        # Set buses from topology to in service
        pp_net.bus['in_service'][bus] = True
        
        # Set loads from topology to corresponding bus
        if 'load' in elements:
            pp_net.load['bus'][elements['load']] = bus
            
        # Set generators from topology to corresponding bus
        if 'gen' in elements:
            pp_net.gen['bus'][elements['gen']] = bus
    
    # Extract line index while iterating over edges in topology
    for from_bus, to_bus, line in topology.edges.data('line'):
        
        # Set lines from topology to in service
        pp_net.line['in_service'][line] = True
        
        # Set lines from topology to corresponding bus
        pp_net.line['from_bus'][line] = from_bus
        pp_net.line['to_bus'][line] = to_bus    
        
    return pp_net

def check_min_degree(topology, min_degree):
    pass

def check_k_edge_connectivity(topology, k):
    pass

def node_split(topology_list):
    
    for topology in topology_list:
        
        # Choose splittable node and remove from list of splittable nodes
        
        new_topology_list = []
        
        # Make copies of topology for each node configuration
        
        # Check k-edge connectivity and delete disconnecting topologies
                       
        topology_list.extend(new_topology_list)
    
    return topology_list

def edge_switch(topology_list):
    
    for topology in topology_list:
        
        # Choose switchable line and remove from list of splittable nodes
        
        new_topology_list = []
        
        # Make copies of topology for each line configuration 
        
        # Check k-edge connectivity and delete disconnecting topologies
                       
        topology_list.extend(new_topology_list)
    
    return output_topologies

