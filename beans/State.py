class State:
    def __init__(self, id_estado, cpu, ram, storage, network):
        self.id_estado=id_estado
        self.cpu=cpu
        self.ram=ram
        self.storage= storage
        self.network=network


    def add_state(self, state):
        self.links.append(state)