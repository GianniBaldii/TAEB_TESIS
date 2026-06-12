# TAEB

Sistema web de gestión de alumnos de Taekwondo desarrollado con Django,
Django Templates, Tailwind CSS y MySQL.

## Tecnologías

- Python 3.13
- Django 5.2 LTS
- Django Templates
- Tailwind CSS
- MySQL 8.4
- Docker y Docker Compose

## Manual de instalación

Este manual explica cómo clonar el proyecto, configurar las credenciales,
levantarlo con Docker y ejecutar comandos de Django desde Docker o desde un
entorno virtual de Python.

### 1. Requisitos

Instalar:

- Git
- Docker Desktop
- Python 3.13, solo si se desea usar un entorno virtual local
- DBeaver, opcional para inspeccionar MySQL

Comprobar las herramientas desde PowerShell:

```powershell
git --version
docker --version
docker compose version
py --version
```

Docker Desktop debe estar abierto antes de ejecutar comandos de Docker.

### 2. Clonar el proyecto

Desde la carpeta donde se desea guardar el proyecto:

```powershell
git clone https://github.com/GianniBaldii/TAEB_TESIS.git
cd TAEB_TESIS
```

Todos los comandos restantes deben ejecutarse desde la raíz del repositorio,
donde se encuentra `docker-compose.yml`.

### 3. Crear el archivo de variables de entorno

El repositorio contiene `.env.example` como plantilla. Crear `.env` con:

```powershell
Copy-Item .env.example .env
```

En Linux, macOS, Git Bash o WSL:

```bash
cp .env.example .env
```

Abrir `.env` y reemplazar los valores de ejemplo:

```dotenv
# Django
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=colocar-una-clave-secreta-larga
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000
DJANGO_PORT=8000

# MySQL
MYSQL_DATABASE=taeb
MYSQL_USER=taeb_user
MYSQL_PASSWORD=colocar-una-contraseña
MYSQL_ROOT_PASSWORD=colocar-otra-contraseña
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_EXTERNAL_PORT=3306
```

El archivo `.env` contiene información sensible y está excluido de Git. No se
debe subir al repositorio.

### 4. Ubicación de las credenciales de la base

Las credenciales reales están en el archivo `.env`, no directamente en
`docker-compose.yml`.

| Variable | Uso |
|---|---|
| `MYSQL_DATABASE` | Nombre de la base de datos |
| `MYSQL_USER` | Usuario utilizado por Django |
| `MYSQL_PASSWORD` | Contraseña del usuario de Django |
| `MYSQL_ROOT_PASSWORD` | Contraseña administrativa de MySQL |
| `MYSQL_HOST` | Host interno; dentro de Docker debe ser `db` |
| `MYSQL_PORT` | Puerto interno de MySQL, normalmente `3306` |
| `MYSQL_EXTERNAL_PORT` | Puerto para conectarse desde Windows o DBeaver |

`docker-compose.yml` lee esos valores mediante expresiones como:

```yaml
MYSQL_DATABASE: ${MYSQL_DATABASE}
MYSQL_USER: ${MYSQL_USER}
MYSQL_PASSWORD: ${MYSQL_PASSWORD}
MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
```

Para ver la configuración que Docker Compose resolvió:

```powershell
docker compose config
```

Este comando muestra también valores sensibles. No compartir su salida sin
revisarla.

### 5. Construir y levantar el proyecto

Construir las imágenes y levantar Django y MySQL:

```powershell
docker compose up --build
```

La primera ejecución puede tardar mientras Docker descarga las imágenes e
instala las dependencias.

Para ejecutar los contenedores en segundo plano:

```powershell
docker compose up -d --build
```

Comprobar su estado:

```powershell
docker compose ps
```

Los servicios esperados son:

- `db`: MySQL.
- `web`: Django.

### 6. Ejecutar las migraciones

Con los contenedores levantados:

```powershell
docker compose exec web python app/manage.py migrate
```

Este comando crea las tablas de Django, incluida `auth_user`.

### 7. Crear el primer usuario

Crear un superusuario:

```powershell
docker compose exec web python app/manage.py createsuperuser
```

Django solicitará:

1. Nombre de usuario.
2. Correo electrónico, opcional.
3. Contraseña.
4. Confirmación de contraseña.

No se recomienda crear usuarios mediante un `INSERT` manual en `auth_user`,
porque Django debe generar correctamente el hash de la contraseña.

### 8. Ingresar al sistema

Abrir:

- Login: <http://localhost:8000/login/>
- Dashboard: <http://localhost:8000/dashboard/>
- Administración: <http://localhost:8000/admin/>

Ingresar con el usuario y la contraseña creados en el paso anterior.

### 9. Detener o volver a iniciar el proyecto

