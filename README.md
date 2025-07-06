# Sistema de Administración de Slices en Cloud Computing

## Descripción General

Este proyecto implementa un sistema de administración de slices de red (network slices) para entornos de cloud computing. Permite crear, configurar, gestionar y desplegar topologías de red virtuales en infraestructuras de Linux Cluster y OpenStack.

## Arquitectura del Sistema

### Componentes Principales

#### 1. **Interfaz de Usuario (`UserInterface.py`)**
- Proporciona una interfaz de línea de comandos interactiva
- Gestiona los menús y opciones del sistema
- Coordina las operaciones entre diferentes módulos

#### 2. **Administrador de Slices (`SliceAdministrator.py`)**
- Controla el ciclo de vida de los slices
- Coordina la creación, actualización y eliminación de topologías
- Gestiona la persistencia de datos

#### 3. **Generador de Topologías (`Topology.py`)**
- Crea diferentes tipos de topologías de red:
  - **Estrella**: Un nodo central conectado a todos los demás
  - **Lineal**: Nodos conectados en secuencia
  - **Anillo**: Nodos conectados en forma circular
  - **Malla**: Nodos organizados en matriz rectangular
  - **Árbol**: Estructura jerárquica multinivel
- Visualiza las topologías usando PyVis

#### 4. **Drivers de Infraestructura**
- **LinuxClusterDriver**: Gestiona deployments en clusters Linux
- **OpenStackDriver**: Maneja deployments en OpenStack

#### 5. **Planificador (`App_Scheduler.py`)**
- Optimiza la asignación de recursos
- Implementa algoritmos de scheduling para VMs

#### 6. **Validador (`Validador.py`)**
- Valida el estado de las VMs
- Monitorea recursos del sistema

#### 7. **Modelos de Datos (`beans/`)**
- **Node**: Representa nodos virtuales
- **Server**: Representa servidores físicos
- **CPU, RAM, Storage**: Modelos de recursos
- **Image**: Gestiona imágenes de sistemas operativos

## Funcionalidades Principales

### 1. **Gestión de Slices**
- **Crear slice desde cero**: Definir nueva topología
- **Continuar configuración**: Modificar slice existente
- **Listar slices**: Ver todos los slices disponibles
- **Borrar slice**: Eliminar slice y sus recursos

### 2. **Creación de Topologías**
- **Agregar nodos individuales**: Crear nodos uno por uno
- **Agregar subgrafos**: Crear conjuntos de nodos con patrones predefinidos
- **Gestionar enlaces**: Conectar/desconectar nodos
- **Configurar recursos**: Asignar CPU, RAM, disco y imágenes

### 3. **Configuración de Recursos**
- **Configuración manual**: Especificar recursos individualmente
- **Configuración por flavors**: Usar plantillas predefinidas
- **Gestión de imágenes**: Seleccionar o importar imágenes del SO

### 4. **Gestión de Zonas de Disponibilidad**
- **Crear zonas**: Definir agrupaciones de servidores
- **Asignar servidores**: Vincular servidores físicos a zonas
- **Balanceo de carga**: Distribuir recursos entre zonas

### 5. **Visualización**
- **Topologías interactivas**: Visualizar slices con PyVis
- **Estados de nodos**: Diferenciación visual entre nodos activos/inactivos
- **Información detallada**: Mostrar recursos y conexiones VNC

## Flujo de Trabajo

### 1. **Creación de Slice**
```
Usuario → Interfaz → SliceAdministrator → Topology
```

### 2. **Deployment**
```
SliceAdministrator → App_Scheduler → LinuxClusterDriver/OpenStackDriver
```

### 3. **Monitoreo**
```
Validador → Base de Datos → Estado VMs
```

## Tecnologías Utilizadas

### Backend
- **Python 3.x**: Lenguaje principal
- **MySQL**: Base de datos (PyMySQL)
- **NetworkX**: Algoritmos de grafos
- **PyVis**: Visualización interactiva

### Frontend
- **Dash**: Interfaz web interactiva
- **Plotly**: Gráficos y visualizaciones
- **Flask**: Servidor web

### Infraestructura
- **OpenStack**: Cloud computing platform
- **Linux Clusters**: Infraestructura de servidores
- **MQTT**: Comunicación asíncrona

## Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd cloud-2022
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar base de datos**
```bash
# Configurar conexión en conf/Conexion.py
```

4. **Ejecutar la aplicación**
```bash
python App.py
```

## Uso

### Iniciar el Sistema
```bash
python App.py
```

### Menú Principal
1. **Configurar**: Crear/modificar slices
2. **Listar slices**: Ver slices existentes
3. **Borrar slice**: Eliminar slice
4. **Definir zona de disponibilidad**: Configurar infraestructura
5. **Salir**: Terminar programa

### Ejemplo de Uso
1. Seleccionar "Configurar" → "Configuración desde cero"
2. Nombrar el slice
3. Agregar nodos o subgrafos
4. Configurar recursos (CPU, RAM, disco)
5. Seleccionar imágenes del SO
6. Guardar e implementar

## Estructura de Archivos

```
cloud-2022/
├── App.py                 # Punto de entrada principal
├── Topology.py           # Generador de topologías
├── Modules/
│   ├── UserInterface.py  # Interfaz de usuario
│   ├── SliceAdministrator.py  # Administrador de slices
│   ├── App_Scheduler.py  # Planificador
│   ├── LinuxClusterDriver.py  # Driver Linux
│   ├── OpenStackDriver.py     # Driver OpenStack
│   ├── Validador.py      # Validador de estados
│   └── Slices/           # Almacén de slices JSON
├── beans/                # Modelos de datos
├── conf/                 # Configuración de BD
├── model/               # Acceso a datos
└── requirements.txt     # Dependencias
```

## Configuración de Base de Datos

El sistema utiliza MySQL para persistir:
- Información de slices
- Estados de VMs
- Configuración de servidores
- Zonas de disponibilidad
- Recursos disponibles

## Contribuir

1. Fork el repositorio
2. Crear branch para features
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## Licencia

Desarrollado por **GRUPO 1** - Proyecto académico de Cloud Computing 2022.

## Soporte

Para problemas o preguntas, contactar al equipo de desarrollo del Grupo 1.