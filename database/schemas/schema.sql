-- ===================================================================
-- ESQUEMA DE BASE DE DATOS - SQLite3
-- ===================================================================
-- Este archivo define la estructura completa del sistema de gestión
-- de slices de red y métricas del cluster.
--
-- Autor: Generado por Claude Code
-- Versión: 3.0
-- ===================================================================

-- Habilitar claves foráneas
PRAGMA foreign_keys = ON;

-- ===================================================================
-- SECCIÓN 1: INFRAESTRUCTURA Y ZONAS
-- ===================================================================

-- TABLA: zona_disponibilidad
-- Almacena las zonas de disponibilidad del sistema
CREATE TABLE IF NOT EXISTS zona_disponibilidad (
    idzona_disponibilidad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT 1
);

-- TABLA: recursos
-- Almacena la configuración de recursos (RAM, CPU, Storage)
CREATE TABLE IF NOT EXISTS recursos (
    id_recursos INTEGER PRIMARY KEY AUTOINCREMENT,
    ram INTEGER NOT NULL,                    -- RAM en MB
    vcpu INTEGER NOT NULL,                   -- Número de vCPUs
    storage INTEGER NOT NULL,                -- Storage en GB
    ram_available INTEGER,                   -- RAM disponible en MB
    vcpu_available INTEGER,                  -- vCPUs disponibles
    storage_available INTEGER,               -- Storage disponible en GB
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TABLA: servidor
-- Almacena información de servidores físicos
CREATE TABLE IF NOT EXISTS servidor (
    id_servidor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ip VARCHAR(45),                          -- Soporte para IPv4 e IPv6
    descripcion TEXT,
    id_zona INTEGER,                         -- FK a zona_disponibilidad
    id_recurso INTEGER,                      -- FK a recursos
    max_vnc INTEGER DEFAULT 0,               -- Puerto VNC máximo usado
    estado VARCHAR(20) DEFAULT 'activo',     -- activo, inactivo, mantenimiento
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_zona) REFERENCES zona_disponibilidad(idzona_disponibilidad),
    FOREIGN KEY (id_recurso) REFERENCES recursos(id_recursos)
);

-- ===================================================================
-- SECCIÓN 2: IMÁGENES Y CONFIGURACIONES
-- ===================================================================

