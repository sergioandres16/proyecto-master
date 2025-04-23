import pymysql
import requests
from conf.Conexion import *
lista_worker_general_filtrada=[]

class Worker:
    def __init__ (self, id_servidor,ram_disponible, disco_disponible, vcpu_disponible, ram, disco, vcpu):
        self.id_servidor=id_servidor
        self.ram_disponible=ram_disponible
        self.disco_disponible=disco_disponible
        self.vcpu_disponible=vcpu_disponible
        self.ram=ram
        self.disco=disco
        self.vcpu=vcpu

class Vm:
    def __init__ (self,nodo_nombre , ram_requerida, disco_requerido, vcpu_requeridas):
        self.nodo_nombre = nodo_nombre
        self.ram_requerida=ram_requerida
        self.disco_requerido=disco_requerido
        self.vcpu_requeridas=vcpu_requeridas



def filtrado(zona_disponibilidad, FACTOR):
    #Hacer select de todos los workers y filtrarlos (query con un where zona_disponibilidad =)#
    query="select s.id_servidor, r.ram_available, r.storage_available, r.vcpu_available, r.ram, r.storage, r.vcpu from recursos as r inner join servidor as s on s.id_recurso=r.id_recursos inner join zona_disponibilidad as zd on zd.idzona_disponibilidad=s.id_zona where zd.nombre= %s"

    ip="10.20.12.35"
    username="grupo1_final"
    paswd="grupo1_final"
    database="bd_general"
    con = pymysql.connect(host=ip,user= username,password=paswd, db=database)
    resultado=[]
    try:
        with con.cursor() as cur1:
            cur1.execute(query, (zona_disponibilidad,))
        resultado1 = cur1.fetchall()

        for f in resultado1:
            worker=Worker(f[0],float(f[1])*FACTOR,float(f[2])*FACTOR,float(f[3])*FACTOR,float(f[4])*FACTOR,float(f[5])*FACTOR,float(f[6])*FACTOR)
            lista_worker_general_filtrada.append(worker)
    finally:
        con.close()
        return lista_worker_general_filtrada

def takeSecond(elem):
    return elem[0]


def calculo_coeficiente(ram_disponible, disco_disponible, vcpu_requeridas, vcpu_disponible,ram,disco):
    if (ram==0 or disco==0 or vcpu_disponible==0):
        coeficiente = 0
    else:
        coeficiente = 0.5*(ram_disponible/ram)+0.25*(disco_disponible/disco) + 0.25*(vcpu_requeridas/vcpu_disponible)
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
            ram_disponible_new= worker.ram_disponible - (vm.ram_requerida*1048576)
            disco_disponible_new = worker.disco_disponible - (vm.disco_requerido*1073741824)
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