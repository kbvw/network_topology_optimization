import pandas as pd
import pandapower as pp
import networkx as nx

class FlexibleGrid():
    def __init__(self, pp_net, 
                 connected_subgrid=None,
                 flexible_nodes=None,
                 flexible_edges=None):
        pass
        
class Topology(nx.Graph):
    def __init__(self, pp_net):
        pass
        

def split_flexible_nodes(pp_net, flexible_nodes):
    
    # Add split busses in main tables with index 'a', 'b'
    pass
        
        
def topology_from_pp(pp_net):
    
    # Extract nodes from bus table
    nodes_list = list(pp_net.bus.index)
    
    # Extract edges from line table, with line index stored as edge attribute
    edges_list = list(zip(pp_net.line['from_bus'], 
                          pp_net.line['to_bus'],
                          [{'line':idx} for idx in pp_net.line.index]))
    
    # Build the graph
    topology = nx.Graph()
    topology.add_nodes_from(nodes_list)
    topology.add_edges_from(edges_list)
    
    return topology

def apply_topology(pp_net, topology):
    
    # Switches lines in pandapower net object, without making a copy
    
    # Set all buses and lines to out of service
    pp_net.bus['in_service'] = False
    pp_net.line['in_service'] = False
    
    # Extract bus index by iterating over nodes in topology
    for idx in topology.nodes:
        
        # Set buses from topology to in service
        pp_net.bus['in_service'][idx] = True
    
    # Extract line index while iterating over edges in topology
    for (from_bus, to_bus, idx) in topology.edges.data('line'):
        
        # Set lines from topology to in service
        pp_net.line['in_service'][idx] = True
        
        # Set lines from topology to in 
        pp_net.line['from_bus'][idx] = from_bus
        pp_net.line['to_bus'][idx] = to_bus
        
    return pp_net

def check_min_degree(topology, min_degree):
    pass

def check_k_edge_connectivity(topology, k):
    pass

def bus_split(input_topology):
            
    output_topologies = []
    
    return output_topologies

def line_cut(input_topology):
    
    output_topologies = []
    
    return output_topologies

