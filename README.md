# SkyNet

Gestión integral de una aerolínea con Django.

## Descripción

SkyNet es una aplicación web desarrollada con **Django** y **templates** que permite gestionar una aerolínea. Los administradores pueden **crear, leer, actualizar y eliminar (CRUD)** entidades como **aviones**, **asientos**, **aeropuertos**, **rutas** y **vuelos**. Los visitantes (no administradores) pueden **buscar/seleccionar vuelos** y **reservar pasajes**.

## Características clave

* CRUD de aviones, asientos, aeropuertos, rutas y vuelos.
* Búsqueda/selección de vuelos por parte de visitantes.
* Reserva de pasajes para usuarios no administradores.
* Validaciones y reglas de negocio en procesos de reserva.
* Panel de administración con permisos diferenciados.

## Stack tecnológico

* **Python 3.10**
* **Django 5.2.4**
* **django-widget-tweaks 1.5.0** – Personalización de formularios en templates
* **Pillow 9.0.1** – Manejo de imágenes
* **SQLite** como base de datos por defecto
* **asgiref** y **sqlparse** – Dependencias internas de Django

## Requisitos e instalación

1. **Clonar el repositorio**

   ```bash
   git clone <URL-del-repo>
   cd Skynet
   ```
2. **Crear y activar un entorno virtual**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # En Linux/Mac
   venv\Scripts\activate      # En Windows
   ```
3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```
4. **Aplicar migraciones**

   ```bash
   python manage.py migrate
   ```
5. **(Opcional) Crear un superusuario para acceder al panel de administración**

   ```bash
   python manage.py createsuperuser
   ```
6. **Levantar el servidor de desarrollo**

   ```bash
   python manage.py runserver
   ```
7. Abrir el navegador en `http://127.0.0.1:8000`

## Uso

### Para administradores

1. Ingresar a `http://127.0.0.1:8000/admin` con las credenciales del superusuario.
2. Desde el panel de administración se pueden crear, editar o eliminar:

   * Aviones y configuración de asientos.
   * Aeropuertos.
   * Rutas.
   * Vuelos.
3. Guardar los cambios para que estén disponibles en la vista pública.

### Para visitantes

1. Acceder a la página principal `http://127.0.0.1:8000`.
2. Buscar vuelos según origen, destino y fecha.
3. Seleccionar el vuelo deseado.
4. Elegir asientos disponibles.
5. Confirmar la reserva completando los datos solicitados.
6. Recibir confirmación de la reserva.

## Estructura del proyecto y módulos clave

* **airplane**: Gestión de aviones y sus asientos.
* **flight**: Administración de rutas y vuelos.
* **home**: Páginas principales y navegación general.
* **reservations**: Gestión de reservas de pasajes

## Autores y créditos

* Cardinali, Nicolás
* Desplats, Jonathan
* Palacios, Rodolfo
