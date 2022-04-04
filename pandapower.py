from .topology_search import Topology

def infer_topology(pp_net, connected_subnet):
    
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