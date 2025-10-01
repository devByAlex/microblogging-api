"""
API Principal del Sistema de Microblogging con IA.

Esta es la aplicación principal de FastAPI que implementa un sistema de microblogging
con las siguientes características:
- Sistema de autenticación JWT
- CRUD completo de usuarios y publicaciones
- Sistema de seguimiento entre usuarios
- Análisis automático de sentimiento con IA
- Feed personalizado basado en seguimiento

Endpoints principales:
- Autenticación: /login
- Usuarios: /users, /users/me, /users/{username}
- Publicaciones: /posts, /posts/{id}
- Seguimiento: /users/{username}/follow
- Feed: /posts/feed

Autor: Alex Ordoñez
Versión: 1.0
"""

from fastapi import FastAPI, HTTPException, status, Depends
import uvicorn 
from sqlalchemy.orm import Session 
from app.database import Base, engine, get_db
from app.models import User as UserModel, Post as PostModel, Follow #esto importa mis modelos
from app import models, schemas, auth
from typing import List #Necesito esto para tipar la lista de posts
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.ml import analyze_sentiment
from sqlalchemy import desc

#Creo todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microblogging API con IA",
              description="API de microblogging con análisis de sentimiento automático",
              version="1.0.0")

#Configuro el esquema OAuth2 para autenticación
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

# ========================================
# ENDPOINT RAÍZ
# ========================================
@app.get("/")
async def read_root():
    return {"message" : "Hola y bienvenidos al nuevo microbloggin"}


# ========================================
# ENDPOINTS DE USUARIOS
# ========================================
@app.post("/users", response_model=schemas.UserResponse) 
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)): 
    """
    Crea un nuevo usuario en el sistema.
    
    Registra un nuevo usuario validando que el email sea único,
    hashea la contraseña de forma segura y almacena la información
    en la base de datos.
    
    Args:
        user (schemas.UserCreate): Datos del usuario a crear
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        schemas.UserResponse: Información del usuario creado (sin contraseña)
        
    Raises:
        HTTPException: 400 Bad Request si el email ya está registrado
        
    Note:
        La contraseña se hashea automáticamente usando bcrypt antes
        del almacenamiento por seguridad.
    """
    
    #Verifico si si el usuario ya existe en el sistema
    existing_user= db.query(UserModel).filter(UserModel.email == user.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )
        
    #Hasheo la contraseña de entrada usando mi función hash_password y pasandole de argumento la entrada del user.
    hashed_password = auth.hash_password(user.password)
    
    #Creo una instancia del modelo SQLAlchemy, usando los datos de entrada del usuario y la contraseña hasheada
    new_user = UserModel(
        username=user.username,
        email = user.email,
        hashed_password= hashed_password
    )   
    
    #Guardo el usuario en la base de datos
    db.add(new_user)
    db.commit()
    #Refresco el objeto para que tenga ID y otros datos generados por la DB
    db.refresh(new_user)
    
    #Devuelvo respuesta, el objeto 'new_user' se convertirá automaticamente en un 'schemas.UserResponde'.
    return new_user

@app.get("/users/me")
async def read_current_user(current_user: schemas.UserResponse = Depends(auth.get_current_user)): 
    """
    Obtiene el perfil del usuario autenticado actual.
    
    Endpoint protegido que devuelve la información del usuario
    que está actualmente autenticado mediante el token JWT.
    
    Args:
        current_user: Usuario autenticado inyectado automáticamente
        
    Returns:
        schemas.UserResponse: Información completa del usuario actual
        
    Note:
        Requiere autenticación JWT válida. La dependencia get_current_user
        maneja automáticamente la validación del token.
    """
    return current_user 

#este endpoint no necesita estar protegido con un token, porque es info pública
@app.get("/users/{username}", response_model=schemas.UserResponse)
async def get_profile(username: str, db: Session = Depends(get_db)): 
    """
    Obtiene el perfil público de un usuario específico.
    
    Endpoint público que permite consultar la información básica
    de cualquier usuario registrado en el sistema.
    
    Args:
        username (str): Nombre de usuario a buscar
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        schemas.UserResponse: Información pública del usuario
        
    Raises:
        HTTPException: 404 Not Found si el usuario no existe
    """
    #Busco el usuario por nombre de usuario
    search_username = db.query(UserModel).filter(UserModel.username == username).first()
    if not search_username: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    return search_username

