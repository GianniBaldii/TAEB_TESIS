# TAEB Mobile

Aplicacion mobile de TAEB para alumnos. Permite iniciar sesion con DNI y
contrasena, consultar datos personales, progreso, historial de cinturones y
examenes desde una interfaz Ionic/Angular conectada a la API Django.

## Tecnologia utilizada

- Ionic 8
- Angular 19
- Capacitor 8
- TypeScript
- RxJS
- JWT con access token y refresh token
- `capacitor-secure-storage-plugin` para guardar tokens en dispositivos nativos

## Requisitos previos

Para desarrollo en navegador:

- Node.js compatible con Angular 19
- npm
- Backend Django de TAEB levantado en `http://localhost:8000`

Para ejecutar en Android:

- Android Studio
- Android SDK
- Java/JDK compatible con Android Studio
- Capacitor CLI incluido como dependencia del proyecto

Para ejecutar en iOS:

- macOS
- Xcode
- CocoaPods, si el flujo nativo lo requiere

## Instalacion de dependencias

Desde la carpeta `mobile/`:

```powershell
npm install
```

Si se trabaja desde Docker, el servicio `mobile` instala las dependencias en el
volumen `mobile_node_modules`.

## Variables de entorno

La URL base de la API se documenta en `.env.example` de la raiz:

```dotenv
IONIC_API_BASE_URL=http://localhost:8000/api/v1/mobile
```

El frontend usa actualmente:

```typescript
apiBaseUrl: 'http://localhost:8000/api/v1/mobile'
```

Archivo relacionado:

```text
src/environments/environment.ts
```

Para usar un emulador o dispositivo fisico puede ser necesario reemplazar
`localhost` por una IP accesible desde el dispositivo.

Ejemplos habituales:

- Navegador local: `http://localhost:8000/api/v1/mobile`
- Android Emulator hacia host local: `http://10.0.2.2:8000/api/v1/mobile`
- Dispositivo fisico en la misma red: `http://IP_DE_LA_PC:8000/api/v1/mobile`

Si se cambia el origen desde el que corre Ionic, tambien debe actualizarse
`CORS_ALLOWED_ORIGINS` en el `.env` del backend.

## Ejecucion local en navegador

Levantar primero backend y base de datos desde la raiz del repositorio:

```powershell
docker compose up -d db backend
docker compose exec backend python app/manage.py migrate
```

Luego iniciar Ionic desde `mobile/`:

```powershell
npm start
```

Abrir:

```text
http://localhost:8100
```

Tambien se puede levantar todo con Docker desde la raiz:

```powershell
docker compose up --build
```

Servicios esperados:

- `db`: MySQL.
- `backend`: Django web + API REST.
- `mobile`: servidor de desarrollo Ionic en `http://localhost:8100`.

## Ejecucion en emulador o dispositivo

Primero generar el build web:

```powershell
npm run build
```

Sincronizar Capacitor:

```powershell
npx cap sync
```

Android:

```powershell
npx cap open android
```

iOS:

```powershell
npx cap open ios
```

Desde Android Studio o Xcode se selecciona el emulador/dispositivo y se ejecuta
la aplicacion.

## Comunicacion con la API backend

La app consume la API versionada:

```text
/api/v1/mobile/
```

Endpoints principales:

- `POST /auth/login/`: login con DNI y contrasena.
- `POST /auth/refresh/`: renovacion de access token.
- `POST /auth/logout/`: cierre de sesion y blacklist del refresh token.
- `GET /me/`: resumen del alumno autenticado.
- `GET /me/profile/`: perfil del alumno.
- `GET /me/progress/`: progreso y estado orientativo.
- `GET /me/belt-history/`: historial de cinturones.
- `GET /me/exams/`: examenes del alumno.

La autenticacion usa JWT. El access token se envia en cada request protegida:

```text
Authorization: Bearer <access_token>
```

Los interceptores en `src/app/core/auth/` agregan el token y tratan de renovar
la sesion cuando la API responde `401`.

## Estructura principal

```text
src/
|-- app/
|   |-- core/
|   |   |-- api/
|   |   |-- auth/
|   |   |-- models/
|   |   `-- services/
|   |-- features/
|   |   |-- auth/login/
|   |   |-- exams/
|   |   |-- home/
|   |   |-- profile/
|   |   |-- progress/
|   |   `-- tabs/
|   `-- app.routes.ts
|-- assets/
|-- environments/
|-- global.scss
`-- main.ts
```

## Credenciales de prueba

No se versionan credenciales reales.

Para crear un usuario de prueba:

1. Crear un superusuario en Django.
2. Crear o elegir un alumno activo.
3. Asociarlo a una escuela activa.
4. Desde la ficha del alumno, usar la card `Acceso mobile`.
5. Generar credenciales mobile con una contrasena temporal.

El usuario mobile es el DNI normalizado del alumno. La contrasena se guarda con
el mecanismo de hash de Django y no se muestra luego de guardarse.

## Comandos utiles

```powershell
npm start
npm run build
npm test
npx cap sync
```

## Notas de seguridad

- No subir `.env` ni credenciales reales.
- No guardar tokens en texto plano en codigo fuente.
- En navegador de desarrollo los tokens quedan en memoria.
- En plataforma nativa los tokens se guardan con
  `capacitor-secure-storage-plugin`.
- En produccion se debe usar HTTPS y configurar correctamente CORS/hosts en el
  backend.
