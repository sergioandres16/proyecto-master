import os
from typing import Dict, Any, List
import logging

class ConfigManager:
    """
    Gestor de configuración que carga variables desde archivo .env
    """
    
    def __init__(self, config_file: str = "config.env"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """
        Carga la configuración desde el archivo .env
        """
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config_file)
            
            if not os.path.exists(config_path):
                logging.warning(f"Archivo de configuración {config_path} no encontrado. Usando valores por defecto.")
                self._load_default_config()
                return
            
            with open(config_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = self._parse_value(value.strip())
            
            logging.info(f"Configuración cargada desde {config_path}")
            
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
            self._load_default_config()
    
    def _parse_value(self, value: str) -> Any:
        """
        Parsea el valor de la configuración al tipo apropiado
        """
        # Verificar si es un número
        if value.isdigit():
            return int(value)
        
        # Verificar si es un float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Verificar si es un booleano
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Verificar si es una lista (separada por comas)
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        # Retornar como string
        return value
    
    def _load_default_config(self):
        """
        Carga configuración por defecto si no se puede cargar el archivo
        """
        self.config = {
            # Base de datos SQLite3
            'DB_PATH': './data/system.db',
            'DB_DATA_DIR': './data/',
            # Legacy para compatibilidad
            'DB_MAIN_PATH': './data/system.db',
            'DB_CLUSTER_PATH': './data/system.db',
            'DB_UNIFIED_PATH': './data/system.db',
            
            # OpenStack
            'OPENSTACK_KEYSTONE_URL': 'http://10.20.12.54:5000/v3/auth/tokens',
            'OPENSTACK_NOVA_URL': 'http://10.20.12.54:8774/v2.1',
            'OPENSTACK_NEUTRON_URL': 'http://10.20.12.54:9696/v2.0',
            'OPENSTACK_ADMIN_USER': 'admin',
            'OPENSTACK_ADMIN_PASSWORD': 'grupo_1',
            'OPENSTACK_DOMAIN_ID': 'default',
            'OPENSTACK_DOMAIN_NAME': 'Default',
            'OPENSTACK_PROJECT_NAME': 'admin',
            
            # Linux Cluster
            'CLUSTER_API_URL': 'http://10.20.12.58:8081',
            'CLUSTER_VM_CREATE_ENDPOINT': '/vm/crear',
            'CLUSTER_VM_DELETE_ENDPOINT': '/vm/borrar',
            'CLUSTER_FLOWS_ENDPOINT': '/OFS/flows',
            'CLUSTER_METRICS_ENDPOINT': '/cpu-metrics',
            
            # Factores y algoritmos
            'RESOURCE_FACTOR': 2,
            'SCHEDULER_RAM_WEIGHT': 0.5,
            'SCHEDULER_DISK_WEIGHT': 0.25,
            'SCHEDULER_VCPU_WEIGHT': 0.25,
            
            # Rutas
            'SLICES_CONFIG_PATH': './Modules/Slices/',
            'SLICE_FILE_EXTENSION': '.json',
            
            # Puertos
            'VNC_BASE_PORT': 5900,
            
            # Conversiones
            'BYTES_TO_MB': 1048576,
            'BYTES_TO_GB': 1073741824,
            
            # Red
            'NETWORK_BASE_CIDR': '10.0.0.0/24',
            'NETWORK_DNS_SERVER': '8.8.8.8',
            
            # Servidores
            'WORKER_NAMES': ['Worker1', 'Worker2', 'Worker3', 'Worker4', 'Worker5', 'Worker6', 'Compute1', 'Compute2', 'Compute3', 'Compute4', 'Compute5', 'Compute6']
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración
        """
        return self.config.get(key, default)
    
    def get_db_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de base de datos SQLite3
        """
        return {
            'db_path': self.get('DB_PATH', self.get('DB_UNIFIED_PATH')),
            'unified_db_path': self.get('DB_PATH', self.get('DB_UNIFIED_PATH')),
            'data_dir': self.get('DB_DATA_DIR'),
            # Configuraciones legacy para compatibilidad
            'main_db_path': self.get('DB_MAIN_PATH'),
            'cluster_db_path': self.get('DB_CLUSTER_PATH')
        }
    
    def get_openstack_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de OpenStack
        """
        return {
            'keystone_url': self.get('OPENSTACK_KEYSTONE_URL'),
            'nova_url': self.get('OPENSTACK_NOVA_URL'),
            'neutron_url': self.get('OPENSTACK_NEUTRON_URL'),
            'admin_user': self.get('OPENSTACK_ADMIN_USER'),
            'admin_password': self.get('OPENSTACK_ADMIN_PASSWORD'),
            'domain_id': self.get('OPENSTACK_DOMAIN_ID'),
            'domain_name': self.get('OPENSTACK_DOMAIN_NAME'),
            'project_name': self.get('OPENSTACK_PROJECT_NAME'),
            'image_id': self.get('OPENSTACK_IMAGE_ID'),
            'ssh_key_name': self.get('OPENSTACK_SSH_KEY_NAME'),
            'security_group': self.get('OPENSTACK_SECURITY_GROUP')
        }
    
    def get_cluster_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración del cluster Linux
        """
        return {
            'api_url': self.get('CLUSTER_API_URL'),
            'vm_create_endpoint': self.get('CLUSTER_VM_CREATE_ENDPOINT'),
            'vm_delete_endpoint': self.get('CLUSTER_VM_DELETE_ENDPOINT'),
            'flows_endpoint': self.get('CLUSTER_FLOWS_ENDPOINT'),
            'metrics_endpoint': self.get('CLUSTER_METRICS_ENDPOINT')
        }
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración del scheduler
        """
        return {
            'resource_factor': self.get('RESOURCE_FACTOR'),
            'ram_weight': self.get('SCHEDULER_RAM_WEIGHT'),
            'disk_weight': self.get('SCHEDULER_DISK_WEIGHT'),
            'vcpu_weight': self.get('SCHEDULER_VCPU_WEIGHT')
        }
    
    def get_network_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de red
        """
        return {
            'base_cidr': self.get('NETWORK_BASE_CIDR'),
            'provider_type': self.get('NETWORK_PROVIDER_TYPE'),
            'physical_network': self.get('NETWORK_PHYSICAL_NETWORK'),
            'gateway_suffix': self.get('NETWORK_GATEWAY_SUFFIX'),
            'allocation_start': self.get('NETWORK_ALLOCATION_START'),
            'allocation_end': self.get('NETWORK_ALLOCATION_END'),
            'dns_server': self.get('NETWORK_DNS_SERVER')
        }
    
    def get_paths_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de rutas
        """
        return {
            'slices_config_path': self.get('SLICES_CONFIG_PATH'),
            'slice_file_extension': self.get('SLICE_FILE_EXTENSION')
        }
    
    def get_worker_names(self) -> List[str]:
        """
        Obtiene la lista de nombres de workers
        """
        return self.get('WORKER_NAMES', [])
    
    def update_config(self, key: str, value: Any):
        """
        Actualiza un valor de configuración
        """
        self.config[key] = value
    
    def validate_config(self) -> bool:
        """
        Valida que la configuración tenga los valores mínimos requeridos
        """
        required_keys = [
            'DB_PATH', 'DB_DATA_DIR',
            'OPENSTACK_KEYSTONE_URL', 'CLUSTER_API_URL'
        ]
        
        # Verificar compatibilidad con nombres anteriores
        if 'DB_PATH' not in self.config and 'DB_UNIFIED_PATH' in self.config:
            self.config['DB_PATH'] = self.config['DB_UNIFIED_PATH']
        
        missing_keys = [key for key in required_keys if key not in self.config]
        
        if missing_keys:
            logging.error(f"Faltan las siguientes configuraciones requeridas: {missing_keys}")
            return False
        
        return True

# Instancia global del gestor de configuración
config = ConfigManager()