"""
===================================================================
MÓDULO DE BASE DE DATOS - SQLite3
===================================================================

Este paquete contiene el gestor de base de datos del sistema
de administración de slices.

Componentes:
- DatabaseManager: Gestor principal de base de datos
- db_initializer: Inicializador de la base de datos

Autor: Generado por Claude Code
Versión: 3.0
===================================================================
"""

from .DatabaseManager import DatabaseManager
from .db_initializer import DatabaseInitializer

__all__ = [
    'DatabaseManager',
    'DatabaseInitializer'
]