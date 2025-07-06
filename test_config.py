#!/usr/bin/env python3
"""
Script de prueba para validar que la configuración externalizada funciona correctamente
"""

import os
import sys
sys.path.append(os.getcwd())

def test_config_manager():
    """
    Prueba el gestor de configuración
    """
    try:
        from conf.ConfigManager import config
        
        print("=== VALIDACIÓN DEL GESTOR DE CONFIGURACIÓN ===\n")
        
        # Validar configuración general
        print("✅ ConfigManager importado correctamente")
        
        # Validar que la configuración se carga
        if config.validate_config():
            print("✅ Configuración válida")
        else:
            print("❌ Configuración inválida")
            return False
        
        # Probar configuraciones específicas
        print("\n=== CONFIGURACIONES CARGADAS ===")
        
        # Base de datos
        db_config = config.get_db_config()
        print(f"📊 Base de datos: {db_config['host']}:{db_config['port']}")
        print(f"📊 BD General: {db_config['database_general']}")
        print(f"📊 BD Cluster: {db_config['database_cluster']}")
        
        # OpenStack
        openstack_config = config.get_openstack_config()
        print(f"☁️  OpenStack Keystone: {openstack_config['keystone_url']}")
        print(f"☁️  OpenStack Nova: {openstack_config['nova_url']}")
        print(f"☁️  OpenStack Neutron: {openstack_config['neutron_url']}")
        
        # Linux Cluster
        cluster_config = config.get_cluster_config()
        print(f"🖥️  Cluster API: {cluster_config['api_url']}")
        print(f"🖥️  VM Create: {cluster_config['vm_create_endpoint']}")
        print(f"🖥️  VM Delete: {cluster_config['vm_delete_endpoint']}")
        
        # Scheduler
        scheduler_config = config.get_scheduler_config()
        print(f"⚖️  Scheduler - RAM Weight: {scheduler_config['ram_weight']}")
        print(f"⚖️  Scheduler - Disk Weight: {scheduler_config['disk_weight']}")
        print(f"⚖️  Scheduler - vCPU Weight: {scheduler_config['vcpu_weight']}")
        
        # Red
        network_config = config.get_network_config()
        print(f"🌐 Red base CIDR: {network_config['base_cidr']}")
        print(f"🌐 DNS: {network_config['dns_server']}")
        
        # Rutas
        paths_config = config.get_paths_config()
        print(f"📂 Ruta de slices: {paths_config['slices_config_path']}")
        print(f"📂 Extensión de archivos: {paths_config['slice_file_extension']}")
        
        # Workers
        worker_names = config.get_worker_names()
        print(f"🔧 Workers configurados: {len(worker_names)} workers")
        print(f"🔧 Primer worker: {worker_names[0] if worker_names else 'N/A'}")
        
        # Constantes varias
        print(f"🔌 Puerto VNC base: {config.get('VNC_BASE_PORT')}")
        print(f"📏 Factor de recursos: {config.get('RESOURCE_FACTOR')}")
        print(f"💾 Bytes a MB: {config.get('BYTES_TO_MB')}")
        print(f"💾 Bytes a GB: {config.get('BYTES_TO_GB')}")
        
        print("\n✅ Todas las configuraciones se cargaron correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en la validación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """
    Prueba que todos los módulos puedan importar ConfigManager
    """
    print("\n=== VALIDACIÓN DE IMPORTS ===\n")
    
    modules_to_test = [
        'conf.Conexion',
        'Modules.App_Scheduler',
        'Modules.SliceAdministrator',
        'Modules.LinuxClusterDriver',
        'Modules.OpenStackDriver',
        'Modules.Validador',
        'Modules.UserInterface'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(modules_to_test)} módulos importados correctamente")
    return success_count == len(modules_to_test)

def main():
    """
    Función principal de prueba
    """
    print("🚀 INICIANDO VALIDACIÓN DE CONFIGURACIÓN EXTERNALIZADA\n")
    
    # Verificar que existe el archivo de configuración
    config_file = "config.env"
    if not os.path.exists(config_file):
        print(f"⚠️  Archivo {config_file} no encontrado, usando configuración por defecto")
    else:
        print(f"✅ Archivo {config_file} encontrado")
    
    # Probar ConfigManager
    config_test = test_config_manager()
    
    # Probar imports
    import_test = test_imports()
    
    # Resultado final
    print("\n" + "="*50)
    if config_test and import_test:
        print("🎉 VALIDACIÓN EXITOSA: La configuración externalizada funciona correctamente")
        return 0
    else:
        print("❌ VALIDACIÓN FALLIDA: Hay problemas con la configuración externalizada")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)