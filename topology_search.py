import pandas as pd
import pandapower as pp
import networkx as nx

class FlexibleGrid():
    def __init__(self, pp_net,
                 connected_subnet='all',
                 splittable_nodes='all',
                 switchable_edges='all'):
        
        # To do: subclass pandapower net?
        # To do: check if 'None' case does not break anything
        # To do: ensure that flexible nodes/edges are subset of connected
        # To do: import doubled buses into networkx object?
        
        # Copy pandapower network
        self.pp_net = pp_net.deepcopy()
        
        # If connected_subnet passed, store node indices in list
        if connected_subnet is not None:
            if connected_subnet == 'all':
                connected_subnet = self.pp_net.bus.index
            self.connected_subnet = list(connected_subnet)
        
        # If splittable nodes passed, generate new buses accordingly
        if splittable_nodes is not None:
            if splittable_nodes == 'all':
                splittable_nodes = self.pp_net.bus.index
            
            # Copy buses and add letter designation to new buses
            aux_buses = self.pp_net.bus.loc[splittable_nodes, :].copy()
            aux_buses['name'] += '_b'
            
            # Add letter designation to old buses that were copied
            self.pp_net.bus.loc[splittable_nodes, 'name'] += '_a'
            
            # Keep track of original and new buses
            self.pp_net.bus['is_aux_bus'] = False
            self.pp_net.bus['original_bus'] = self.pp_net.bus.index
            aux_buses['is_aux_bus'] = True
            aux_buses['original_bus'] = aux_buses.index

            # Change index of new buses to ensure unique indices
            aux_buses.index += (max(self.pp_net.bus.index) + 1)
            
            # Set new buses to out of service
            aux_buses['in_service'] = False
            
            # Create mapping from old buses to new buses
            self.splittable_nodes = list(zip(aux_buses['original_bus'], 
                                             aux_buses.index))
            
            # Append new bus table to existing bus table
            self.pp_net.bus = self.pp_net.bus.append(aux_buses)
            
        # If switchable edges passed, store indices in list
        if switchable_edges is not None:
            if switchable_edges == 'all':
                switchable_edges = self.pp_net.line.index
            self.switchable_edges = list(switchable_edges)
            
        # Generate main topology object for pandapower network
        self.main_topology = topology_from_pp(self.pp_net)
        self.main_topology.splittable_nodes = self.splittable_nodes
        self.main_topology.switchable_edges = self.switchable_edges
            
class Topology(nx.Graph):
    def __init__(self, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        
        self._splittable_nodes = []
        self._switchable_edges = []
    
    @property
    def splittable_nodes(self):
        
        return self._splittable_nodes
    
    @splittable_nodes.setter
    def splittable_nodes(self, value):
        
        self._splittable_nodes = value[:]
    
    @property
    def switchable_edges(self):
        
        return self._switchable_edges
    
    @switchable_edges.setter
    def switchable_edges(self, value):
        
        self._switchable_edges = value[:]
        
    def copy(self, *args, **kwargs):
        T = super(Topology, self).copy(*args, **kwargs)
        
        # Copy splittable_nodes and switchable edges
        T.splittable_nodes = self.splittable_nodes
        T.switchable_edges = self.switchable_edges
        
        return T
        
def topology_from_pp(pp_net):
    
    # Extract nodes from bus table
    bus_list = list(pp_net.bus[pp_net.bus['is_aux_bus']==False].index)
    
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

