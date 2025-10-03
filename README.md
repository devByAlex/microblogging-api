# Microblogging API con Análisis de Sentimiento

Una API REST de microblogging que incluye análisis automático de sentimiento usando  **FastAPI** , **SQLAlchemy** y  **TextBlob** .

## Características Principales

* Autenticación con JWT (registro, login y autorización)
* CRUD de publicaciones (crear, leer, actualizar, eliminar)
* Sistema de seguimiento entre usuarios (follow/unfollow)
* Análisis automático de sentimiento (positivo/negativo/neutral) en cada post
* Feed personalizado con publicaciones de usuarios seguidos
* Documentación interactiva generada con FastAPI (Swagger UI / ReDoc)
* Base de datos relacional con PostgreSQL + SQLAlchemy ORM

## Tecnologías Utilizadas

* **Backend Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Base de Datos:** PostgreSQL
* **Autenticación:** JWT (python-jose), bcrypt
* **Machine Learning:** TextBlob (NLP para análisis de sentimiento)
* **Servidor:** Uvicorn

## Requisitos Previos

* Python 3.8+
* PostgreSQL 12+ (o SQLite para pruebas locales)
* pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/devByAlex/microblogging-api.git
cd microblogging-api
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto (puedes guiarte con `.env.example`). Aquí un ejemplo típico:

```bash
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/microblog_db
SECRET_KEY=super_clave_ultra_segura_123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Crear la base de datos

```bash
# En PostgreSQL
createdb microblog_db
```

### 6. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://127.0.0.1:8000`

## Documentación de la API

Una vez iniciado el servidor, accede a la documentación interactiva:

* **Swagger UI:** http://127.0.0.1:8000/docs
* **ReDoc:** http://127.0.0.1:8000/redoc

## Endpoints Principales

### Autenticación

* `POST /users` - Registrar nuevo usuario
* `POST /login` - Iniciar sesión y obtener token JWT
* `GET /users/me` - Obtener perfil del usuario autenticado

### Usuarios

* `GET /users/{username}` - Ver perfil de usuario
* `POST /users/{username}/follow` - Seguir usuario
* `DELETE /users/{username}/follow` - Dejar de seguir

### Publicaciones

* `GET /posts/` - Listar todas las publicaciones
* `GET /posts/feed` - Feed personalizado (usuarios seguidos)
* `GET /posts/{post_id}` - Ver publicación específica
* `POST /posts/` - Crear nueva publicación
* `PUT /posts/{post_id}` - Actualizar publicación
* `DELETE /posts/{post_id}` - Eliminar publicación

## Análisis de Sentimiento

Cada publicación es analizada automáticamente al crearse. El sistema clasifica el sentimiento en:

* **Positivo:** Contenido optimista, alegre
* **Negativo:** Contenido pesimista, triste
* **Neutral:** Contenido objetivo, sin carga emocional

**Por ejemplo:**

```json
{
  "content": "¡Qué día más guay hace hoy!",
  "sentiment": "positive"
}
```

## Estructura del Proyecto

```
microblogging-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # Punto de entrada y definición de endpoints
│   ├── models.py         # Modelos de base de datos (SQLAlchemy)
│   ├── schemas.py        # Esquemas Pydantic para validación
│   ├── auth.py           # Lógica de autenticación JWT
│   ├── database.py       # Configuración de base de datos
│   └── ml.py             # Análisis de sentimiento con TextBlob
├── .env.example          # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
├── reset_db.py          # Script de utilidad (solo desarrollo)
└── README.md
```

## Ejemplos de Uso

### Registrar Usuario

```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username":"Pedro","email":"pedro@example.com","password":"p12345"}'
```

### Crear Publicación

```bash
curl -X POST "http://127.0.0.1:8000/posts/" \
  -H "Authorization: Bearer TU_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "¡Aprender FastAPI mola!"
  }'
```

## Seguridad

* ✅ Contraseñas hasheadas con bcrypt
* ✅ Autenticación JWT con tokens de expiración
* ✅ Variables de entorno para información sensible
* ✅ Validación de datos con Pydantic
* ✅ Control de acceso basado en propietario

## Mejoras Futuras

* [ ] Sistema de likes y comentarios
* [ ] Paginación en endpoints de listado
* [ ] Upload de imágenes
* [ ] Notificaciones en tiempo real
* [ ] Tests unitarios y de integración
* [ ] Deploy en producción (Render/Railway)
* [ ] CI/CD con GitHub Actions

## 👨‍💻Autor

*Alex Ordoñez*

* **GitHub**: [@devByAlex](https://github.com/tu-usuario)
* **LinkedIn:** www.linkedin.com/in/alexander-perez-ordoñez-79061934b
* **Email:** a.perezordonez98@gmail.com
