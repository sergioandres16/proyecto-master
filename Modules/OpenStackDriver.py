import secrets as s
import requests
from conf.Conexion import *
from datetime import datetime
import json
import random

TOKEN = ""
id_flavor_list = []


def get_token():
    d = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "domain": {
                            "id": "default",
                            "name": "Default"
                        },
                        "name": "admin",
                        "password": "grupo_1"
                    }
                }
            },
            "scope": {
                "project": {
                    "domain": {
                        "id": "default"
                    },
                    "name": "admin"
                }
            }
        }
    }
    response = requests.post(f'http://10.20.12.54:5000/v3/auth/tokens', json=d)
    return response


def create_flavor(token, nombre, ram, vcpu, disk):
    h = {"X-Auth-Token": token}
    d = {
        "flavor": {
            "name": nombre,
            "ram": ram,
            "vcpus": vcpu,
            "disk": disk,
            "rxtx_factor": 1.0
        }
    }
    response = requests.post(f'http://10.20.12.54:8774/v2.1/flavors', headers=h, json=d)
    return response.json()["flavor"]["id"]


def get_flavors_id(token, nombre):
    h = {"X-Auth-Token": token}
    response = requests.get(f'http://10.20.12.54:8774/v2.1/flavors/detail', headers=h)
    id_flavor = ""
    for fl in response.json()["flavors"]:
        if (fl["name"] == nombre):
            id_flavor = fl["id"]
    return id_flavor


