"""
===================================================================
RUTAS LINUX CLUSTER - API REST
===================================================================

Endpoints específicos para el driver de Linux Cluster.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import sys
from pathlib import Path as PathLib

# Agregar el directorio raíz al path
root_dir = PathLib(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from api.models import APIResponse, WorkerInfo
from drivers.linux_cluster_driver import LinuxClusterDriver

router = APIRouter(prefix="/linux-cluster", tags=["linux-cluster"])
logger = logging.getLogger(__name__)


@router.get("/workers", response_model=APIResponse)
async def get_workers():
    """
    Obtiene información de todos los workers del cluster Linux.
    
    Returns:
        APIResponse con lista de workers
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Obtener workers con sus recursos
        workers = conn.Select(
            "s.id_servidor,s.nombre,s.ip,s.descripcion,s.max_vnc,"
            "r.ram,r.vcpu,r.storage,r.ram_available,r.vcpu_available,r.storage_available,"
            "z.nombre as zona_nombre",
            "servidor s "
            "LEFT JOIN recursos r ON s.id_recurso = r.id_recursos "
            "LEFT JOIN zona_disponibilidad z ON s.id_zona = z.idzona_disponibilidad",
            "-1"
        )
        
        worker_list = []
        for worker_row in workers:
            (worker_id, nombre, ip, descripcion, max_vnc,
             ram_total, vcpu_total, storage_total,
             ram_available, vcpu_available, storage_available,
             zona_nombre) = worker_row
            
            # Calcular utilización
            ram_uso = 0
            vcpu_uso = 0
            storage_uso = 0
            
            if ram_total and ram_available:
                ram_uso = ((ram_total - ram_available) / ram_total) * 100
            if vcpu_total and vcpu_available:
                vcpu_uso = ((vcpu_total - vcpu_available) / vcpu_total) * 100
            if storage_total and storage_available:
                storage_uso = ((storage_total - storage_available) / storage_total) * 100
            
            worker_info = {
                "id": worker_id,
                "nombre": nombre,
                "ip": ip,
                "descripcion": descripcion,
                "max_vnc": max_vnc,
                "zona": zona_nombre,
                "recursos": {
                    "ram_total": ram_total,
                    "ram_disponible": ram_available,
                    "ram_uso_pct": round(ram_uso, 2),
                    "vcpu_total": vcpu_total,
                    "vcpu_disponible": vcpu_available,
                    "vcpu_uso_pct": round(vcpu_uso, 2),
                    "storage_total": storage_total,
                    "storage_disponible": storage_available,
                    "storage_uso_pct": round(storage_uso, 2)
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


@router.get("/workers/{worker_id}/vms", response_model=APIResponse)
async def get_worker_vms(worker_id: int):
    """
    Obtiene todas las VMs de un worker específico.
    
    Args:
        worker_id: ID del worker
        
    Returns:
        APIResponse con VMs del worker
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Verificar que el worker existe
        worker_info = conn.Select("nombre", "servidor", f"id_servidor={worker_id}")
        if not worker_info:
            raise HTTPException(
                status_code=404,
                detail=f"Worker {worker_id} no encontrado"
            )
        
        worker_name = worker_info[0][0]
        
        # Obtener VMs del worker
        vms = conn.Select(
            "v.id_vm,v.nombre,v.estado,v.vnc,v.fecha_creacion,"
            "s.nombre as slice_nombre,r.ram,r.vcpu,r.storage",
            "vm v "
            "LEFT JOIN slice s ON v.topologia_id_topologia = s.id_slice "
            "LEFT JOIN recursos r ON v.recursos_id_estado = r.id_recursos",
            f"v.servidor_id_servidor={worker_id}"
        )
        
        vm_list = []
        for vm_row in vms:
            (vm_id, vm_nombre, estado, vnc_port, fecha_creacion,
             slice_nombre, ram, vcpu, storage) = vm_row
            
            vm_info = {
                "id": vm_id,
                "nombre": vm_nombre,
                "estado": estado,
                "vnc_port": vnc_port,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None,
                "slice": slice_nombre,
                "recursos": {
                    "ram": ram,
                    "vcpu": vcpu,
                    "storage": storage
                }
            }
            
            vm_list.append(vm_info)
        
        return APIResponse(
            success=True,
            message=f"Worker {worker_name} tiene {len(vm_list)} VMs",
            data={
                "worker_id": worker_id,
                "worker_name": worker_name,
                "vms": vm_list,
                "total_vms": len(vm_list)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo VMs del worker {worker_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/cluster-metrics", response_model=APIResponse)
async def get_cluster_metrics(
    hours: int = Query(default=24, ge=1, le=168, description="Horas hacia atrás")
):
    """
    Obtiene métricas del cluster Linux.
    
    Args:
        hours: Número de horas hacia atrás para las métricas
        
    Returns:
        APIResponse con métricas del cluster
    """
    try:
        driver = LinuxClusterDriver()
        metrics = driver.get_cluster_metrics_summary(hours)
        
        if not metrics:
            return APIResponse(
                success=True,
                message="No hay métricas disponibles",
                data={"metricas": {}, "periodo_horas": hours}
            )
        
        return APIResponse(
            success=True,
            message=f"Métricas del cluster para las últimas {hours} horas",
            data=metrics
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas del cluster: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/network-status", response_model=APIResponse)
async def get_network_status():
    """
    Obtiene el estado de la red del cluster Linux.
    
    Returns:
        APIResponse con estado de la red
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Obtener VLANs en uso
        vlans = conn.Select(
            "vlan_id,nombre,COUNT(*) as slices_count",
            "slice",
            "vlan_id IS NOT NULL GROUP BY vlan_id,nombre"
        )
        
        # Obtener próximo VLAN ID
        max_vlan = conn.GetMaxVlan()
        next_vlan = (max_vlan[0][0] + 1) if max_vlan[0][0] else 1
        
        # Obtener estadísticas de enlaces
        enlaces_stats = conn.Select(
            "COUNT(*) as total_enlaces",
            "enlace",
            "-1"
        )
        
        vlan_list = []
        for vlan_row in vlans:
            vlan_id, slice_name, slice_count = vlan_row
            vlan_list.append({
                "vlan_id": vlan_id,
                "slice_name": slice_name,
                "slices_count": slice_count
            })
        
        network_status = {
            "vlans_en_uso": vlan_list,
            "total_vlans": len(vlan_list),
            "proximo_vlan_id": next_vlan,
            "total_enlaces": enlaces_stats[0][0] if enlaces_stats else 0
        }
        
        return APIResponse(
            success=True,
            message="Estado de la red del cluster",
            data=network_status
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de red: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/test-connection", response_model=APIResponse)
async def test_cluster_connection():
    """
    Prueba la conexión con la API del cluster Linux.
    
    Returns:
        APIResponse con resultado de la prueba
    """
    try:
        import requests
        from conf.ConfigManager import config
        
        cluster_config = config.get_cluster_config()
        api_url = cluster_config['api_url']
        
        # Probar conectividad básica
        response = requests.get(f"{api_url}/health", timeout=10)
        
        if response.status_code == 200:
            return APIResponse(
                success=True,
                message="Conexión exitosa con el cluster",
                data={
                    "api_url": api_url,
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            )
        else:
            return APIResponse(
                success=False,
                message="Conexión fallida con el cluster",
                data={
                    "api_url": api_url,
                    "status_code": response.status_code,
                    "error": "Respuesta no exitosa"
                }
            )
        
    except requests.exceptions.ConnectionError:
        return APIResponse(
            success=False,
            message="No se pudo conectar al cluster",
            error="Error de conexión - verifique que la API del cluster esté ejecutándose"
        )
    except requests.exceptions.Timeout:
        return APIResponse(
            success=False,
            message="Timeout conectando al cluster",
            error="La conexión tardó más de 10 segundos"
        )
    except Exception as e:
        logger.error(f"Error probando conexión del cluster: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")