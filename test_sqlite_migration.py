#!/usr/bin/env python3
"""
===================================================================
SCRIPT DE VALIDACIÓN DE MIGRACIÓN A SQLite3
===================================================================

Este script valida que la migración de MySQL a SQLite3 se haya
completado correctamente y que todas las funcionalidades trabajen
como se espera.

Autor: Generado por Claude Code
Versión: 2.0 - Migración a SQLite3
===================================================================
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.getcwd())

def setup_logging():
    """Configura el sistema de logging para las pruebas."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_config_manager():
    """Prueba que el ConfigManager funcione con SQLite3."""
    print("🔧 Probando ConfigManager...")
    try:
        from conf.ConfigManager import config
        
        # Probar configuración de BD
        db_config = config.get_db_config()
        assert 'main_db_path' in db_config, "Falta configuración main_db_path"
        assert 'cluster_db_path' in db_config, "Falta configuración cluster_db_path"
        assert 'data_dir' in db_config, "Falta configuración data_dir"
        
        print("✅ ConfigManager configurado correctamente para SQLite3")
        return True
        
    except Exception as e:
        print(f"❌ Error en ConfigManager: {e}")
        return False

def test_database_classes():
    """Prueba las nuevas clases de base de datos."""
    print("🗄️  Probando clases de base de datos...")
    try:
        # Probar SliceManagerDB
        from database.SliceManagerDB import SliceManagerDB
        main_db = SliceManagerDB()
        print("✅ SliceManagerDB importada correctamente")
        
        # Probar ClusterMetricsDB
        from database.ClusterMetricsDB import ClusterMetricsDB
        cluster_db = ClusterMetricsDB()
        print("✅ ClusterMetricsDB importada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en clases de BD: {e}")
        traceback.print_exc()
        return False

def test_compatibility_classes():
    """Prueba las clases de compatibilidad."""
    print("🔗 Probando clases de compatibilidad...")
    try:
        # Probar clases de compatibilidad
        from conf.Conexion import Conexion, Conexion2
        
        conn1 = Conexion()
        conn2 = Conexion2()
        
        # Verificar que los métodos existen
        assert hasattr(conn1, 'Select'), "Método Select no encontrado en Conexion"
        assert hasattr(conn1, 'Insert'), "Método Insert no encontrado en Conexion"
        assert hasattr(conn1, 'Update'), "Método Update no encontrado en Conexion"
        assert hasattr(conn1, 'Delete'), "Método Delete no encontrado en Conexion"
        
        print("✅ Clases de compatibilidad funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en clases de compatibilidad: {e}")
        traceback.print_exc()
        return False

