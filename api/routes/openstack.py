"""
===================================================================
RUTAS OPENSTACK - API REST
===================================================================

Endpoints específicos para el driver de OpenStack.

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

from api.models import APIResponse, HypervisorInfo, FlavorInfo
from drivers.openstack_driver import OpenStackDriver

router = APIRouter(prefix="/openstack", tags=["openstack"])
logger = logging.getLogger(__name__)


@router.get("/hypervisors", response_model=APIResponse)
async def get_hypervisors():
    """
    Obtiene información de todos los hipervisores de OpenStack.
    
    Returns:
        APIResponse con lista de hipervisores
    """
    try:
        driver = OpenStackDriver()
        hypervisors = driver.get_hypervisor_info()
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(hypervisors)} hipervisores",
            data={"hypervisors": hypervisors, "total": len(hypervisors)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo hipervisores: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/hypervisors/{hypervisor_name}/vms", response_model=APIResponse)
async def get_hypervisor_vms(hypervisor_name: str):
    """
    Obtiene todas las VMs de un hipervisor específico.
    
    Args:
        hypervisor_name: Nombre del hipervisor
        
    Returns:
        APIResponse con VMs del hipervisor
    """
    try:
        from conf.Conexion import Conexion
        
        conn = Conexion()
        
        # Obtener ID del servidor por nombre
        server_info = conn.Select("id_servidor", "servidor", f"nombre='{hypervisor_name}'")
        if not server_info:
            raise HTTPException(
                status_code=404,
                detail=f"Hipervisor {hypervisor_name} no encontrado en BD local"
            )
        
        server_id = server_info[0][0]
        
        # Obtener VMs del hipervisor
        vms = conn.Select(
            "v.id_vm,v.nombre,v.estado,v.fecha_creacion,"
            "s.nombre as slice_nombre,s.tipo as slice_tipo,"
            "r.ram,r.vcpu,r.storage",
            "vm v "
            "LEFT JOIN slice s ON v.topologia_id_topologia = s.id_slice "
            "LEFT JOIN recursos r ON v.recursos_id_estado = r.id_recursos",
            f"v.servidor_id_servidor={server_id} AND s.tipo='openstack'"
        )
        
        vm_list = []
        driver = OpenStackDriver()
        
        for vm_row in vms:
            (vm_id, vm_nombre, estado, fecha_creacion,
             slice_nombre, slice_tipo, ram, vcpu, storage) = vm_row
            
            # Obtener estado de OpenStack
            openstack_status = driver._get_vm_status_from_openstack(vm_nombre)
            
            vm_info = {
                "id": vm_id,
                "nombre": vm_nombre,
                "estado": estado,
                "fecha_creacion": str(fecha_creacion) if fecha_creacion else None,
                "slice": slice_nombre,
                "recursos": {
                    "ram": ram,
                    "vcpu": vcpu,
                    "storage": storage
                },
                "openstack_status": openstack_status
            }
            
            vm_list.append(vm_info)
        
        return APIResponse(
            success=True,
            message=f"Hipervisor {hypervisor_name} tiene {len(vm_list)} VMs",
            data={
                "hypervisor_name": hypervisor_name,
                "vms": vm_list,
                "total_vms": len(vm_list)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo VMs del hipervisor {hypervisor_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/flavors", response_model=APIResponse)
async def get_flavors():
    """
    Obtiene todos los flavors disponibles en la base de datos local.
    
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


