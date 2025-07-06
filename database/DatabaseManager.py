"""
===================================================================
GESTOR DE BASE DE DATOS - SQLite3
===================================================================

Este módulo proporciona acceso a toda la información del sistema 
en una base de datos SQLite3, incluyendo gestión de slices, VMs, 
recursos, servidores y métricas del cluster.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

import sqlite3
import os
import logging
from typing import List, Tuple, Any, Optional, Union, Dict
from pathlib import Path
from conf.ConfigManager import config


class DatabaseManager:
    """
    Gestor de base de datos que maneja toda la información del sistema.
    
    Esta clase centraliza el acceso a:
    - Slices de red y máquinas virtuales
    - Servidores físicos y zonas de disponibilidad
    - Recursos y configuraciones
    - Nodos del cluster y métricas detalladas
    - Eventos, auditoría y configuración del sistema
    
    Beneficios:
    - Consultas relacionales eficientes
    - Transacciones ACID entre todas las entidades
    - Administración simplificada
    - Backup y restore centralizado
    """
    
    def __init__(self):
        """
        Inicializa el gestor de base de datos.
        Crea el directorio de datos si no existe.
        """
        self.db_config = config.get_db_config()
        self.db_path = self.db_config.get('db_path', './data/system.db')
        self.data_dir = self.db_config.get('data_dir', './data/')
        
        # Crear directorio de datos si no existe
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Establece y configura una conexión a la base de datos.
        
        Returns:
            sqlite3.Connection: Conexión configurada a la base de datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            # Configurar para devolver filas como diccionarios
            conn.row_factory = sqlite3.Row
            # Habilitar claves foráneas
            conn.execute("PRAGMA foreign_keys = ON")
            # Configurar WAL mode para mejor concurrencia
            conn.execute("PRAGMA journal_mode = WAL")
            # Optimizar para consultas complejas
            conn.execute("PRAGMA cache_size = 20000")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA temp_store = MEMORY")
            return conn
        except Exception as e:
            self.logger.error(f"Error conectando a la base de datos: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Union[Tuple, List]] = None) -> List[sqlite3.Row]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (optional): Parámetros para la consulta
            
        Returns:
            List[sqlite3.Row]: Lista de filas resultado
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            results = cursor.fetchall()
            return results
            
        except Exception as e:
            self.logger.error(f"Error ejecutando consulta: {e}")
            self.logger.error(f"Query: {query}")
            if params:
                self.logger.error(f"Params: {params}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_transaction(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """
        Ejecuta múltiples operaciones en una sola transacción.
        
        Args:
            operations: Lista de operaciones con formato:
                       [{'type': 'query|insert|update|delete', 'sql': '...', 'params': ...}]
                       
        Returns:
            List[Any]: Lista de resultados de cada operación
        """
        conn = None
        results = []
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for operation in operations:
                op_type = operation.get('type', 'query')
                sql = operation['sql']
                params = operation.get('params')
                
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                if op_type == 'query':
                    results.append(cursor.fetchall())
                elif op_type in ['insert', 'update', 'delete']:
                    if op_type == 'insert':
                        results.append(cursor.lastrowid)
                    else:
                        results.append(cursor.rowcount)
            
            conn.commit()
            return results
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error en transacción: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_insert(self, table: str, columns: str, values: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una inserción y retorna el ID del registro creado.
        
        Args:
            table (str): Nombre de la tabla
            columns (str): Columnas separadas por comas
            values (str): Placeholders de valores
            params (optional): Parámetros para la inserción
            
        Returns:
            int: ID del registro insertado
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            row_id = cursor.lastrowid
            conn.commit()
            return row_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error en inserción: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_update(self, table: str, set_clause: str, where_clause: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una actualización y retorna el número de filas afectadas.
        
        Args:
            table (str): Nombre de la tabla
            set_clause (str): Cláusula SET
            where_clause (str): Cláusula WHERE
            params (optional): Parámetros para la actualización
            
        Returns:
            int: Número de filas afectadas
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error en actualización: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_delete(self, table: str, where_clause: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una eliminación y retorna el número de filas afectadas.
        
        Args:
            table (str): Nombre de la tabla
            where_clause (str): Cláusula WHERE
            params (optional): Parámetros para la eliminación
            
        Returns:
            int: Número de filas eliminadas
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
            
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error en eliminación: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # ===================================================================
    # MÉTODOS ESPECÍFICOS PARA SLICES Y VMs
    # ===================================================================
    
    def get_slice_with_vms(self, slice_id: int) -> Dict[str, Any]:
        """
        Obtiene un slice completo con todas sus VMs y recursos.
        
        Args:
            slice_id (int): ID del slice
            
        Returns:
            Dict: Información completa del slice
        """
        try:
            # Obtener información del slice
            slice_query = """
            SELECT s.*, z.nombre as zona_nombre 
            FROM slice s 
            LEFT JOIN zona_disponibilidad z ON z.idzona_disponibilidad = (
                SELECT DISTINCT srv.id_zona 
                FROM vm v 
                JOIN servidor srv ON v.servidor_id_servidor = srv.id_servidor 
                WHERE v.topologia_id_topologia = s.id_slice 
                LIMIT 1
            )
            WHERE s.id_slice = ?
            """
            
            # Obtener VMs del slice
            vms_query = """
            SELECT v.*, s.nombre as servidor_nombre, i.nombre as imagen_nombre,
                   r.ram, r.vcpu, r.storage
            FROM vm v
            JOIN servidor s ON v.servidor_id_servidor = s.id_servidor
            LEFT JOIN imagen i ON v.imagen_id_imagen = i.id_imagen
            LEFT JOIN recursos r ON v.recursos_id_estado = r.id_recursos
            WHERE v.topologia_id_topologia = ?
            """
            
            # Obtener enlaces entre VMs
            enlaces_query = """
            SELECT ve.*, v1.nombre as vm_origen_nombre, v2.nombre as vm_destino_nombre
            FROM vm_enlaces ve
            JOIN vm v1 ON ve.vm_origen = v1.id_vm
            JOIN vm v2 ON ve.vm_destino = v2.id_vm
            WHERE v1.topologia_id_topologia = ? OR v2.topologia_id_topologia = ?
            """
            
            slice_info = self.execute_query(slice_query, (slice_id,))
            vms_info = self.execute_query(vms_query, (slice_id,))
            enlaces_info = self.execute_query(enlaces_query, (slice_id, slice_id))
            
            if not slice_info:
                return {}
            
            return {
                'slice': dict(slice_info[0]),
                'vms': [dict(vm) for vm in vms_info],
                'enlaces': [dict(enlace) for enlace in enlaces_info]
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo slice completo {slice_id}: {e}")
            return {}
    
    def get_server_utilization(self, server_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene utilización de recursos de servidores.
        
        Args:
            server_id (optional): ID del servidor específico
            
        Returns:
            List[Dict]: Información de utilización
        """
        try:
            if server_id:
                query = """
                SELECT s.id_servidor, s.nombre, s.ip,
                       r.ram, r.vcpu, r.storage,
                       r.ram_available, r.vcpu_available, r.storage_available,
                       COUNT(v.id_vm) as vms_count,
                       z.nombre as zona_nombre
                FROM servidor s
                LEFT JOIN recursos r ON s.id_recurso = r.id_recursos
                LEFT JOIN vm v ON v.servidor_id_servidor = s.id_servidor AND v.estado = 'ACTIVA'
                LEFT JOIN zona_disponibilidad z ON s.id_zona = z.idzona_disponibilidad
                WHERE s.id_servidor = ?
                GROUP BY s.id_servidor
                """
                params = (server_id,)
            else:
                query = """
                SELECT s.id_servidor, s.nombre, s.ip,
                       r.ram, r.vcpu, r.storage,
                       r.ram_available, r.vcpu_available, r.storage_available,
                       COUNT(v.id_vm) as vms_count,
                       z.nombre as zona_nombre
                FROM servidor s
                LEFT JOIN recursos r ON s.id_recurso = r.id_recursos
                LEFT JOIN vm v ON v.servidor_id_servidor = s.id_servidor AND v.estado = 'ACTIVA'
                LEFT JOIN zona_disponibilidad z ON s.id_zona = z.idzona_disponibilidad
                GROUP BY s.id_servidor
                ORDER BY s.nombre
                """
                params = None
            
            results = self.execute_query(query, params)
            
            utilization = []
            for row in results:
                data = dict(row)
                # Calcular porcentajes de uso
                if data['ram'] and data['ram'] > 0:
                    data['ram_uso_pct'] = ((data['ram'] - data['ram_available']) / data['ram']) * 100
                else:
                    data['ram_uso_pct'] = 0
                
                if data['vcpu'] and data['vcpu'] > 0:
                    data['vcpu_uso_pct'] = ((data['vcpu'] - data['vcpu_available']) / data['vcpu']) * 100
                else:
                    data['vcpu_uso_pct'] = 0
                    
                if data['storage'] and data['storage'] > 0:
                    data['storage_uso_pct'] = ((data['storage'] - data['storage_available']) / data['storage']) * 100
                else:
                    data['storage_uso_pct'] = 0
                
                utilization.append(data)
            
            return utilization
            
        except Exception as e:
            self.logger.error(f"Error obteniendo utilización de servidores: {e}")
            return []
    
    def get_cluster_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene resumen de métricas del cluster en las últimas horas.
        
        Args:
            hours (int): Horas hacia atrás a consultar
            
        Returns:
            Dict: Resumen de métricas
        """
        try:
            # Métricas promedio por tipo
            metrics_query = """
            SELECT tipo_metrica, 
                   AVG(valor) as promedio,
                   MAX(valor) as maximo,
                   MIN(valor) as minimo,
                   COUNT(*) as total_registros
            FROM metricas_tiempo_real
            WHERE timestamp >= datetime('now', '-{} hours')
            GROUP BY tipo_metrica
            """.format(hours)
            
            # Nodos activos
            nodes_query = """
            SELECT COUNT(*) as total_nodos,
                   SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) as nodos_activos
            FROM nodo_cluster
            """
            
            # Eventos recientes
            events_query = """
            SELECT tipo_evento, severidad, COUNT(*) as cantidad
            FROM eventos_cluster
            WHERE timestamp >= datetime('now', '-{} hours')
            GROUP BY tipo_evento, severidad
            ORDER BY cantidad DESC
            """.format(hours)
            
            metrics_results = self.execute_query(metrics_query)
            nodes_results = self.execute_query(nodes_query)
            events_results = self.execute_query(events_query)
            
            return {
                'metricas_por_tipo': [dict(row) for row in metrics_results],
                'resumen_nodos': dict(nodes_results[0]) if nodes_results else {},
                'eventos_recientes': [dict(row) for row in events_results],
                'periodo_horas': hours
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de métricas: {e}")
            return {}
    
    # ===================================================================
    # MÉTODOS DE COMPATIBILIDAD CON LA API ANTERIOR
    # ===================================================================
    
    def Select(self, campos: str, tabla: str, condicion: str) -> List[Tuple]:
        """
        Método de compatibilidad con la API anterior.
        Ejecuta una consulta SELECT manteniendo la interfaz original.
        
        Args:
            campos (str): Campos a seleccionar
            tabla (str): Nombre de la tabla
            condicion (str): Condición WHERE ("-1" para sin condición)
            
        Returns:
            List[Tuple]: Resultados como tuplas (compatible con código anterior)
        """
        try:
            if condicion == "-1":
                query = f"SELECT {campos} FROM {tabla}"
                results = self.execute_query(query)
            else:
                query = f"SELECT {campos} FROM {tabla} WHERE {condicion}"
                results = self.execute_query(query)
            
            # Convertir sqlite3.Row a tuplas para compatibilidad
            return [tuple(row) for row in results]
            
        except Exception as e:
            self.logger.error(f"Error en Select: {e}")
            return []
    
    def Insert(self, tabla: str, columnas: str, valores: str) -> int:
        """
        Método de compatibilidad con la API anterior.
        Ejecuta una inserción manteniendo la interfaz original.
        
        Args:
            tabla (str): Nombre de la tabla
            columnas (str): Columnas separadas por comas
            valores (str): Valores en formato string
            
        Returns:
            int: ID del registro insertado
        """
        try:
            # Convertir al formato SQLite
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores})"
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            row_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return row_id
            
        except Exception as e:
            self.logger.error(f"Error en Insert: {e}")
            raise
    
    def Update(self, tabla: str, valores: str, condicion: str) -> None:
        """
        Método de compatibilidad con la API anterior.
        Ejecuta una actualización manteniendo la interfaz original.
        
        Args:
            tabla (str): Nombre de la tabla
            valores (str): Cláusula SET
            condicion (str): Cláusula WHERE
        """
        try:
            self.execute_update(tabla, valores, condicion)
        except Exception as e:
            self.logger.error(f"Error en Update: {e}")
            raise
    
    def Delete(self, tabla: str, condicion: str) -> None:
        """
        Método de compatibilidad con la API anterior.
        Ejecuta una eliminación manteniendo la interfaz original.
        
        Args:
            tabla (str): Nombre de la tabla
            condicion (str): Cláusula WHERE
        """
        try:
            self.execute_delete(tabla, condicion)
        except Exception as e:
            self.logger.error(f"Error en Delete: {e}")
            raise
    
    def Consult(self, query: str) -> List[Tuple]:
        """
        Método de compatibilidad para consultas personalizadas.
        
        Args:
            query (str): Consulta SQL completa
            
        Returns:
            List[Tuple]: Resultados como tuplas
        """
        try:
            results = self.execute_query(query)
            return [tuple(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error en Consult: {e}")
            return []
    
    def GetMaxVlan(self) -> List[Tuple]:
        """
        Método específico para obtener el máximo VLAN ID.
        Mantiene compatibilidad con la API anterior.
        
        Returns:
            List[Tuple]: Resultado con el máximo VLAN ID
        """
        try:
            query = "SELECT MAX(vlan_id) as max_vlan FROM slice"
            results = self.execute_query(query)
            return [tuple(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error en GetMaxVlan: {e}")
            return [(None,)]
    
    def close(self):
        """
        Método para cerrar conexiones si es necesario.
        En SQLite3 no es crítico ya que cada operación maneja su propia conexión.
        """
        pass
    
    def __enter__(self):
        """Soporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Soporte para context manager"""
        self.close()


# Aliases para compatibilidad con código anterior
class Conexion(DatabaseManager):
    """
    Alias principal para mantener compatibilidad con Conexion original.
    Representa el acceso a todas las tablas del sistema.
    """
    pass


class Conexion2(DatabaseManager):
    """
    Alias secundario para mantener compatibilidad con Conexion2 original.
    Mantiene la interfaz original del sistema.
    """
    pass