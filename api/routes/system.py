"""
===================================================================
RUTAS DEL SISTEMA - API REST
===================================================================

Endpoints para información general del sistema, health checks
y gestión de recursos.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import sys
from pathlib import Path as PathLib

# Agregar el directorio raíz al path
root_dir = PathLib(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from api.models import APIResponse, HealthCheck, WorkerInfo, FlavorInfo, ImageInfo

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Endpoint de health check del sistema.
    
    Returns:
        HealthCheck con estado del sistema
    """
    try:
        # Verificar estado de la base de datos
        db_status = "ok"
        try:
            from conf.Conexion import Conexion
            conn = Conexion()
            conn.execute_query("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Verificar configuración
        config_status = "ok"
        try:
            from conf.ConfigManager import config
            if not config.validate_config():
                config_status = "error: invalid configuration"
        except Exception as e:
            config_status = f"error: {str(e)}"
        
        # Verificar drivers
        drivers_status = "ok"
        try:
            from drivers.linux_cluster_driver import LinuxClusterDriver
            from drivers.openstack_driver import OpenStackDriver
            LinuxClusterDriver()
            OpenStackDriver()
        except Exception as e:
            drivers_status = f"error: {str(e)}"
        
        services = {
            "database": db_status,
            "configuration": config_status,
            "drivers": drivers_status
        }
        
        overall_status = "healthy" if all("error" not in status for status in services.values()) else "degraded"
        
        return HealthCheck(
            status=overall_status,
            version="3.0",
            timestamp=datetime.now().isoformat(),
            services=services
        )
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthCheck(
            status="error",
            version="3.0",
            timestamp=datetime.now().isoformat(),
            services={"error": str(e)}
        )


@router.get("/info", response_model=APIResponse)
async def get_system_info():
    """
    Obtiene información general del sistema.
    
    Returns:
        APIResponse con información del sistema
    """
    try:
        from conf.Conexion import Conexion
        from conf.ConfigManager import config
        
        conn = Conexion()
        
        # Estadísticas generales
        total_slices = conn.Select("COUNT(*)", "slice", "-1")[0][0]
        total_vms = conn.Select("COUNT(*)", "vm", "-1")[0][0]
        total_workers = conn.Select("COUNT(*)", "servidor", "-1")[0][0]
        
        # Slices por tipo
        slices_linux = conn.Select("COUNT(*)", "slice", "tipo='linux_cluster'")[0][0]
        slices_openstack = conn.Select("COUNT(*)", "slice", "tipo='openstack'")[0][0]
        
        # VMs por estado
        vms_activas = conn.Select("COUNT(*)", "vm", "estado='ACTIVA'")[0][0]
        vms_pausadas = conn.Select("COUNT(*)", "vm", "estado='PAUSADA'")[0][0]
        vms_eliminadas = conn.Select("COUNT(*)", "vm", "estado='ELIMINADA'")[0][0]
        
        # Configuración actual
        db_config = config.get_db_config()
        
        system_info = {
            "version": "3.0",
            "database": {
                "type": "SQLite3",
                "path": db_config.get('db_path'),
                "status": "connected"
            },
            "statistics": {
                "total_slices": total_slices,
                "total_vms": total_vms,
                "total_workers": total_workers,
                "slices_by_type": {
                    "linux_cluster": slices_linux,
                    "openstack": slices_openstack
                },
                "vms_by_status": {
                    "activas": vms_activas,
                    "pausadas": vms_pausadas,
                    "eliminadas": vms_eliminadas
                }
            },
            "drivers": {
                "linux_cluster": "enabled",
                "openstack": "enabled"
            }
        }
        
        return APIResponse(
            success=True,
            message="Información del sistema",
            data=system_info
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/workers", response_model=APIResponse)
async def get_all_workers():
    """
    Obtiene todos los workers/servidores del sistema.
    
    Returns:
        APIResponse con lista de workers
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        workers = conn.Select(
            "s.id_servidor,s.nombre,s.ip,s.descripcion,"
            "z.nombre as zona_nombre,r.ram,r.vcpu,r.storage,"
            "r.ram_available,r.vcpu_available,r.storage_available",
            "servidor s "
            "LEFT JOIN zona_disponibilidad z ON s.id_zona = z.idzona_disponibilidad "
            "LEFT JOIN recursos r ON s.id_recurso = r.id_recursos",
            "-1"
        )
        
        worker_list = []
        for worker_row in workers:
            (worker_id, nombre, ip, descripcion, zona_nombre,
             ram_total, vcpu_total, storage_total,
             ram_available, vcpu_available, storage_available) = worker_row
            
            worker_info = {
                "id": worker_id,
                "nombre": nombre,
                "ip": ip,
                "descripcion": descripcion,
                "zona": zona_nombre,
                "recursos": {
                    "ram_total": ram_total,
                    "ram_disponible": ram_available,
                    "vcpu_total": vcpu_total,
                    "vcpu_disponible": vcpu_available,
                    "storage_total": storage_total,
                    "storage_disponible": storage_available
                }
            }
            
            worker_list.append(worker_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(worker_list)} workers",
            data={"workers": worker_list, "total": len(worker_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo workers: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/flavors", response_model=APIResponse)
async def get_all_flavors():
    """
    Obtiene todos los flavors disponibles.
    
    Returns:
        APIResponse con lista de flavors
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        flavors = conn.Select(
            "id_flavor,nombre,cpu,ram,storage,descripcion,fecha_creacion",
            "flavor",
            "-1"
        )
        
        flavor_list = []
        for flavor_row in flavors:
            (flavor_id, nombre, cpu, ram, storage, descripcion, fecha_creacion) = flavor_row
            
            flavor_info = {
                "id": flavor_id,
                "nombre": nombre,
                "cpu": cpu,
                "ram": ram,
                "storage": storage,
                "descripcion": descripcion,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None
            }
            
            flavor_list.append(flavor_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(flavor_list)} flavors",
            data={"flavors": flavor_list, "total": len(flavor_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo flavors: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/images", response_model=APIResponse)
async def get_all_images():
    """
    Obtiene todas las imágenes disponibles.
    
    Returns:
        APIResponse con lista de imágenes
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        images = conn.Select(
            "id_imagen,nombre,descripcion,fecha_creacion",
            "imagen",
            "-1"
        )
        
        image_list = []
        for image_row in images:
            (image_id, nombre, descripcion, fecha_creacion) = image_row
            
            image_info = {
                "id": image_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None
            }
            
            image_list.append(image_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(image_list)} imágenes",
            data={"images": image_list, "total": len(image_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo imágenes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/zones", response_model=APIResponse)
async def get_availability_zones():
    """
    Obtiene todas las zonas de disponibilidad.
    
    Returns:
        APIResponse con lista de zonas
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        zones = conn.Select(
            "z.idzona_disponibilidad,z.nombre,z.descripcion,z.activa,z.fecha_creacion,"
            "COUNT(s.id_servidor) as total_servidores",
            "zona_disponibilidad z "
            "LEFT JOIN servidor s ON z.idzona_disponibilidad = s.id_zona",
            "-1 GROUP BY z.idzona_disponibilidad,z.nombre,z.descripcion,z.activa,z.fecha_creacion"
        )
        
        zone_list = []
        for zone_row in zones:
            (zone_id, nombre, descripcion, activa, fecha_creacion, total_servidores) = zone_row
            
            zone_info = {
                "id": zone_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "activa": bool(activa),
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None,
                "total_servidores": total_servidores
            }
            
            zone_list.append(zone_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(zone_list)} zonas",
            data={"zones": zone_list, "total": len(zone_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo zonas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/config", response_model=APIResponse)
async def get_system_config():
    """
    Obtiene la configuración actual del sistema.
    
    Returns:
        APIResponse con configuración del sistema
    """
    try:
        from conf.ConfigManager import config
        
        # Obtener configuraciones sin datos sensibles
        db_config = config.get_db_config()
        cluster_config = config.get_cluster_config()
        network_config = config.get_network_config()
        paths_config = config.get_paths_config()
        
        # Remover información sensible
        openstack_config = config.get_openstack_config()
        safe_openstack_config = {
            "keystone_url": openstack_config.get("keystone_url"),
            "nova_url": openstack_config.get("nova_url"),
            "neutron_url": openstack_config.get("neutron_url"),
            "domain_name": openstack_config.get("domain_name"),
            "project_name": openstack_config.get("project_name"),
            "image_id": openstack_config.get("image_id")
        }
        
        system_config = {
            "database": {
                "type": "SQLite3",
                "data_dir": db_config.get("data_dir")
            },
            "cluster": cluster_config,
            "network": network_config,
            "paths": paths_config,
            "openstack": safe_openstack_config
        }
        
        return APIResponse(
            success=True,
            message="Configuración del sistema",
            data=system_config
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/stats", response_model=APIResponse)
async def get_system_stats():
    """
    Obtiene estadísticas detalladas del sistema.
    
    Returns:
        APIResponse con estadísticas del sistema
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Estadísticas por driver
        stats_by_driver = {}
        for driver_type in ['linux_cluster', 'openstack']:
            slices_count = conn.Select("COUNT(*)", "slice", f"tipo='{driver_type}'")[0][0]
            
            # VMs por driver (basado en slices)
            vms_count = conn.Select(
                "COUNT(*)",
                "vm v JOIN slice s ON v.topologia_id_topologia = s.id_slice",
                f"s.tipo='{driver_type}'"
            )[0][0]
            
            stats_by_driver[driver_type] = {
                "slices": slices_count,
                "vms": vms_count
            }
        
        # Utilización de recursos por zona
        zone_stats = conn.Select(
            "z.nombre,COUNT(s.id_servidor) as servidores,"
            "SUM(r.ram) as ram_total,SUM(r.ram_available) as ram_disponible,"
            "SUM(r.vcpu) as vcpu_total,SUM(r.vcpu_available) as vcpu_disponible",
            "zona_disponibilidad z "
            "LEFT JOIN servidor s ON z.idzona_disponibilidad = s.id_zona "
            "LEFT JOIN recursos r ON s.id_recurso = r.id_recursos",
            "-1 GROUP BY z.idzona_disponibilidad,z.nombre"
        )
        
        zone_utilization = []
        for zone_row in zone_stats:
            (zona_nombre, servidores, ram_total, ram_disponible, vcpu_total, vcpu_disponible) = zone_row
            
            ram_uso_pct = 0
            vcpu_uso_pct = 0
            
            if ram_total and ram_disponible:
                ram_uso_pct = ((ram_total - ram_disponible) / ram_total) * 100
            if vcpu_total and vcpu_disponible:
                vcpu_uso_pct = ((vcpu_total - vcpu_disponible) / vcpu_total) * 100
            
            zone_utilization.append({
                "zona": zona_nombre,
                "servidores": servidores,
                "ram_uso_pct": round(ram_uso_pct, 2),
                "vcpu_uso_pct": round(vcpu_uso_pct, 2)
            })
        
        # Slices más recientes
        recent_slices = conn.Select(
            "nombre,tipo,estado,fecha_creacion",
            "slice",
            "-1 ORDER BY fecha_creacion DESC LIMIT 5"
        )
        
        recent_list = []
        for slice_row in recent_slices:
            nombre, tipo, estado, fecha_creacion = slice_row
            recent_list.append({
                "nombre": nombre,
                "tipo": tipo,
                "estado": estado,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None
            })
        
        stats = {
            "drivers": stats_by_driver,
            "zone_utilization": zone_utilization,
            "recent_slices": recent_list
        }
        
        return APIResponse(
            success=True,
            message="Estadísticas del sistema",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")