Detener los contenedores:

```powershell
docker compose down
```

Volver a iniciarlos:

```powershell
docker compose up -d
```

Ver los logs:

```powershell
docker compose logs -f
```

Ver únicamente los logs de Django:

```powershell
docker compose logs -f web
```

Los datos de MySQL se conservan en el volumen `mysql_data` al ejecutar
`docker compose down`.

No usar `docker compose down -v` salvo que se desee eliminar también toda la
base de datos local.

## Conexión desde DBeaver

Primero levantar MySQL:

```powershell
docker compose up -d db
```

En DBeaver seleccionar **Nueva conexión** y luego **MySQL**.

Usar los valores del archivo `.env`:

| Campo de DBeaver | Valor |
|---|---|
| Host | `localhost` |
| Puerto | valor de `MYSQL_EXTERNAL_PORT`, por defecto `3306` |
| Base de datos | valor de `MYSQL_DATABASE` |
| Usuario | valor de `MYSQL_USER` |
| Contraseña | valor de `MYSQL_PASSWORD` |

Presionar **Test Connection**. Si DBeaver solicita descargar el driver de
MySQL, aceptar la descarga.

Si aparece un problema de clave pública, revisar las propiedades del driver:

```text
allowPublicKeyRetrieval = true
useSSL = false
```

Si el puerto `3306` está ocupado, cambiar únicamente el puerto externo en
`.env`:

```dotenv
MYSQL_EXTERNAL_PORT=3307
```

Después recrear el servicio:

```powershell
docker compose up -d
```

En DBeaver se deberá usar el puerto `3307`. `MYSQL_PORT` y `MYSQL_HOST` deben
continuar con `3306` y `db` para la comunicación interna de Docker.

## Línea de comandos con entorno virtual

Docker es el método recomendado para ejecutar el proyecto completo. El entorno
virtual es útil para ejecutar Django directamente desde PowerShell mientras
MySQL sigue funcionando en Docker.

### 1. Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
py -m venv .venv
```

Este paso se realiza una sola vez.

### 2. Habilitar la activación en PowerShell

Si PowerShell bloquea la ejecución de `Activate.ps1`, habilitar scripts
solamente para la terminal actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

El permiso desaparece al cerrar la terminal.

Para habilitar scripts locales de forma permanente solo para el usuario actual:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

No se recomienda utilizar `Unrestricted`.

### 3. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Cuando está activo, PowerShell muestra `(.venv)` al comienzo de la línea.

### 4. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Comprobar Django:

```powershell
python -m django --version
```

El error `ModuleNotFoundError: No module named 'django'` indica que todavía no
se ejecutó la instalación de `requirements.txt` dentro del entorno activo.

Si `mysqlclient` no puede instalarse en Windows, ejecutar los comandos de
Django mediante Docker.

### 5. Levantar MySQL

```powershell
docker compose up -d db
```

### 6. Configurar el host para la ejecución local

Dentro de Docker, Django encuentra MySQL con el host `db`. Desde Windows debe
usar `localhost`.

Configurar la variable temporal:

```powershell
$env:MYSQL_HOST = "localhost"
```

Esta variable solo afecta la terminal actual y tiene prioridad sobre el valor
del archivo `.env`.

### 7. Ejecutar comandos de Django

```powershell
python app/manage.py migrate
python app/manage.py createsuperuser
python app/manage.py check
python app/manage.py test apps --settings=config.settings.test
python app/manage.py runserver
```

Con `runserver`, abrir <http://localhost:8000/login/>.

No ejecutar al mismo tiempo el servidor local y el servicio Docker `web` sobre
el mismo puerto `8000`. Para trabajar localmente se recomienda levantar solo
la base con `docker compose up -d db`.

### 8. Usar una terminal nueva

Cada vez que se abra PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
$env:MYSQL_HOST = "localhost"
```

### 9. Salir del entorno virtual

```powershell
deactivate
```

Para eliminar la variable temporal:

```powershell
Remove-Item Env:MYSQL_HOST
```

### Ejecutar sin activar el entorno

También se puede invocar directamente el ejecutable de Python:

```powershell
$env:MYSQL_HOST = "localhost"
.\.venv\Scripts\python.exe app\manage.py migrate
.\.venv\Scripts\python.exe app\manage.py createsuperuser
.\.venv\Scripts\python.exe app\manage.py runserver
```

## Comandos frecuentes con Docker

Levantar todo:

```powershell
docker compose up -d
```

Levantar solo MySQL:

```powershell
docker compose up -d db
```

Reconstruir Django después de cambiar dependencias o el Dockerfile:

```powershell
docker compose up -d --build web
```

Ejecutar migraciones:

```powershell
docker compose exec web python app/manage.py migrate
```

Crear un superusuario:

