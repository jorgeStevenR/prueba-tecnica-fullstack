# Prueba Tecnica Fullstack

Aplicacion fullstack para autenticacion JWT y gestion de numeros asociados al usuario autenticado.

## Stack

- Backend: Python + FastAPI + TinyDB
- Frontend: React + TypeScript + Vite
- Base de datos: TinyDB local, archivo JSON
- Documentacion API: Swagger/OpenAPI en FastAPI

## Requisitos

**Opcion local (sin Docker):**

- Python 3.11+
- Node.js 18+

**Opcion Docker:**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine + Docker Compose v2)

## Ejecucion rapida

| Metodo | Comando principal | Frontend | Backend |
|--------|-------------------|----------|---------|
| Docker | `docker compose up --build` | http://localhost:3000 | http://localhost:8080 |
| Local | Ver secciones Backend y Frontend | http://localhost:3000 | http://localhost:8080 |

Credenciales de prueba: **admin** / **1234**

---

## Docker (recomendado para evaluar el proyecto)

Desde la raiz del repositorio (`prueba-tecnica-fullstack`):

```bash
docker compose up --build
```

Cuando backend y frontend esten listos, veras un bloque **`Listo - Prueba Tecnica Fullstack`** en la consola con las URLs.

**Alternativa (mensaje al final en PowerShell):**

```powershell
.\scripts\docker-up.ps1
```

Levanta los contenedores en segundo plano, espera a que respondan y muestra el resumen de puertos.

La primera vez construye las imagenes del backend y del frontend. Tambien puedes abrir directamente:

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8080
- **Swagger:** http://localhost:8080/docs

### Comandos utiles

```bash
# Levantar en segundo plano
docker compose up --build -d

# Ver logs
docker compose logs -f

# Detener
docker compose down

# Detener y borrar datos de la base (TinyDB en volumen)
docker compose down -v
```

### Notas Docker

- No necesitas crear `backend/.env` ni `frontend/.env` para Docker: las variables van en `docker-compose.yml`.
- El frontend se compila con `VITE_API_BASE_URL=http://localhost:8080` (el navegador llama al backend en tu maquina, no al nombre del contenedor).
- Los datos de TinyDB persisten en el volumen Docker `backend_data` (`/app/data/db.json` dentro del contenedor).
- Si cambias codigo del frontend, reconstruye: `docker compose up --build`.
- Si ves `exec /docker-entrypoint.sh: no such file or directory`, reconstruye sin cache: `docker compose build --no-cache && docker compose up`.

---

## Backend (local)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

La API queda disponible en:

- API: http://localhost:8080
- Swagger: http://localhost:8080/docs
- OpenAPI JSON: http://localhost:8080/openapi.json

Credenciales predefinidas:

```json
{
  "username": "admin",
  "password": "1234"
}
```

## Frontend (local)

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

La aplicacion queda disponible en http://localhost:3000.

## Variables de entorno (ejecucion local)

Backend (`backend/.env`):

```env
JWT_SECRET=change-me-access-secret
JWT_REFRESH_SECRET=change-me-refresh-secret
DB_URL=./data/db.json
PORT=8080
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Frontend (`frontend/.env`):

```env
VITE_API_BASE_URL=http://localhost:8080
```

## Tests backend

```bash
cd backend
.venv\Scripts\activate
pytest tests -q
```

## Endpoints principales

- `POST /login`: retorna access token y refresh token.
- `POST /auth/refresh`: renueva access y refresh token (rotacion).
- `POST /auth/logout`: invalida el refresh token (blacklist).
- `POST /numbers`: crea un numero del usuario autenticado.
- `GET /numbers`: lista numeros con paginacion.
- `GET /numbers/{id}`: consulta un numero por ID.
- `PUT /numbers/{id}`: actualiza un numero.
- `DELETE /numbers/{id}`: elimina un numero.
- `GET /stats`: estadisticas de numeros del usuario autenticado.

## Coleccion Bruno

La carpeta `bruno/Prueba Tecnica Fullstack` contiene la coleccion para probar la API. Abrela desde Bruno y ejecuta primero `Login`; el script guarda `access_token` y `refresh_token` como variables de entorno.

## Decisiones tecnicas

El backend esta organizado con una arquitectura limpia:

- `domain`: entidades, contratos de repositorio y reglas base del negocio.
- `application`: casos de uso y servicios de aplicacion.
- `infrastructure`: persistencia TinyDB, seguridad JWT/hash y configuracion.
- `web`: controladores FastAPI, dependencias HTTP y esquemas request/response.

Se aplican patrones simples y utiles para la prueba:

- Repository: `UserRepository` y `NumberRepository` desacoplan la aplicacion de TinyDB.
- Use Case / Application Service: cada flujo principal vive en servicios de aplicacion.
- DTO / Schemas: requests y responses tipados con Pydantic.
- Dependency Injection: FastAPI construye las dependencias por request.
- Mapper: la infraestructura transforma registros TinyDB a entidades de dominio.

El frontend centraliza llamadas HTTP en `src/api`, maneja sesion en `AuthContext` y protege rutas con `ProtectedRoute`.

### Extras implementados

- **Docker Compose** para backend + frontend.
- **Tests** de integracion con `pytest` (auth, rotacion de refresh, CRUD numeros).
- **Refresh token rotation + blacklist** en TinyDB (`refresh_tokens`).
- **Frontend:** Tailwind CSS, validacion con Zod (`src/schemas`), toasts con `react-hot-toast`.
