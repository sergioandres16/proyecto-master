"""
===================================================================
PLANIFICADOR DE RECURSOS - App_Scheduler
===================================================================

Este módulo implementa algoritmos de scheduling y placement para 
asignar VMs a servidores físicos de manera óptima.

Migrado a SQLite3 y configuración externalizada.
Autor: Generado por Claude Code
Versión: 2.0 - Migración a SQLite3
===================================================================
"""

import requests
from database.SliceManagerDB import SliceManagerDB
from conf.ConfigManager import config
lista_worker_general_filtrada=[]

class Worker:
    """
    Representa un servidor físico (worker) con sus recursos disponibles.
    
    Atributos:
        id_servidor: ID único del servidor
        ram_disponible: RAM disponible en MB
        disco_disponible: Disco disponible en GB
        vcpu_disponible: vCPUs disponibles
        ram: RAM total en MB
        disco: Disco total en GB
        vcpu: vCPUs totales
    """
    def __init__ (self, id_servidor, ram_disponible, disco_disponible, vcpu_disponible, ram, disco, vcpu):
        self.id_servidor = id_servidor
        self.ram_disponible = ram_disponible
        self.disco_disponible = disco_disponible
        self.vcpu_disponible = vcpu_disponible
        self.ram = ram
        self.disco = disco
        self.vcpu = vcpu

class Vm:
    """
    Representa una máquina virtual con sus recursos requeridos.
    
    Atributos:
        nodo_nombre: Nombre del nodo/VM
        ram_requerida: RAM requerida en MB
        disco_requerido: Disco requerido en GB
        vcpu_requeridas: vCPUs requeridas
    """
    def __init__ (self, nodo_nombre, ram_requerida, disco_requerido, vcpu_requeridas):
        self.nodo_nombre = nodo_nombre
        self.ram_requerida = ram_requerida
        self.disco_requerido = disco_requerido
        self.vcpu_requeridas = vcpu_requeridas



def filtrado(zona_disponibilidad, FACTOR):
    """
    Filtra workers por zona de disponibilidad y aplica factor de recursos.
    
    Args:
        zona_disponibilidad (str): Nombre de la zona de disponibilidad
        FACTOR (float): Factor de multiplicación para recursos disponibles
        
    Returns:
        List[Worker]: Lista de workers filtrados y configurados
    """
    # Query adaptada a SQLite3
    query = """
    SELECT s.id_servidor, r.ram_available, r.storage_available, r.vcpu_available, 
           r.ram, r.storage, r.vcpu 
    FROM recursos r 
    INNER JOIN servidor s ON s.id_recurso = r.id_recursos 
    INNER JOIN zona_disponibilidad zd ON zd.idzona_disponibilidad = s.id_zona 
    WHERE zd.nombre = ?
    """

    db = SliceManagerDB()
    resultado = []
    
    try:
        # Ejecutar consulta con parámetro SQLite3
        results = db.execute_query(query, (zona_disponibilidad,))
        
        for row in results:
            worker = Worker(
                row[0],                    # id_servidor
                float(row[1]) * FACTOR,    # ram_disponible
                float(row[2]) * FACTOR,    # storage_disponible  
                float(row[3]) * FACTOR,    # vcpu_disponible
                float(row[4]) * FACTOR,    # ram_total
                float(row[5]) * FACTOR,    # storage_total
                float(row[6]) * FACTOR     # vcpu_total
            )
            lista_worker_general_filtrada.append(worker)
            
        return lista_worker_general_filtrada
        
    except Exception as e:
        print(f"Error en filtrado de workers: {e}")
        return []

def takeSecond(elem):
    return elem[0]


def calculo_coeficiente(ram_disponible, disco_disponible, vcpu_requeridas, vcpu_disponible,ram,disco):
    scheduler_config = config.get_scheduler_config()
    if (ram==0 or disco==0 or vcpu_disponible==0):
        coeficiente = 0
    else:
        coeficiente = (scheduler_config['ram_weight']*(ram_disponible/ram) + 
                      scheduler_config['disk_weight']*(disco_disponible/disco) + 
                      scheduler_config['vcpu_weight']*(vcpu_requeridas/vcpu_disponible))
    return coeficiente

