import pandas as pd
import pandapower as pp

from .topology_search import Topology, topology_generator

class FlexibleNet(pp.auxiliary.pandapowerNet):
    @classmethod
    def from_pp_net(cls, pp_net,
                    connected_subnet='all',
                    splittable_nodes='all',
                    switchable_edges='all'):
        
        # To do: 
        # - Subclass pandapower net?
        # - Check if 'None' case does not break anything
        # - Ensure that flexible nodes/edges are subset of connected
        # - Import doubled buses into networkx object?
        # - Update bus geodata table for plotting
        
        # Construct instance as copy of Pandapower network
        net = pp_net.deepcopy()
        net._setattr('__class__', cls)
        
        # If connected_subnet passed, store node indices in list
        if connected_subnet is not None:
            if connected_subnet == 'all':
                connected_subnet = net.bus.index
            net.connected_subnet = list(connected_subnet)
        
        # If splittable nodes passed, generate new buses accordingly
        if splittable_nodes is not None:
            if splittable_nodes == 'all':
                splittable_nodes = net.bus.index
            
            # Copy buses and add letter designation to new buses
            aux_buses = net.bus.loc[splittable_nodes, :].copy()
            aux_buses['name'] += '_b'
            
            # Add letter designation to old buses that were copied
            net.bus.loc[splittable_nodes, 'name'] += '_a'
            
            # Keep track of original and new buses
            net.bus['is_aux_bus'] = False
            net.bus['original_bus'] = net.bus.index
            aux_buses['is_aux_bus'] = True
            aux_buses['original_bus'] = aux_buses.index

            # Change index of new buses to ensure unique indices
            aux_buses.index += (max(net.bus.index) + 1)
            
            # Set new buses to out of service
            aux_buses['in_service'] = False
            
            # Create mapping from old buses to new buses
            net.splittable_nodes = dict(zip(aux_buses['original_bus'], 
                                            aux_buses.index))
            
            # Append new bus table to existing bus table
            net.bus = pd.concat([net.bus, aux_buses])
            
            # Add coordinates for the new bus
            if hasattr(net, 'bus_geodata'):
                og_index = aux_buses['original_bus']
                aux_buses_geodata = net.bus_geodata.loc[og_index]
                aux_buses_geodata.index = aux_buses.index
                net.bus_geodata = pd.concat([net.bus_geodata, 
                                             aux_buses_geodata])
                  
        # If switchable edges passed, store tuples with line endpoints
        if switchable_edges is not None:
            if switchable_edges == 'all':
                switchable_edges = net.line.index
            switchable_edges = net.line.loc[switchable_edges]
            edge_zip = zip(switchable_edges['from_bus'],
                           switchable_edges['to_bus'])
            edge_set_list = [frozenset(edge) for edge in edge_zip]
            net.switchable_edges = dict(zip(edge_set_list,
                                            switchable_edges.index))
            
        # Generate main topology object for pandapower network
        net.main_topology = topology_from_pp(net, net.connected_subnet)
        net.main_topology.splittable_nodes = net.splittable_nodes
        net.main_topology.switchable_edges = net.switchable_edges
        
        return net
              
    def topology_search(self, k=2, node_split=True, edge_switch=True):
        
        self.topology_list = topology_generator([self.main_topology], k,
                                                node_split, edge_switch)
        
        return len(self.topology_list)
    
    def reset_topology(self):
        apply_topology(self, 
                       self.splittable_nodes, self.switchable_edges, 
                       self.main_topology)
        
    def apply_topology(self, topology):
        apply_topology(self, 
                       self.splittable_nodes, self.switchable_edges, 
                       topology)
        
    def run_all_pf(self):
        
        self.all_res_line = {}
        
        for topology in self.topology_list:
            self.apply_topology(topology)
            pp.runpp(self)
            self.all_res_line[topology] = self.res_line
            
    def plot_pf_res(self, topology, plot_function):
        
        if topology == 'main':
            topology = self.main_topology
        
        apply_topology(self, 
                       self.splittable_nodes, self.switchable_edges, 
                       topology)
        pp.runpp(self)
        
        plot_function(self)
        
def topology_from_pp(pp_net, connected_subnet):
    
    # Extract nodes from bus table, keeping non-auxiliary buses
    bus_list = list(pp_net.bus[pp_net.bus['is_aux_bus']==False].index)
    
    # Extract edges from line table, with line index stored as edge attribute
    line_list = list(zip(pp_net.line['from_bus'], 
                         pp_net.line['to_bus'],
                         [{'line':idx} for idx in pp_net.line.index]))
    
    # Extract attributes from load and generator tables
    load_list = list(zip(pp_net.load['bus'], pp_net.load.index))
    gen_list = list(zip(pp_net.gen['bus'], pp_net.gen.index))
    
    # Keep only elements in connected subnet
    bus_list = [bus for bus in bus_list if bus in connected_subnet]
    line_list = [line for line in line_list if (line[0] in bus_list 
                                                and line[1] in bus_list)]
    load_list = [line for line in load_list if line[0] in bus_list]
    gen_list = [gen for gen in gen_list if gen[0] in bus_list]
    
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

def apply_topology(pp_net, 
                   splittable_nodes, 
                   switchable_edges,
                   topology):
    
    # Switches lines in pandapower net object, without making a copy
    
    # Create masks for acting on relevant nodes and edges
    original_buses, aux_buses = zip(*splittable_nodes.items())
    switchable_lines = list(switchable_edges.values())
       
    # Set all buses and lines to out of service
    pp_net.bus.loc[original_buses, 'in_service'] = False
    pp_net.bus.loc[aux_buses, 'in_service'] = False
    pp_net.line.loc[switchable_lines, 'in_service'] = False
    
    # Extract bus index and bus elements by iterating over nodes in topology
    for bus, elements in topology.nodes.data():
        
        # Set buses from topology to in service
        pp_net.bus.loc[bus, 'in_service'] = True
        
        # Set loads from topology to corresponding bus
        if 'load' in elements:
            pp_net.load.loc[elements['load'], 'bus'] = bus
            
        # Set generators from topology to corresponding bus
        if 'gen' in elements:
            pp_net.gen.loc[elements['gen'], 'bus'] = bus
    
    # Extract line index while iterating over edges in topology
    for from_bus, to_bus, line in topology.edges.data('line'):
        
        # Set lines from topology to in service
        pp_net.line.loc[line, 'in_service'] = True
        
        # Set lines from topology to corresponding bus
        pp_net.line.loc[line, 'from_bus'] = from_bus
        pp_net.line.loc[line, 'to_bus'] = to_bus
        
    return pp_net
