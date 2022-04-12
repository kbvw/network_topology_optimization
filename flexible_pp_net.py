import pandas as pd
import pandapower as pp

from .pandapower import infer_topology, apply_topology
from .topology_search import topology_generator

__all__ = ['FlexibleNet']

class FlexibleNet(pp.auxiliary.pandapowerNet):
    
    # To do:
    # - Serialization (frozensets, graph objects)
    
    # Circumvent Pandapower attribute restrictions when changing class
    def __setattr__(self, key, value):
        if key == '__class__':
            pp.auxiliary.pandapowerNet._setattr(self, key, value)
        else:
            pp.auxiliary.pandapowerNet.__setattr__(self, key, value)
    
    # Copy constructor method
    @classmethod
    def from_pp_net(cls, pp_net,
                    connected_subnet='all',
                    splittable_nodes='all',
                    switchable_edges='all'):
        
        # To do: 
        # - Check if 'None' case does not break anything
        # - Ensure that flexible nodes/edges are subset of connected
        
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
        net.main_topology = infer_topology(net, net.connected_subnet)
        net.main_topology.splittable_nodes = net.splittable_nodes
        net.main_topology.switchable_edges = net.switchable_edges
        
        return net
    
    def displace_aux_buses(self, x, y):
        self.bus_geodata.loc[self.bus['is_aux_bus']==True, 'x'] += x
        self.bus_geodata.loc[self.bus['is_aux_bus']==True, 'y'] += y
              
    def topology_search(self, k=2, node_split=True, edge_switch=True):
        
        topo = topology_generator([self.main_topology], k,
                                           node_split, edge_switch)
        
        self.topo = pd.Series(topo, dtype=object, name='topo_obj')
        
        return len(self.topo)
    
    def reset_topology(self):
        apply_topology(self, 
                       self.splittable_nodes, self.switchable_edges, 
                       self.main_topology)
        
    def apply_topology(self, topology):
        apply_topology(self, 
                       self.splittable_nodes, self.switchable_edges, 
                       topology)
        
    def run_all_pf(self, metrics):
        """Run load flow for each topology and store specified metrics.
        
        Metrics are passed as an iterable of tuples (name, function),
        where 'name' is a string that will be used for logging the metrics
        and 'function' maps a Pandapower network object to a scalar.
        The results are accessible through the 'res_topo' attribute.
        """
        
        # To do: proper handling of non-convergence
        # To do: avoid unnecessary last load flow
        
        # Initialize dataframe
        metric_names, _ = zip(*metrics)
        metric_names = list(metric_names) + ['converged']
        self.res_topo = pd.DataFrame(index=self.topo.index, 
                                     columns=metric_names,
                                     dtype=float)
        
        # Log metrics for every topology
        for n, topology in self.topo.iteritems():
            self.apply_topology(topology)
            try:
                pp.runpp(self)
            except pp.powerflow.LoadflowNotConverged:
                self.res_topo.loc[n, 'converged'] = False
            else:
                self.res_topo.loc[n, 'converged'] = True
                for metric_name, metric in metrics:
                    result = metric(self)
                    self.res_topo.loc[n, metric_name] = result
                    
    def plot_pf_res(self, topology='main'):
        if topology == 'main':
            topology = self.main_topology
            
        # To do: proper handling of non-convergence
        
        # Temporary copy of network object, adjusted for plotting
        net = self.deepcopy()
        
        # Load flow for specified topology
        net.apply_topology(topology)
        try: 
            pp.runpp(net)
        except pp.powerflow.LoadflowNotConverged:
            print('Load flow did not converge')
            
        # Plot in case of convergence
        else:    
        
            # Select only components in service
            for element in ('bus', 'line', 'trafo', 'ext_grid'):
                _select_in_service(net, element)
            
            return pp.plotting.pf_res_plotly(net) 
            
def _select_in_service(net, element):
    
    # Obtain grid element table and corresponding result table
    element_df = getattr(net, element)
    res_df = getattr(net, 'res_' + element)
    
    # Keep only in-service components
    setattr(net, 'res_' + element, res_df[element_df['in_service'] == True])
    setattr(net, element, element_df[element_df['in_service'] == True])