"""
===================================================================
OPENSTACK DRIVER - DRIVER MODULAR
===================================================================

Driver modular para gestión de OpenStack.
Proporciona funcionalidades para crear, gestionar y eliminar
slices en infraestructura OpenStack.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

import requests
import secrets
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .base_driver import BaseDriver
from conf.Conexion import Conexion, Conexion2


class OpenStackDriver(BaseDriver):
    """
    Driver para gestión de OpenStack.
    
    Características:
    - Autenticación con Keystone
    - Gestión de redes y subredes VLAN
    - Creación de flavors dinámicos
    - Despliegue de instancias en hipervisores específicos
    - Monitoreo de recursos de hipervisores
    """
    
    def __init__(self):
        """
        Inicializa el driver de OpenStack.
        """
        super().__init__()
        self.openstack_config = self.config.get_openstack_config()
        self.network_config = self.config.get_network_config()
        self._token = None
        self._token_expiry = None
        
    def create_slice(self, slice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un slice completo en OpenStack.
        
        Args:
            slice_data: Datos del slice a crear
            
        Returns:
            Dict con el slice actualizado
        """
        try:
            if not self.validate_slice_data(slice_data):
                raise ValueError("Datos de slice inválidos")
            
            self.logger.info(f"Iniciando creación de slice OpenStack: {slice_data['nombre']}")
            
            # 1. Autenticación
            token = self._get_token()
            
            # 2. Crear red virtual
            network_info = self._create_network(token, slice_data['nombre'])
            network_id = network_info['id']
            
            # 3. Crear subred
            cidr = self._generate_cidr()
            self._create_subnet(token, network_id, f"{slice_data['nombre']}_subred", cidr)
            
            # 4. Obtener o crear ID del slice
            slice_id = self._get_or_create_slice_id(slice_data)
            
            # 5. Generar nombres únicos para VMs
            vm_names = self._generate_vm_names(slice_data['nodos'])
            
            # 6. Crear VMs por nodo
            flavor_counter = 1
            for node_key, node_data in slice_data['nodos'].items():
                if node_data.get('instanciado', 'false') == 'false':
                    success = self._create_vm_for_node(
                        node_key, node_data, vm_names, slice_id,
                        token, network_id, flavor_counter
                    )
                    
                    if success:
                        node_data['instanciado'] = 'true'
                        flavor_counter += 1
            
            # 7. Actualizar estado y guardar
            slice_data['estado'] = 'ejecutado'
            slice_data['mapeo_nombres'] = vm_names
            slice_data['network_id'] = network_id
            slice_data['cidr'] = cidr
            
            self.save_slice_to_file(slice_data)
            
            self.logger.info(f"Slice OpenStack {slice_data['nombre']} creado exitosamente")
            return slice_data
            
        except Exception as e:
            self.logger.error(f"Error creando slice OpenStack: {e}")
            raise
    
    def delete_slice(self, slice_data: Dict[str, Any]) -> bool:
        """
        Elimina un slice completo de OpenStack.
        
        Args:
            slice_data: Datos del slice a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            self.logger.info(f"Iniciando eliminación de slice OpenStack: {slice_data['nombre']}")
            
            conn = Conexion()
            conn2 = Conexion2()
            token = self._get_token()
            
            # Obtener ID del slice
            slice_id_result = conn.Select("id_slice", "slice", f"nombre='{slice_data['nombre']}'")
            if not slice_id_result:
                self.logger.warning(f"Slice {slice_data['nombre']} no encontrado en BD")
                return False
            
            slice_id = slice_id_result[0][0]
            
            # Obtener VMs del slice
            vms = conn.Select("nombre,servidor_id_servidor", "vm", f"topologia_id_topologia={slice_id}")
            
            # Eliminar cada VM
            for vm_name, worker_id in vms:
                success = self._delete_vm(vm_name, token, conn, conn2)
                if not success:
                    self.logger.warning(f"Fallo eliminando VM {vm_name}")
            
            # Eliminar slice de BD
            conn.Delete("slice", f"nombre='{slice_data['nombre']}'")
            
            # TODO: Eliminar red y subred de OpenStack si es necesario
            
            self.logger.info(f"Slice OpenStack {slice_data['nombre']} eliminado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando slice OpenStack: {e}")
            return False
    
    def get_slice_status(self, slice_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un slice OpenStack.
        
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
                # Obtener estado en OpenStack
                openstack_status = self._get_vm_status_from_openstack(vm_name)
                
                vm_list.append({
                    "nombre": vm_name,
                    "estado": vm_estado,
                    "vnc_port": vnc_port,
                    "worker_id": worker_id,
                    "openstack_status": openstack_status
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
            self.logger.error(f"Error obteniendo estado del slice OpenStack: {e}")
            return {"error": str(e)}
    
    def get_hypervisor_info(self) -> List[Dict[str, Any]]:
        """
        Obtiene información de recursos de todos los hipervisores.
        
        Returns:
            List con información de hipervisores
        """
        try:
            token = self._get_token()
            headers = {
                "X-Auth-Token": token,
                "X-OpenStack-Nova-API-Version": "2.47"
            }
            
            response = requests.get(
                f"{self.openstack_config['nova_url']}/os-hypervisors/detail",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            hypervisors = []
            mega = self.config.get('BYTES_TO_MB', 1048576)
            giga = self.config.get('BYTES_TO_GB', 1073741824)
            
            for hy in response.json()["hypervisors"]:
                hypervisor_info = {
                    "nombre": hy["hypervisor_hostname"],
                    "ram_total_mb": hy["memory_mb"],
                    "ram_libre_mb": hy["free_ram_mb"],
                    "ram_total_bytes": mega * hy["memory_mb"],
                    "ram_libre_bytes": mega * hy["free_ram_mb"],
                    "vcpus_total": hy["vcpus"],
                    "vcpus_usados": hy["vcpus_used"],
                    "vcpus_libres": hy["vcpus"] - hy["vcpus_used"],
                    "storage_total_gb": hy["local_gb"],
                    "storage_libre_gb": hy["free_disk_gb"],
                    "storage_total_bytes": giga * hy["local_gb"],
                    "storage_libre_bytes": giga * hy["free_disk_gb"],
                    "estado": hy.get("state", "unknown"),
                    "status": hy.get("status", "unknown")
                }
                
                hypervisors.append(hypervisor_info)
                
                # Actualizar en base de datos
                self._update_hypervisor_resources(hypervisor_info)
            
            return hypervisors
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de hipervisores: {e}")
            return []
    
    def _get_token(self) -> str:
        """
        Obtiene un token de autenticación de Keystone.
        
        Returns:
            str: Token de autenticación
        """
        try:
            # TODO: Implementar cache de token con expiración
            auth_data = {
                "auth": {
                    "identity": {
                        "methods": ["password"],
                        "password": {
                            "user": {
                                "domain": {
                                    "id": self.openstack_config['domain_id'],
                                    "name": self.openstack_config['domain_name']
                                },
                                "name": self.openstack_config['admin_user'],
                                "password": self.openstack_config['admin_password']
                            }
                        }
                    },
                    "scope": {
                        "project": {
                            "domain": {
                                "id": self.openstack_config['domain_id']
                            },
                            "name": self.openstack_config['project_name']
                        }
                    }
                }
            }
            
            response = requests.post(
                self.openstack_config['keystone_url'],
                json=auth_data,
                timeout=30
            )
            response.raise_for_status()
            
            token = response.headers["X-Subject-Token"]
            self.logger.info("Token de OpenStack obtenido exitosamente")
            return token
            
        except Exception as e:
            self.logger.error(f"Error obteniendo token de OpenStack: {e}")
            raise
    
    def _create_network(self, token: str, network_name: str) -> Dict[str, Any]:
        """
        Crea una red virtual en OpenStack.
        
        Args:
            token: Token de autenticación
            network_name: Nombre de la red
            
        Returns:
            Dict con información de la red creada
        """
        try:
            headers = {"X-Auth-Token": token}
            network_data = {
                "network": {
                    "admin_state_up": True,
                    "name": network_name,
                    "provider:network_type": self.network_config.get('provider_type', 'vlan'),
                    "provider:physical_network": self.network_config.get('physical_network', 'external'),
                    "provider:segmentation_id": str(random.randrange(10, 100)),
                    "shared": True
                }
            }
            
            response = requests.post(
                f"{self.openstack_config['neutron_url']}/networks",
                json=network_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            network_info = response.json()["network"]
            self.logger.info(f"Red {network_name} creada con ID {network_info['id']}")
            return network_info
            
        except Exception as e:
            self.logger.error(f"Error creando red {network_name}: {e}")
            raise
    
    def _create_subnet(self, token: str, network_id: str, subnet_name: str, cidr: str):
        """
        Crea una subred en OpenStack.
        
        Args:
            token: Token de autenticación
            network_id: ID de la red
            subnet_name: Nombre de la subred
            cidr: CIDR de la subred
        """
        try:
            headers = {"X-Auth-Token": token}
            ip_numbers = cidr.split(".")
            
            gateway_ip = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}{self.network_config.get('gateway_suffix', '.1')}"
            net_start = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}{self.network_config.get('allocation_start', '.2')}"
            net_end = f"{ip_numbers[0]}.{ip_numbers[1]}.{ip_numbers[2]}{self.network_config.get('allocation_end', '.254')}"
            
            subnet_data = {
                "subnet": {
                    "name": subnet_name,
                    "network_id": network_id,
                    "cidr": cidr,
                    "gateway_ip": gateway_ip,
                    "dns_nameservers": [self.network_config.get('dns_server', '8.8.8.8')],
                    "allocation_pools": [{
                        "start": net_start,
                        "end": net_end
                    }],
                    "ip_version": 4
                }
            }
            
            response = requests.post(
                f"{self.openstack_config['neutron_url']}/subnets",
                json=subnet_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info(f"Subred {subnet_name} creada con CIDR {cidr}")
            
        except Exception as e:
            self.logger.error(f"Error creando subred {subnet_name}: {e}")
            raise
    
    def _generate_cidr(self) -> str:
        """
        Genera un CIDR aleatorio para la red.
        
        Returns:
            str: CIDR generado
        """
        base_cidr = self.network_config.get('base_cidr', '10.0.0.0/24')
        
        # Si hay configuración base, usar esa
        if base_cidr != '10.0.0.0/24':
            return base_cidr
        
        # Generar CIDR aleatorio
        n1 = random.randint(0, 254)
        n2 = random.randint(0, 255)
        return f"10.{n1}.{n2}.0/24"
    
    def _create_flavor(self, token: str, name: str, ram: int, vcpus: int, disk: int) -> str:
        """
        Crea un flavor en OpenStack.
        
        Args:
            token: Token de autenticación
            name: Nombre del flavor
            ram: RAM en MB
            vcpus: Número de vCPUs
            disk: Disco en GB
            
        Returns:
            str: ID del flavor creado
        """
        try:
            headers = {"X-Auth-Token": token}
            flavor_data = {
                "flavor": {
                    "name": name,
                    "ram": ram,
                    "vcpus": vcpus,
                    "disk": disk,
                    "rxtx_factor": self.config.get('RXTX_FACTOR', 1.0)
                }
            }
            
            response = requests.post(
                f"{self.openstack_config['nova_url']}/flavors",
                json=flavor_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            flavor_id = response.json()["flavor"]["id"]
            self.logger.info(f"Flavor {name} creado con ID {flavor_id}")
            return flavor_id
            
        except Exception as e:
            self.logger.error(f"Error creando flavor {name}: {e}")
            raise
    
    def _get_flavor_id(self, token: str, flavor_name: str) -> Optional[str]:
        """
        Obtiene el ID de un flavor existente.
        
        Args:
            token: Token de autenticación
            flavor_name: Nombre del flavor
            
        Returns:
            Optional[str]: ID del flavor o None si no existe
        """
        try:
            headers = {"X-Auth-Token": token}
            response = requests.get(
                f"{self.openstack_config['nova_url']}/flavors/detail",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            for flavor in response.json()["flavors"]:
                if flavor["name"] == flavor_name:
                    return flavor["id"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo ID del flavor {flavor_name}: {e}")
            return None
    
    def _create_server(
        self,
        token: str,
        vm_name: str,
        flavor_id: str,
        network_id: str,
        hypervisor_hostname: str
    ) -> Optional[str]:
        """
        Crea una instancia en OpenStack.
        
        Args:
            token: Token de autenticación
            vm_name: Nombre de la VM
            flavor_id: ID del flavor
            network_id: ID de la red
            hypervisor_hostname: Nombre del hipervisor
            
        Returns:
            Optional[str]: ID de la instancia creada o None si falló
        """
        try:
            headers = {
                "X-Auth-Token": token,
                "X-OpenStack-Nova-API-Version": "2.74"
            }
            
            server_data = {
                "server": {
                    "name": vm_name,
                    "flavorRef": flavor_id,
                    "imageRef": self.openstack_config.get('image_id'),
                    "networks": [{"uuid": network_id}],
                    "key_name": self.openstack_config.get('ssh_key_name'),
                    "security_groups": [{"name": self.openstack_config.get('security_group', 'default')}],
                    "hypervisor_hostname": hypervisor_hostname
                }
            }
            
            response = requests.post(
                f"{self.openstack_config['nova_url']}/servers",
                json=server_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            server_id = response.json()["server"]["id"]
            self.logger.info(f"Instancia {vm_name} creada con ID {server_id}")
            return server_id
            
        except Exception as e:
            self.logger.error(f"Error creando instancia {vm_name}: {e}")
            return None
    
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
            f"'{slice_name}','openstack',{vlan_id},now(),now()"
        )
        
        self.logger.info(f"Slice OpenStack creado con ID {slice_id} y VLAN {vlan_id}")
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
        token: str,
        network_id: str,
        flavor_counter: int
    ) -> bool:
        """
        Crea una VM para un nodo específico.
        
        Args:
            node_key: Clave del nodo
            node_data: Datos del nodo
            vm_names: Mapeo de nombres de VM
            slice_id: ID del slice
            token: Token de autenticación
            network_id: ID de la red
            flavor_counter: Contador para nombres de flavor
            
        Returns:
            bool: True si la creación fue exitosa
        """
        try:
            conn = Conexion()
            conn2 = Conexion2()
            
            vm_name = vm_names[node_key]
            
            # Obtener recursos de VM
            vm_resources = self._get_vm_resources(node_data, conn)
            
            # Obtener o crear flavor
            if node_data['config']['type'] == 'manual':
                flavor_name = str(flavor_counter)
                flavor_id = self._create_flavor(
                    token, flavor_name,
                    vm_resources['ram'],
                    vm_resources['vcpu'],
                    vm_resources['disk']
                )
            else:
                flavor_name = node_data['config']['info_config']
                flavor_id = self._get_flavor_id(token, flavor_name)
                if not flavor_id:
                    raise ValueError(f"Flavor {flavor_name} no encontrado")
            
            # Obtener imagen
            image_id = self._get_or_create_image(node_data['config']['imagen'], conn)
            
            # Obtener worker/hipervisor
            worker_id = node_data['id_worker']
            server_info = conn.Select('nombre', 'servidor', f'id_servidor={worker_id}')
            if not server_info:
                raise ValueError(f"Servidor {worker_id} no encontrado")
            
            hypervisor_hostname = server_info[0][0]
            
            # Preparar enlaces
            enlaces = []
            if 'enlaces' in node_data:
                enlaces = [vm_names[link] for link in node_data['enlaces'] if link in vm_names]
            
            # Crear instancia en OpenStack
            full_vm_name = f"vm-{vm_name}"
            server_id = self._create_server(token, full_vm_name, flavor_id, network_id, hypervisor_hostname)
            
            if server_id:
                # Guardar en base de datos
                self._save_vm_to_database(
                    full_vm_name, vm_resources, worker_id,
                    slice_id, image_id, enlaces, conn, conn2
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error creando VM OpenStack para nodo {node_key}: {e}")
            return False
    
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
        
        # Para OpenStack, usar imagen por defecto
        image_id = conn.Insert("imagen", "nombre,fecha_creacion", f"'{image_name}',now()")
        return image_id
    
    def _save_vm_to_database(
        self,
        vm_name: str,
        vm_resources: Dict[str, int],
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
            worker_id: ID del worker
            slice_id: ID del slice
            image_id: ID de la imagen
            enlaces: Lista de enlaces
            conn: Conexión a BD principal
            conn2: Conexión a BD de cluster
        """
        # Base de datos principal
        vnc_port = -100  # OpenStack maneja VNC automáticamente
        
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
            f"'{vm_name}','ACTIVO',now(),1,now(),1,{vnc_port},{worker_id},{slice_id},{image_id},{recursos_id}"
        )
        
        # Base de datos de cluster
        nodo_id = conn2.Insert("nodo", "nombre,tipo,puerto_vnc", f"'{vm_name}',1,{vnc_port}")
        
        # Métricas iniciales
        conn2.Insert("ram", "memoria_total,creacion,Nodo_id_nodo", f"{vm_resources['ram']},now(),{nodo_id}")
        conn2.Insert("cpu", "memoria_total,creacion,Nodo_id_nodo", f"{vm_resources['disk']},now(),{nodo_id}")
        conn2.Insert("vcpu", "vcpu_total,creacion,Nodo_id_nodo", f"{vm_resources['vcpu']},now(),{nodo_id}")
        
        # Enlaces
        if enlaces:
            conn2.Insert("enlace", "nombre,nodo_id_nodo", f"'{','.join(enlaces)}',{nodo_id}")
    
    def _get_vm_status_from_openstack(self, vm_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una VM desde OpenStack.
        
        Args:
            vm_name: Nombre de la VM
            
        Returns:
            Dict con el estado de la VM
        """
        try:
            token = self._get_token()
            headers = {
                "X-Auth-Token": token,
                "X-OpenStack-Nova-API-Version": "2.47"
            }
            
            response = requests.get(
                f"{self.openstack_config['nova_url']}/servers/detail",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            for server in response.json()["servers"]:
                if server["name"] == vm_name:
                    return {
                        "id": server["id"],
                        "status": server["status"],
                        "power_state": server.get("OS-EXT-STS:power_state"),
                        "task_state": server.get("OS-EXT-STS:task_state"),
                        "created": server["created"],
                        "updated": server["updated"]
                    }
            
            return {"error": "VM no encontrada en OpenStack"}
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de VM {vm_name}: {e}")
            return {"error": str(e)}
    
    def _get_vm_id_from_openstack(self, vm_name: str) -> Optional[str]:
        """
        Obtiene el ID de una VM en OpenStack.
        
        Args:
            vm_name: Nombre de la VM
            
        Returns:
            Optional[str]: ID de la VM o None si no existe
        """
        try:
            token = self._get_token()
            headers = {
                "X-Auth-Token": token,
                "X-OpenStack-Nova-API-Version": "2.47"
            }
            
            response = requests.get(
                f"{self.openstack_config['nova_url']}/servers/detail",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            for server in response.json()["servers"]:
                if server["name"] == vm_name:
                    return server["id"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo ID de VM {vm_name}: {e}")
            return None
    
    def _delete_vm_from_openstack(self, vm_id: str) -> bool:
        """
        Elimina una VM de OpenStack.
        
        Args:
            vm_id: ID de la VM
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            token = self._get_token()
            headers = {
                "X-Auth-Token": token,
                "X-OpenStack-Nova-API-Version": "2.47"
            }
            
            response = requests.delete(
                f"{self.openstack_config['nova_url']}/servers/{vm_id}",
                headers=headers,
                timeout=30
            )
            
            # OpenStack devuelve 204 para eliminación exitosa
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Error eliminando VM {vm_id} de OpenStack: {e}")
            return False
    
    def _delete_vm(self, vm_name: str, token: str, conn: Conexion, conn2: Conexion2) -> bool:
        """
        Elimina una VM específica.
        
        Args:
            vm_name: Nombre de la VM
            token: Token de autenticación
            conn: Conexión a BD principal
            conn2: Conexión a BD de cluster
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            # Obtener ID de la VM en OpenStack
            vm_id = self._get_vm_id_from_openstack(vm_name)
            
            if vm_id:
                # Eliminar de OpenStack
                openstack_success = self._delete_vm_from_openstack(vm_id)
                
                if openstack_success:
                    # Eliminar de base de datos principal
                    vm_result = conn.Select("id_vm,recursos_id_estado", "vm", f"nombre='{vm_name}'")
                    if vm_result:
                        vm_db_id, recursos_id = vm_result[0]
                        conn.Delete("vm", f"id_vm={vm_db_id}")
                        conn.Delete("recursos", f"id_recursos={recursos_id}")
                    
                    # Eliminar de base de datos de cluster
                    nodo_result = conn2.Select("id_nodo", "nodo", f"nombre='{vm_name}'")
                    if nodo_result:
                        nodo_id = nodo_result[0][0]
                        conn2.Delete("enlace", f"nodo_id_nodo={nodo_id}")
                        conn2.Delete("vcpu", f"Nodo_id_nodo={nodo_id}")
                        conn2.Delete("cpu", f"Nodo_id_nodo={nodo_id}")
                        conn2.Delete("ram", f"Nodo_id_nodo={nodo_id}")
                        conn2.Delete("nodo", f"id_nodo={nodo_id}")
                    
                    self.logger.info(f"VM OpenStack {vm_name} eliminada exitosamente")
                    return True
                else:
                    self.logger.error(f"Error eliminando VM {vm_name} de OpenStack")
                    return False
            else:
                self.logger.warning(f"VM {vm_name} no encontrada en OpenStack")
                return False
                
        except Exception as e:
            self.logger.error(f"Error eliminando VM OpenStack {vm_name}: {e}")
            return False
    
    def _update_hypervisor_resources(self, hypervisor_info: Dict[str, Any]):
        """
        Actualiza los recursos del hipervisor en la base de datos.
        
        Args:
            hypervisor_info: Información del hipervisor
        """
        try:
            conn = Conexion()
            nombre = hypervisor_info['nombre']
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Buscar servidor existente
            tupla = conn.Select('id_recurso', 'servidor', f"nombre='{nombre}'")
            
            if tupla:
                # Actualizar recursos existentes
                id_recurso = tupla[0][0]
                conn.Update(
                    'recursos',
                    f'ram_available="{hypervisor_info["ram_libre_bytes"]}",'
                    f'storage_available="{hypervisor_info["storage_libre_bytes"]}",'
                    f'vcpu_available="{hypervisor_info["vcpus_libres"]}"',
                    f'id_recursos={id_recurso}'
                )
                conn.Update(
                    'servidor',
                    f"fecha_modificacion='{fecha_actual}'",
                    f'id_recurso={id_recurso}'
                )
            else:
                # Crear nuevo servidor
                id_recurso = conn.Insert(
                    'recursos',
                    'ram,storage,vcpu,ram_available,storage_available,vcpu_available',
                    f'{hypervisor_info["ram_total_bytes"]},'
                    f'{hypervisor_info["storage_total_bytes"]},'
                    f'{hypervisor_info["vcpus_total"]},'
                    f'{hypervisor_info["ram_libre_bytes"]},'
                    f'{hypervisor_info["storage_libre_bytes"]},'
                    f'{hypervisor_info["vcpus_libres"]}'
                )
                
                conn.Insert(
                    'servidor',
                    'nombre,descripcion,fecha_creacion,ip,id_zona,id_recurso,fecha_modificacion',
                    f'"{nombre}","openstack","{fecha_actual}","openstack",1,{id_recurso},"{fecha_actual}"'
                )
            
        except Exception as e:
            self.logger.error(f"Error actualizando recursos del hipervisor {hypervisor_info['nombre']}: {e}")