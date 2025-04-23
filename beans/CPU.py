class CPU:
    def __init__(self, user_time, system_time, idle_time, creation_time, node_id):
        self.user_time=user_time
        self.system_time=system_time
        self.idle_time=idle_time
        self.creation_time=creation_time
        self.node_id=node_id
        pass