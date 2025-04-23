class Topology:
    def __init__(self, id_topology, name, type, network, mask, vlan_id, time_creation, time_updated):
        self.id_topology=id_topology
        self.name=name
        self.type=type
        self.network= network
        self.mask=mask
        self.vlan_id=vlan_id
        self.time_creation=time_creation
        self.time_updated=time_updated


    def add_node(self, topology):
        self.links.append(topology)