def OpenStack_main(slice):
    conn = Conexion()
    conn2 = Conexion2()
    response = get_token()
    TOKEN = response.headers["X-Subject-Token"]
    id_s = conn.Select("id_slice", "slice", "nombre=" + "'" + slice["nombre"] + "'" + "limit 1")
    # nombre_red=input("Ingresa nombre: ")
    nombre_slice = slice["nombre"]
    network_complete = create_network(TOKEN, nombre_slice)
    network_id = network_complete["id"]
    create_subnet(TOKEN, network_id, nombre_slice + "_subred", generarCIDR())
    maxvlan = conn.GetMaxVlan()
    maxvlan = maxvlan[0][0]
    if maxvlan == None:
        maxvlan = 0
    vlan = maxvlan + 1
    if (len(id_s) == 0):
        id_slice = conn.Insert("slice", "nombre,tipo,vlan_id,fecha_creacion,fecha_modificacion",
                               f"'{nombre_slice}','openstack',{vlan},now(),now()")
    else:
        id_slice = id_s[0][0]
    vm_nombres = generar_vm_token(slice["nodos"])
    nombre_flavor = 1
    for nodo_key in slice["nodos"]:
        nodo = slice["nodos"][nodo_key]
        if ((nodo["config"]["imagen"]["url"]) == "-"):
            id_i = conn.Select("id_imagen", "imagen",
                               "nombre=" + "'" + nodo["config"]["imagen"]["nombre"] + "'" + "limit 1")
            id_imagen = id_i[0][0]
        else:
            imagen_nombre = nodo["config"]["imagen"]["nombre"]
            id_i = conn.Select("id_imagen", "imagen",
                               "nombre=" + "'" + nodo["config"]["imagen"]["nombre"] + "'" + "limit 1")

            if (len(id_i) == 0):
                id_imagen = conn.Insert("imagen", "nombre,fecha_creacion", f"'{imagen_nombre}',now()")
            else:
                id_imagen = id_i[0][0]
        if (nodo["instanciado"] == "false"):
            vm_nombre = vm_nombres[nodo_key]
            if nodo["config"]["type"] == "manual":
                recursos = nodo["config"]["info_config"]
                vm_recursos = {"vcpu": int(recursos[0]), "ram": int(recursos[1]), "disk": int(recursos[2])}
                id_flavor = create_flavor(TOKEN, str(nombre_flavor), int(recursos[1]), int(recursos[0]),
                                          int(recursos[2]))
                id_flavor_list.append(id_flavor)
            else:
                recursos = conn.Select("cpu,ram,storage", "flavor",
                                       "nombre=" + "'" + nodo["config"]["info_config"] + "'")
                vm_recursos = {"vcpu": int(recursos[0][0]), "ram": int(recursos[0][1]), "disk": int(recursos[0][2])}
                nombre_flavor = nodo["config"]["info_config"]
                id_flavor = get_flavors_id(TOKEN, nombre_flavor)
            # EXTRA
            enlaces = []
            vnc_port = -100
            for i in range(len(nodo["enlaces"])):
                enlaces.append(vm_nombres[nodo["enlaces"][i]])
            imagen = nodo["config"]["imagen"]
            vm_worker_id = nodo["id_worker"]

            # if str(vm_worker_id) not in worker_list:
            #     worker_list.append(str(vm_worker_id))

            enlaces = ",".join(enlaces)
            data = {"vm_token": vm_nombre,
                    "vm_recursos": vm_recursos,
                    "enlaces": enlaces,
                    "imagen": imagen,
                    "vlan_id": vlan,
                    "vnc_port": vnc_port,
                    "vm_worker_id": vm_worker_id}
            # FIN EXTRA
            servidor = conn.Select('nombre', 'servidor', f'id_servidor={vm_worker_id}')
            nombre_servidor = servidor[0][0]
            id_vm_creada = create_server(TOKEN, "vm-" + vm_nombre, id_flavor, network_id, nombre_servidor)

            if (id_vm_creada != ""):
                nodo["instanciado"] = "True"
                # AGREGAR PARÁMETROS A BD
                # --------CREACIÓN DE TABLA RECURSOS--------#
                ram = vm_recursos["ram"]
                disk = vm_recursos["disk"]
                vcpu = vm_recursos["vcpu"]
                nombre = "vm-" + data["vm_token"]

                id_recursos = conn.Insert("recursos", "ram,storage,vcpu", f"'{ram}','{disk}','{vcpu}'")

                id_vm = conn.Insert("vm",
                                    "nombre,estado,fecha_creacion,creado_por,fecha_modificacion,modificado_por,vnc,servidor_id_servidor,topologia_id_topologia,imagen_id_imagen,recursos_id_estado",
                                    f"'{nombre}','ACTIVO',now(),1,now(),1,{vnc_port},{vm_worker_id},{id_slice},1,{id_recursos}")

                id_nodo = conn2.Insert("nodo", "nombre,tipo,puerto_vnc", f"'{nombre}',1,{vnc_port}")
                id_ram = conn2.Insert("ram", "memoria_total, creacion, Nodo_id_nodo", f"'{ram}',now(),{id_nodo}")
                id_cpu = conn2.Insert("cpu", "memoria_total, creacion, Nodo_id_nodo", f"'{disk}',now(),{id_nodo}")
                id_vcpu = conn2.Insert("vcpu", "vcpu_total, creacion, Nodo_id_nodo", f"'{vcpu}',now(),{id_nodo}")
                id_enlace = conn2.Insert("enlace", "nombre,nodo_id_nodo", f"'{enlaces}',{id_nodo}")

            else:
                print("Falló la creación de la vm " + data["vm_nombre"])
    slice["estado"] = "ejecutado"
    slice["mapeo_nombres"] = vm_nombres
    return slice


def generar_vm_token(nodos):
    vm_nombres = {}
    for nodo_key in nodos:
        vm_nombres[nodo_key] = s.token_hex(3)
    return vm_nombres


def generarCIDR():
    cidr = "10."
    n1 = random.randint(0, 254)
    n2 = random.randint(0, 255)
    cidr = cidr + str(n1) + "." + str(n2) + "." + "0/24"
    return cidr


