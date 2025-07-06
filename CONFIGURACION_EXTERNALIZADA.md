# 🔧 CONFIGURACIÓN EXTERNALIZADA

## ✅ **IMPLEMENTACIÓN COMPLETADA**

Se ha exitosamente externalizado toda la configuración hardcodeada del proyecto a archivos de configuración centralizados.

---

## 📋 **ARCHIVOS CREADOS**

### 1. `config.env`
Archivo principal de configuración con todas las variables del sistema:
- ✅ Configuración de base de datos (host, credenciales, nombres de BD)
- ✅ URLs y credenciales de OpenStack 
- ✅ URLs y endpoints del cluster Linux
- ✅ Configuración de red (CIDR, DNS, gateways)
- ✅ Factores del scheduler (pesos de RAM, CPU, disco)
- ✅ Rutas de archivos y extensiones
- ✅ Lista de nombres de workers
- ✅ Puertos, timeouts y límites
- ✅ Configuración de logging y monitoreo

### 2. `conf/ConfigManager.py`
Gestor centralizado de configuración que:
- ✅ Carga variables desde archivo `.env`
- ✅ Parsea automáticamente tipos de datos (int, float, bool, listas)
- ✅ Proporciona métodos específicos por componente
- ✅ Incluye validación de configuración
- ✅ Maneja configuración por defecto como fallback

### 3. `config.env.example`
Archivo de ejemplo para nuevas instalaciones

### 4. `test_config.py`
Script de validación automática de la configuración

---

## 🔄 **REFACTORIZACIÓN REALIZADA**

### **Archivos Modificados:**

#### `conf/Conexion.py`
- ✅ Reemplazadas credenciales hardcodeadas de BD
- ✅ Usa `config.get_db_config()` para conexiones

#### `Modules/App_Scheduler.py`
- ✅ Externalizados factores del scheduler (0.5, 0.25, 0.25)
- ✅ Externalizados factores de conversión (bytes a MB/GB)
- ✅ Configuración de BD desde ConfigManager

#### `Modules/SliceAdministrator.py`
- ✅ Factor de recursos configurable
- ✅ Rutas de archivos externalizadas

#### `Modules/LinuxClusterDriver.py`
- ✅ URLs del cluster API externalizadas
- ✅ Endpoints configurables (/vm/crear, /vm/borrar, /OFS/flows)
- ✅ Rutas de archivos desde configuración

#### `Modules/OpenStackDriver.py`
- ✅ URLs de OpenStack externalizadas (Keystone, Nova, Neutron)
- ✅ Credenciales y configuración de dominio
- ✅ Factor RXTX configurable

#### `Modules/Validador.py`
- ✅ Lista de workers desde configuración
- ✅ URL de métricas externalizada

#### `Modules/UserInterface.py`
- ✅ Puerto VNC base configurable
- ✅ Rutas de slices externalizadas

---

## 📊 **DATOS EXTERNALIZADOS**

### **Base de Datos**
```env
DB_HOST=10.20.12.35
DB_USER=grupo1_final
DB_PASSWORD=grupo1_final
DB_NAME_GENERAL=bd_general
DB_NAME_CLUSTER=bd_cluster_final
```

### **OpenStack**
```env
OPENSTACK_KEYSTONE_URL=http://10.20.12.54:5000/v3/auth/tokens
OPENSTACK_NOVA_URL=http://10.20.12.54:8774/v2.1
OPENSTACK_NEUTRON_URL=http://10.20.12.54:9696/v2.0
OPENSTACK_ADMIN_USER=admin
OPENSTACK_ADMIN_PASSWORD=grupo_1
```

### **Linux Cluster**
```env
CLUSTER_API_URL=http://10.20.12.58:8081
CLUSTER_VM_CREATE_ENDPOINT=/vm/crear
CLUSTER_VM_DELETE_ENDPOINT=/vm/borrar
CLUSTER_FLOWS_ENDPOINT=/OFS/flows
```

### **Algoritmo de Scheduling**
```env
SCHEDULER_RAM_WEIGHT=0.5
SCHEDULER_DISK_WEIGHT=0.25
SCHEDULER_VCPU_WEIGHT=0.25
RESOURCE_FACTOR=2
```

### **Red y Servicios**
```env
NETWORK_BASE_CIDR=10.0.0.0/24
NETWORK_DNS_SERVER=8.8.8.8
VNC_BASE_PORT=5900
```

---

## 🚀 **VENTAJAS OBTENIDAS**

### **Flexibilidad**
- ✅ Cambios de configuración sin modificar código
- ✅ Múltiples entornos (desarrollo, producción, testing)
- ✅ Configuración específica por deployment

### **Seguridad**
- ✅ Credenciales fuera del código fuente
- ✅ Posibilidad de usar variables de entorno del sistema
- ✅ Archivo .env puede ser excluido del control de versiones

### **Mantenibilidad**
- ✅ Configuración centralizada en un solo lugar
- ✅ Validación automática de parámetros requeridos
- ✅ Documentación clara de todas las opciones

### **Escalabilidad**
- ✅ Fácil adición de nuevos parámetros
- ✅ Configuración granular por componente
- ✅ Soporte para configuraciones complejas (listas, objetos)

---

## 📝 **USO DE LA CONFIGURACIÓN**

### **En cualquier módulo:**
```python
from conf.ConfigManager import config

# Obtener configuración específica
db_config = config.get_db_config()
openstack_config = config.get_openstack_config()
cluster_config = config.get_cluster_config()

# Obtener valor individual
vnc_port = config.get('VNC_BASE_PORT')
workers = config.get_worker_names()
```

### **Validar configuración:**
```python
if config.validate_config():
    print("Configuración válida")
else:
    print("Faltan parámetros requeridos")
```

---

## ⚡ **INSTALACIÓN**

1. **Copiar archivo de configuración:**
   ```bash
   cp config.env.example config.env
   ```

2. **Personalizar valores:**
   Editar `config.env` con los valores específicos del entorno

3. **Validar configuración:**
   ```bash
   python3 test_config.py
   ```

4. **Usar el sistema:**
   Todos los módulos ahora usan la configuración externalizada automáticamente

---

## 🎯 **IMPACTO EN REQUERIMIENTOS**

Esta mejora contribuye significativamente a:

- **R1C - Slice Manager**: ✅ Mejor gestión de configuración
- **R1 - Control de Slices**: ✅ Configuración independiente por entorno
- **R5 - Networking**: ✅ URLs y parámetros de red configurables
- **Todos los requerimientos**: ✅ Mayor flexibilidad y mantenibilidad

---

## 🔒 **NOTA DE SEGURIDAD**

⚠️ **IMPORTANTE**: El archivo `config.env` contiene credenciales sensibles y **NO debe ser incluido en el control de versiones**. Asegúrate de añadir `config.env` al `.gitignore`.

✅ **COMPLETADO**: Toda la configuración hardcodeada ha sido exitosamente externalizada.