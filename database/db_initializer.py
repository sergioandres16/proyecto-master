"""
===================================================================
INICIALIZADOR DE BASE DE DATOS - SQLite3
===================================================================

Este módulo se encarga de inicializar la base de datos SQLite3
del sistema, crear las tablas necesarias y poblar con datos iniciales.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Optional

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from conf.ConfigManager import config


class DatabaseInitializer:
    """
    Inicializador de base de datos SQLite3.
    
    Responsabilidades:
    - Crear directorios de datos
    - Inicializar esquema de base de datos
    - Poblar con datos iniciales
    - Verificar integridad de la base de datos
    - Migrar datos desde versiones anteriores si es necesario
    """
    
    def __init__(self):
        """
        Inicializa el inicializador de base de datos.
        """
        self.db_config = config.get_db_config()
        self.data_dir = Path(self.db_config['data_dir'])
        self.db_path = Path(self.db_config.get('db_path', self.db_config.get('unified_db_path', './data/system.db')))
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Rutas de esquemas SQL
        self.schemas_dir = Path(__file__).parent / 'schemas'
        self.schema_path = self.schemas_dir / 'schema.sql'
    
    def create_data_directory(self) -> bool:
        """
        Crea el directorio de datos si no existe.
        
        Returns:
            bool: True si el directorio existe o fue creado exitosamente
        """
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Directorio de datos creado/verificado: {self.data_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Error creando directorio de datos: {e}")
            return False
    
    def load_schema_file(self, schema_path: Path) -> Optional[str]:
        """
        Carga un archivo de esquema SQL.
        
        Args:
            schema_path (Path): Ruta al archivo de esquema
            
        Returns:
            Optional[str]: Contenido del archivo o None si hay error
        """
        try:
            if not schema_path.exists():
                self.logger.error(f"Archivo de esquema no encontrado: {schema_path}")
                return None
            
            with open(schema_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.logger.info(f"Esquema cargado: {schema_path}")
                return content
                
        except Exception as e:
            self.logger.error(f"Error leyendo esquema {schema_path}: {e}")
            return None
    
    def execute_schema(self, db_path: Path, schema_sql: str) -> bool:
        """
        Ejecuta un esquema SQL en una base de datos.
        
        Args:
            db_path (Path): Ruta a la base de datos
            schema_sql (str): Contenido del esquema SQL
            
        Returns:
            bool: True si la ejecución fue exitosa
        """
        conn = None
        try:
            conn = sqlite3.connect(str(db_path))
            
            # Habilitar claves foráneas
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Ejecutar el esquema
            conn.executescript(schema_sql)
            conn.commit()
            
            self.logger.info(f"Esquema ejecutado exitosamente en: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando esquema en {db_path}: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self) -> bool:
        """
        Inicializa la base de datos del sistema.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            self.logger.info("Inicializando base de datos...")
            
            # Cargar esquema
            schema_sql = self.load_schema_file(self.schema_path)
            if not schema_sql:
                return False
            
            # Ejecutar esquema
            if not self.execute_schema(self.db_path, schema_sql):
                return False
            
            self.logger.info("Base de datos inicializada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            return False
    
    
    def verify_database_integrity(self, db_path: Path) -> bool:
        """
        Verifica la integridad de una base de datos.
        
        Args:
            db_path (Path): Ruta a la base de datos
            
        Returns:
            bool: True si la base de datos está íntegra
        """
        conn = None
        try:
            conn = sqlite3.connect(str(db_path))
            
            # Verificar integridad
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            is_ok = result and result[0] == 'ok'
            
            if is_ok:
                self.logger.info(f"Integridad verificada: {db_path}")
            else:
                self.logger.warning(f"Problemas de integridad en: {db_path}")
            
            return is_ok
            
        except Exception as e:
            self.logger.error(f"Error verificando integridad de {db_path}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_database_info(self, db_path: Path) -> dict:
        """
        Obtiene información sobre una base de datos.
        
        Args:
            db_path (Path): Ruta a la base de datos
            
        Returns:
            dict: Información de la base de datos
        """
        conn = None
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Obtener tamaño de archivo
            file_size = db_path.stat().st_size if db_path.exists() else 0
            
            # Obtener versión de SQLite
            cursor.execute("SELECT sqlite_version()")
            sqlite_version = cursor.fetchone()[0]
            
            info = {
                'path': str(db_path),
                'exists': db_path.exists(),
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'tables': tables,
                'table_count': len(tables),
                'sqlite_version': sqlite_version
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de {db_path}: {e}")
            return {'path': str(db_path), 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def populate_sample_data(self) -> bool:
        """
        Pobla la base de datos con datos de ejemplo para testing.
        
        Returns:
            bool: True si los datos fueron insertados exitosamente
        """
        try:
            self.logger.info("Poblando base de datos con datos de ejemplo...")
            
            # Datos de ejemplo para la base de datos
            unified_sample_data = """
            -- Zona de disponibilidad de ejemplo
            INSERT OR IGNORE INTO zona_disponibilidad (nombre, descripcion) 
            VALUES ('Zona-Principal', 'Zona principal del datacenter');
            
            -- Recursos de ejemplo
            INSERT OR IGNORE INTO recursos (ram, vcpu, storage, ram_available, vcpu_available, storage_available)
            VALUES 
                (16384, 8, 500, 12288, 6, 300),
                (32768, 16, 1000, 20480, 12, 600),
                (65536, 32, 2000, 49152, 24, 1200);
            
            -- Servidores de ejemplo
            INSERT OR IGNORE INTO servidor (nombre, ip, descripcion, id_zona, id_recurso) 
            VALUES 
                ('Worker1', '10.20.12.58', 'Servidor Worker 1', 1, 1),
                ('Worker2', '10.20.12.59', 'Servidor Worker 2', 1, 2),
                ('Compute1', '10.20.12.54', 'Servidor Compute 1', 1, 3);
            
            -- Nodos del cluster
            INSERT OR IGNORE INTO nodo_cluster (nombre, ip_address, puerto_vnc, estado, worker_id)
            VALUES 
                ('worker1-node', '10.20.12.58', 5901, 'activo', 1),
                ('worker2-node', '10.20.12.59', 5902, 'activo', 2),
                ('compute1-node', '10.20.12.54', 5903, 'activo', 3);
            
            -- Slice de ejemplo
            INSERT OR IGNORE INTO slice (nombre, tipo, vlan_id, estado)
            VALUES ('slice-ejemplo', 'linux_cluster', 100, 'creado');
            """
            
            # Ejecutar datos de ejemplo en base de datos
            conn = sqlite3.connect(str(self.db_path))
            conn.executescript(unified_sample_data)
            conn.commit()
            conn.close()
            
            self.logger.info("Datos de ejemplo insertados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error poblando datos de ejemplo: {e}")
            return False
    
    def initialize_all(self, populate_samples: bool = False) -> bool:
        """
        Inicializa el sistema de base de datos.
        
        Args:
            populate_samples (bool): Si incluir datos de ejemplo
            
        Returns:
            bool: True si toda la inicialización fue exitosa
        """
        try:
            self.logger.info("=== INICIANDO INICIALIZACIÓN DE BASE DE DATOS ===")
            
            # 1. Crear directorio de datos
            if not self.create_data_directory():
                return False
            
            # 2. Inicializar base de datos
            if not self.initialize_database():
                return False
            
            # 3. Verificar integridad
            db_ok = self.verify_database_integrity(self.db_path)
            
            if not db_ok:
                self.logger.error("Fallo en verificación de integridad")
                return False
            
            # 4. Poblar con datos de ejemplo si se solicita
            if populate_samples:
                if not self.populate_sample_data():
                    self.logger.warning("Fallo poblando datos de ejemplo")
            
            self.logger.info("=== INICIALIZACIÓN COMPLETADA EXITOSAMENTE ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en inicialización completa: {e}")
            return False
    
    def reset_database(self) -> bool:
        """
        Resetea la base de datos eliminando el archivo existente.
        ¡CUIDADO: Esta operación elimina todos los datos!
        
        Returns:
            bool: True si el reset fue exitoso
        """
        try:
            self.logger.warning("RESETEANDO BASE DE DATOS - SE PERDERÁN TODOS LOS DATOS")
            
            # Eliminar archivo de base de datos
            if self.db_path.exists():
                self.db_path.unlink()
                self.logger.info(f"Base de datos eliminada: {self.db_path}")
            
            # Eliminar archivos WAL y SHM si existen
            wal_path = Path(str(self.db_path) + '-wal')
            shm_path = Path(str(self.db_path) + '-shm')
            
            if wal_path.exists():
                wal_path.unlink()
            if shm_path.exists():
                shm_path.unlink()
            
            self.logger.info("Reset de base de datos completado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en reset de base de datos: {e}")
            return False
    
    def get_status_report(self) -> dict:
        """
        Genera un reporte del estado de la base de datos.
        
        Returns:
            dict: Reporte completo del estado
        """
        try:
            report = {
                'timestamp': str(Path(__file__).stat().st_mtime),
                'data_directory': {
                    'path': str(self.data_dir),
                    'exists': self.data_dir.exists()
                },
                'database': self.get_database_info(self.db_path),
                'integrity': {
                    'database': self.verify_database_integrity(self.db_path) if self.db_path.exists() else False
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de estado: {e}")
            return {'error': str(e)}


def main():
    """
    Función principal para ejecutar la inicialización desde línea de comandos.
    """
    import argparse
    import json
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Inicializador de base de datos SQLite3')
    parser.add_argument('--reset', action='store_true', help='Resetear base de datos existente')
    parser.add_argument('--samples', action='store_true', help='Incluir datos de ejemplo')
    parser.add_argument('--status', action='store_true', help='Mostrar estado de la base de datos')
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer()
    
    if args.status:
        # Mostrar estado
        report = initializer.get_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    
    if args.reset:
        # Resetear base de datos
        if initializer.reset_database():
            print("✅ Base de datos reseteada exitosamente")
        else:
            print("❌ Error reseteando base de datos")
            return
    
    # Inicializar base de datos
    if initializer.initialize_all(populate_samples=args.samples):
        print("✅ Base de datos inicializada exitosamente")
        if args.samples:
            print("📊 Datos de ejemplo incluidos")
    else:
        print("❌ Error inicializando base de datos")


if __name__ == '__main__':
    main()