```powershell
docker compose exec web python app/manage.py createsuperuser
```

Comprobar la configuración de Django:

```powershell
docker compose exec web python app/manage.py check
```

Ejecutar tests:

```powershell
docker compose exec web python app/manage.py test apps `
  --settings=config.settings.test
```

Abrir una consola de Django:

```powershell
docker compose exec web python app/manage.py shell
```

## Uso de la consola y protocolo Git

Todos los comandos de Git deben ejecutarse desde la raíz del proyecto:

```powershell
cd C:\proyectos\TAEB_TESIS
```

Para comprobar la carpeta actual:

```powershell
Get-Location
```

Para revisar archivos modificados y la rama activa:

```powershell
git status
git branch --show-current
```

### Ramas principales

El proyecto utiliza:

- `main`: versión estable.
- `desarrollo`: integración de funcionalidades terminadas.
- Ramas de trabajo: cambios de cada tarea o funcionalidad.

No se debe trabajar ni hacer commits directamente sobre `main` o `desarrollo`.
Cada tarea debe realizarse en una rama nueva creada desde `desarrollo`.

### Nombres recomendados para ramas

Utilizar nombres breves, descriptivos y sin espacios:

```text
feature/modulo-alumnos
feature/barra-lateral
fix/error-login
docs/manual-instalacion
refactor/estructura-templates
```

Prefijos sugeridos:

| Prefijo | Uso |
|---|---|
| `feature/` | Nueva funcionalidad |
| `fix/` | Corrección de un error |
| `docs/` | Cambios de documentación |
| `refactor/` | Reorganización sin cambiar el comportamiento |
| `test/` | Incorporación o modificación de pruebas |

### 1. Actualizar `desarrollo`

Antes de crear una rama nueva:

```powershell
git switch desarrollo
git pull --ff-only origin desarrollo
```

`--ff-only` evita crear un commit de merge accidental al actualizar la rama
local.

Si existen cambios locales sin guardar, no continuar hasta revisarlos:

```powershell
git status
```

### 2. Crear una rama de trabajo

Crear la rama desde `desarrollo` actualizado:

```powershell
git switch -c feature/nombre-de-la-tarea
```

Ejemplo:

```powershell
git switch -c feature/modulo-alumnos
```

Comprobar la rama activa:

```powershell
git branch --show-current
```

### 3. Trabajar y revisar los cambios

Durante el desarrollo:

```powershell
git status
git diff
```

Agregar archivos al área de preparación:

```powershell
git add ruta\del\archivo
```

Para agregar todos los cambios revisados:

```powershell
git add .
```

Antes de crear el commit:

```powershell
git diff --staged
```

Crear el commit:

```powershell
git commit -m "feat: agregar módulo inicial de alumnos"
```

Ejemplos de mensajes:

```text
feat: agregar navegación lateral
fix: corregir redirección del login
docs: actualizar manual de instalación
refactor: reorganizar templates por apartados
test: agregar pruebas del dashboard
```

Se pueden crear varios commits pequeños y relacionados durante una tarea.

### 4. Actualizar la rama antes del Pull Request

Antes de integrar o crear el Pull Request, actualizar nuevamente `desarrollo`:

```powershell
git switch desarrollo
git pull --ff-only origin desarrollo
```

Volver a la rama de trabajo:

```powershell
git switch feature/nombre-de-la-tarea
```

Integrar los cambios recientes de `desarrollo`:

```powershell
git merge desarrollo
```

Este paso permite detectar y resolver conflictos en la rama de trabajo, antes
de abrir el Pull Request.

### 5. Resolver conflictos de merge

Si Git informa conflictos:

```powershell
git status
```

Abrir cada archivo marcado, elegir el contenido correcto y eliminar los
marcadores:

```text
[Inicio de cambios de la rama actual]
Cambios de la rama de trabajo
[Separador]
Cambios de desarrollo
[Fin de cambios provenientes de desarrollo]
```

En el archivo real, Git muestra esos bloques con los símbolos `<`, `=` y `>`.
Se debe conservar únicamente el contenido correcto y eliminar todos los
marcadores.

Después de resolverlos:

```powershell
git add ruta\del\archivo-resuelto
git commit
```

No utilizar `git reset --hard` ni descartar archivos sin revisar, porque se
pueden perder cambios locales.

### 6. Probar antes de publicar

Ejecutar como mínimo:

```powershell
docker compose exec web python app/manage.py check
docker compose exec web python app/manage.py test apps `
  --settings=config.settings.test
```

También se debe probar manualmente la funcionalidad modificada.

Comprobar el estado final:

```powershell
git status
```

### 7. Subir la rama a GitHub

La primera vez:

```powershell
git push -u origin feature/nombre-de-la-tarea
```

