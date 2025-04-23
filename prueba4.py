import requests
from conf.Conexion import *
slice={"nodos": {"n0": {"enlaces": ["n1"], "config": {"type": "manual", "info_config": ["1", "256", "1"], "imagen": "cirros"}, "id_worker": 6, "instanciado":"False"}, "n1": {"enlaces": ["n0", "n2"], "config": {"type": "manual", "info_config": ["1", "256", "1"], "imagen": "cirros"}, "id_worker": 1, "instanciado":"False"}, "n2": {"enlaces": ["n1"], "config": {"type": "manual", "info_config": ["1", "256", "1"], "imagen": "cirros"}, "id_worker": 4,"instanciado":"False"}}, "nombre": "prueba2", "ultimo_nodo": 1, "zona": {"nombre": "Pabellon V"}, "nodo_eliminar":"n0", "mapeo_nombre":{"n0":"ccc","n1":"ddd","n2":"eee"}}






conn2=Conexion2()

taps=conn2.Select("nombre","enlace","nodo_id_nodo= "+"2")
print(taps)

'''
recursos=conn.Select("cpu,ram,storage","flavor","nombre="+"'"+"m1.tiny"+"'")
vm_recursos = {"vcpu": int(recursos[0][0]), "ram": int(recursos[0][1]), "disk":int(recursos[0][2])}
print(vm_recursos)

conn=Conexion()
id_s=conn.Select("id_slice","slice","nombre='prueba2' limit 1")
print(id)

if(len(id)==0):
    print("Hola")



for n in list(slice["nodos"]):
    nodo = slice["nodos"][n]
    nodo["instanciado"]="True"

print(slice)


for nodo in list(slice["nodos"]):
    nombre_vm= slice["mapeo_nombre"][nodo]
    vm_worker_id = slice["nodos"][nodo]["id_worker"]
    nombre_nodo=nodo
    #print(nombre_vm)
    #print(vm_worker_id)
    conn2=Conexion2()
    id_nodo_cluster=conn2.Select("id_nodo","nodo","nombre= "+nombre_vm)
    taps=conn2.Select("nombre","enlace","nodo_id_nodo= "+id_nodo_cluster)
    result = requests.get("http://10.20.12.58:8081/vm/borrar?worker_id="+vm_worker_id+"&vm_name="+nombre_vm+"&taps="+taps)
    if (result):
        conn= Conexion()
        id_nodo_general= conn.Select("id_vm","vm","nombre= "+nombre_vm)
        id_recurso_general= conn.Select("recursos_id_estado","vm","nombre= "+nombre_vm)
        conn.Delete("recursos","id_recursos= "+id_recurso_general)
        conn.Delete("vm","id_vm= "+id_nodo_general)
        conn2.Delete("nodo", "nombre= "+nombre_vm)
        conn2.Delete("enlace","nodo_id_nodo= "+id_nodo_cluster)

'''

