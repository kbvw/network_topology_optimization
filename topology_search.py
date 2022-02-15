import pandas as pd
import pandapower as pp
import networkx as nx

class FlexibleGrid():
    def __init__(self, pp_net, 
                 connected_subnet='all',
                 splittable_nodes='all',
                 switchable_edges='all'):
        
        # To do: subclass pandapower net?
        
        # Copy pandapower network
        self.net = pp_net.deepcopy()
        
        # If splittable nodes passed, generate new buses accordingly
        if splittable_nodes is not None:
            if splittable_nodes == 'all':
                splittable_nodes = self.net.bus.index
            
            # Copy buses and add letter designation to new buses
            aux_buses = self.net.bus.loc[splittable_nodes, :].copy()
            aux_buses['name'] += '_b'
            
            # Add letter designation to old buses that were copied
            self.net.bus.loc[splittable_nodes, 'name'] += '_a'
            
            # Store old index of new buses to create mapping
            old_idx = aux_buses.index.copy()

            # Change index of new buses to ensure unique indices
            aux_buses.index += (max(self.net.bus.index) + 1)
            
            # Create mapping from old buses to new buses
            self.splittable_nodes = list(zip(old_idx, aux_buses.index))
            
            # Append new bus table to existing bus table
            self.net.bus = self.net.bus.append(aux_buses)
            
class Topology(nx.Graph):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        
        self._splittable_nodes = []
        self._switchable_edges = []
    
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
    
    # To do:
    # - Should be applied to connected subnet only
    # - Clean up chained assignment in pandas
    
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