def create_network(token, net_name):
    # TODO: ver bien lo que es 'segmentation_id'
    response = 0
    h = {"X-Auth-Token": token}
    d = {
        "network": {
            "admin_state_up": "true",
            "name": net_name,
            "provider:network_type": "vlan",
            "provider:physical_network": "external",
            "provider:segmentation_id": str(random.randrange(10, 100)),
            "shared": "true"
        }
    }
    response = requests.post(f'http://10.20.12.54:9696/v2.0/networks', json=d, headers=h)
    # print(response.json())
    return response.json()["network"]


def create_subnet(token, network_id, subnet_name, cidr):
    h = {"X-Auth-Token": token}
    ip_numbers = cidr.split(".")
    gateway_ip = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}.1"
    net_start = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}.2"
    net_end = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}.254"
    d = {
        "subnet": {
            "name": subnet_name,
            "network_id": network_id,
            "cidr": cidr,
            "gateway_ip": gateway_ip,
            "dns_nameservers": ["8.8.8.8"],
            "allocation_pools": [
                {
                    "start": net_start,
                    "end": net_end
                }
            ],
            "ip_version": 4
        }
    }
    response = requests.post(f'http://10.20.12.54:9696/v2.0/subnets', json=d, headers=h)
    # print(f"CODE STATUS: {response.status_code}")


def create_server(token, vm_name, flavor_id, network_id, compute):
    h = {"X-Auth-Token": token, "X-OpenStack-Nova-API-Version": "2.74"}
    d = {
        "server": {
            "name": vm_name,
            "flavorRef": flavor_id,
            "imageRef": "5541ad5d-28ea-448f-a99d-2c5a20be5db3",
            "networks": [{
                "uuid": network_id
            }],
            "key_name": "llaves",
            "security_groups": [
                {
                    "name": "default"
                }
            ],
            "hypervisor_hostname": compute
        }
    }

    response = requests.post(f'http://10.20.12.54:8774/v2.1/servers', json=d, headers=h)
    # print(response.json())
    return response.json()["server"]["id"]


def borrar_slice_openstack(slice):
    # print("-------OPENSTACK - BORRANDO SLICE ---------")
    # print(slice)
    conn = Conexion()
    conn2 = Conexion2()
    nombre_slice = slice["nombre"]
    id_s = conn.Select("id_slice", "slice", "nombre=" + "'" + slice["nombre"] + "'")
    vms = conn.Select("nombre,servidor_id_servidor", "vm", "topologia_id_topologia= " + str(id_s[0][0]))
    i = 0
    for nodo in list(slice["nodos"]):
        nombre_vm = vms[i][0]
        # print(nombre_vm +" -> nombre de la vm a borrar openstack")
        vm_worker_id = vms[i][1]
        nombre_nodo = nodo

        id_nodo_cluster = conn2.Select("id_nodo", "nodo", "nombre= " + "'" + nombre_vm + "'")
        # taps=conn2.Select("nombre","enlace","nodo_id_nodo= "+id_nodo_cluster[0][0])

        id_vm = get_vms_id(TOKEN, nombre_vm)
        delete_vms_id(TOKEN, id_vm)

        if (id_vm != ""):
            id_nodo_general = conn.Select("id_vm", "vm", "nombre= " + "'" + nombre_vm + "'")
            id_recurso_general = conn.Select("recursos_id_estado", "vm", "nombre= " + "'" + nombre_vm + "'")
            conn.Delete("vm", "id_vm= " + str(id_nodo_general[0][0]))
            conn.Delete("recursos", "id_recursos= " + str(id_recurso_general[0][0]))

            conn2.Delete("enlace", "nodo_id_nodo= " + str(id_nodo_cluster[0][0]))
            conn2.Delete("vcpu", "Nodo_id_nodo= " + str(id_nodo_cluster[0][0]))
            conn2.Delete("cpu", "Nodo_id_nodo= " + str(id_nodo_cluster[0][0]))
            conn2.Delete("ram", "Nodo_id_nodo= " + str(id_nodo_cluster[0][0]))

        i = i + 1
    conn.Delete("slice", "nombre= " + "'" + slice["nombre"] + "'")
    conn2.Delete("nodo", "nombre= " + "'" + nombre_vm + "'")
    print("Slice " + nombre_slice + " BORRADO EXITOSAMENTE!")


