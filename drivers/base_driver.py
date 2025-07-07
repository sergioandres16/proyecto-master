"""
===================================================================
DRIVER BASE - CLASE ABSTRACTA
===================================================================

Clase base abstracta que define la interfaz común para todos
los drivers de infraestructura.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
import json
from pathlib import Path
from conf.ConfigManager import config


class BaseDriver(ABC):
    """
    Clase base abstracta para todos los drivers de infraestructura.
    Define la interfaz común y métodos utilitarios compartidos.
    """
    
    def __init__(self):
        """
        Inicializa el driver base.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
    @abstractmethod
    def create_slice(self, slice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un slice en la infraestructura.
        
        Args:
            slice_data: Datos del slice a crear
            
        Returns:
            Dict con el slice actualizado después de la creación
        """
        pass
    
    @abstractmethod
    def delete_slice(self, slice_data: Dict[str, Any]) -> bool:
        """
        Elimina un slice de la infraestructura.
        
        Args:
            slice_data: Datos del slice a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        pass
    
    @abstractmethod
    def get_slice_status(self, slice_name: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un slice.
        
        Args:
            slice_name: Nombre del slice
            
        Returns:
            Dict con el estado del slice
        """
        pass
    
    def save_slice_to_file(self, slice_data: Dict[str, Any]) -> bool:
        """
        Guarda el slice en un archivo JSON.
        
        Args:
            slice_data: Datos del slice
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            paths_config = self.config.get_paths_config()
            slice_path = f"{paths_config['slices_config_path']}{slice_data['nombre']}{paths_config['slice_file_extension']}"
            
            # Crear directorio si no existe
            Path(slice_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(slice_path, 'w', encoding='utf-8') as f:
                json.dump(slice_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Slice {slice_data['nombre']} guardado en {slice_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando slice: {e}")
            return False
    
    def load_slice_from_file(self, slice_name: str) -> Dict[str, Any]:
        """
        Carga un slice desde archivo JSON.
        
        Args:
            slice_name: Nombre del slice
            
        Returns:
            Dict con los datos del slice o dict vacío si no existe
        """
        try:
            paths_config = self.config.get_paths_config()
            slice_path = f"{paths_config['slices_config_path']}{slice_name}{paths_config['slice_file_extension']}"
            
            if not Path(slice_path).exists():
                self.logger.warning(f"Archivo de slice no encontrado: {slice_path}")
                return {}
            
            with open(slice_path, 'r', encoding='utf-8') as f:
                slice_data = json.load(f)
            
            self.logger.info(f"Slice {slice_name} cargado desde {slice_path}")
            return slice_data
            
        except Exception as e:
            self.logger.error(f"Error cargando slice: {e}")
            return {}
    
    def validate_slice_data(self, slice_data: Dict[str, Any]) -> bool:
        """
        Valida la estructura básica de datos del slice.
        
        Args:
            slice_data: Datos del slice a validar
            
        Returns:
            bool: True si los datos son válidos
        """
        required_fields = ['nombre', 'nodos']
        
        for field in required_fields:
            if field not in slice_data:
                self.logger.error(f"Campo requerido faltante: {field}")
                return False
        
        if not isinstance(slice_data['nodos'], dict):
            self.logger.error("El campo 'nodos' debe ser un diccionario")
            return False
        
        # Validar estructura de nodos
        for nodo_key, nodo_data in slice_data['nodos'].items():
            required_node_fields = ['config', 'instanciado']
            for field in required_node_fields:
                if field not in nodo_data:
                    self.logger.error(f"Campo requerido faltante en nodo {nodo_key}: {field}")
                    return False
        
        return True
    
    def generate_unique_id(self, prefix: str = "", length: int = 6) -> str:
        """
        Genera un ID único para recursos.
        
        Args:
            prefix: Prefijo opcional para el ID
            length: Longitud del ID aleatorio
            
        Returns:
            str: ID único generado
        """
        import secrets
        random_id = secrets.token_hex(length // 2)
        return f"{prefix}{random_id}" if prefix else random_id
    
    def generate_mac_address(self) -> str:
        """
        Genera una dirección MAC aleatoria.
        
        Returns:
            str: Dirección MAC en formato XX:XX:XX:XX:XX:XX
        """
        import random
        return "02:%02x:%02x:%02x:%02x:%02x" % (
            random.randint(0, 255), random.randint(0, 255),
            random.randint(0, 255), random.randint(0, 255),
            random.randint(0, 255)
        )