class Node:
    def __init__(self, imagen, flavor):
        self.imagen = imagen
        self.flavor = flavor #flavor object
        self.list_links =[] # list of link objets

    def add_node(self, node):
        self.list_links.append(node)