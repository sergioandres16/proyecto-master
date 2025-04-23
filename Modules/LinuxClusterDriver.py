
import random
import secrets as s
import requests
from conf.Conexion import *
from Modules.SliceAdministrator import *
from datetime import datetime
import json

def generador_mac():
    return "02:%02x:%02x:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generar_vm_token(nodos):
    vm_nombres = {}
    for nodo_key in nodos:
        vm_nombres[nodo_key] = s.token_hex(3)
    return vm_nombres

def linux_driver_main(slice):
    print(slice)
    #fecha_actual= datetime.today()
    conn = Conexion()
    conn2= Conexion2()
    id_s=conn.Select("id_slice","slice","nombre="+"'"+slice["nombre"]+"'"+"limit 1")
    
    # VLAN ID actually ranges from 1 to 4094
    maxvlan= conn.GetMaxVlan()
    maxvlan=maxvlan[0][0]
    if maxvlan==None:
        maxvlan=0
    #print(type(maxvlan))
    #print(maxvlan)
    #TODO: COMPLETAR
    vlan=maxvlan+1
    nombre_slice = slice["nombre"]
    if(len(id_s)==0):
        id_slice=conn.Insert("slice", "nombre,tipo,vlan_id,fecha_creacion,fecha_modificacion", f"'{nombre_slice}','linux_cluster',{vlan},now(),now()")
    else:
        id_slice=id_s[0][0]
    #print(id_slice)
    vm_nombres = generar_vm_token(slice["nodos"])
    
    worker_list = [] #Para crear el flow
    for nodo_key in slice["nodos"]:
        nodo = slice["nodos"][nodo_key]
        #print(nodo["instanciado"])
        print(nodo["config"]["imagen"]["nombre"])

        if ((nodo["config"]["imagen"]["url"])=="-"):
            id_i= conn.Select("id_imagen","imagen","nombre="+"'"+nodo["config"]["imagen"]["nombre"]+"'"+"limit 1")
            id_imagen=id_i[0][0]
        else:
            imagen_nombre=nodo["config"]["imagen"]["nombre"]
            id_i= conn.Select("id_imagen","imagen","nombre="+"'"+nodo["config"]["imagen"]["nombre"]+"'"+"limit 1")
            
            if (len(id_i)==0):
                id_imagen=conn.Insert("imagen", "nombre,fecha_creacion", f"'{imagen_nombre}',now()")
            else:
                id_imagen=id_i[0][0]

        
        if(nodo["instanciado"]=="false"):
            vm_nombre = vm_nombres[nodo_key]
            if nodo["config"]["type"] == "manual":
                recursos = nodo["config"]["info_config"]
                vm_recursos = {"vcpu": int(recursos[0]), "ram": int(recursos[1]), "disk":int(recursos[2])}
            else:
                recursos=conn.Select("cpu,ram,storage","flavor","nombre="+"'"+nodo["config"]["info_config"]+"'")
                vm_recursos = {"vcpu": int(recursos[0][0]), "ram": int(recursos[0][1]), "disk":int(recursos[0][2])}
            enlaces=[]
            for i in range(len(nodo["enlaces"])):
                enlaces.append(vm_nombres[nodo["enlaces"][i]])
            imagen = nodo["config"]["imagen"]
            vm_worker_id = nodo["id_worker"]
            print(type(vm_worker_id))
            max_vnc=conn.Select("max_vnc","servidor","id_servidor= "+str(vm_worker_id))
            vnc_port = max_vnc[0][0]+1

            if str(vm_worker_id) not in worker_list:
                worker_list.append(str(vm_worker_id))
            enlaces = ",".join(enlaces)
            data = {"vm_token": vm_nombre,
                    "vm_recursos": vm_recursos,
                    "enlaces":enlaces,
                    "imagen": imagen,
                    "vlan_id": vlan,
                    "vnc_port": vnc_port,
                    "vm_worker_id" : vm_worker_id}
            result = requests.post("http://10.20.12.58:8081/vm/crear", json= data)
            print(result.json())
            if (result):
                nodo["instanciado"]="true"
                #AGREGAR PARÁMETROS A BD
                #--------CREACIÓN DE TABLA RECURSOS--------#
                print(vm_recursos)
                ram= vm_recursos["ram"]
                disk=vm_recursos["disk"]
                vcpu=vm_recursos["vcpu"]
                nombre="vm-"+data["vm_token"]
                
                conn.Update("servidor","max_vnc= "+str((vnc_port)),"id_servidor= "+str(vm_worker_id))
                id_recursos=conn.Insert("recursos", "ram,storage,vcpu", f"'{ram}','{disk}','{vcpu}'")

                id_vm=conn.Insert("vm", "nombre,estado,fecha_creacion,creado_por,fecha_modificacion,modificado_por,vnc,servidor_id_servidor,topologia_id_topologia,imagen_id_imagen,recursos_id_estado", f"'{nombre}','ACTIVO',now(),1,now(),1,{vnc_port},{vm_worker_id},{id_slice},{id_imagen},{id_recursos}")

                id_nodo=conn2.Insert("nodo", "nombre,tipo,puerto_vnc", f"'{nombre}',1,{vnc_port}")
                id_ram=conn2.Insert("ram", "memoria_total, creacion, Nodo_id_nodo", f"'{ram}',now(),{id_nodo}")
                id_cpu=conn2.Insert("cpu", "memoria_total, creacion, Nodo_id_nodo", f"'{disk}',now(),{id_nodo}")
                id_vcpu=conn2.Insert("vcpu", "vcpu_total, creacion, Nodo_id_nodo", f"'{vcpu}',now(),{id_nodo}")
                id_enlace=conn2.Insert("enlace", "nombre,nodo_id_nodo", f"'{enlaces}',{id_nodo}")
                
            else:
                print("Falló la creación de la vm "+ data["vm_token"])
            vnc_port += 1
    #Creamos el flow:
    # worker_list = "-" if len(worker_list)==0 else ",".join(worker_list)
    #print("-------------------------------------------------------------------------------------------")
    slice["estado"]="ejecutado"
    worker_list = ",".join(worker_list)
    flow_data={"vlan_id": vlan, "workers_id": worker_list}
    result = requests.post("http://10.20.12.58:8081/OFS/flows", json= flow_data)
    slice["mapeo_nombres"] = vm_nombres
    #sliceobj=SliceAdministrator()
    #sliceobj.save_slice(slice)
    f = open(f"./Modules/Slices/{slice['nombre']}.json", "w")
    f.write(json.dumps(slice))
    f.close()
    #print(f"* Slice {slice['nombre']} guardado.")

    print (slice)
    return slice
    
