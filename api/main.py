"""
===================================================================
API REST PRINCIPAL - GESTOR DE SLICES Y RECURSOS
===================================================================

Aplicación FastAPI que centraliza todos los endpoints para la gestión
de slices, recursos del sistema y monitorización.

Autor: Generado por Gemini
Versión: 1.0
===================================================================
"""

from fastapi import FastAPI
from api.routes import system, slices, linux_cluster, openstack

# Metadatos para la documentación de la API
tags_metadata = [
    {
        "name": "system",
        "description": "Endpoints para información y estado del sistema.",
    },
    {
        "name": "slices",
        "description": "Operaciones para crear, gestionar y eliminar slices.",
    },
    {
        "name": "linux_cluster",
        "description": "Endpoints específicos para el driver de Linux Cluster.",
    },
    {
        "name": "openstack",
        "description": "Endpoints específicos para el driver de OpenStack.",
    },
]

# Creación de la aplicación FastAPI
app = FastAPI(
    title="Gestor de Slices y Recursos Cloud",
    description="API para la orquestación de infraestructura virtualizada en clusters Linux y OpenStack.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Equipo de Desarrollo",
        "url": "http://example.com/contact",
        "email": "dev@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Inclusión de los routers de los diferentes módulos
app.include_router(system.router)
app.include_router(slices.router)
app.include_router(linux_cluster.router)
app.include_router(openstack.router)
app.include_router(linux_cluster.router)
app.include_router(openstack.router)

@app.get("/", tags=["root"])
async def read_root():
    """
    Endpoint raíz que devuelve un mensaje de bienvenida.
    """
    return {"message": "Bienvenido a la API de gestión de Slices y Recursos Cloud"}

# Para ejecutar la aplicación (usar uvicorn en producción)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