@router.get("/flavors/openstack", response_model=APIResponse)
async def get_openstack_flavors():
    """
    Obtiene flavors directamente de OpenStack.
    
    Returns:
        APIResponse con flavors de OpenStack
    """
    try:
        import requests
        from conf.ConfigManager import config
        
        driver = OpenStackDriver()
        token = driver._get_token()
        
        openstack_config = config.get_openstack_config()
        headers = {"X-Auth-Token": token}
        
        response = requests.get(
            f"{openstack_config['nova_url']}/flavors/detail",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        openstack_flavors = response.json()["flavors"]
        
        flavor_list = []
        for flavor in openstack_flavors:
            flavor_info = {
                "id": flavor["id"],
                "nombre": flavor["name"],
                "vcpus": flavor["vcpus"],
                "ram": flavor["ram"],
                "disk": flavor["disk"],
                "public": flavor.get("os-flavor-access:is_public", True)
            }
            flavor_list.append(flavor_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(flavor_list)} flavors en OpenStack",
            data={"flavors": flavor_list, "total": len(flavor_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo flavors de OpenStack: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/images", response_model=APIResponse)
async def get_images():
    """
    Obtiene todas las imágenes disponibles en la base de datos local.
    
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


@router.get("/networks", response_model=APIResponse)
async def get_networks():
    """
    Obtiene todas las redes de OpenStack.
    
    Returns:
        APIResponse con lista de redes
    """
    try:
        import requests
        from conf.ConfigManager import config
        
        driver = OpenStackDriver()
        token = driver._get_token()
        
        openstack_config = config.get_openstack_config()
        headers = {"X-Auth-Token": token}
        
        response = requests.get(
            f"{openstack_config['neutron_url']}/networks",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        networks = response.json()["networks"]
        
        network_list = []
        for network in networks:
            network_info = {
                "id": network["id"],
                "nombre": network["name"],
                "estado": network["status"],
                "admin_state": network["admin_state_up"],
                "shared": network["shared"],
                "external": network.get("router:external", False),
                "provider_type": network.get("provider:network_type"),
                "segmentation_id": network.get("provider:segmentation_id")
            }
            network_list.append(network_info)
        
        return APIResponse(
            success=True,
            message=f"Se encontraron {len(network_list)} redes en OpenStack",
            data={"networks": network_list, "total": len(network_list)}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo redes de OpenStack: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/test-connection", response_model=APIResponse)
async def test_openstack_connection():
    """
    Prueba la conexión con OpenStack.
    
    Returns:
        APIResponse con resultado de la prueba
    """
    try:
        driver = OpenStackDriver()
        
        # Probar autenticación
        start_time = __import__('time').time()
        token = driver._get_token()
        auth_time = (__import__('time').time() - start_time) * 1000
        
        # Probar APIs
        services_status = {}
        
        # Test Keystone
        services_status["keystone"] = {
            "status": "ok" if token else "error",
            "response_time_ms": auth_time
        }
        
        # Test Nova
        try:
            import requests
            from conf.ConfigManager import config
            
            openstack_config = config.get_openstack_config()
            headers = {"X-Auth-Token": token}
            
            start_time = __import__('time').time()
            nova_response = requests.get(
                f"{openstack_config['nova_url']}/",
                headers=headers,
                timeout=10
            )
            nova_time = (__import__('time').time() - start_time) * 1000
            
            services_status["nova"] = {
                "status": "ok" if nova_response.status_code == 200 else "error",
                "response_time_ms": nova_time,
                "status_code": nova_response.status_code
            }
        except Exception as e:
            services_status["nova"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test Neutron
        try:
            start_time = __import__('time').time()
            neutron_response = requests.get(
                f"{openstack_config['neutron_url']}/",
                headers=headers,
                timeout=10
            )
            neutron_time = (__import__('time').time() - start_time) * 1000
            
            services_status["neutron"] = {
                "status": "ok" if neutron_response.status_code == 200 else "error",
                "response_time_ms": neutron_time,
                "status_code": neutron_response.status_code
            }
        except Exception as e:
            services_status["neutron"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Determinar estado general
        all_ok = all(
            service["status"] == "ok" 
            for service in services_status.values()
        )
        
        return APIResponse(
            success=all_ok,
            message="Conexión exitosa con OpenStack" if all_ok else "Problemas conectando con OpenStack",
            data={
                "services": services_status,
                "overall_status": "ok" if all_ok else "error"
            }
        )
        
    except Exception as e:
        logger.error(f"Error probando conexión de OpenStack: {e}")
        return APIResponse(
            success=False,
            message="Error probando conexión con OpenStack",
            error=str(e)
        )


@router.post("/refresh-hypervisors", response_model=APIResponse)
async def refresh_hypervisors():
    """
    Actualiza la información de hipervisores desde OpenStack.
    
    Returns:
        APIResponse con resultado de la actualización
    """
    try:
        driver = OpenStackDriver()
        hypervisors = driver.get_hypervisor_info()
        
        return APIResponse(
            success=True,
            message=f"Información de {len(hypervisors)} hipervisores actualizada",
            data={
                "hypervisors_updated": len(hypervisors),
                "hypervisors": hypervisors
            }
        )
        
    except Exception as e:
        logger.error(f"Error actualizando hipervisores: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")