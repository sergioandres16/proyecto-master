# Guía de Instalación y Configuración

Este documento describe cómo instalar y configurar la aplicación de gestión de Slices en una máquina virtual (VM) que actuará como nodo de control.

El despliegue se realizará en una **VM de Control** que debe tener acceso a:
1.  Los nodos "worker" del clúster Linux a través de SSH.
2.  La API del entorno OpenStack a través de la red.

## Paso 1: Preparar la VM de Control

Asegúrate de que la VM de Control cumple con los siguientes requisitos:

1.  **Acceso SSH sin Contraseña:** La VM debe poder conectarse por SSH a todos los nodos worker del clúster Linux sin necesidad de una contraseña.
    *   Copia tu clave pública (`~/.ssh/id_rsa.pub`) al archivo `~/.ssh/authorized_keys` en cada nodo worker.

2.  **Software Requerido:** Instala `git` y las herramientas de `python3`.

    *   **En sistemas Debian/Ubuntu:**
        ```bash
        sudo apt update
        sudo apt install git python3-full python3-venv -y
        ```
    *   **En sistemas RedHat/CentOS:**
        ```bash
        sudo yum install git python3 python3-pip -y
        ```

## Paso 2: Clonar el Repositorio

Clona el código del proyecto en la VM de Control.

```bash
git clone <URL_DEL_REPOSITORIO>
cd cloud-2022
```

## Paso 3: Configurar el Entorno Virtual

Para aislar las dependencias del proyecto, crearemos y activaremos un entorno virtual.

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```
> **Nota:** A partir de ahora, todos los comandos deben ejecutarse dentro de este entorno virtual activado.

## Paso 4: Instalar Dependencias

Instala todas las librerías de Python requeridas por el proyecto.

```bash
pip install -r requirements.txt
```

## Paso 5: Configurar la Aplicación

### 5.1. Archivo de Configuración Principal

La configuración se gestiona a través del archivo `config.env`.

1.  **Copia el archivo de ejemplo:**
    ```bash
    cp config.env.example config.env
    ```

2.  **Edita `config.env`:** Abre el archivo con un editor (como `nano` o `vim`) y rellena las secciones según tu infraestructura.

    ```ini
    # Ejemplo de config.env

    [database]
    data_dir = data/

    [linux_cluster]
    user = tu_usuario_ssh
    ssh_key_path = /home/tu_usuario_ssh/.ssh/id_rsa

    [openstack]
    keystone_url = http://<IP_OPENSTACK_KEYSTONE>:5000/v3
    nova_url = http://<IP_OPENSTACK_NOVA>:8774/v2.1
    neutron_url = http://<IP_OPENSTACK_NEUTRON>:9696/v2.0
    user = tu_usuario_openstack
    password = tu_contraseña_openstack
    domain_name = Default
    project_name = tu_proyecto_openstack
    image_id = ID_de_la_imagen_por_defecto
    flavor_id = ID_del_flavor_por_defecto
    network_id = ID_de_la_red_externa
    ```

### 5.2. Acceso SSH a VMs de OpenStack (vía Bastion/Jump Host)

Si no tienes acceso directo por SSH a las VMs de OpenStack y necesitas pasar por una VM intermediaria (jump host), configura tu cliente SSH en la **VM de Control**.

1.  Edita o crea el archivo `~/.ssh/config`:
    ```bash
    nano ~/.ssh/config
    ```

2.  Añade la siguiente configuración, reemplazando los valores de ejemplo:

    ```ini
    # Host: Patrón para las IPs de las VMs de OpenStack (usa wildcard *)
    # Ejemplo: Host 10.20.1.*
    Host <patron_ip_vms_openstack>

      # ProxyJump: Usuario e IP de tu VM intermediaria (jump host)
      ProxyJump <usuario_jump_host>@<ip_del_jump_host>

      # Opcional: Usuario para conectarse a las VMs finales de OpenStack
      User <usuario_vm_final>
    ```

## Paso 6: Inicializar la Base de Datos

La aplicación debería crear e inicializar las bases de datos automáticamente. Si necesitas hacerlo manualmente, ejecuta:

```bash
python3 database/db_initializer.py
```

## Paso 7: Ejecutar la Aplicación y la API

Necesitas ejecutar dos procesos principales en segundo plano.

```bash
# (Asegúrate de estar en el entorno virtual: '''source venv/bin/activate''')

# Iniciar la aplicación principal en segundo plano
python3 App.py &

# Iniciar la API con Uvicorn en segundo plano
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

## Paso 8: Verificación

1.  **Revisa los Logs:** La aplicación generará archivos de log. Revísalos para detectar errores.
2.  **Accede a la Documentación de la API:** Abre un navegador y ve a `http://<IP_DE_TU_VM_DE_CONTROL>:8000/docs`.
3.  **Prueba el Endpoint de Salud:** En la interfaz de Swagger, ejecuta el endpoint `/system/health`. Debería devolver un estado `"healthy"`.