En los siguientes envíos:

```powershell
git push
```

### 8. Crear el Pull Request

En GitHub:

1. Abrir el repositorio `GianniBaldii/TAEB_TESIS`.
2. Seleccionar **Pull requests**.
3. Presionar **New pull request**.
4. Elegir `desarrollo` como rama base.
5. Elegir la rama de trabajo como rama de comparación.
6. Agregar un título claro y describir los cambios y pruebas realizadas.
7. Crear el Pull Request.

La dirección correcta debe ser:

```text
feature/nombre-de-la-tarea -> desarrollo
```

En GitHub se llama **Pull Request**. **Merge Request** es el nombre utilizado
por GitLab.

No crear normalmente Pull Requests directos hacia `main`. El paso de
`desarrollo` a `main` debe realizarse cuando se prepara una versión estable.

### 9. Integrar el Pull Request

Antes de aprobar el merge se debe comprobar:

- No hay conflictos.
- Los tests pasan.
- Los cambios fueron revisados.
- El Pull Request apunta a `desarrollo`.
- No se incluyeron `.env`, contraseñas, dumps ni archivos temporales.

Después de integrar el Pull Request se puede eliminar la rama remota desde
GitHub.

### 10. Limpiar la rama local

Una vez integrado el Pull Request:

```powershell
git switch desarrollo
git pull --ff-only origin desarrollo
git branch -d feature/nombre-de-la-tarea
git fetch --prune
```

`git branch -d` solo elimina una rama que Git reconoce como integrada. Evitar
`git branch -D` salvo que se tenga certeza de que sus cambios ya no son
necesarios.

### Flujo resumido

```powershell
# Actualizar desarrollo
git switch desarrollo
git pull --ff-only origin desarrollo

# Crear una rama
git switch -c feature/nombre-de-la-tarea

# Trabajar y crear commits
git status
git add .
git commit -m "feat: describir el cambio"

# Actualizar antes del Pull Request
git switch desarrollo
git pull --ff-only origin desarrollo
git switch feature/nombre-de-la-tarea
git merge desarrollo

# Probar y publicar
docker compose exec web python app/manage.py check
git push -u origin feature/nombre-de-la-tarea

# Crear en GitHub:
# feature/nombre-de-la-tarea -> desarrollo
```

## Dumps de MySQL

Los respaldos se guardan en `docker/mysql/dumps/` y no se versionan.

Los scripts requieren Git Bash, WSL o una terminal compatible con `sh`.

Crear un dump con nombre automático:

```bash
sh scripts/dump_db.sh
```

Crear un dump con nombre específico:

```bash
sh scripts/dump_db.sh respaldo_inicial.sql
```

Restaurar un dump:

```bash
sh scripts/restore_db.sh respaldo_inicial.sql
```

Se recomienda crear un respaldo antes de realizar una restauración.

## Solución de problemas

### Docker no encuentra `.env`

Crear el archivo desde la plantilla:

```powershell
Copy-Item .env.example .env
```

### Django no está instalado

Con el entorno virtual activo:

```powershell
python -m pip install -r requirements.txt
```

### PowerShell bloquea `Activate.ps1`

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Django local no encuentra el host `db`

Al ejecutar Django fuera de Docker:

```powershell
$env:MYSQL_HOST = "localhost"
```

### El puerto 8000 está ocupado

Comprobar si el servicio web de Docker está activo:

```powershell
docker compose ps
```

Detenerlo antes de ejecutar `python app/manage.py runserver`:

```powershell
docker compose stop web
```

### El puerto 3306 está ocupado

Cambiar `MYSQL_EXTERNAL_PORT` en `.env`, por ejemplo:

```dotenv
MYSQL_EXTERNAL_PORT=3307
```

## Estructura principal

```text
app/
|-- apps/
|   |-- core/
|   `-- usuarios/
|-- config/
|   `-- settings/
|       |-- base.py
|       |-- local.py
|       |-- production.py
|       `-- test.py
|-- static/
|   |-- iconos/
|   `-- imagenes/logos/
|-- templates/
|   |-- autenticacion/
|   |-- layouts/
|   |-- parciales/
|   `-- tablero/
`-- manage.py
docker/
|-- django/
`-- mysql/dumps/
scripts/
docker-compose.yml
requirements.txt
```

## Configuración por entorno

Desarrollo:

```text
DJANGO_SETTINGS_MODULE=config.settings.local
```

Tests:

```text
DJANGO_SETTINGS_MODULE=config.settings.test
```

Producción:

```text
DJANGO_SETTINGS_MODULE=config.settings.production
```

Producción requiere una clave secreta segura, hosts y orígenes CSRF válidos,
HTTPS y un servidor WSGI o ASGI apropiado.