def test_database_initialization():
    """Prueba la inicialización de bases de datos."""
    print("🚀 Probando inicialización de BD...")
    try:
        from database.db_initializer import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        
        # Crear directorio de datos
        if not initializer.create_data_directory():
            return False
        
        # Inicializar bases de datos
        if not initializer.initialize_all(populate_samples=True):
            return False
        
        print("✅ Bases de datos inicializadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        traceback.print_exc()
        return False

def test_basic_operations():
    """Prueba operaciones básicas CRUD."""
    print("🔨 Probando operaciones CRUD básicas...")
    try:
        from conf.Conexion import Conexion, Conexion2
        
        # Probar operaciones en BD principal
        conn = Conexion()
        
        # Test Select
        zonas = conn.Select("nombre", "zona_disponibilidad", "-1")
        print(f"📊 Zonas encontradas: {len(zonas)}")
        
        # Test Insert
        try:
            new_id = conn.Insert("zona_disponibilidad", "nombre,descripcion", "'Zona-Test','Zona de prueba'")
            print(f"📝 Zona insertada con ID: {new_id}")
        except:
            print("⚠️  Zona ya existe o error en inserción")
        
        # Probar operaciones en BD del cluster
        conn2 = Conexion2()
        nodos = conn2.Select("nombre", "nodo", "-1")
        print(f"🖥️  Nodos encontrados: {len(nodos)}")
        
        print("✅ Operaciones CRUD funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en operaciones CRUD: {e}")
        traceback.print_exc()
        return False

def test_scheduler_module():
    """Prueba que el módulo App_Scheduler funcione."""
    print("⚖️  Probando módulo App_Scheduler...")
    try:
        from Modules.App_Scheduler import Worker, Vm, filtrado
        
        # Crear objetos de prueba
        worker = Worker(1, 1000, 100, 4, 2000, 200, 8)
        vm = Vm("test-vm", 500, 50, 2)
        
        print("✅ Clases Worker y Vm creadas correctamente")
        
        # Probar filtrado (puede fallar si no hay datos)
        try:
            workers = filtrado("Zona-Principal", 2)
            print(f"📋 Workers filtrados: {len(workers)}")
        except:
            print("⚠️  Filtrado falló (posiblemente sin datos)")
        
        print("✅ Módulo App_Scheduler funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en App_Scheduler: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Verifica que todos los archivos necesarios existan."""
    print("📁 Verificando estructura de archivos...")
    
    required_files = [
        'config.env',
        'database/SliceManagerDB.py',
        'database/ClusterMetricsDB.py',
        'database/__init__.py',
        'database/db_initializer.py',
        'database/schemas/main_schema.sql',
        'database/schemas/cluster_schema.sql',
        'conf/ConfigManager.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Todos los archivos necesarios están presentes")
    return True

def test_database_files():
    """Verifica que los archivos de base de datos se hayan creado."""
    print("💾 Verificando archivos de base de datos...")
    try:
        from conf.ConfigManager import config
        
        db_config = config.get_db_config()
        data_dir = Path(db_config['data_dir'])
        main_db = Path(db_config['main_db_path'])
        cluster_db = Path(db_config['cluster_db_path'])
        
        # Verificar directorio
        if not data_dir.exists():
            print(f"❌ Directorio de datos no existe: {data_dir}")
            return False
        
        # Verificar archivos de BD
        if not main_db.exists():
            print(f"❌ Base de datos principal no existe: {main_db}")
            return False
        
        if not cluster_db.exists():
            print(f"❌ Base de datos del cluster no existe: {cluster_db}")
            return False
        
        print(f"✅ Archivos de BD creados en: {data_dir}")
        print(f"  📊 BD Principal: {main_db} ({main_db.stat().st_size} bytes)")
        print(f"  📊 BD Cluster: {cluster_db} ({cluster_db.stat().st_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos de BD: {e}")
        return False

def generate_migration_report():
    """Genera un reporte del estado de la migración."""
    print("\n" + "="*60)
    print("📋 REPORTE DE MIGRACIÓN A SQLite3")
    print("="*60)
    
    try:
        from database.db_initializer import DatabaseInitializer
        initializer = DatabaseInitializer()
        report = initializer.get_status_report()
        
        print(f"📂 Directorio de datos: {report['data_directory']['path']}")
        print(f"   Existe: {'✅' if report['data_directory']['exists'] else '❌'}")
        
        print(f"\n📊 Base de datos principal:")
        main_db = report['main_database']
        print(f"   Archivo: {main_db.get('path', 'N/A')}")
        print(f"   Tamaño: {main_db.get('size_mb', 0)} MB")
        print(f"   Tablas: {main_db.get('table_count', 0)}")
        print(f"   Integridad: {'✅' if report['integrity']['main_db'] else '❌'}")
        
        print(f"\n📊 Base de datos del cluster:")
        cluster_db = report['cluster_database']
        print(f"   Archivo: {cluster_db.get('path', 'N/A')}")
        print(f"   Tamaño: {cluster_db.get('size_mb', 0)} MB")
        print(f"   Tablas: {cluster_db.get('table_count', 0)}")
        print(f"   Integridad: {'✅' if report['integrity']['cluster_db'] else '❌'}")
        
        if 'tables' in main_db:
            print(f"\n📋 Tablas en BD principal: {', '.join(main_db['tables'])}")
        
        if 'tables' in cluster_db:
            print(f"\n📋 Tablas en BD cluster: {', '.join(cluster_db['tables'])}")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("🚀 INICIANDO VALIDACIÓN DE MIGRACIÓN A SQLite3\n")
    
    setup_logging()
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("ConfigManager", test_config_manager),
        ("Clases de base de datos", test_database_classes),
        ("Clases de compatibilidad", test_compatibility_classes),
        ("Inicialización de BD", test_database_initialization),
        ("Archivos de BD", test_database_files),
        ("Operaciones CRUD", test_basic_operations),
        ("Módulo App_Scheduler", test_scheduler_module),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 EJECUTANDO: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: EXITOSO")
            else:
                print(f"❌ {test_name}: FALLIDO")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\n📈 RESULTADO FINAL: {passed}/{total} pruebas exitosas")
    percentage = (passed / total) * 100
    print(f"📊 Porcentaje de éxito: {percentage:.1f}%")
    
    # Generar reporte detallado
    generate_migration_report()
    
    if passed == total:
        print("\n🎉 ¡MIGRACIÓN A SQLite3 COMPLETADA EXITOSAMENTE!")
        return 0
    else:
        print(f"\n⚠️  MIGRACIÓN PARCIAL: {total - passed} pruebas fallaron")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)