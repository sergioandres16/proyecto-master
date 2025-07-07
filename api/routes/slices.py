"""
===================================================================
RUTAS DE SLICES - API REST
===================================================================

Endpoints para gestión de slices usando drivers modulares.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
import logging
import sys
from pathlib import Path as PathLib

# Agregar el directorio raíz al path
root_dir = PathLib(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from api.models import (
    SliceCreate, SliceUpdate, SliceResponse, SliceStatus, 
    APIResponse, SliceListParams, DriverType
)
from drivers.linux_cluster_driver import LinuxClusterDriver
from drivers.openstack_driver import OpenStackDriver

router = APIRouter(prefix="/slices", tags=["slices"])
logger = logging.getLogger(__name__)


def get_driver(driver_type: DriverType):
    """
    Factory para obtener el driver apropiado.
    
    Args:
        driver_type: Tipo de driver solicitado
        
    Returns:
        Driver instance
        
    Raises:
        HTTPException: Si el tipo de driver no es válido
    """
    if driver_type == DriverType.LINUX_CLUSTER:
        return LinuxClusterDriver()
    elif driver_type == DriverType.OPENSTACK:
        return OpenStackDriver()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de driver no soportado: {driver_type}"
        )


@router.post("/", response_model=APIResponse, status_code=201)
async def create_slice(slice_data: SliceCreate):
    """
    Crea un nuevo slice usando el driver especificado.
    
    Args:
        slice_data: Datos del slice a crear
        
    Returns:
        APIResponse con el slice creado
        
    Raises:
        HTTPException: Si hay errores en la creación
    """
    try:
        logger.info(f"Creando slice {slice_data.nombre} con driver {slice_data.driver_type}")
        
        # Obtener driver apropiado
        driver = get_driver(slice_data.driver_type)
        
        # Convertir modelo Pydantic a dict para el driver
        slice_dict = {
            "nombre": slice_data.nombre,
            "estado": "guardado",
            "nodos": {}
        }
        
        # Convertir nodos
        for node_key, node_data in slice_data.nodos.items():
            slice_dict["nodos"][node_key] = {
                "config": {
                    "type": node_data.config.type.value,
                    "info_config": node_data.config.info_config,
                    "imagen": {
                        "nombre": node_data.config.imagen.nombre,
                        "url": node_data.config.imagen.url
                    }
                },
                "instanciado": node_data.instanciado,
                "enlaces": node_data.enlaces,
                "id_worker": node_data.id_worker
            }
        
        # Crear slice usando el driver
        created_slice = driver.create_slice(slice_dict)
        
        return APIResponse(
            success=True,
            message=f"Slice {slice_data.nombre} creado exitosamente",
            data=created_slice
        )
        
    except ValueError as e:
        logger.error(f"Error de validación creando slice: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error interno creando slice: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=APIResponse)
async def list_slices(
    skip: int = Query(default=0, ge=0, description="Registros a saltar"),
    limit: int = Query(default=100, ge=1, le=1000, description="Límite de registros"),
    driver_type: Optional[DriverType] = Query(None, description="Filtrar por tipo"),
    estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """
    Lista todos los slices con filtros opcionales.
    
    Args:
        skip: Número de registros a saltar
        limit: Límite de registros a devolver
        driver_type: Filtrar por tipo de driver
        estado: Filtrar por estado
        
    Returns:
        APIResponse con lista de slices
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Construir query con filtros
        where_conditions = []
        if driver_type:
            where_conditions.append(f"tipo='{driver_type.value}'")
        if estado:
            where_conditions.append(f"estado='{estado}'")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "-1"
        
        # Obtener slices con paginación
        slices = conn.Select(
            "id_slice,nombre,tipo,vlan_id,estado,fecha_creacion",
            "slice",
            f"{where_clause} LIMIT {limit} OFFSET {skip}"
        )
        
        slice_list = []
        for slice_row in slices:
            slice_id, nombre, tipo, vlan_id, estado, fecha_creacion = slice_row
            slice_list.append({
                "id": slice_id,
                "nombre": nombre,
                "tipo": tipo,
                "vlan_id": vlan_id,
                "estado": estado,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None
            })
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(slice_list)} slices",
            data={
                "slices": slice_list,
                "total": len(slice_list),
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Error listando slices: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{slice_name}", response_model=APIResponse)
async def get_slice(
    slice_name: str = Path(..., description="Nombre del slice")
):
    """
    Obtiene información detallada de un slice específico.
    
    Args:
        slice_name: Nombre del slice
        
    Returns:
        APIResponse con información del slice
        
    Raises:
        HTTPException: Si el slice no existe
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Obtener información básica del slice
        slice_info = conn.Select(
            "id_slice,nombre,tipo,vlan_id,estado,fecha_creacion",
            "slice",
            f"nombre='{slice_name}'"
        )
        
        if not slice_info:
            raise HTTPException(
                status_code=404,
                detail=f"Slice {slice_name} no encontrado"
            )
        
        slice_id, nombre, tipo, vlan_id, estado, fecha_creacion = slice_info[0]
        
        # Determinar tipo de driver y obtener estado detallado
        if tipo == "linux_cluster":
            driver = LinuxClusterDriver()
        elif tipo == "openstack":
            driver = OpenStackDriver()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de driver desconocido: {tipo}"
            )
        
        # Obtener estado detallado del driver
        detailed_status = driver.get_slice_status(slice_name)
        
        return APIResponse(
            success=True,
            message=f"Información del slice {slice_name}",
            data=detailed_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo slice {slice_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{slice_name}", response_model=APIResponse)
async def update_slice(
    slice_name: str = Path(..., description="Nombre del slice"),
    slice_update: SliceUpdate = None
):
    """
    Actualiza un slice existente.
    
    Args:
        slice_name: Nombre del slice
        slice_update: Datos a actualizar
        
    Returns:
        APIResponse con resultado de la actualización
        
    Raises:
        HTTPException: Si el slice no existe o hay errores
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Verificar que el slice existe
        existing_slice = conn.Select("id_slice,tipo", "slice", f"nombre='{slice_name}'")
        if not existing_slice:
            raise HTTPException(
                status_code=404,
                detail=f"Slice {slice_name} no encontrado"
            )
        
        slice_id, driver_type = existing_slice[0]
        
        # Construir query de actualización
        update_fields = []
        if slice_update.estado:
            update_fields.append(f"estado='{slice_update.estado.value}'")
        if slice_update.descripcion is not None:
            update_fields.append(f"descripcion='{slice_update.descripcion}'")
        
        if update_fields:
            update_fields.append("fecha_modificacion=now()")
            update_clause = ",".join(update_fields)
            
            conn.Update("slice", update_clause, f"id_slice={slice_id}")
        
        # TODO: Manejar actualización de nodos si se proporciona
        
        return APIResponse(
            success=True,
            message=f"Slice {slice_name} actualizado exitosamente",
            data={"slice_name": slice_name, "updates": len(update_fields)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando slice {slice_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{slice_name}", response_model=APIResponse)
async def delete_slice(
    slice_name: str = Path(..., description="Nombre del slice")
):
    """
    Elimina un slice y todos sus recursos asociados.
    
    Args:
        slice_name: Nombre del slice a eliminar
        
    Returns:
        APIResponse con resultado de la eliminación
        
    Raises:
        HTTPException: Si el slice no existe o hay errores
    """
    try:
        from conf.Conexion import Conexion
        from drivers.base_driver import BaseDriver
        
        conn = Conexion()
        
        # Verificar que el slice existe y obtener su tipo
        slice_info = conn.Select("id_slice,tipo", "slice", f"nombre='{slice_name}'")
        if not slice_info:
            raise HTTPException(
                status_code=404,
                detail=f"Slice {slice_name} no encontrado"
            )
        
        slice_id, driver_type = slice_info[0]
        
        # Cargar slice desde archivo para tener datos completos
        base_driver = BaseDriver()
        slice_data = base_driver.load_slice_from_file(slice_name)
        
        if not slice_data:
            # Si no hay archivo, crear estructura mínima
            slice_data = {"nombre": slice_name, "nodos": {}}
        
        # Obtener driver apropiado
        if driver_type == "linux_cluster":
            driver = LinuxClusterDriver()
        elif driver_type == "openstack":
            driver = OpenStackDriver()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de driver desconocido: {driver_type}"
            )
        
        # Eliminar usando el driver
        success = driver.delete_slice(slice_data)
        
        if success:
            return APIResponse(
                success=True,
                message=f"Slice {slice_name} eliminado exitosamente",
                data={"slice_name": slice_name}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando slice {slice_name}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando slice {slice_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{slice_name}/status", response_model=APIResponse)
async def get_slice_status(
    slice_name: str = Path(..., description="Nombre del slice")
):
    """
    Obtiene el estado detallado de un slice y sus VMs.
    
    Args:
        slice_name: Nombre del slice
        
    Returns:
        APIResponse con estado detallado del slice
        
    Raises:
        HTTPException: Si el slice no existe
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Verificar tipo de slice
        slice_info = conn.Select("tipo", "slice", f"nombre='{slice_name}'")
        if not slice_info:
            raise HTTPException(
                status_code=404,
                detail=f"Slice {slice_name} no encontrado"
            )
        
        driver_type = slice_info[0][0]
        
        # Obtener driver apropiado
        if driver_type == "linux_cluster":
            driver = LinuxClusterDriver()
        elif driver_type == "openstack":
            driver = OpenStackDriver()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de driver desconocido: {driver_type}"
            )
        
        # Obtener estado detallado
        status = driver.get_slice_status(slice_name)
        
        if "error" in status:
            raise HTTPException(
                status_code=404 if "no encontrado" in status["error"].lower() else 500,
                detail=status["error"]
            )
        
        return APIResponse(
            success=True,
            message=f"Estado del slice {slice_name}",
            data=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado del slice {slice_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")