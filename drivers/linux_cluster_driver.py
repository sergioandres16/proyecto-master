"""
===================================================================
LINUX CLUSTER DRIVER - DRIVER MODULAR
===================================================================

Driver modular para gestión de clusters Linux con OpenFlow.
Proporciona funcionalidades para crear, gestionar y eliminar
slices en infraestructura de cluster Linux.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

import requests
import secrets
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .base_driver import BaseDriver
from conf.Conexion import Conexion, Conexion2


class LinuxClusterDriver(BaseDriver):
    """
    Driver para gestión de clusters Linux con VMs y switches OpenFlow.
    
    Características:
    - Creación de VMs en workers específicos
    - Gestión automática de VLANs
    - Configuración de flows OpenFlow
    - Asignación de puertos VNC
    - Persistencia en base de datos
    """
    
    def __init__(self):
        """
        Inicializa el driver de Linux Cluster.
        """
        super().__init__()
        self.cluster_config = self.config.get_cluster_config()
        
    def create_slice(self, slice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un slice completo en el cluster Linux.
        
        Args:
            slice_data: Datos del slice a crear
            
        Returns:
            Dict con el slice actualizado
        """
        try:
            if not self.validate_slice_data(slice_data):
                raise ValueError("Datos de slice inválidos")
            
            self.logger.info(f"Iniciando creación de slice: {slice_data['nombre']}")
            
            # 1. Obtener o crear ID del slice
            slice_id = self._get_or_create_slice_id(slice_data)
            
            # 2. Generar nombres únicos para VMs
            vm_names = self._generate_vm_names(slice_data['nodos'])
            
            # 3. Crear VMs por nodo
            worker_list = []
            for node_key, node_data in slice_data['nodos'].items():
                if node_data.get('instanciado', 'false') == 'false':
                    success, worker_id = self._create_vm_for_node(
                        node_key, node_data, vm_names, slice_id, slice_data
                    )
                    
                    if success:
                        node_data['instanciado'] = 'true'
                        if str(worker_id) not in worker_list:
                            worker_list.append(str(worker_id))
            
            # 4. Configurar flows OpenFlow
            if worker_list:
                self._configure_openflow_flows(slice_data.get('vlan_id'), worker_list)
            
            # 5. Actualizar estado y guardar
            slice_data['estado'] = 'ejecutado'
            slice_data['mapeo_nombres'] = vm_names
            
            self.save_slice_to_file(slice_data)
            
            self.logger.info(f"Slice {slice_data['nombre']} creado exitosamente")
            return slice_data
            
        except Exception as e:
            self.logger.error(f"Error creando slice: {e}")
            raise
    
    def delete_slice(self, slice_data: Dict[str, Any]) -> bool:
        """
        Elimina un slice completo del cluster Linux.
        
        Args:
            slice_data: Datos del slice a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            self.logger.info(f"Iniciando eliminación de slice: {slice_data['nombre']}")
            
            conn = Conexion()
            conn2 = Conexion2()
            
            # Obtener ID del slice
            slice_id_result = conn.Select("id_slice", "slice", f"nombre='{slice_data['nombre']}'")
            if not slice_id_result:
                self.logger.warning(f"Slice {slice_data['nombre']} no encontrado en BD")
                return False
            
            slice_id = slice_id_result[0][0]
            
            # Obtener VMs del slice
            vms = conn.Select("nombre,servidor_id_servidor", "vm", f"topologia_id_topologia={slice_id}")
            
            # Eliminar cada VM
            for i, (vm_name, worker_id) in enumerate(vms):
                success = self._delete_vm(vm_name, worker_id, conn, conn2)
                if not success:
                    self.logger.warning(f"Fallo eliminando VM {vm_name}")
            
            # Eliminar slice de BD
            conn.Delete("slice", f"nombre='{slice_data['nombre']}'")
            
            self.logger.info(f"Slice {slice_data['nombre']} eliminado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando slice: {e}")
            return False
    
    def get_slice_status(self, slice_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un slice.
        
        Args:
            slice_name: Nombre del slice
            
        Returns:
            Dict con el estado del slice
        """
        try:
            conn = Conexion()
            
            # Obtener información del slice
            slice_info = conn.Select(
                "id_slice,nombre,tipo,vlan_id,estado,fecha_creacion",
                "slice",
                f"nombre='{slice_name}'"
            )
            
            if not slice_info:
                return {"error": "Slice no encontrado"}
            
            slice_id, name, tipo, vlan_id, estado, fecha_creacion = slice_info[0]
            
            # Obtener VMs del slice
            vms = conn.Select(
                "nombre,estado,vnc,servidor_id_servidor",
                "vm",
                f"topologia_id_topologia={slice_id}"
            )
            
            vm_list = []
            for vm_name, vm_estado, vnc_port, worker_id in vms:
                vm_list.append({
                    "nombre": vm_name,
                    "estado": vm_estado,
                    "vnc_port": vnc_port,
                    "worker_id": worker_id
                })
            
            return {
                "id": slice_id,
                "nombre": name,
                "tipo": tipo,
                "vlan_id": vlan_id,
                "estado": estado,
                "fecha_creacion": str(fecha_creacion),
                "vms": vm_list,
                "total_vms": len(vm_list)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del slice: {e}")
            return {"error": str(e)}
    
    def _get_or_create_slice_id(self, slice_data: Dict[str, Any]) -> int:
        """
        Obtiene o crea el ID del slice en la base de datos.
        
        Args:
            slice_data: Datos del slice
            
        Returns:
            int: ID del slice
        """
        conn = Conexion()
        slice_name = slice_data['nombre']
        
        # Buscar slice existente
        existing_slice = conn.Select("id_slice", "slice", f"nombre='{slice_name}' limit 1")
        
        if existing_slice:
            return existing_slice[0][0]
        
        # Obtener próximo VLAN ID
        vlan_id = self._get_next_vlan_id()
        slice_data['vlan_id'] = vlan_id
        
        # Crear nuevo slice
        slice_id = conn.Insert(
            "slice",
            "nombre,tipo,vlan_id,fecha_creacion,fecha_modificacion",
            f"'{slice_name}','linux_cluster',{vlan_id},now(),now()"
        )
        
        self.logger.info(f"Slice creado con ID {slice_id} y VLAN {vlan_id}")
        return slice_id
    
    def _get_next_vlan_id(self) -> int:
        """
        Obtiene el próximo VLAN ID disponible.
        
        Returns:
            int: Próximo VLAN ID
        """
        conn = Conexion()
        max_vlan_result = conn.GetMaxVlan()
        max_vlan = max_vlan_result[0][0]
        
        if max_vlan is None:
            max_vlan = 0
        
        return max_vlan + 1
    
    def _generate_vm_names(self, nodos: Dict[str, Any]) -> Dict[str, str]:
        """
        Genera nombres únicos para las VMs.
        
        Args:
            nodos: Diccionario de nodos
            
        Returns:
            Dict con mapeo de nodo_key -> vm_name
        """
        vm_names = {}
        for nodo_key in nodos:
            vm_names[nodo_key] = secrets.token_hex(3)
        return vm_names
    
    def _create_vm_for_node(
        self, 
        node_key: str,
        node_data: Dict[str, Any],
        vm_names: Dict[str, str],
        slice_id: int,
        slice_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[int]]:
        """
        Crea una VM para un nodo específico.
        
        Args:
            node_key: Clave del nodo
            node_data: Datos del nodo
            vm_names: Mapeo de nombres de VM
            slice_id: ID del slice
            slice_data: Datos completos del slice
            
        Returns:
            Tuple[bool, Optional[int]]: (éxito, worker_id)
        """
        try:
            conn = Conexion()
            conn2 = Conexion2()
            
            vm_name = vm_names[node_key]
            
            # Obtener recursos de VM
            vm_resources = self._get_vm_resources(node_data, conn)
            
            # Obtener imagen
            image_id = self._get_or_create_image(node_data['config']['imagen'], conn)
            
            # Obtener worker ID y puerto VNC
            worker_id = node_data['id_worker']
            vnc_port = self._get_next_vnc_port(worker_id, conn)
            
            # Preparar enlaces
            enlaces = []
            if 'enlaces' in node_data:
                enlaces = [vm_names[link] for link in node_data['enlaces'] if link in vm_names]
            
            # Crear VM en el cluster
            success = self._create_vm_in_cluster(
                vm_name, vm_resources, enlaces, node_data['config']['imagen'],
                slice_data.get('vlan_id'), vnc_port, worker_id
            )
            
            if success:
                # Guardar en base de datos
                self._save_vm_to_database(
                    vm_name, vm_resources, vnc_port, worker_id,
                    slice_id, image_id, enlaces, conn, conn2
                )
                
                # Actualizar puerto VNC máximo
                conn.Update("servidor", f"max_vnc={vnc_port}", f"id_servidor={worker_id}")
                
                return True, worker_id
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error creando VM para nodo {node_key}: {e}")
            return False, None
    
    def _get_vm_resources(self, node_data: Dict[str, Any], conn: Conexion) -> Dict[str, int]:
        """
        Obtiene los recursos de la VM según la configuración.
        
        Args:
            node_data: Datos del nodo
            conn: Conexión a la base de datos
            
        Returns:
            Dict con recursos de la VM
        """
        config = node_data['config']
        
        if config['type'] == 'manual':
            recursos = config['info_config']
            return {
                "vcpu": int(recursos[0]),
                "ram": int(recursos[1]),
                "disk": int(recursos[2])
            }
        else:
            # Obtener recursos del flavor
            flavor_name = config['info_config']
            recursos = conn.Select("cpu,ram,storage", "flavor", f"nombre='{flavor_name}'")
            
            if not recursos:
                raise ValueError(f"Flavor {flavor_name} no encontrado")
            
            return {
                "vcpu": int(recursos[0][0]),
                "ram": int(recursos[0][1]),
                "disk": int(recursos[0][2])
            }
    
    def _get_or_create_image(self, image_config: Dict[str, Any], conn: Conexion) -> int:
        """
        Obtiene o crea el ID de la imagen.
        
        Args:
            image_config: Configuración de la imagen
            conn: Conexión a la base de datos
            
        Returns:
            int: ID de la imagen
        """
        image_name = image_config['nombre']
        
        # Buscar imagen existente
        existing_image = conn.Select("id_imagen", "imagen", f"nombre='{image_name}' limit 1")
        
        if existing_image:
            return existing_image[0][0]
        
        # Crear nueva imagen si tiene URL
        if image_config.get('url', '-') != '-':
            image_id = conn.Insert("imagen", "nombre,fecha_creacion", f"'{image_name}',now()")
            return image_id
        
        raise ValueError(f"Imagen {image_name} no encontrada y no tiene URL")
    
    def _get_next_vnc_port(self, worker_id: int, conn: Conexion) -> int:
        """
        Obtiene el próximo puerto VNC disponible para un worker.
        
        Args:
            worker_id: ID del worker
            conn: Conexión a la base de datos
            
        Returns:
            int: Próximo puerto VNC
        """
        max_vnc_result = conn.Select("max_vnc", "servidor", f"id_servidor={worker_id}")
        
        if not max_vnc_result or max_vnc_result[0][0] is None:
            # Puerto VNC base desde configuración
            return self.config.get('VNC_BASE_PORT', 5900) + 1
        
        return max_vnc_result[0][0] + 1
    
    def _create_vm_in_cluster(
        self,
        vm_name: str,
        vm_resources: Dict[str, int],
        enlaces: List[str],
        imagen: Dict[str, Any],
        vlan_id: int,
        vnc_port: int,
        worker_id: int
    ) -> bool:
        """
        Crea la VM en el cluster Linux a través de la API.
        
        Args:
            vm_name: Nombre de la VM
            vm_resources: Recursos de la VM
            enlaces: Lista de enlaces
            imagen: Configuración de imagen
            vlan_id: ID de VLAN
            vnc_port: Puerto VNC
            worker_id: ID del worker
            
        Returns:
            bool: True si la creación fue exitosa
        """
        try:
            data = {
                "vm_token": vm_name,
                "vm_recursos": vm_resources,
                "enlaces": ",".join(enlaces),
                "imagen": imagen,
                "vlan_id": vlan_id,
                "vnc_port": vnc_port,
                "vm_worker_id": worker_id
            }
            
            vm_create_url = f"{self.cluster_config['api_url']}{self.cluster_config['vm_create_endpoint']}"
            
            response = requests.post(vm_create_url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"VM {vm_name} creada exitosamente: {result}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en API del cluster: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error creando VM en cluster: {e}")
            return False
    
    def _save_vm_to_database(
        self,
        vm_name: str,
        vm_resources: Dict[str, int],
        vnc_port: int,
        worker_id: int,
        slice_id: int,
        image_id: int,
        enlaces: List[str],
        conn: Conexion,
        conn2: Conexion2
    ):
        """
        Guarda la información de la VM en las bases de datos.
        
        Args:
            vm_name: Nombre de la VM
            vm_resources: Recursos de la VM
            vnc_port: Puerto VNC
            worker_id: ID del worker
            slice_id: ID del slice
            image_id: ID de la imagen
            enlaces: Lista de enlaces
            conn: Conexión a BD principal
            conn2: Conexión a BD de cluster
        """
        # Base de datos principal
        nombre_completo = f"vm-{vm_name}"
        
        # Crear recursos
        recursos_id = conn.Insert(
            "recursos",
            "ram,storage,vcpu",
            f"{vm_resources['ram']},{vm_resources['disk']},{vm_resources['vcpu']}"
        )
        
        # Crear VM
        vm_id = conn.Insert(
            "vm",
            "nombre,estado,fecha_creacion,creado_por,fecha_modificacion,modificado_por,vnc,servidor_id_servidor,topologia_id_topologia,imagen_id_imagen,recursos_id_estado",
            f"'{nombre_completo}','ACTIVO',now(),1,now(),1,{vnc_port},{worker_id},{slice_id},{image_id},{recursos_id}"
        )
        
        # Base de datos de cluster
        nodo_id = conn2.Insert("nodo", "nombre,tipo,puerto_vnc", f"'{nombre_completo}',1,{vnc_port}")
        
        # Métricas iniciales
        conn2.Insert("ram", "memoria_total,creacion,Nodo_id_nodo", f"{vm_resources['ram']},now(),{nodo_id}")
        conn2.Insert("cpu", "memoria_total,creacion,Nodo_id_nodo", f"{vm_resources['disk']},now(),{nodo_id}")
        conn2.Insert("vcpu", "vcpu_total,creacion,Nodo_id_nodo", f"{vm_resources['vcpu']},now(),{nodo_id}")
        
        # Enlaces
        if enlaces:
            conn2.Insert("enlace", "nombre,nodo_id_nodo", f"'{','.join(enlaces)}',{nodo_id}")
    
    def _configure_openflow_flows(self, vlan_id: int, worker_list: List[str]):
        """
        Configura los flows OpenFlow para el slice.
        
        Args:
            vlan_id: ID de VLAN
            worker_list: Lista de workers
        """
        try:
            flow_data = {
                "vlan_id": vlan_id,
                "workers_id": ",".join(worker_list)
            }
            
            flows_url = f"{self.cluster_config['api_url']}{self.cluster_config['flows_endpoint']}"
            
            response = requests.post(flows_url, json=flow_data, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Flows OpenFlow configurados para VLAN {vlan_id}")
            
        except Exception as e:
            self.logger.error(f"Error configurando flows OpenFlow: {e}")
    
    def _delete_vm(self, vm_name: str, worker_id: int, conn: Conexion, conn2: Conexion2) -> bool:
        """
        Elimina una VM específica.
        
        Args:
            vm_name: Nombre de la VM
            worker_id: ID del worker
            conn: Conexión a BD principal
            conn2: Conexión a BD de cluster
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            # Obtener información de enlaces
            nodo_cluster_result = conn2.Select("id_nodo", "nodo", f"nombre='{vm_name}'")
            if not nodo_cluster_result:
                self.logger.warning(f"Nodo {vm_name} no encontrado en BD cluster")
                return False
            
            nodo_id = nodo_cluster_result[0][0]
            
            # Obtener enlaces para construir TAPs
            enlaces_result = conn2.Select("nombre", "enlace", f"nodo_id_nodo={nodo_id}")
            taps_list = []
            
            if enlaces_result and enlaces_result[0][0]:
                enlaces_list = enlaces_result[0][0].split(",")
                for enlace_nombre in enlaces_list:
                    tap = f"{vm_name[3:]}-{enlace_nombre}"  # Remover 'vm-' del prefijo
                    taps_list.append(tap)
            
            # Eliminar VM del cluster
            vm_delete_url = (
                f"{self.cluster_config['api_url']}{self.cluster_config['vm_delete_endpoint']}"
                f"?worker_id={worker_id}&vm_name={vm_name}&taps={','.join(taps_list)}"
            )
            
            response = requests.get(vm_delete_url, timeout=30)
            
            if response.ok:
                # Eliminar de base de datos principal
                vm_result = conn.Select("id_vm,recursos_id_estado", "vm", f"nombre='{vm_name}'")
                if vm_result:
                    vm_id, recursos_id = vm_result[0]
                    conn.Delete("vm", f"id_vm={vm_id}")
                    conn.Delete("recursos", f"id_recursos={recursos_id}")
                
                # Eliminar de base de datos de cluster
                conn2.Delete("enlace", f"nodo_id_nodo={nodo_id}")
                conn2.Delete("vcpu", f"Nodo_id_nodo={nodo_id}")
                conn2.Delete("cpu", f"Nodo_id_nodo={nodo_id}")
                conn2.Delete("ram", f"Nodo_id_nodo={nodo_id}")
                conn2.Delete("nodo", f"id_nodo={nodo_id}")
                
                self.logger.info(f"VM {vm_name} eliminada exitosamente")
                return True
            else:
                self.logger.error(f"Error eliminando VM del cluster: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error eliminando VM {vm_name}: {e}")
            return False