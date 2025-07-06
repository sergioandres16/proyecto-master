"""
===================================================================
MÓDULO DE COMPATIBILIDAD - CONEXIÓN A BASE DE DATOS
===================================================================

Este módulo mantiene compatibilidad con el código existente que usa
las clases Conexion y Conexion2.

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from database.DatabaseManager import DatabaseManager

class Conexion(DatabaseManager):
    """
    Clase de compatibilidad que redirige a DatabaseManager.
    Mantiene la interfaz original para evitar romper código existente.
    """
    
    def conectar(self):
        """
        Método de compatibilidad que simula la conexión MySQL anterior.
        En SQLite3 cada operación maneja su propia conexión.
        
        Returns:
            DatabaseManager: Instancia de la clase para encadenamiento
        """
        return self


class Conexion2(DatabaseManager):
    """
    Clase de compatibilidad que redirige a DatabaseManager.
    Mantiene la interfaz original para compatibilidad total.
    """
    
    def conectar(self):
        """
        Método de compatibilidad que simula la conexión MySQL anterior.
        En SQLite3 cada operación maneja su propia conexión.
        
        Returns:
            DatabaseManager: Instancia de la clase para encadenamiento
        """
        return self

