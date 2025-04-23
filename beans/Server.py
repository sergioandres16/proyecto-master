class Server:
    def __init__(self, id_servidor, name, description,time_creation, hardware_group, availability_zone):
        self.id_servidor=id_servidor
        self.name=name
        self.description=description
        self.hardware_group= hardware_group
        self.time_creation=time_creation
        self.availability_zone=availability_zone
    

    def add_server(self, server):
        self.links.append(server)