def borrar_slice(slice):
    print("---------------------------")
    print(slice)
    conn= Conexion()
    id_s=conn.Select("id_slice","slice","nombre="+"'"+slice["nombre"]+"'")
    vms=conn.Select("nombre,servidor_id_servidor","vm","topologia_id_topologia= "+str(id_s[0][0]))
    print(vms)
    i=0
    for nodo in list(slice["nodos"]):
        print(nodo)
        nombre_vm= vms[i][0]
        vm_worker_id = vms[i][1]
        nombre_nodo=nodo
        print(nombre_vm)
        print(vm_worker_id)
        conn2=Conexion2()
        id_nodo_cluster=conn2.Select("id_nodo","nodo","nombre= "+"'"+nombre_vm+"'")
        enlaces_db=conn2.Select("nombre","enlace","nodo_id_nodo= "+str(id_nodo_cluster[0][0]))
        enlaces_list = enlaces_db[0][0].split(",")
        taps_list = []
        for enlace_nombre in enlaces_list:
            tap = f"{nombre_vm[3:]}-{enlace_nombre}"
            taps_list.append(tap)
        result = requests.get("http://10.20.12.58:8081/vm/borrar?worker_id="+str(vm_worker_id)+"&vm_name="+nombre_vm+"&taps="+str(",".join(taps_list)))
        if (result):
            
            id_nodo_general= conn.Select("id_vm","vm","nombre= "+"'"+nombre_vm+"'")
            id_recurso_general= conn.Select("recursos_id_estado","vm","nombre= "+"'"+nombre_vm+"'")
            conn.Delete("vm","id_vm= "+str(id_nodo_general[0][0]))
            conn.Delete("recursos","id_recursos= "+str(id_recurso_general[0][0]))
            
            conn2.Delete("enlace","nodo_id_nodo= "+str(id_nodo_cluster[0][0]))
            conn2.Delete("vcpu","Nodo_id_nodo= "+str(id_nodo_cluster[0][0]))
            conn2.Delete("cpu","Nodo_id_nodo= "+str(id_nodo_cluster[0][0]))
            conn2.Delete("ram","Nodo_id_nodo= "+str(id_nodo_cluster[0][0]))
            
            i=i+1
    conn.Delete("slice", "nombre= "+"'"+slice["nombre"]+"'")
    conn2.Delete("nodo", "nombre= "+"'"+nombre_vm+"'")
            

    

    