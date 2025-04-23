from pyvis.network import Network
class Topology:
    def __init__(self):
        pass

    def create_star_topology(self,prox_node, nodos):
        i = 0
        start = prox_node
        array_nodos = []
        for i in range(nodos + 1):
            i = i + 1
            nodo = "n" + str(i+start)
            array_nodos.append(nodo)
        j = 0
        sub_grafo = {}
        for k in range(nodos + 1):
            if k == 1:
                nodos_enlaces = []
                for i in range(nodos):
                    nodos_enlaces.append(array_nodos[i+ 1])
                    i = i + 1
                    sub_grafo[array_nodos[k - 1]] = {"enlaces": nodos_enlaces}
            else:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[0])
                sub_grafo[array_nodos[k - 1]] = {"enlaces": nodos_enlaces}
            k = k + 1
        last_node = len(array_nodos) + start
        return sub_grafo,last_node

    def create_lineal_topology(self,prox_node, nodos):
        i = 0
        array_nodos = []
        start = prox_node
        for i in range(nodos):
            i = i + 1
            nodo = "n" + str(i+start)
            array_nodos.append(nodo)
        j = 0
        sub_grafo = {}
        for k in range(nodos):
            if k == 0:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k + 1])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            elif k == nodos-1:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k - 1])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            else:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k-1])
                nodos_enlaces.append(array_nodos[k + 1])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            k = k + 1
        last_node = len(array_nodos) + start
        return sub_grafo,last_node
        pass

    def create_ring_topology(self,prox_node, nodos):
        i = 0
        start = prox_node
        array_nodos = []
        for i in range(nodos):
            i = i + 1
            nodo = "n" + str(i+start)
            array_nodos.append(nodo)
        j = 0
        sub_grafo={}
        for k in range(nodos):
            if k == 0:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k + 1])
                nodos_enlaces.append(array_nodos[nodos-1])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            elif k == nodos-1:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k - 1])
                nodos_enlaces.append(array_nodos[0])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            else:
                nodos_enlaces = []
                nodos_enlaces.append(array_nodos[k-1])
                nodos_enlaces.append(array_nodos[k + 1])
                sub_grafo[array_nodos[k]] = {"enlaces": nodos_enlaces}
            k = k + 1
        last_node = len(array_nodos) + start
        return sub_grafo,last_node
        pass

    def create_malla_topology(self,prox_node,filas,columnas):
        nodos = filas * columnas
        i = 0
        array_nodos = []
        start = prox_node
        array_total=[]
        for i in range(filas):
            i = i + 1
            array_parcial = []
            for j in range(columnas):
                j=j+1
                nodo = "Mn" + str(i+start)
                nodo = nodo + str(j+start)
                array_nodos.append(nodo)
                array_parcial.append(nodo)
            array_total.append(array_parcial)
        k = 0
        sub_grafo = {}
        for k in range(filas):
            for j in range(columnas):
                if k == 0:
                    #primera fila
                    if j == 0:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k][j+1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    elif j == columnas-1:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    else:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        nodos_enlaces.append(array_total[k][j + 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                elif k==filas-1:
                    # ultima fila
                    if j == 0:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j + 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    elif j == columnas - 1:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    else:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        nodos_enlaces.append(array_total[k][j + 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                else:
                    # filas intermedias
                    if j == 0:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j + 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    elif j == columnas - 1:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
                    else:
                        nodos_enlaces = []
                        nodos_enlaces.append(array_total[k + 1][j])
                        nodos_enlaces.append(array_total[k - 1][j])
                        nodos_enlaces.append(array_total[k][j - 1])
                        nodos_enlaces.append(array_total[k][j + 1])
                        sub_grafo[array_total[k][j]] = {"enlaces": nodos_enlaces}
        last_node = len(array_nodos) + start
        return sub_grafo,last_node

    def create_tree_topology(self,prox_node, degree):
        start = prox_node
        N = degree
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
        last_node = node+start-1
        return sub_grafo, last_node

    def draw_topology(self, slice):
        net = Network("100%","100%")
        nodos = slice["nodos"]
        mapeo_nombre = slice.get("mapeo_nombres")
        nodos_listos = []
        for nodo_name in nodos:
            if nodo_name not in nodos_listos:
                instanciado = nodos[nodo_name]["instanciado"] == "true"
                nodo_nombre = f"vm-{nodo_name if not instanciado else mapeo_nombre[nodo_name]}"
                net.font_color = "#00ff00" if nodos[nodo_name]["instanciado"] == "true" else "#ff0000"
                net.add_node(nodo_nombre, shape="image", color="#ffffff", image="https://www.nicepng.com/png/full/118-1187674_computer-pc-clipart-computer-application-computer-svg.png")
                enlaces = nodos[nodo_name]["enlaces"]
                for nodo_enlace in enlaces:
                    if nodo_enlace not in nodos_listos:
                        instanciado = nodos[nodo_enlace]["instanciado"] == "true"
                        nodo_enlace_nombre = f"vm-{nodo_enlace if not instanciado else mapeo_nombre[nodo_enlace]}"
                        net.font_color = "#00ff00" if nodos[nodo_enlace]["instanciado"] == "true" else "#ff0000"
                        net.add_node(nodo_enlace_nombre, shape="image", color="#ffffff", image="https://www.nicepng.com/png/full/118-1187674_computer-pc-clipart-computer-application-computer-svg.png")
                    net.add_edge(nodo_nombre, nodo_enlace_nombre)
        net.show('nx.html')

