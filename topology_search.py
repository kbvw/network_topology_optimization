import networkx as nx
from networkx.algorithms.connectivity import is_locally_k_edge_connected
import math
from itertools import combinations
       
class Topology(nx.Graph):
    def __init__(self, *args, **kwargs):
        self.splittable_nodes = kwargs.pop('splittable_nodes', {})
        self.switchable_edges = kwargs.pop('switchable_edges', {})
        self.number_of_removed_edges = 0
        super(Topology, self).__init__(*args, **kwargs)
        
    def copy(self, *args, **kwargs):
        T = super(Topology, self).copy(*args, **kwargs)
        
        # Shallow copy of splittable nodes and switchable edges
        T.splittable_nodes = self.splittable_nodes.copy()
        T.switchable_edges = self.switchable_edges.copy()
        
        T.number_of_removed_edges = self.number_of_removed_edges
        
        return T

def check_node_min_degree(topology, node, min_degree):
    pass

def check_edge_min_degree(topology, edge, min_degree):
    pass

def check_k_edge_connectivity(topology, edge, k):
    if is_locally_k_edge_connected(topology, edge[0], edge[1], k):
        return True
    else:
        return False
    
def topology_generator(full_topology_list, k=2,
                       node_split=True, edge_switch=True):
    
    # Copy full topology objects to leave the original unchanged
    input_topology_list = [t.copy() for t in full_topology_list]
    
    # Node split recursion for every input topology
    if node_split:
        output_topology_list = []
        for topology in input_topology_list:
            output_topology_list.extend(node_split_recursor(topology, k))
            
        # Set resulting topologies as new input toplogies
        input_topology_list = output_topology_list[:]
       
    # Edge switch recursion for every input topology
    if edge_switch:
        output_topology_list = []
        for topology in input_topology_list:
            output_topology_list.extend(edge_switch_recursor(topology, k))
        
    return output_topology_list

def node_split_recursor(input_topology, k=2):
    
    # Check if splittable nodes remain
    if input_topology.splittable_nodes:
            
        # Remove node pair from dictionary of splittable nodes
        node_pair = input_topology.splittable_nodes.popitem()
        
        # Check degree
        
        # Execute node split
        new_topology_list = node_split(input_topology, node_pair, k)
        
        # Recursion for new topologies including input topology
        recursion_list = [input_topology, *new_topology_list]
        output_topology_list = []
        for topology in recursion_list:
            output_topology_list.extend(node_split_recursor(topology, k))
            
        return output_topology_list
             
    else:
        return [input_topology]

def edge_switch_recursor(input_topology, k=2):
    
    # Check if switchable edges remain
    if input_topology.switchable_edges:
        
        # Remove edge from dictionary of switchable edges
        edge = tuple(input_topology.switchable_edges.popitem()[0])
        
        # Check degree
        
        # Execute edge switch
        new_topology_list = edge_switch(input_topology, edge, k)
        
        # Recursion for new topologies including input topology
        recursion_list = [input_topology, *new_topology_list]
        output_topology_list = []
        for topology in recursion_list:
            output_topology_list.extend(edge_switch_recursor(topology, k))
            
        return output_topology_list
             
    else:
        return [input_topology]

def node_split(topology, node_pair, k=2):
    
    # To do:
    # - Unnecessary check of degree?
    # - Check k-edge-connectedness before copying?
    
    new_topology_list = []
    
    # Obtain degree and neighboring edges
    deg = topology.degree[node_pair[0]]
    neighbors = list(topology.adj[node_pair[0]])
    edges = [(node_pair[0], n) for n in neighbors]
    
    # Check if degree is high enough for bus split
    if deg >= 2*k:
        
        max_uneven_split = math.ceil(deg/2)
        splits = list(range(k, max_uneven_split))
        
        # Iterate over total number of edges to be moved to other node
        for split in splits:
            new_topology_list = []

            # Obtain all combinations for this number of edges
            combs = combinations(edges, split)
                
            # Create new topology for each combination
            for comb in combs:
                new_topology = topology.copy()
                apply_split(new_topology, comb, node_pair)
                
                # Check k-edge connectivity
                if check_k_edge_connectivity(new_topology, 
                                             node_pair, k):
        
                    # If check passed, keep topology
                    new_topology_list.append(new_topology)
                    
                    # Create subsplits for node element combinations
                    if new_topology.nodes[node_pair[0]]:
                        sub_list = generate_subsplits(new_topology,
                                                      node_pair)
                        new_topology_list.extend(sub_list)
            
        # If degree is even, compute unique half splits
        if (deg%2 == 0):
            half_split = int(deg/2) - 1
            
            # Take arbitrary first edge
            first_edge = edges.pop()
            combs = combinations(edges, half_split)
            
            # Create new topology for each combination
            for comb in combs:
                new_topology = topology.copy()
                
                # Include first edge
                full_comb = (first_edge, *comb)
                apply_split(new_topology, full_comb, node_pair)
                
                # Check k-edge connectivity
                if check_k_edge_connectivity(new_topology, 
                                             node_pair, k):
        
                    # If check passed, keep topology
                    new_topology_list.append(new_topology)
                    
                    # Create subsplits for node element combinations
                    if new_topology.nodes[node_pair[0]]:
                        sub_list = generate_subsplits(new_topology,
                                                      node_pair)
                        new_topology_list.extend(sub_list)
                       
    return new_topology_list

def edge_switch(topology, edge, k=2):
    
    # To do:
    # - Max depth?
    # - Check k-edge-connectedness before copying?
    
    new_topology_list = []
        
    # Create copy of topology object and remove edge
    new_topology = topology.copy()
    new_topology.remove_edge(*edge)
    
    # Check k-edge connectivity
    if check_k_edge_connectivity(new_topology, edge, k):
        
        # If check passed, keep topology
        new_topology_list.append(new_topology)
    
    return new_topology_list

def apply_split(topology, combination, node_pair):
    
    # Applies node split without copying topology

    # Switch every edge in combination to alternative node
    for edge in combination:
        
        # Keep track of old edge attributes
        attributes = topology.edges[edge]
        
        # Remove old edge
        topology.remove_edge(*edge)
        
        # Add new edge
        new_edge = (node_pair[1], edge[1])
        topology.add_edge(*new_edge, **attributes)
        
        # Change edge in dictionary of switchable edges
        if frozenset(edge) in topology.switchable_edges:
            attribute = topology.switchable_edges.pop(frozenset(edge))
            topology.switchable_edges[frozenset(new_edge)] = attribute
            
def generate_subsplits(topology, node_pair):
    
    # Generates subsplits without affecting input topology object
    
    # Extract node elements
    elements = topology.nodes[node_pair[0]]
    elements = list(elements.items())
    
    sub_comb_list = []
    
    # Generate combinations of distributing elements over node pair
    for n in range(len(elements)):
        sub_combs = list(combinations(elements, n+1))
        sub_comb_list.extend(sub_combs)
        
    sub_topology_list = []
    
    # Generate sub topology for each combination
    for sub_comb in sub_comb_list:
        sub_topology = topology.copy()
        for element in sub_comb:
            sub_topology.nodes[node_pair[0]].pop(element[0])
            sub_topology.nodes[node_pair[1]][element[0]] = element[1]
        sub_topology_list.append(sub_topology)
        
    return sub_topology_list