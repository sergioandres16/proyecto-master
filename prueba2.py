
network = {'nodos': {'n0': {'enlaces': ['n4']}, 'n1': {'enlaces': []}, 'n2': {'enlaces': ['n3', 'n4']}, 'n3': {'enlaces': []}, 'n4': {'enlaces': ['n0']}}, 'nombre': 'tel145'}

start = 5
N = 3
sub_grafo = {}
node = 0
for k in range(1, N+1):
    nodes_cant = 2**(k-1)
    for i in range(nodes_cant):
        node_name = f"n{node+start}"
        if k == N:
            enlaces = []
        else:
            enlaces = [f"n{node*2+1+start}", f"n{node*2+2+start}"]
        if node != 0:
            if node%2==0:
                enlaces.append(f"n{int((node-2)/2)+start}")
            else:
                enlaces.append(f"n{int((node-1)/2)+start}")
        sub_grafo[node_name] = {"enlaces": enlaces}
        node += 1

print(sub_grafo)