# ========================================
# AUTENTICACIÓN
# ========================================
@app.post("/login") 
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): 
    """
    Autentica un usuario y genera un token de acceso JWT.
    
    Valida las credenciales del usuario (username/password) y, si son correctas,
    genera un token JWT que puede ser utilizado para acceder a endpoints protegidos.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Formulario con username y password
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        dict: Token de acceso JWT y tipo de token
            - access_token (str): Token JWT firmado
            - token_type (str): Tipo de token ("bearer")
            
    Raises:
        HTTPException: 401 Unauthorized si las credenciales son incorrectas
        
    Note:
        El token tiene una duración limitada definida por ACCESS_TOKEN_EXPIRE_MINUTES.
        Utiliza el estándar OAuth2 Password Flow.
    """
    
    # Busco el usuario en la BD por su username. 
    search_user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not search_user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Error: Credenciales Incorrectas")
    
    #Si el usuario existe, verifico su contraseña. >Uso mi función 'auth.verify_password()' con la contrasña del formulario ('form_data.password) y la contraseña hasheada del usuario que encontré en la BD
    if not auth.verify_password(form_data.password, search_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error: Credenciales incorrectas")
    
    #Si todo es correcto creo un token de acceso. > Defino el payload del token(un diccionario con la información del usuario. > Uso mi función 'auth.create_access_token()', para generar el token)
    acccess_token = auth.create_access_token(
        data={"sub" : search_user.username} 
    )
    
    # Retorno el token en formato estándar OAuth2
    return {"access_token": acccess_token, "token_type": "bearer"}   

# ========================================
# ENDPOINTS DE PUBLICACIONES
# ========================================
@app.get("/posts/", response_model=List[schemas.PostResponse])#Uso List para tipar la respuesta.
async def get_all_posts(db: Session = Depends(get_db)): 
    """
    Obtiene todas las publicaciones del sistema.
    
    Endpoint público que devuelve todas las publicaciones existentes
    ordenadas por fecha de creación (más recientes primero).
    
    Args:
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        List[schemas.PostResponse]: Lista de todas las publicaciones con
                                   información del autor
                                   
    Note:
        Este endpoint es público y no requiere autenticación.
        Útil para mostrar un timeline global del sistema.
    """
    #Obtengo todas las publicaciones por orden de fecha descendente.
    all_posts = db.query(PostModel).order_by(PostModel.created_at.desc()).all()
    return all_posts

@app.get("/posts/feed", response_model= List[schemas.PostResponse])
async def show_posts(current_user: UserModel = Depends(auth.get_current_user), db: Session = Depends(get_db)): 
    """
    Obtiene el feed personalizado del usuario autenticado.
    
    Devuelve las publicaciones de todos los usuarios que el usuario
    autenticado sigue, ordenadas por fecha de creación (más recientes primero).
    
    Args:
        current_user (UserModel): Usuario autenticado
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        List[schemas.PostResponse]: Lista de publicaciones del feed personalizado
        
    Note:
        - Requiere autenticación JWT válida
        - Solo muestra posts de usuarios seguidos
        - Retorna lista vacía si no se sigue a nadie
        - Ordenado cronológicamente (más reciente primero)
    """
    
    # Obtiene la lista de relaciones de seguimiento del usuario actual
    list_of_follow_object = db.query(Follow).filter(Follow.follower_id == current_user.id).all()
    
    #Uso mi "comprensión de listas" para extraer el ID de los usuarios que son seguidos
    followed_users_id = [
        follow_record.followed_id # Extrae el ID del usuario seguido
        for follow_record in list_of_follow_object
    ]
    
    # Si no sigue a nadie, retorna lista vacía
    if not followed_users_id:
        return [] 
    
    # Obtiene las publicaciones de usuarios seguidos ordenadas por fecha
    current_posts = db.query(PostModel).filter(PostModel.owner_id.in_(followed_users_id)).order_by(PostModel.created_at.desc()).all()
    
    return current_posts

@app.get("/posts/{post_id}", response_model=schemas.PostResponse)#Aquí no uso List[] porque no usaré .all que ese si que devuelve una lista
async def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una publicación específica por su ID.
    
    Endpoint público que permite consultar los detalles completos
    de una publicación individual incluyendo información del autor.
    
    Args:
        post_id (int): ID único de la publicación a buscar
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        schemas.PostResponse: Datos completos de la publicación
        
    Raises:
        HTTPException: 404 Not Found si la publicación no existe
    """
    
    #Busco la publicación por su ID
    post = db.query(PostModel).filter(PostModel.id == post_id).first()#Aquí uso first porque solo quiero una publicación en especifico.
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada, prueba con otra")
    
    return post

@app.post("/posts/", response_model=schemas.PostCreate)
async def create_new_post(post: schemas.PostCreate, 
                          db: Session = Depends(get_db),
                          current_user: UserModel = Depends(auth.get_current_user)
                          ):
    """
    Crea una nueva publicación con análisis de sentimiento automático.
    
    Permite a usuarios autenticados crear publicaciones en el sistema.
    Automáticamente analiza el sentimiento del contenido usando IA
    y almacena el resultado junto con la publicación.
    
    Args:
        post (schemas.PostCreate): Datos de la publicación a crear
        db (Session): Sesión de base de datos inyectada
        current_user (UserModel): Usuario autenticado que crea el post
        
    Returns:
        schemas.PostCreate: Datos de la publicación creada
        app
    Note:
        - Requiere autenticación JWT válida
        - El análisis de sentimiento se realiza automáticamente con TextBlob
        - El usuario se asigna automáticamente como propietario del post
    """
    # Analizo el sentimiento del contenido usando IA
    # Llamo a la función y guardo el resultado de la variable
    sentiment_result = analyze_sentiment(post.content)
    
    #2. Creo una nueva instancia del modelo Post
    new_post = PostModel(
        content = post.content,
        owner_id = current_user.id, #Asigna el id del usuario autenticado como dueño 
        sentiment = sentiment_result #Ahora asigno el resultado del análisis a la columna 'sentiment'
    )
    
    
    # Guardo la publicación en mi base de datos.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post

@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post_by_id(
                            post_id: int,
                            post_data: schemas.PostCreate,
                            current_user: UserModel = Depends(auth.get_current_user, ), 
                            db:Session = Depends(get_db)
                            ):
    """
    Actualiza una publicación existente.
    
    Permite al propietario de una publicación modificar su contenido.
    Solo el autor original puede editar sus propias publicaciones.
    
    Args:
        post_id (int): ID de la publicación a actualizar
        post_data (schemas.PostCreate): Nuevo contenido de la publicación
        current_user (UserModel): Usuario autenticado
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        schemas.PostResponse: Datos actualizados de la publicación
        
    Raises:
        HTTPException: 
            - 404 Not Found si la publicación no existe
            - 403 Forbidden si el usuario no es el propietario
            
    Note:
        Implemento control de acceso: solo el autor puede editar sus posts.
    """
    # Busco la publicación por ID
    post = db.query(PostModel).filter(PostModel.id == post_id).first()  
     
    # Manejo el caso de que la publicación no exista
    if not post: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # SEGURIDAD: Verifico que el usuario autenticado sea el propietario
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "No tienes permiso para actualizar esta publicación")

    # Actualizo los datos del objeto de la publicación. 
    post.content = post_data.content

    db.commit()
    db.refresh(post)
    
    return post 

@app.delete("/posts/{post_id}") 
async def delete_post_by_id(
    post_id: int,
    current_user: UserModel = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
    ):
    
    """
    Elimina una publicación del sistema.
    
    Permite al propietario de una publicación eliminarla permanentemente.
    Solo el autor original puede eliminar sus propias publicaciones.
    
    Args:
        post_id (int): ID de la publicación a eliminar
        current_user (UserModel): Usuario autenticado
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        dict: Mensaje de confirmación de eliminación
        
    Raises:
        HTTPException: 
            - 404 Not Found si la publicación no existe
            - 403 Forbidden si el usuario no es el propietario
            
    Note:
        La eliminación es permanente y no se puede deshacer.
    """
    #Busco la publicación por ID
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
    
    # SEGURIDAD: Verifico que el usuario autenticado sea el propietario
    if post.owner_id != current_user.id: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para borrar este post")
    
    #Elimino la publicación permanentemente
    db.delete(post)
    db.commit()
    
    return {"message": "Publicación eliminada correctamente"}     

# ========================================
# ENDPOINTS DE SEGUIMIENTO
# ========================================

@app.post("/users/{username}/follow")
async def follow_user(username: str, 
                      current_user: UserModel = Depends(auth.get_current_user), 
                      db: Session = Depends(get_db)): 
    """
    Permite seguir a otro usuario del sistema.
    
    Crea una relación de seguimiento entre el usuario autenticado
    y el usuario especificado, permitiendo personalizar el feed.
    
    Args:
        username (str): Nombre de usuario a seguir
        current_user (UserModel): Usuario autenticado que realiza el seguimiento
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        dict: Mensaje de confirmación del seguimiento
        
    Raises:
        HTTPException: 
            - 404 Not Found si el usuario a seguir no existe
            - 400 Bad Request si intenta seguirse a sí mismo
            - 400 Bad Request si ya sigue al usuario
            
    Note:
        - No se puede seguir a uno mismo
        - No se puede seguir al mismo usuario múltiples veces
        - Requiere autenticación JWT válida
    """
    # Busco el usuario a seguir.
    search_follower = db.query(UserModel).filter(UserModel.username == username ).first()
    
    if not search_follower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Me aseguro que un usuario no se siga a sí mismo.
    if search_follower.id == current_user.id: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "No se puede seguir así mismo")
    
    # Verifico si el usuario ya está siendo seguido
    existing_follow = db.query(Follow).filter(Follow.follower_id == current_user.id, 
                                              Follow.followed_id == search_follower.id).first()
    if existing_follow: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Ya sigues a este usuario")
    
    
    #Creo la relación con la base de datos. 
    #Creo una instancia del modelo 'Follow'
    #Asigno el ID del usuario actual como el 'follower_id'
    #Asigno el ID del usuario que se quiere seguir como el 'followed_id'
    
    new_follow = Follow(
        follower_id = current_user.id,
        followed_id = search_follower.id
    )
    
    #Añado el objeto o instancia de Follow a mi BD
    db.add(new_follow)
    db.commit()
    
    return {"message": f"Has comenzado a seguir a: {search_follower.username}"}
    
@app.delete("/users/{username}/follow")
async def unfowllow_to_user(username: str, 
                            current_user: UserModel = Depends(auth.get_current_user), 
                            db:Session = Depends(get_db)):
    """
    Permite dejar de seguir a un usuario.
    
    Elimina la relación de seguimiento entre el usuario autenticado
    y el usuario especificado.
    
    Args:
        username (str): Nombre de usuario a dejar de seguir
        current_user (UserModel): Usuario autenticado
        db (Session): Sesión de base de datos inyectada
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: 
            - 400 Bad Request si el usuario no existe
            - 400 Bad Request si no se sigue al usuario
            
    Note:
        Solo se puede dejar de seguir a usuarios que ya se siguen.
    """
    
    #Verifico si el usuario existe
    user_to_unfollow = db.query(UserModel).filter(UserModel.username == username).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Error, el usuario no se encuentra")
    
    
    #Busco la relación de seguimiento existente
    unfollow_user = db.query(Follow).filter(Follow.follower_id == current_user.id,
                                            Follow.followed_id == user_to_unfollow.id
                                            ).first()
    if not unfollow_user: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error, no sigues a este usuario")
    
    #Elimino la relación de seguimiento.
    db.delete(unfollow_user)
    db.commit()
    
    return {"mensaje": "Ya no sigues a este usuario"}
    

# ========================================
# CONFIGURACIÓN DE EJECUCIÓN
# ========================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

    
    
