
from Modules.App_Scheduler import *
from Modules.LinuxClusterDriver import *
from Modules.OpenStackDriver import *
from conf.Conexion import *
from conf.ConfigManager import config
from Modules.Validador import  *
import json
import os

class SliceAdministrator:
    def __init__(self):
        pass

    def create_topology(self, grafo,tipo):
        resource_factor = config.get('RESOURCE_FACTOR')
        slice, result = scheduler_main(grafo, resource_factor)
        if result:
            print("-----------------")
            print(slice)
            if (tipo == "1"):
                nuevo_slice = linux_driver_main(slice)
            if (tipo == "2"):
                nuevo_slice = OpenStack_main(slice)
            return nuevo_slice
        else:
            return False


    def delete_slice(self,slice,tipo):
        print("-----")
        print(slice)
        conn = Conexion()
        nombre=slice["nombre"]
        id = conn.Select("id_slice", "slice", f" nombre = '{nombre}'")
        id=id[0]
        vms= conn.Select("nombre,estado","vm", f" topologia_id_topologia = {id[0]}")
        lista_activo=[]
        lista_inactivo=[]
        message=""
        validador = Validador()
        for vm in vms:
            val = validador.validar_estado_vm(vm[0])
            if val == 'INACTIVO':
                lista_inactivo.append(vm[0])
            elif val == 'ACTIVO':
                lista_activo.append(vm[0])

        if len(lista_inactivo) == len(vms):
            if (tipo == "1"):
                borrar_slice(slice)
            if (tipo == "2"):
                borrar_slice_openstack(slice)
            message = f"Se borró el slice {slice} y sus respectivas VMs"
        else:
            message = f"No se pudo borrar el slice {slice} porque las VMs: {lista_activo} están activas."
        return message

    def update_slice(self, slice, tipo):
        sa = SliceAdministrator()
        slice_actualizado = sa.create_topology(slice, tipo)
        return  slice_actualizado

    def save_slice(self, slice):
        #llamar a driver para actualizar
        paths_config = config.get_paths_config()
        slice_path = f"{paths_config['slices_config_path']}{slice['nombre']}{paths_config['slice_file_extension']}"
        f = open(slice_path, "w")
        f.write(json.dumps(slice))
        f.close()
        print(f"* Slice {slice['nombre']} guardado.")

    def register_data(self):
        validador = Validador()
        validador.registrarDataCadaMinuto()

    def create_slice(self, slice,tipo):
        #tipo 1- clustter linux
        #tipo 2- openstack
        sa = SliceAdministrator()
        slice_nuevo = sa.create_topology(slice,tipo)
        return slice_nuevo