-- TABLA: imagen
-- Almacena imágenes de sistemas operativos para VMs
CREATE TABLE IF NOT EXISTS imagen (
    id_imagen INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    url TEXT,                                -- URL de descarga de la imagen
    descripcion TEXT,
    tamaño INTEGER,                         -- Tamaño en MB
    formato VARCHAR(20),                    -- qcow2, raw, etc.
    activa BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TABLA: flavor
-- Almacena configuraciones predefinidas de recursos
CREATE TABLE IF NOT EXISTS flavor (
    id_flavor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ram INTEGER NOT NULL,                    -- RAM en MB
    cpu INTEGER NOT NULL,                    -- Número de vCPUs
    storage INTEGER NOT NULL,                -- Storage en GB
    descripcion TEXT,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- SECCIÓN 3: SLICES Y MÁQUINAS VIRTUALES
-- ===================================================================

-- TABLA: slice
-- Almacena información de slices de red
CREATE TABLE IF NOT EXISTS slice (
    id_slice INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,               -- linux_cluster, openstack
    vlan_id INTEGER,                         -- ID de VLAN asignada
    estado VARCHAR(20) DEFAULT 'creado',     -- creado, ejecutado, pausado, eliminado
    descripcion TEXT,
    configuracion_json TEXT,                 -- Configuración en formato JSON
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    creado_por INTEGER DEFAULT 1,           -- ID del usuario (futuro)
    modificado_por INTEGER DEFAULT 1        -- ID del usuario (futuro)
);

-- TABLA: vm
-- Almacena información de máquinas virtuales
CREATE TABLE IF NOT EXISTS vm (
    id_vm INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    estado VARCHAR(20) DEFAULT 'CREADA',     -- CREADA, ACTIVA, PAUSADA, ELIMINADA
    vnc INTEGER,                             -- Puerto VNC
    token VARCHAR(50),                       -- Token único de la VM
    mac_address VARCHAR(17),                 -- Dirección MAC
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    creado_por INTEGER DEFAULT 1,
    modificado_por INTEGER DEFAULT 1,
    
    -- Claves foráneas
    servidor_id_servidor INTEGER,           -- Servidor físico donde está la VM
    topologia_id_topologia INTEGER,         -- Slice al que pertenece
    imagen_id_imagen INTEGER,               -- Imagen del SO
    recursos_id_estado INTEGER,             -- Recursos asignados
    
    FOREIGN KEY (servidor_id_servidor) REFERENCES servidor(id_servidor),
    FOREIGN KEY (topologia_id_topologia) REFERENCES slice(id_slice) ON DELETE CASCADE,
    FOREIGN KEY (imagen_id_imagen) REFERENCES imagen(id_imagen),
    FOREIGN KEY (recursos_id_estado) REFERENCES recursos(id_recursos)
);

-- TABLA: vm_enlaces
-- Almacena las conexiones entre VMs (enlaces de red)
CREATE TABLE IF NOT EXISTS vm_enlaces (
    id_enlace INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_origen INTEGER NOT NULL,
    vm_destino INTEGER NOT NULL,
    tipo_enlace VARCHAR(20) DEFAULT 'ethernet',  -- ethernet, wifi, etc.
    ancho_banda INTEGER,                          -- Mbps
    latencia REAL,                               -- ms
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vm_origen) REFERENCES vm(id_vm) ON DELETE CASCADE,
    FOREIGN KEY (vm_destino) REFERENCES vm(id_vm) ON DELETE CASCADE,
    
    -- Evitar enlaces duplicados
    UNIQUE(vm_origen, vm_destino)
);

-- ===================================================================
-- SECCIÓN 4: NODOS DEL CLUSTER (MÉTRICAS DETALLADAS)
-- ===================================================================

-- TABLA: nodo_cluster
-- Almacena información detallada de nodos del cluster Linux
CREATE TABLE IF NOT EXISTS nodo_cluster (
    id_nodo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tipo INTEGER DEFAULT 1,                  -- Tipo de nodo (1=VM, 2=Container, etc.)
    ip_address VARCHAR(45),                  -- IP del nodo
    puerto_vnc INTEGER,                      -- Puerto VNC asignado
    estado VARCHAR(20) DEFAULT 'activo',     -- activo, inactivo, error
    worker_id INTEGER,                       -- ID del worker físico
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_conexion DATETIME,
    
    -- Metadatos adicionales
    sistema_operativo VARCHAR(50),
    version_kernel VARCHAR(50),
    arquitectura VARCHAR(20) DEFAULT 'x86_64',
    
    -- Relación con la VM correspondiente (si aplica)
    vm_id INTEGER,
    
    FOREIGN KEY (vm_id) REFERENCES vm(id_vm) ON DELETE SET NULL
);

-- TABLA: nodo_ram
-- Almacena información de memoria RAM de nodos del cluster
CREATE TABLE IF NOT EXISTS nodo_ram (
    id_ram INTEGER PRIMARY KEY AUTOINCREMENT,
    memoria_total INTEGER NOT NULL,          -- RAM total en MB
    memoria_usada INTEGER DEFAULT 0,         -- RAM usada en MB
    memoria_disponible INTEGER,              -- RAM disponible en MB
    swap_total INTEGER DEFAULT 0,            -- Swap total en MB
    swap_usada INTEGER DEFAULT 0,            -- Swap usada en MB
    porcentaje_uso REAL DEFAULT 0.0,        -- Porcentaje de uso
    creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave foránea
    nodo_id INTEGER NOT NULL,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- TABLA: nodo_cpu
-- Almacena información de CPU de nodos del cluster
CREATE TABLE IF NOT EXISTS nodo_cpu (
    id_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
    nucleos_totales INTEGER NOT NULL,        -- Número total de núcleos
    nucleos_disponibles INTEGER,             -- Núcleos disponibles
    frecuencia_mhz INTEGER,                  -- Frecuencia en MHz
    uso_promedio REAL DEFAULT 0.0,          -- % de uso promedio
    carga_1min REAL DEFAULT 0.0,            -- Load average 1min
    carga_5min REAL DEFAULT 0.0,            -- Load average 5min
    carga_15min REAL DEFAULT 0.0,           -- Load average 15min
    temperatura REAL,                        -- Temperatura en °C
    creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave foránea
    nodo_id INTEGER NOT NULL,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- TABLA: nodo_vcpu
-- Almacena información de vCPUs asignadas a nodos del cluster
CREATE TABLE IF NOT EXISTS nodo_vcpu (
    id_vcpu INTEGER PRIMARY KEY AUTOINCREMENT,
    vcpu_total INTEGER NOT NULL,             -- vCPUs totales asignadas
    vcpu_usadas INTEGER DEFAULT 0,           -- vCPUs en uso
    vcpu_disponibles INTEGER,                -- vCPUs disponibles
    factor_sobrecarga REAL DEFAULT 1.0,     -- Factor de overcommit
    politica_asignacion VARCHAR(20) DEFAULT 'shared',  -- shared, dedicated
    creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave foránea
    nodo_id INTEGER NOT NULL,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- TABLA: nodo_almacenamiento
-- Almacena información de storage de nodos del cluster
CREATE TABLE IF NOT EXISTS nodo_almacenamiento (
    id_storage INTEGER PRIMARY KEY AUTOINCREMENT,
    capacidad_total INTEGER NOT NULL,        -- Capacidad total en GB
    capacidad_usada INTEGER DEFAULT 0,       -- Espacio usado en GB
    capacidad_disponible INTEGER,            -- Espacio disponible en GB
    tipo_storage VARCHAR(20) DEFAULT 'hdd',  -- hdd, ssd, nvme
    punto_montaje VARCHAR(100),              -- Punto de montaje
    sistema_archivos VARCHAR(20),            -- ext4, xfs, btrfs, etc.
    iops_lectura INTEGER,                    -- IOPS de lectura
    iops_escritura INTEGER,                  -- IOPS de escritura
    porcentaje_uso REAL DEFAULT 0.0,        -- Porcentaje de uso
    creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave foránea
    nodo_id INTEGER NOT NULL,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- TABLA: nodo_enlace
-- Almacena información de enlaces entre nodos del cluster
CREATE TABLE IF NOT EXISTS nodo_enlace (
    id_enlace INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(200),                     -- Lista de nodos conectados
    tipo_enlace VARCHAR(20) DEFAULT 'ethernet',  -- ethernet, infiniband, etc.
    ancho_banda INTEGER,                     -- Mbps
    latencia REAL,                          -- Latencia en ms
    paquetes_enviados INTEGER DEFAULT 0,    -- Contador de paquetes TX
    paquetes_recibidos INTEGER DEFAULT 0,   -- Contador de paquetes RX
    bytes_enviados INTEGER DEFAULT 0,       -- Bytes transmitidos
    bytes_recibidos INTEGER DEFAULT 0,      -- Bytes recibidos
    errores_tx INTEGER DEFAULT 0,           -- Errores de transmisión
    errores_rx INTEGER DEFAULT 0,           -- Errores de recepción
    estado VARCHAR(20) DEFAULT 'activo',    -- activo, inactivo, error
    creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave foránea
    nodo_id INTEGER NOT NULL,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- ===================================================================
-- SECCIÓN 5: MÉTRICAS Y MONITOREO
-- ===================================================================

-- TABLA: metricas_sistema
-- Almacena métricas históricas generales del sistema
CREATE TABLE IF NOT EXISTS metricas_sistema (
    id_metrica INTEGER PRIMARY KEY AUTOINCREMENT,
    servidor_id INTEGER,
    vm_id INTEGER,                           -- Métricas específicas de VM
    tipo_metrica VARCHAR(20) NOT NULL,       -- cpu, ram, storage, network
    valor REAL NOT NULL,
    unidad VARCHAR(10),                      -- %, MB, GB, etc.
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (servidor_id) REFERENCES servidor(id_servidor),
    FOREIGN KEY (vm_id) REFERENCES vm(id_vm)
);

-- TABLA: metricas_tiempo_real
-- Almacena métricas en tiempo real del cluster
CREATE TABLE IF NOT EXISTS metricas_tiempo_real (
    id_metrica INTEGER PRIMARY KEY AUTOINCREMENT,
    nodo_id INTEGER NOT NULL,
    tipo_metrica VARCHAR(30) NOT NULL,       -- cpu_usage, mem_usage, disk_io, net_io
    valor REAL NOT NULL,
    valor_maximo REAL,                       -- Valor máximo en el periodo
    valor_minimo REAL,                       -- Valor mínimo en el periodo
    unidad VARCHAR(10),                      -- %, MB/s, GB, etc.
    intervalo_segundos INTEGER DEFAULT 60,   -- Intervalo de muestreo
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE CASCADE
);

-- ===================================================================
-- SECCIÓN 6: EVENTOS Y AUDITORÍA
-- ===================================================================

-- TABLA: eventos_cluster
-- Registro de eventos importantes del cluster
CREATE TABLE IF NOT EXISTS eventos_cluster (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    nodo_id INTEGER,                         -- NULL para eventos globales
    servidor_id INTEGER,                     -- Servidor relacionado
    slice_id INTEGER,                        -- Slice relacionado
    vm_id INTEGER,                           -- VM relacionada
    tipo_evento VARCHAR(30) NOT NULL,        -- start, stop, error, warning, info
    severidad VARCHAR(10) DEFAULT 'info',    -- critical, error, warning, info
    mensaje TEXT NOT NULL,
    detalles_json TEXT,                      -- Detalles adicionales en JSON
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resuelto BOOLEAN DEFAULT 0,              -- Si el evento fue resuelto
    fecha_resolucion DATETIME,
    
    FOREIGN KEY (nodo_id) REFERENCES nodo_cluster(id_nodo) ON DELETE SET NULL,
    FOREIGN KEY (servidor_id) REFERENCES servidor(id_servidor) ON DELETE SET NULL,
    FOREIGN KEY (slice_id) REFERENCES slice(id_slice) ON DELETE SET NULL,
    FOREIGN KEY (vm_id) REFERENCES vm(id_vm) ON DELETE SET NULL
);

-- TABLA: auditoria
-- Registro de auditoría para tracking de cambios
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla_afectada VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    accion VARCHAR(10) NOT NULL,             -- INSERT, UPDATE, DELETE
    datos_anteriores TEXT,                   -- JSON con datos previos
    datos_nuevos TEXT,                       -- JSON con datos nuevos
    usuario_id INTEGER DEFAULT 1,
    ip_origen VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- SECCIÓN 7: CONFIGURACIÓN GLOBAL
-- ===================================================================

-- TABLA: configuracion_sistema
-- Configuración global del sistema completo
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo_valor VARCHAR(20) DEFAULT 'string', -- string, integer, float, boolean, json
    categoria VARCHAR(50) DEFAULT 'general', -- general, network, storage, compute, cluster
    modificable BOOLEAN DEFAULT 1,          -- Si puede ser modificado
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ===================================================================

-- Índices principales
CREATE INDEX IF NOT EXISTS idx_servidor_zona ON servidor(id_zona);
CREATE INDEX IF NOT EXISTS idx_servidor_recurso ON servidor(id_recurso);
CREATE INDEX IF NOT EXISTS idx_vm_servidor ON vm(servidor_id_servidor);
CREATE INDEX IF NOT EXISTS idx_vm_slice ON vm(topologia_id_topologia);
CREATE INDEX IF NOT EXISTS idx_vm_estado ON vm(estado);
CREATE INDEX IF NOT EXISTS idx_slice_tipo ON slice(tipo);
CREATE INDEX IF NOT EXISTS idx_slice_estado ON slice(estado);

-- Índices de nodos del cluster
CREATE INDEX IF NOT EXISTS idx_nodo_cluster_estado ON nodo_cluster(estado);
CREATE INDEX IF NOT EXISTS idx_nodo_cluster_worker ON nodo_cluster(worker_id);
CREATE INDEX IF NOT EXISTS idx_nodo_cluster_vm ON nodo_cluster(vm_id);
CREATE INDEX IF NOT EXISTS idx_nodo_ram_nodo ON nodo_ram(nodo_id);
CREATE INDEX IF NOT EXISTS idx_nodo_cpu_nodo ON nodo_cpu(nodo_id);
CREATE INDEX IF NOT EXISTS idx_nodo_vcpu_nodo ON nodo_vcpu(nodo_id);
CREATE INDEX IF NOT EXISTS idx_nodo_storage_nodo ON nodo_almacenamiento(nodo_id);
CREATE INDEX IF NOT EXISTS idx_nodo_enlace_nodo ON nodo_enlace(nodo_id);

-- Índices de métricas
CREATE INDEX IF NOT EXISTS idx_metricas_servidor ON metricas_sistema(servidor_id);
CREATE INDEX IF NOT EXISTS idx_metricas_vm ON metricas_sistema(vm_id);
CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas_sistema(timestamp);
CREATE INDEX IF NOT EXISTS idx_metricas_tipo ON metricas_sistema(tipo_metrica);
CREATE INDEX IF NOT EXISTS idx_metricas_realtime_nodo ON metricas_tiempo_real(nodo_id);
CREATE INDEX IF NOT EXISTS idx_metricas_realtime_timestamp ON metricas_tiempo_real(timestamp);
CREATE INDEX IF NOT EXISTS idx_metricas_realtime_tipo ON metricas_tiempo_real(tipo_metrica);

-- Índices de eventos
CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos_cluster(timestamp);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos_cluster(tipo_evento);
CREATE INDEX IF NOT EXISTS idx_eventos_severidad ON eventos_cluster(severidad);
CREATE INDEX IF NOT EXISTS idx_eventos_nodo ON eventos_cluster(nodo_id);
CREATE INDEX IF NOT EXISTS idx_eventos_servidor ON eventos_cluster(servidor_id);

-- Índices compuestos para consultas complejas
CREATE INDEX IF NOT EXISTS idx_metricas_nodo_timestamp ON metricas_tiempo_real(nodo_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_metricas_tipo_timestamp ON metricas_tiempo_real(tipo_metrica, timestamp);
CREATE INDEX IF NOT EXISTS idx_vm_servidor_slice ON vm(servidor_id_servidor, topologia_id_topologia);

-- ===================================================================
-- DATOS INICIALES
-- ===================================================================

-- Insertar configuraciones básicas de recursos
INSERT OR IGNORE INTO recursos (ram, vcpu, storage, ram_available, vcpu_available, storage_available) 
VALUES 
    (1024, 1, 10, 1024, 1, 10),     -- Micro
    (2048, 2, 20, 2048, 2, 20),     -- Small
    (4096, 4, 40, 4096, 4, 40),     -- Medium
    (8192, 8, 80, 8192, 8, 80);     -- Large

-- Insertar flavors predeterminados
INSERT OR IGNORE INTO flavor (nombre, ram, cpu, storage, descripcion) 
VALUES 
    ('micro', 1024, 1, 10, 'Configuración mínima para pruebas'),
    ('small', 2048, 2, 20, 'Configuración pequeña para desarrollo'),
    ('medium', 4096, 4, 40, 'Configuración media para producción'),
    ('large', 8192, 8, 80, 'Configuración grande para aplicaciones pesadas');

-- Insertar imagen por defecto
INSERT OR IGNORE INTO imagen (nombre, url, descripcion, formato) 
VALUES ('cirros', 'http://download.cirros-cloud.net/0.5.2/cirros-0.5.2-x86_64-disk.img', 'Imagen ligera de prueba', 'qcow2');

-- Configuración inicial del sistema
INSERT OR IGNORE INTO configuracion_sistema (clave, valor, descripcion, tipo_valor, categoria) 
VALUES 
    ('system_name', 'Cloud-2022-Unified', 'Nombre del sistema', 'string', 'general'),
    ('max_vms', '500', 'Número máximo de VMs', 'integer', 'general'),
    ('max_slices', '100', 'Número máximo de slices', 'integer', 'general'),
    ('monitoring_interval', '60', 'Intervalo de monitoreo en segundos', 'integer', 'monitoring'),
    ('retention_days', '30', 'Días de retención de métricas', 'integer', 'monitoring'),
    ('enable_auto_cleanup', 'true', 'Habilitar limpieza automática', 'boolean', 'maintenance'),
    ('network_overlay', 'vlan', 'Tipo de overlay de red', 'string', 'network'),
    ('storage_backend', 'local', 'Backend de almacenamiento', 'string', 'storage'),
    ('cluster_enabled', 'true', 'Habilitar funciones de cluster', 'boolean', 'cluster'),
    ('max_nodes_per_cluster', '100', 'Número máximo de nodos por cluster', 'integer', 'cluster');

-- ===================================================================
-- TRIGGERS PARA MANTENIMIENTO AUTOMÁTICO
-- ===================================================================

-- Trigger para actualizar fecha_modificacion en slice
CREATE TRIGGER IF NOT EXISTS update_slice_timestamp 
    AFTER UPDATE ON slice
BEGIN
    UPDATE slice 
    SET fecha_modificacion = CURRENT_TIMESTAMP 
    WHERE id_slice = NEW.id_slice;
END;

-- Trigger para actualizar fecha_modificacion en vm
CREATE TRIGGER IF NOT EXISTS update_vm_timestamp 
    AFTER UPDATE ON vm
BEGIN
    UPDATE vm 
    SET fecha_modificacion = CURRENT_TIMESTAMP 
    WHERE id_vm = NEW.id_vm;
END;

-- Trigger para actualizar fecha_actualizacion en recursos
CREATE TRIGGER IF NOT EXISTS update_recursos_timestamp 
    AFTER UPDATE ON recursos
BEGIN
    UPDATE recursos 
    SET fecha_actualizacion = CURRENT_TIMESTAMP 
    WHERE id_recursos = NEW.id_recursos;
END;

-- Trigger para actualizar timestamp de actualización en métricas de nodos
CREATE TRIGGER IF NOT EXISTS update_nodo_ram_timestamp 
    AFTER UPDATE ON nodo_ram
BEGIN
    UPDATE nodo_ram 
    SET actualizacion = CURRENT_TIMESTAMP 
    WHERE id_ram = NEW.id_ram;
END;

CREATE TRIGGER IF NOT EXISTS update_nodo_cpu_timestamp 
    AFTER UPDATE ON nodo_cpu
BEGIN
    UPDATE nodo_cpu 
    SET actualizacion = CURRENT_TIMESTAMP 
    WHERE id_cpu = NEW.id_cpu;
END;

CREATE TRIGGER IF NOT EXISTS update_nodo_vcpu_timestamp 
    AFTER UPDATE ON nodo_vcpu
BEGIN
    UPDATE nodo_vcpu 
    SET actualizacion = CURRENT_TIMESTAMP 
    WHERE id_vcpu = NEW.id_vcpu;
END;

CREATE TRIGGER IF NOT EXISTS update_nodo_storage_timestamp 
    AFTER UPDATE ON nodo_almacenamiento
BEGIN
    UPDATE nodo_almacenamiento 
    SET actualizacion = CURRENT_TIMESTAMP 
    WHERE id_storage = NEW.id_storage;
END;

-- Trigger para calcular valores derivados en nodo_ram
CREATE TRIGGER IF NOT EXISTS calculate_nodo_ram_values
    AFTER INSERT ON nodo_ram
BEGIN
    UPDATE nodo_ram 
    SET 
        memoria_disponible = memoria_total - memoria_usada,
        porcentaje_uso = (CAST(memoria_usada AS REAL) / memoria_total) * 100
    WHERE id_ram = NEW.id_ram;
END;

-- Trigger para calcular valores derivados en nodo_almacenamiento
CREATE TRIGGER IF NOT EXISTS calculate_nodo_storage_values
    AFTER INSERT ON nodo_almacenamiento
BEGIN
    UPDATE nodo_almacenamiento 
    SET 
        capacidad_disponible = capacidad_total - capacidad_usada,
        porcentaje_uso = (CAST(capacidad_usada AS REAL) / capacidad_total) * 100
    WHERE id_storage = NEW.id_storage;
END;

-- Trigger para configuración
CREATE TRIGGER IF NOT EXISTS update_config_timestamp 
    AFTER UPDATE ON configuracion_sistema
BEGIN
    UPDATE configuracion_sistema 
    SET fecha_modificacion = CURRENT_TIMESTAMP 
    WHERE id_config = NEW.id_config;
END;