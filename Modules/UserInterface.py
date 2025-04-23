from Modules.SliceAdministrator import SliceAdministrator
from Topology import *
from Modules.UserInterface import *
from Modules.OpenStackDriver import *
import json
import os
from conf.Conexion import *
import logging
import math
import schedule

class UserInterface:
    def __init__(self):
        self.Menu=None

    @staticmethod
    def main_menu():
        print('1. Configurar')
        print('2. Listar slices')
        print('3. Borrar slice')
        print('4. Definir zona de disponibilidad')
        print('5. Salir')
        return input('Opción: ')

    @staticmethod
    def def_zona_disponibilidad_menu():
        print('*********************************')
        print('Ingrese el nombre de la zona de disponibilidad:')
        return input('Nombre: ')


    @staticmethod
    def def_zona_disponibilidad_menu2():
        print('*********************************')
        print('Seleccionar:')
        print('1. Cluster de servidores Linux')
        print('2. Openstack')
        print('3. Salir')
        return input('Opción: ')

    @staticmethod
    def listar_zonas(tipo):
        conn = Conexion()
        zonas = conn.Select("nombre,idzona_disponibilidad","zona_disponibilidad",f"descripcion='{tipo}'")
        i=0
        lista=[]
        for zona in zonas:
            i=i+1
            servers=conn.Select("nombre,id_recurso","servidor",f"id_zona={zona[1]}")
            message = f"{i}. {zona[0]} :"
            for server in servers:
                recurso = conn.Select("ram_available,vcpu_available,storage_available","recursos",f"id_recursos={server[1]}")
                recurso = recurso[0]
                ram = round(int(recurso[0])/1000000,2)
                disco = round(int(recurso[2])/1000000000,2)
                message = message + f" ( {server[0]} RAM: {str(ram)} MB CPU: {recurso[1]} DISCO: {str(disco)} GB ) "
                #print(f"{i}. {zona[0]} : {server[0]} RAM: {recurso[0]} CPU: {recurso[1]} DISCO: {recurso[2]}")
            print(message)
            dic = {i: zona[0]}
            lista.append(dic)
        return lista

    @staticmethod
    def listar_slices(tipo):
        conn = Conexion()
        server = conn.Select("nombre,id_slice", "slice",f"tipo = '{tipo}' ")
        i=0
        lista=[]
        for nombre in server:
            i=i+1
            print(f"{i}. Slice: {nombre[0]}")
            dic = {i: nombre[0]}
            lista.append(dic)
        return lista


    @staticmethod
    def def_zona_disponibilidad_menu3(tipo):
        print('*********************************')
        conn = Conexion()
        server = conn.Select("nombre", "servidor",f"id_zona is null  && descripcion = '{tipo}'")
        #server = conn.Select("nombre", "servidor", "-1")
        i=0
        lista=[]
        if len(server) == 0:
            print("No hay servidores disponibles")
            return lista,''
        else:
            print("Seleccione lo servidores indicando los número separandolo por comas (1,2)")
            print('Lista de servidores disponibles:')
            for nombre in server:
                i=i+1
                id = conn.Select("id_recurso", "servidor", f"nombre = '{nombre[0]}'")
                id2=id[0]
                id3=id2[0]
                data = conn.Select("ram,vcpu,storage", "recursos", f"id_recursos = {id3}")
                ram=int(data[0][0])/1000000
                disco = int(data[0][2]) / 1000000
                print(f"{i}. {nombre[0]} - Capacidad: RAM:{str(ram)} MB CPU:{data[0][1]} DISCO:{str(disco)} MB")
                dic = {i: nombre[0]}
                lista.append(dic)
            print("Escriba 'exit' si terminó de escoger los servidores para su zona de disponibilidad")
            return lista,input('Opción: ')

    @staticmethod
    def def_register_zona(zona,tipo):
        nombre=zona[0]
        conn = Conexion()
        conn.Insert("zona_disponibilidad","nombre,descripcion",f"'{nombre}','{tipo}'")
        id = conn.Select("idzona_disponibilidad","zona_disponibilidad",f"nombre='{nombre}'")
        id=id[0][0]
        servers = zona[1]
        for server in servers:
            conn.Update("servidor",f"id_zona={id}",f"nombre='{server}'")
        print(f"Se registró la zona {nombre} con los servers {zona[1]}")

    @staticmethod
    def def_listar_menu1():
        print('*********************************')
        conn = Conexion()
        slices = conn.Select("nombre","slice","-1")
        print('Ingrese el número del slice si desea verlo con mayor detalle:')
        print('Lista de slices:')
        i=0
        lista=[]
        for nombre in slices:
            i=i+1
            print(f"{i}. Slice: {nombre[0]}")
            dic = {i: nombre[0]}
            lista.append(dic)
        print("Escriba 'exit' para salir del menú")
        return lista,input('Opción: ')

    @staticmethod
    def detalle_slice(slice):
        print("******************************")
        conn = Conexion()
        id=conn.Select("id_slice","slice",f"nombre='{slice}'")
        id=id[0]
        info_vm = conn.Select("nombre,recursos_id_estado,vnc,servidor_id_servidor","vm",f"topologia_id_topologia='{id[0]}'")
        for vm in info_vm:
            #print(f"Nombre VM: {info_vm[0]}")
            recursos = conn.Select("ram,vcpu,storage","recursos",f"id_recursos={vm[1]}")
            ip = conn.Select("ip","servidor",f"id_Servidor='{vm[3]}'")
            ip=ip[0]
            ram = int(recursos[0][0]) #/ 1000000
            disco = int(recursos[0][2]) #/ 1000000
            vnc_port=5900+vm[2]
            print(f"VM: {vm[0]} - Capacidad: RAM:{str(ram)} MB CPU:{recursos[0][1]} DISCO:{str(disco)} GB - ACCESO_VNC: {ip[0]}:{vnc_port}")

    @staticmethod
    def def_listar_menu2(zona):
        print('*********************************')
        conn = Conexion()
        zonas = conn.Select("nombre", "zona_disponibilidad", "-1")
        print('Seleccione una zona de disponibilidad:')
        print('Lista de zonas de disponibilidad:')
        i = 0
        lista = []
        for zona in zonas:
            i = i + 1
            print(f"{i}. Zona: {zona[0]}")
            dic = {i: zona[0]}
            lista.append(dic)
        print("Escriba 'exit' para salir del menú")
        return lista, input('Opción: ')

    @staticmethod
    def def_borrar_menu3(nombre):
        print('*********************************')
        print('¿Está seguro que desea borrar el slice?', nombre)
        print('1. SI')
        print('2. NO')
        print("Escriba 'exit' para salir del menú")
        return input('Opción: ')



    @staticmethod
    def def_borrar_menu1():
        print('*********************************')
        conn = Conexion()
        slices = conn.Select("nombre", "slice", "-1")
        print('Ingrese el número del slice si desea borrarlo:')
        print('Lista de slices:')
        i = 0
        lista = []
        for nombre in slices:
            i = i + 1
            print(f"{i}. Slice: {nombre[0]}")
            dic = {i: nombre[0]}
            lista.append(dic)
        print("Escriba 'exit' para salir del menú")
        return lista, input('Opción: ')

    @staticmethod
    def def_borrar_menu2(slice):
        print('*********************************')
        conn = Conexion()
        id = conn.Select("id_slice","slice",f" nombre = {slice}")
        conn.Delete("vm",f" topologia_id_topologia = {id[0]}")
        conn.Delete("slice",f" nombre = {slice}")
        return input('Opción: ')

    @staticmethod
    def id_imagen(imagen):
        id_imagen = Conexion().Select("id_imagen", "imagen", f"nombre = '{imagen}'")
        id_imagen = id_imagen[0]

    @staticmethod
    def def_conf_menu1():
        print('*********************************')
        print('Seleccionar:')
        print('1. Configuración desde cero')
        print('2. Continuar configuración:')
        print("Escriba 'exit' para salir del menú")
        return input('Opción: ')

    @staticmethod
    def def_conf_menu2():
        print('*********************************')
        print('Seleccionar:')
        print('1. Cluster de servidores Linux')
        print('2. Openstack')
        print('3. Salir')
        return input('Opción: ')

    @staticmethod
    def def_conf_menu3():
        print('*********************************')
        print('Seleccionar:')
        print('1. Cluster de servidores Linux')
        print('2. Openstack')
        print('3. Salir')
        return input('Opción: ')

    @staticmethod
    def def_conf_nodos1():
        print('*********************************')
        print('Seleccione:')
        print('1. Configurar todos los nodos')
        print('2. Configurar un nodo o una lista de nodos')
        print("Escriba 'exit' para salir del menú")
        return input('Opción: ')

    @staticmethod
    def def_conf_nodos2():
        print('*********************************')
        print('Seleccionar:')
        print('1. Configuración con flavors')
        print('2. Configuración manual')
        print("Escriba 'exit' para salir del menú")
        return input('Opción: ')

    @staticmethod
    def def_config_slice():
        print('*********************************')
        print('Seleccionar:')
        print('1. Agregar un nodo')
        print('2. Agregar conjunto de nodos(subgrafo)')
        print('3. Agregar enlace')
        print('4. Borrar nodo')
        print('5. Borrar enlace')
        print('6. Configurar Nodos')
        print('7. Guardar cambios')
        print('8. Ver slice actual')
        print("Escriba 'exit' para salir del menú")
        return input('Opción: ')

    @staticmethod
    def draw_subgrafo(slice, prox_node):
        # Metodo que recibe el slice actual (slice) y el nodo por el cual empezara el subgrafo (prox_node)
        # Devuelve el nuevo slice y valor del proximo valor nodo a utilizar
        topology = Topology()
        sub_topologies = ["lineal", "malla", "árbol", "anillo", "bus", "estrella"]
        print("Escoja la topología del subgrafo que desea agregar:")
        index = 0
        sub_grafo, last_node = None, None
        for sub_topology_name in sub_topologies:
            print(f"{index+1}. {sub_topology_name}")
            index += 1
        topo_type = input('Opción: ')
        if topo_type == "1":
            nodo = int(input("Ingrese el número de nodos: "))
            sub_grafo, last_node = topology.create_lineal_topology(prox_node, nodo)
        elif topo_type == "2":
            nodo = input("Ingrese el número de filas y columnas con el formato '3-3': ")
            formato = nodo.split("-")
            sub_grafo, last_node = topology.create_malla_topology(prox_node, int(formato[0]),int(formato[1]))
        elif topo_type == "3":
            nivel = int(input("Ingrese el número de niveles: "))
            sub_grafo, last_node = topology.create_tree_topology(prox_node, nivel)
        elif topo_type == "4":
            nodo = int(input("Ingrese el número de nodos: "))
            sub_grafo, last_node = topology.create_ring_topology(prox_node, nodo)
        elif topo_type == "5":
            #BUS
            nivel = int(input("Ingrese el número de niveles: "))
            sub_grafo, last_node = topology.create_star_topology(prox_node, nivel)
        elif topo_type == "6":
            nodo = int(input("Ingrese el número de nodos que irán alrededor del nodo principal: "))
            sub_grafo, last_node = topology.create_star_topology(prox_node, nodo)
        else:
            print("Opción no válida")
        prox_node = last_node+1
        slice["nodos"].update(sub_grafo) # Agrega los nuevos valores de sub_grafo al diccionario slice.
        for nodo in slice["nodos"]:
            slice["nodos"][nodo]["instanciado"] = "false"
        print(f"* Subgrafo del tipo {sub_topologies[int(topo_type)-1]} agregado.")

        return slice, prox_node

    @staticmethod
    def save_changes(slice, from_scratch):
        if from_scratch:
            print("1. Guardar borrador")
            print("2. Implementar slice")
            print("Escriba 'exit' para salir del menú")
            opt = input("Opcion: ")
            if opt == "1" or opt == "2":
                if opt == "1":
                    f = open(f"./Modules/Slices/{slice['nombre']}.json", "w")
                    f.write(json.dumps(slice))
                    f.close()
                    print(f"* Slice {slice['nombre']} guardado.")
                elif opt == "2":
                    lista_zonas=[["zona1"," 4 discos-60%, 8GB RAM-50%, 8 CPUs-20%"],["zona2","4 discos-60%, 8GB RAM-70%, 8 CPUs-40%"],["zona3","4 discos-80%, 8GB RAM-90%, 8 CPUs-70%"]]
                    print("Seleccionar zona de disponibilidad:")
                    print("Lista de zonas:")
                    for zona in lista_zonas:
                        print(f"* {zona[0]}  Consumo usado: {zona[1]} ")
                    opt = input("Opcion: ")
                    slice["zona"] = {"nombre":opt}
                    print("**************************************")
                    print("Se está implementando...")
                    print(f"Se envía al administrador de slice: {slice}")
                    print("**************************************")
                    result = UserInterface.create_topology(slice)
        else:
            f = open(f"./Modules/Slices/{slice['nombre']}.json", "w")
            f.write(json.dumps(slice))
            f.close()
            print("* Cambios guardados e implementando slice ...")
            result = UserInterface.create_topology(slice)
            # TODO

    @staticmethod
    def lista_flavors():
        conn=Conexion()
        flavors=conn.Select("nombre,id_flavor,ram,cpu,storage","flavor","-1")
        print('Ingrese el número del flavor que desea agregar:')
        print('Lista de slices:')
        i = 0
        lista = []
        for nombre in flavors:
            i = i + 1
            print(f"{i}. {nombre[0]} RAM: {nombre[2]} MB CPU: {nombre[3]} DISCO: {nombre[4]} GB ")
            dic = {i: nombre[0]}
            lista.append(dic)
        print("Escriba 'exit' para salir del menú")
        return lista, input('Opción: ')

    @staticmethod
    def lista_imagenes():
        conn = Conexion()
        imagenes = conn.Select("nombre", "imagen", "-1")
        print('Ingrese el número de la imagen que desea agregar:')
        print('Lista de imágenes:')
        i = 0
        lista = []
        for nombre in imagenes:
            i = i + 1
            print(f"{i}. {nombre[0]} ")
            dic = {i: nombre[0]}
            lista.append(dic)
        print("Escriba 'exit' para salir del menú")
        return lista, input('Opción: ')


    @staticmethod
    def validate_option(option):
        if not((option > 0) and (option < 100)):
            raise Exception('Invalid option')
        else:
            return True

    @staticmethod
    def exit():
        print('Elaborado por GRUPO 1\n')

    @staticmethod
    def iniciar_programa():
        sa = SliceAdministrator()
        #sa.register_data()
        o = UserInterface()
        while True:
            print('*********************************')
            print('')
            option = UserInterface.main_menu()
            try:
                option = int(option)
                UserInterface.validate_option(option)

                if option == 1:
                    while True:
                        config_mode = o.def_conf_menu1()
                        if config_mode=="exit":
                            break
                        elif int(config_mode) == 1 or int(config_mode) == 2:
                            slice = {"nodos":{}}
                            prox_node = 0
                            from_scratch = False #TODO: Cambiar a si esta implementado o no
                            if int(config_mode) == 1:
                                slice_name = input("Nombre del slice: ")
                                slice["nombre"] = slice_name
                                print(f"* Slice {slice_name} creado.")
                                slice["estado"] = "guardado"
                                from_scratch = True # Es verdadero si se inicia desde cero la creacion del slice
                            else:
                                print("*********************************")
                                #lista1 = o.listar_slices("linux_cluster")
                                #lista2 = o.listar_slices("openstack")
                                print("*********************************")
                                files = os.listdir('./Modules/Slices')
                                i = 0
                                for file_name in files:
                                    print(f"{i+1}. {file_name[:-5]}")
                                    i += 1
                                slice_opt = input("Seleccionar slice: ")
                                file_name = files[int(slice_opt)-1]
                                f = open(f"./Modules/Slices/{file_name}", "r")
                                slice = json.loads(f.read())
                                prox_node = slice["ultimo_nodo"]+1
                                f.close()
                            while True:
                                opt =  o.def_config_slice()
                                if opt == "exit":
                                    break
                                elif int(opt) == 1:
                                    slice["nodos"][f"n{prox_node}"] = {"enlaces":[]}
                                    slice["nodos"][f"n{prox_node}"]["instanciado"] = "false"
                                    print(f"* Nodo n{prox_node} agregado.")
                                    prox_node += 1
                                    pass
                                elif int(opt) == 2:
                                    new_slice, new_prox_node = o.draw_subgrafo(slice, prox_node)
                                    slice = new_slice
                                    prox_node = new_prox_node
                                elif int(opt) == 3:
                                    while True:
                                        nodos_dict = slice["nodos"]
                                        i = 1
                                        for node_name in nodos_dict.keys():
                                            instanciado = nodos_dict[node_name]["instanciado"] == "true"
                                            print(f"-{node_name}: {node_name if not instanciado else slice['mapeo_nombres'][node_name]}")
                                            i += 1
                                        link = input("Indicar nodos en formato 'n1-n2', escriba 'exit' para terminar: ")
                                        if link == "exit":
                                            break
                                        else:
                                            nodos = link.split("-")
                                            slice["nodos"][nodos[0]]["enlaces"].append(nodos[1])
                                            slice["nodos"][nodos[1]]["enlaces"].append(nodos[0])
                                            print(f"* Enlace {link} creado.")
                                elif int(opt) == 4:
                                    if slice["estado"] == "guardado":
                                        nodos_dict = slice["nodos"]
                                        i = 1
                                        for node_name in nodos_dict.keys():
                                            print(f"- {node_name}")
                                            i += 1
                                        node_opt = input("Indicar nodo que desea borrar: ")
                                        for node_name in slice["nodos"].keys():
                                            enlaces = slice["nodos"][node_name]["enlaces"]
                                            if node_opt in enlaces:
                                                slice["nodos"][node_name]["enlaces"].remove(node_opt)
                                        del slice["nodos"][node_opt]
                                        print(f"* Nodo {node_opt} borrado del slice {slice['nombre']}.")
                                    elif slice["estado"] == "ejecutado":
                                        print("***************************")
                                        print(f"* No se pueden borrar nodos del slice {slice['nombre']} porque ya está implementado")
                                        print("***************************")
                                elif int(opt) == 5:
                                    if slice["estado"] == "guardado":
                                        nodos_dict = slice["nodos"]
                                        print(f"- {nodos_dict}")
                                        i = 1
                                        enlaces_repe = []
                                        for nodo_origin in nodos_dict:
                                            enlaces_dict = nodos_dict.get(nodo_origin)
                                            for enlaces_array in enlaces_dict.values():
                                                for nodo_enlace in enlaces_array:
                                                    if len(enlaces_repe) > 0:
                                                        enlace_par = nodo_origin + "-" + nodo_enlace
                                                        if (enlace_par in enlaces_repe):
                                                            print("")
                                                        else:
                                                            print(f"*{nodo_origin}-{nodo_enlace}")
                                                    else:
                                                        print(f"*{nodo_origin}-{nodo_enlace}")
                                                    enlace = nodo_origin + "-" + nodo_enlace
                                                    enlace_inv = nodo_enlace + "-" + nodo_origin
                                                    enlaces_repe.append(enlace)
                                                    enlaces_repe.append(enlace_inv)
                                            i += 1
                                        enlace_opt = input(
                                            "Indicar enlace que desea borrar en formato 'n1-n2', escriba 'exit' para terminar: ")
                                        if enlace_opt == "exit":
                                            break
                                        else:
                                            nodos = enlace_opt.split("-")
                                            slice["nodos"][nodos[0]]["enlaces"].remove(nodos[1])
                                            slice["nodos"][nodos[1]]["enlaces"].remove(nodos[0])
                                            print(f"* Enlace {enlace_opt} borrado.")
                                    elif slice["estado"] == "ejecutado":
                                        print("***************************")
                                        print(f"* No se pueden borrar enlaces del slice {slice['nombre']} porque ya está implementado")
                                        print("***************************")

                                elif int(opt) == 6:
                                    conf_nodos_mode = o.def_conf_nodos1()
                                    if conf_nodos_mode == 'exit':
                                        pass
                                    elif int(conf_nodos_mode) == 1:
                                        nodos_dict = slice["nodos"]
                                        nodos_lista = []
                                        if slice["estado"] == "ejecutado":
                                            print("Se configurará todos los nodos que no se han implementado.")
                                            for node_name in nodos_dict.keys():
                                                if slice["nodos"][node_name]["instanciado"] == "false":
                                                    nodos_lista.append(node_name)
                                        else:
                                            for node_name in nodos_dict.keys():
                                                nodos_lista.append(node_name)
                                        nodos=nodos_lista
                                        print(f"Configurará: {nodos_lista}")
                                        conf_nodos_mode2 = o.def_conf_nodos2()
                                        if conf_nodos_mode == 'exit':
                                            pass
                                        elif int(conf_nodos_mode2) == 1:
                                            print("***************************************")
                                            lista,flavor_escogido=o.lista_flavors()
                                            for dic in lista:
                                                flavor = dic.get(int(flavor_escogido))
                                                if flavor is not None:
                                                    print(f"El flavor que configurará es: {flavor}")
                                                    flavor2 = [flavor]
                                            for nodo in nodos:
                                                type = {"type": "flavor", "info_config": flavor2[0]}
                                                slice["nodos"][nodo]["config"] = type
                                            print("***************************************")
                                            print("1. Seleccionar la imagen desde una lista:")
                                            print("2. Importar una imagen (ingresando un link):")
                                            opcion = input("Seleccione:")
                                            if int(opcion) == 1:
                                                print("***************************************")
                                                lista,imagen_escogida=o.lista_imagenes()

                                                for dic in lista:
                                                    imagen = dic.get(int(imagen_escogida))
                                                    if imagen is not None:
                                                        print(f"La imagen que configurará es: {imagen}")
                                                        info_config = {"nombre": imagen, "url": "-"}
                                                        imagen2=imagen
                                                for nodo in nodos:
                                                    #type = {"imagen": info_config}
                                                    slice["nodos"][nodo]["config"]["imagen"] = info_config
                                            elif int(opcion) == 2:
                                                print("***************************************")
                                                print("* Puede importar una imagen desde: https://docs.google.com/document/d/1htiLHrXIsEkm9U_b201QaSHzYYCZjQHyMa2cDii7QSE/edit?usp=sharing)")
                                                link = input("Ingrese un link:")
                                                nombre = input("Ingrese el nombre:")
                                                imagen2=nombre
                                                info_config = {"nombre": nombre, "url": link}
                                                for nodo in nodos:
                                                    slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                imagen2 = imagen2+f" desde {link}"
                                            print(f"Se configuró los siguientes nodos {nodos} con flavor: {flavor2[0]} e imagen: {imagen2}")

                                        elif int(conf_nodos_mode2) == 2:
                                            cpu = input("Indicar el # de CPUs:")
                                            ram = input("Indicar la capacidad de la memoria RAM en MB:")
                                            disco = input("Indicar la capacidad de disco en GB:")
                                            info_config = [cpu, ram, disco]
                                            config = {}
                                            for nodo in nodos:
                                                type = {"type": "manual", "info_config": info_config}
                                                slice["nodos"][nodo]["config"] = type
                                            print("***************************************")
                                            print("1. Seleccionar la imagen desde una lista:")
                                            print("2. Importar una imagen (ingresando un link):")
                                            opcion = input("Seleccione:")
                                            if int(opcion) == 1:
                                                print("***************************************")
                                                lista, imagen_escogida = o.lista_imagenes()

                                                for dic in lista:
                                                    imagen = dic.get(int(imagen_escogida))
                                                    if imagen is not None:
                                                        print(f"La imagen que configurará es: {imagen}")
                                                        info_config = {"nombre": imagen, "url": "-"}
                                                        imagen2=imagen
                                                for nodo in nodos:
                                                    # type = {"imagen": info_config}
                                                    slice["nodos"][nodo]["config"]["imagen"] = info_config
                                            elif int(opcion) == 2:
                                                print("***************************************")
                                                print(
                                                    "* Puede importar una imagen desde: https://docs.google.com/document/d/1htiLHrXIsEkm9U_b201QaSHzYYCZjQHyMa2cDii7QSE/edit?usp=sharing)")
                                                link = input("Ingrese un link:")
                                                nombre = input("Ingrese un nombre:")
                                                imagen2=nombre
                                                info_config = {"nombre":nombre,"url":link}
                                                for nodo in nodos:
                                                    slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                imagen2 = imagen2+f" desde {link}"
                                            print(f"Se configuró los siguientes nodos {nodos} con:")
                                            print(f"RAM: {ram} , CPU: {cpu}, DISCO: {disco} e imagen: {imagen2}")
                                        else:
                                            print("Opción no válida")
                                    elif int(conf_nodos_mode) == 2:

                                        nodos_dict = slice["nodos"]
                                        if slice["estado"] == "ejecutado":
                                            print("Se configurará todos los nodos que no se han implementado.")
                                            for node_name in nodos_dict.keys():
                                                if slice["nodos"][node_name]["instanciado"] == "false":
                                                    print(f"- {node_name}")
                                        else:
                                            for node_name in nodos_dict.keys():
                                                print(f"- {node_name}")

                                        enlace_opt = input("Indicar nodos que desea configurar en formato 'n1,n2,n3,etc', escriba 'exit' para terminar: ")
                                        if enlace_opt == "exit":
                                            break
                                        else:
                                            nodos = enlace_opt.split(",")
                                            print(f"Configurará: {nodos}")
                                            conf_nodos_mode2 = o.def_conf_nodos2()
                                            if conf_nodos_mode == 'exit':
                                                pass
                                            elif int(conf_nodos_mode2) == 1:
                                                lista, flavor_escogido = o.lista_flavors()
                                                for dic in lista:
                                                    flavor = dic.get(int(flavor_escogido))
                                                    if flavor is not None:
                                                        print(f"El flavor que configurará es: {flavor}")
                                                        flavor2 = [flavor]
                                                for nodo in nodos:
                                                    type = {"type": "flavor", "info_config": flavor2[0]}
                                                    slice["nodos"][nodo]["config"] = type
                                                print("***************************************")
                                                print("1. Seleccionar la imagen desde una lista:")
                                                print("2. Importar una imagen (ingresando un link):")
                                                opcion = input("Seleccione:")
                                                if int(opcion) == 1:
                                                    print("***************************************")
                                                    lista, imagen_escogida = o.lista_imagenes()

                                                    for dic in lista:
                                                        imagen = dic.get(int(imagen_escogida))
                                                        if imagen is not None:
                                                            print(f"La imagen que configurará es: {imagen}")
                                                            info_config = {"nombre":imagen,"url":"-"}
                                                            imagen2=imagen
                                                    for nodo in nodos:
                                                        # type = {"imagen": info_config}
                                                        slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                elif int(opcion) == 2:
                                                    print("***************************************")
                                                    print(
                                                        "* Puede importar una imagen desde: https://docs.google.com/document/d/1htiLHrXIsEkm9U_b201QaSHzYYCZjQHyMa2cDii7QSE/edit?usp=sharing)")
                                                    link = input("Ingrese un link:")
                                                    nombre = input("Ingrese un nombre:")
                                                    imagen2=nombre
                                                    info_config={"nombre": nombre, "url": "-"}
                                                    for nodo in nodos:
                                                        slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                    imagen2 = imagen2+ f" desde {link}"
                                                print(f"Se configuró los siguientes nodos {nodos} con flavor: {flavor2[0]} e imagen: {imagen2}")
                                            elif int(conf_nodos_mode2) == 2:
                                                cpu = input("Indicar el # de CPUs:")
                                                ram = input("Indicar la capacidad de la memoria RAM en MB:")
                                                disco = input("Indicar la capacidad de disco en GB:")
                                                info_config = [cpu, ram, disco]
                                                config = {}
                                                for nodo in nodos:
                                                    type = {"type": "manual", "info_config": info_config}
                                                    slice["nodos"][nodo]["config"] = type
                                                print("***************************************")
                                                print("1. Seleccionar la imagen desde una lista:")
                                                print("2. Importar una imagen (ingresando un link):")
                                                opcion = input("Seleccione:")
                                                if int(opcion) == 1:
                                                    print("***************************************")
                                                    lista, imagen_escogida = o.lista_imagenes()

                                                    for dic in lista:
                                                        imagen = dic.get(int(imagen_escogida))
                                                        if imagen is not None:
                                                            print(f"La imagen que configurará es: {imagen}")
                                                            info_config = {"nombre":imagen,"url":"-"}
                                                            imagen2=imagen
                                                    for nodo in nodos:
                                                        # type = {"imagen": info_config}
                                                        slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                elif int(opcion) == 2:
                                                    print("***************************************")
                                                    print("* Puede importar una imagen desde: https://docs.google.com/document/d/1htiLHrXIsEkm9U_b201QaSHzYYCZjQHyMa2cDii7QSE/edit?usp=sharing)")
                                                    link = input("Ingrese un link:")
                                                    nombre = input("Ingrese un nombre:")
                                                    imagen2=nombre
                                                    info_config={"nombre":nombre,"url":link}
                                                    for nodo in nodos:
                                                        slice["nodos"][nodo]["config"]["imagen"] = info_config
                                                    imagen2 = imagen2 + f" desde {link}"
                                                print(f"Se configuró los siguientes nodos {nodos} con:")
                                                print(f"RAM: {ram} , CPU: {cpu}, DISCO: {disco} e imagen: {imagen2}")
                                            else:
                                                print("Opción no válida")
                                elif int(opt) == 7:
                                    slice["ultimo_nodo"] = prox_node-1
                                    print("------Data a enviar-----")
                                    print(slice)
                                    #slice["estado"] = "guardado"
                                    if slice["estado"] == "guardado":
                                        print("*************************************")
                                        print("1. Guardar como borrardor")
                                        print("2. Implementar el slice")
                                        opcion = input("Escoja la opción:")
                                        sa = SliceAdministrator()
                                        if int(opcion) == 1:
                                            slice["estado"] = "guardado"
                                            print("*************************************")
                                            print("Guardando .....")
                                            sa.save_slice(slice)
                                        elif int(opcion) == 2:
                                            print("*************************************")
                                            # listar_zonas
                                            tipo = o.def_zona_disponibilidad_menu2()
                                            if int(tipo) == 3:
                                                print("-----")
                                            elif int(tipo) == 1:
                                                tipo_zona = "linux_cluster"
                                                lista = o.listar_zonas(tipo_zona)
                                                if len(lista)>0:
                                                    zona = input("Escoja la zona:")
                                                    for dic in lista:
                                                        zona_escogida = dic.get(int(zona))
                                                        if zona_escogida is not None:
                                                            print(f"Zona escogida: {zona_escogida}")
                                                            slice["zona"] = {"nombre":zona_escogida}
                                                            #print(slice)
                                                    print("Implementando .....")

                                                    slice_nuevo = sa.create_slice(slice,"1")
                                                    sa.save_slice(slice)

                                                    print("*************************************")
                                                    print(slice_nuevo)
                                                    # slice["estado"] = "ejecutado"
                                                    print("Slice " + slice_nuevo["nombre"] + " IMPLEMENTADO EXITOSAMENTE!")
                                                    print("*************************************")
                                                else:
                                                    print("No hay zonas de disponibilidad")
                                            elif int(tipo) == 2:
                                                tipo_zona = "openstack"
                                                info_computes()
                                                lista = o.listar_zonas(tipo_zona)
                                                if len(lista) > 0:
                                                    zona = input("Escoja la zona:")
                                                    for dic in lista:
                                                        zona_escogida = dic.get(int(zona))
                                                        if zona_escogida is not None:
                                                            print(f"Zona escogida: {zona_escogida}")
                                                            slice["zona"] = {"nombre":zona_escogida}
                                                            #print(slice)
                                                    print("Implementando .....")
                                                    slice_nuevo = sa.create_slice(slice,"2")
                                                    sa.save_slice(slice)
                                                    print("*************************************")
                                                    print(slice_nuevo)
                                                    print("Slice " + slice_nuevo["nombre"] + " IMPLEMENTADO EXITOSAMENTE!")
                                                    # slice["estado"] = "ejecutado"
                                                    print("*************************************")
                                                else:
                                                    print("No hay zonas de disponibilidad")
                                            else:
                                                print("Opción no válida ...")

                                    elif slice["estado"] == "ejecutado":
                                        print(f"* Actualizando el slice {slice['nombre']}")
                                        slice_actualizado = sa.update_slice(slice,"1")
                                        sa.save_slice(slice_actualizado)
                                        print(slice_actualizado)
                                    print("------------------------")
                                    #o.save_changes(slice, from_scratch)
                                    pass
                                elif int(opt) == 8:
                                    topo = Topology()
                                    print(slice)
                                    topo.draw_topology(slice)
                        else:
                            print("* Opcion no valida.")
                            break
                elif option == 3:
                    while True:
                        lista,slice_escogido = o.def_borrar_menu1()
                        tipo = ""
                        if slice_escogido == "exit":
                            break
                        else:
                            nombre_slice = ""
                            for dic in lista:
                                slice = dic.get(int(slice_escogido))
                                if slice is not None:
                                    print(f"El slice que borrará es: {slice}")
                                    nombre_slice = slice
                                    tipoTupla = Conexion().Select("tipo", "slice", f"nombre='{nombre_slice}'")
                                    if (tipoTupla[0][0] == "linux_custer"):
                                        tipo = "1"
                                    if (tipoTupla[0][0] == "openstack"):
                                        tipo = "2"
                            confirma_borrado = o.def_borrar_menu3(slice_escogido)
                            if confirma_borrado == "exit":
                                break
                            else:
                                if int(confirma_borrado) == 2:
                                    print("***********************************")
                                    print("No se borró nada")
                                    print("***********************************")
                                elif int(confirma_borrado) == 1:
                                    #o.def_borrar_menu2(slice)
                                    print("***********************************")
                                    f = open(f"./Modules/Slices/{nombre_slice}.json")
                                    data=f.readlines()
                                    data=data[0]
                                    json_slice = json.loads(data)
                                    f.close()
                                    sa= SliceAdministrator()
                                    message = sa.delete_slice(json_slice,tipo)
                                    json_slice["estado"] = "guardado"
                                    sa.save_slice(json_slice)
                                    print(message)
                                    print("***********************************")
                elif option == 2:
                    while True:
                        lista,slice_escogido = o.def_listar_menu1()
                        if slice_escogido == "exit":
                            break
                        else:
                            for dic in lista:
                                nombre_escogido = dic.get(int(slice_escogido))
                                if nombre_escogido is not None:
                                    print(f"Slice escogido: {nombre_escogido}")
                                    o.detalle_slice(nombre_escogido)

                elif option == 4:
                    nombre_zona = o.def_zona_disponibilidad_menu()
                    tipo_zona = o.def_zona_disponibilidad_menu2()
                    tipo_zona = int(tipo_zona)
                    if tipo_zona == 1:
                        server_linux_cluster = []
                        lista,server_escogido = o.def_zona_disponibilidad_menu3("linux_cluster")
                        if len(lista)>0:
                            if server_escogido == "exit":
                                #print("Se registró su zona de disponibilidad" , nombre_zona, " de tipo Linux cluster en los servidores", server_linux_cluster)
                                break
                            else:
                                servers = server_escogido.split(',')
                                for server in servers:
                                    for dic in lista:
                                        nombre_escogido=dic.get(int(server))
                                        if nombre_escogido is not None:
                                            print(f"Server escogido: {nombre_escogido}")
                                            server_linux_cluster.append(nombre_escogido)
                            zona = [nombre_zona, server_linux_cluster]
                            #print(f"Zona: {zona}")
                            o.def_register_zona(zona,"linux_cluster")
                    elif tipo_zona == 2:
                        server_openstack = []
                        lista, server_escogido = o.def_zona_disponibilidad_menu3("openstack")
                        if len(lista)>0:
                            if server_escogido == "exit":
                                # print("Se registró su zona de disponibilidad" , nombre_zona, " de tipo Linux cluster en los servidores", server_linux_cluster)
                                break
                            else:
                                servers = server_escogido.split(',')
                                for server in servers:
                                    for dic in lista:
                                        nombre_escogido = dic.get(int(server))
                                        if nombre_escogido is not None:
                                            print(f"Server escogido: {nombre_escogido}")
                                            server_openstack.append(nombre_escogido)
                            zona = [nombre_zona, server_openstack]
                            # print(f"Zona: {zona}")
                            o.def_register_zona(zona,"openstack")
                    else:
                        break
                elif option == 5:
                    o.exit()
                    break
                else:
                    print("Opción no válida")

            except Exception as e:
                logging.exception(e)

    @staticmethod
    def create_topology(grafo):
        sliceAdministrator = SliceAdministrator()
        nuevo_slice = sliceAdministrator.create_topology(grafo)
        UserInterface.save_changes(nuevo_slice, False)