"""
===================================================================
MODELOS PYDANTIC - API REST
===================================================================

Modelos de datos para validación y serialización en la API REST.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class DriverType(str, Enum):
    """Tipos de drivers disponibles."""
    LINUX_CLUSTER = "linux_cluster"
    OPENSTACK = "openstack"


class SliceState(str, Enum):
    """Estados de slice."""
    CREADO = "creado"
    GUARDADO = "guardado"
    EJECUTADO = "ejecutado"
    PAUSADO = "pausado"
    ELIMINADO = "eliminado"


class VMState(str, Enum):
    """Estados de VM."""
    CREADA = "CREADA"
    ACTIVA = "ACTIVA"
    PAUSADA = "PAUSADA"
    ELIMINADA = "ELIMINADA"


class ConfigType(str, Enum):
    """Tipos de configuración de recursos."""
    MANUAL = "manual"
    FLAVOR = "flavor"


class ImageConfig(BaseModel):
    """Configuración de imagen de VM."""
    nombre: str = Field(..., description="Nombre de la imagen")
    url: str = Field(default="-", description="URL de la imagen o '-' si es local")


class NodeConfig(BaseModel):
    """Configuración de un nodo de slice."""
    type: ConfigType = Field(..., description="Tipo de configuración")
    info_config: Union[List[int], str] = Field(
        ..., 
        description="Lista [cpu, ram, disk] para manual o nombre del flavor"
    )
    imagen: ImageConfig = Field(..., description="Configuración de imagen")

    @validator('info_config')
    def validate_info_config(cls, v, values):
        """Valida que info_config sea consistente con el tipo."""
        config_type = values.get('type')
        if config_type == ConfigType.MANUAL:
            if not isinstance(v, list) or len(v) != 3:
                raise ValueError("Para tipo manual, info_config debe ser lista [cpu, ram, disk]")
            if not all(isinstance(x, int) and x > 0 for x in v):
                raise ValueError("Recursos deben ser enteros positivos")
        elif config_type == ConfigType.FLAVOR:
            if not isinstance(v, str) or not v.strip():
                raise ValueError("Para tipo flavor, info_config debe ser nombre del flavor")
        return v


class SliceNode(BaseModel):
    """Definición de un nodo en el slice."""
    config: NodeConfig = Field(..., description="Configuración del nodo")
    instanciado: str = Field(default="false", description="Si el nodo está instanciado")
    enlaces: List[str] = Field(default=[], description="Lista de enlaces a otros nodos")
    id_worker: int = Field(..., description="ID del worker/servidor donde desplegar", gt=0)

    @validator('instanciado')
    def validate_instanciado(cls, v):
        """Valida que instanciado sea 'true' o 'false'."""
        if v not in ['true', 'false']:
            raise ValueError("instanciado debe ser 'true' o 'false'")
        return v


class SliceCreate(BaseModel):
    """Modelo para crear un slice."""
    nombre: str = Field(..., description="Nombre único del slice", min_length=1, max_length=100)
    driver_type: DriverType = Field(..., description="Tipo de driver a usar")
    nodos: Dict[str, SliceNode] = Field(..., description="Diccionario de nodos del slice")
    descripcion: Optional[str] = Field(None, description="Descripción opcional del slice")

    @validator('nombre')
    def validate_nombre(cls, v):
        """Valida el formato del nombre."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Nombre solo puede contener letras, números, guiones y guiones bajos")
        return v

    @validator('nodos')
    def validate_nodos(cls, v):
        """Valida que haya al menos un nodo."""
        if not v:
            raise ValueError("Debe haber al menos un nodo")
        return v


class SliceUpdate(BaseModel):
    """Modelo para actualizar un slice."""
    estado: Optional[SliceState] = Field(None, description="Nuevo estado del slice")
    descripcion: Optional[str] = Field(None, description="Nueva descripción")
    nodos: Optional[Dict[str, SliceNode]] = Field(None, description="Nuevos nodos")


class SliceResponse(BaseModel):
    """Respuesta con información de slice."""
    id: Optional[int] = Field(None, description="ID del slice en BD")
    nombre: str = Field(..., description="Nombre del slice")
    tipo: DriverType = Field(..., description="Tipo de driver")
    estado: SliceState = Field(..., description="Estado actual")
    vlan_id: Optional[int] = Field(None, description="ID de VLAN asignada")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    fecha_modificacion: Optional[str] = Field(None, description="Fecha de modificación")
    nodos: Dict[str, SliceNode] = Field(..., description="Nodos del slice")
    mapeo_nombres: Optional[Dict[str, str]] = Field(None, description="Mapeo de nombres de VM")
    network_id: Optional[str] = Field(None, description="ID de red (OpenStack)")
    cidr: Optional[str] = Field(None, description="CIDR de red")