def get_vms_id(token, nombre):
    response = get_token()
    TOKEN = response.headers["X-Subject-Token"]
    h = {"X-Auth-Token": TOKEN, "X-OpenStack-Nova-API-Version": "2.47"}
    response = requests.get(f'http://10.20.12.54:8774/v2.1/servers/detail', headers=h)
    vm_id = "-1"
    # print(response.json())
    for vm in response.json()["servers"]:
        if (vm["name"] == nombre):
            vm_id = vm["id"]
    return vm_id


def delete_vms_id(token, id_vm):
    response = get_token()
    TOKEN = response.headers["X-Subject-Token"]
    h = {"X-Auth-Token": TOKEN, "X-OpenStack-Nova-API-Version": "2.47"}
    response = requests.delete(f'http://10.20.12.54:8774/v2.1/servers/{id_vm}', headers=h)


def info_computes():
    response = get_token()
    TOKEN = response.headers["X-Subject-Token"]
    h = {"X-Auth-Token": TOKEN, "X-OpenStack-Nova-API-Version": "2.47"}
    rp = requests.get(f'http://10.20.12.54:8774/v2.1/os-hypervisors/detail', headers=h)
    # valores en bytes
    # print(rp.json())
    mega = 1048576
    gb = 1073741824
    valor = '['
    for hy in rp.json()["hypervisors"]:
        # print(hy["hypervisor_hostname"]+"----freeram "+str(hy["free_ram_mb"])+" vcpufree"+str(hy["vcpus"]-hy["vcpus_used"])+"free_disk_gb "+str(hy["free_disk_gb"]))
        ram = str(mega * hy["free_ram_mb"])
        ramT = str(mega * hy["memory_mb"])
        storage = str(gb * hy["free_disk_gb"])
        storageT = str(gb * hy["local_gb"])
        cores = str(hy["vcpus"] - hy["vcpus_used"])
        coreT = str(hy["vcpus"])
        nombre = hy["hypervisor_hostname"]
        valor = valor + '{"' + nombre + '": {"ram": "' + ram + '", "vcpu": "' + cores + '", "storage": "' + storage + '"}}, '
        guardarRecursos(nombre, coreT, ramT, storageT, ram, storage, coreT, cores)
    valor = valor[:-2] + ']'
    out = json.loads(valor)
    return out


def guardarRecursos(nombre, cpu, ram, storage, ramUtil, storageU, vcpu, vcpuUtil):
    conexion = Conexion()
    tupla = conexion.Select('id_recurso', 'servidor', f"nombre= '{nombre}'")
    fecha_actual = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    if (len(tupla) != 0):
        id_recurso_encontrado = tupla[0][0]
        conexion.Update('recursos', f'ram_available="{ramUtil}",storage_available="{storageU}"',
                        f'id_recursos={int(id_recurso_encontrado)}')
        conexion.Update('servidor', f"fecha_modificacion='{fecha_actual}'", f'id_recurso={id_recurso_encontrado}')
        # valor=conexion.Select('vcpu_available','recursos',f'id_recursos={id_recurso_encontrado}')
    else:
        id_recurso = conexion.Insert('recursos', 'cpu,ram,storage,ram_available,storage_available,vcpu,vcpu_available',
                                     f'{cpu},{ram},{storage},{ramUtil},{storageU},{vcpu},{vcpuUtil}')
        conexion.Insert('servidor', 'nombre,descripcion,fecha_creacion,ip,id_zona,id_recurso,fecha_modificacion',
                        f'"{nombre}","openstack","{fecha_actual}","openstack",{1},{id_recurso},"{fecha_actual}"')