def ordenamiento_coeficiente(lista_worker_general_filtrada,vm):

    #lista_worker=[]
    lista_worker_coeficiente=[]
    lista_worker_ordenada=[]
    lista_worker_ordenadas_par=[]
    
    contador=0
    #lista_worker_filtradas=filtrado()
    w = 0
    for worker in lista_worker_general_filtrada:
        coeficiente= calculo_coeficiente(worker.ram_disponible, worker.disco_disponible, vm.vcpu_requeridas, worker.vcpu_disponible,worker.ram,worker.disco)
        #par=[coeficiente,worker]
        par=[coeficiente,w]
        lista_worker_coeficiente.append(par)
        w += 1
  
    lista_worker_coeficiente.sort(key=takeSecond, reverse = True)
    
    new_list = []
    for par in lista_worker_coeficiente:
        lista_worker_ordenada.append(lista_worker_general_filtrada[par[1]])
        new_list.append(f"worker_{lista_worker_general_filtrada[par[1]].id_servidor}")
    # print(f"** Orden de prioridad: {new_list} ==> {new_list[0]} es el tentativo servidor físico")
    # print("-- Evaluacion de recursos: ")
    contador1 = 0
    # print(f"Se necesita {vm.ram_requerida} de RAM, {vm.disco_requerido} de disco y {vm.vcpu_requeridas} vcpus")
    for worker in lista_worker_ordenada:
        # print(f"Worker {worker.id_servidor} tiene de {worker.ram_disponible} RAM, {worker.disco_disponible} de disco y {worker.vcpu_disponible} vcpus")
        if (worker.ram_disponible >= vm.ram_requerida and worker.disco_disponible >= vm.disco_requerido and worker.vcpu_disponible >= vm.vcpu_requeridas):
            worker_elegido = worker
            worker_nuevo = worker_elegido
            bytes_to_mb = config.get('BYTES_TO_MB')
            bytes_to_gb = config.get('BYTES_TO_GB')
            ram_disponible_new= worker.ram_disponible - (vm.ram_requerida*bytes_to_mb)
            disco_disponible_new = worker.disco_disponible - (vm.disco_requerido*bytes_to_gb)
            vcpu_total_new= worker.vcpu_disponible - vm.vcpu_requeridas
            worker_nuevo.ram_disponible=ram_disponible_new
            worker_nuevo.disco_disponible=disco_disponible_new
            worker_nuevo.vcpu_disponible=vcpu_total_new
            lista_worker_general_filtrada= lista_worker_ordenada
            lista_worker_general_filtrada[contador]=worker_nuevo
            # print(f"Worker {worker.id_servidor} cumple con los recursos solicitados.")
            break
        else :
            contador1 += 1
            if (contador1 == len(lista_worker_ordenada)):
                # print("Ningun worker cumple con los recursos solicitados.")
                worker_elegido = None
        contador= contador+1
    return worker_elegido


def scheduler_main(data, FACTOR):
    conn = Conexion()
    #Actualizamos los valores en base de datos: mas adelante esto lo hara el validador
    # x = requests.get('http://10.20.12.58:8081/cpu-metrics')
    #VCPU-RAM-STORAGE
    lista_vm_topologia=[]
    nodos=data['nodos']
    for nodo_key in nodos:
        if (nodos[nodo_key]['config']['type'] == 'manual'):
            vcpu=nodos[nodo_key]['config']['info_config'][0]
            ram=nodos[nodo_key]['config']['info_config'][1]
            storage=nodos[nodo_key]['config']['info_config'][2]
            vm=Vm(nodo_key ,int(ram),int(storage),int(vcpu))
            lista_vm_topologia.append(vm)
        else:
            recursos=conn.Select("cpu,ram,storage","flavor","nombre="+"'"+nodos[nodo_key]["config"]["info_config"]+"'")
            vm_recursos = {"vcpu": int(recursos[0][0]), "ram": int(recursos[0][1]), "disk":int(recursos[0][2])}
            vm=Vm(nodo_key ,vm_recursos["ram"],vm_recursos["disk"],vm_recursos["vcpu"])
            lista_vm_topologia.append(vm)

    zona_disponibilidad= data['zona']['nombre']
    lista_worker_general_filtrada=filtrado(zona_disponibilidad, FACTOR)
    # print("** Los workers filtrados por zona de disponibilidad son:")
    # for worker in lista_worker_general_filtrada:
    #     print(f"- Worker {worker.id_servidor}")
    # print("---------------------------------------------------")
    
    result = True
    for vm in lista_vm_topologia:
        worker_elegido= ordenamiento_coeficiente(lista_worker_general_filtrada,vm)
        if worker_elegido==None:
            result = False
            break
        else:
            data["nodos"][vm.nodo_nombre]["id_worker"] = worker_elegido.id_servidor
            # print(data)
            # print("---------------------------------------------------")

    return data, result