class VMInfo(BaseModel):
    """Información de una VM."""
    nombre: str = Field(..., description="Nombre de la VM")
    estado: VMState = Field(..., description="Estado de la VM")
    vnc_port: Optional[int] = Field(None, description="Puerto VNC")
    worker_id: int = Field(..., description="ID del worker")
    recursos: Optional[Dict[str, int]] = Field(None, description="Recursos asignados")
    openstack_status: Optional[Dict[str, Any]] = Field(None, description="Estado en OpenStack")


class SliceStatus(BaseModel):
    """Estado detallado de un slice."""
    id: int = Field(..., description="ID del slice")
    nombre: str = Field(..., description="Nombre del slice")
    tipo: DriverType = Field(..., description="Tipo de driver")
    vlan_id: Optional[int] = Field(None, description="ID de VLAN")
    estado: SliceState = Field(..., description="Estado del slice")
    fecha_creacion: str = Field(..., description="Fecha de creación")
    vms: List[VMInfo] = Field(..., description="Lista de VMs")
    total_vms: int = Field(..., description="Total de VMs")


class HypervisorInfo(BaseModel):
    """Información de un hipervisor OpenStack."""
    nombre: str = Field(..., description="Nombre del hipervisor")
    ram_total_mb: int = Field(..., description="RAM total en MB")
    ram_libre_mb: int = Field(..., description="RAM libre en MB")
    vcpus_total: int = Field(..., description="vCPUs totales")
    vcpus_libres: int = Field(..., description="vCPUs libres")
    storage_total_gb: int = Field(..., description="Storage total en GB")
    storage_libre_gb: int = Field(..., description="Storage libre en GB")
    estado: str = Field(..., description="Estado del hipervisor")
    status: str = Field(..., description="Status del hipervisor")


class APIResponse(BaseModel):
    """Respuesta estándar de la API."""
    success: bool = Field(..., description="Si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Any] = Field(None, description="Datos de respuesta")
    error: Optional[str] = Field(None, description="Detalles del error si aplica")


class HealthCheck(BaseModel):
    """Respuesta de health check."""
    status: str = Field(..., description="Estado del servicio")
    version: str = Field(..., description="Versión de la API")
    timestamp: str = Field(..., description="Timestamp del check")
    services: Dict[str, str] = Field(..., description="Estado de servicios dependientes")


# Modelos para validación de parámetros de consulta
class SliceListParams(BaseModel):
    """Parámetros para listar slices."""
    skip: int = Field(default=0, ge=0, description="Número de registros a saltar")
    limit: int = Field(default=100, ge=1, le=1000, description="Límite de registros")
    driver_type: Optional[DriverType] = Field(None, description="Filtrar por tipo de driver")
    estado: Optional[SliceState] = Field(None, description="Filtrar por estado")


class WorkerInfo(BaseModel):
    """Información de un worker/servidor."""
    id: int = Field(..., description="ID del worker")
    nombre: str = Field(..., description="Nombre del worker")
    ip: Optional[str] = Field(None, description="IP del worker")
    descripcion: Optional[str] = Field(None, description="Descripción")
    recursos: Optional[Dict[str, Any]] = Field(None, description="Recursos disponibles")
    zona: Optional[str] = Field(None, description="Zona de disponibilidad")


class FlavorInfo(BaseModel):
    """Información de un flavor."""
    id: Optional[int] = Field(None, description="ID del flavor")
    nombre: str = Field(..., description="Nombre del flavor")
    cpu: int = Field(..., description="CPUs", gt=0)
    ram: int = Field(..., description="RAM en MB", gt=0)
    storage: int = Field(..., description="Storage en GB", gt=0)
    descripcion: Optional[str] = Field(None, description="Descripción del flavor")


class ImageInfo(BaseModel):
    """Información de una imagen."""
    id: Optional[int] = Field(None, description="ID de la imagen")
    nombre: str = Field(..., description="Nombre de la imagen")
    descripcion: Optional[str] = Field(None, description="Descripción")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    url: Optional[str] = Field(None, description="URL de la imagen")