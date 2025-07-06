import requests
#import schedule as sch
import time
import datetime

import schedule

from conf.Conexion import *
from conf.ConfigManager import config


class Validador:
    def __init__(self):
        pass

    def validar_recursos(self, nombre,recursos):
        validador= Validador()
        data_actual = validador.obtenerDataActual()
        data_actual=data_actual[0]
        data_actual = data_actual[nombre]
        ram_actual = data_actual["ram"]
        vcpu_actual = data_actual["vcpu"]
        storage_actual = data_actual["storage"]
        valid = False
        if vcpu_actual > recursos[0] & ram_actual > recursos[1] & storage_actual > recursos[2]:
            valid = True
        return valid


    def validar_estado_vm(delf, vm):
        con = Conexion()
        estado_vm = con.Select("estado","vm",f"nombre = '{vm}'")
        estado_vm=estado_vm[0]
        return estado_vm[0]

    def registrarDataCadaMinuto(self):
        conn = Conexion()
        con = conn.conectar()
        server_names = config.get_worker_names()
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        try:
            with con.cursor() as cur:
                validador = Validador()
                schedule.every(1).minutes.do(validador.registerAllData(server_names),cur=cur,conn=con,timestamp=timestamp)
                while True:
                    schedule.run_pending()
                    time.sleep(1)
        finally:
            con.close()

    def obtenerDataActual(self):
        cluster_config = config.get_cluster_config()
        url = f"{cluster_config['api_url']}{cluster_config['metrics_endpoint']}"
        data_actual = requests.get(url)
        #datos = [ram]
        #header = {'accept': 'application/json'}
        return data_actual.json()

    def registerData(self,nombre):
        validador = Validador()
        conn = Conexion()
        #nombre = "headnode"
        id = conn.Select("id_recurso","servidor",f"nombre = '{nombre}'")
        id=id[0]
        #data = conn.Select("ram,vcpu,storage","recursos",f"id_estado = {id[0]}")
        data_actual = validador.obtenerDataActual()
        print("datos validador")
        print(data_actual)
        data_actual=data_actual[0]
        print(data_actual[nombre])
        data_actual = data_actual[nombre]
        ram_actual = data_actual["ram"]
        vcpu_actual = data_actual["vcpu"]
        storage_actual = data_actual["storage"]
        #porcentajes
        #ram_actual = ((data[0]-ram_actual)/data[0])*100
        #vcpu_actual = ((data[1]-vcpu_actual)/data[1])*100
        #vcpu_actual = data[1]-vcpu_actual
        #storage_actual = ((data[2]-storage_actual)/data[2])*100
        #registrar
        conn.Insert("recursos","ram_available,vcpu_available,storage_available",f"{ram_actual},{vcpu_actual},{storage_actual}")


    def registerAllData(cur, server_names):
        validador = Validador()
        #server_names = [headnode,worker1,worker2]
        for i in server_names:
            validador.registerData(i)

