"""
Modelos de base de datos para la API de microblogging.

Este módulo define las tablas y relaciones de la base de datos utilizando
SQLAlchemy ORM. Incluye modelos para usuarios, publicaciones, comentarios
y un sistema de seguimiento entre usuarios.

Models:
    - User: Usuarios del sistema
    - Post: Publicaciones de los usuarios  
    - Comment: Comentarios en las publicaciones
    - Follow: Relaciones de seguimiento entre usuarios
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base



class User(Base): 
    """
    Modelo de usuario del sistema de microblogging.
    
    Representa a los usuarios registrados en la plataforma, incluyendo
    su información básica, credenciales y relaciones con otros usuarios.
    
    Attributes:
        id (int): Identificador único del usuario
        username (str): Nombre de usuario único en el sistema
        email (str): Dirección de correo electrónico única
        hashed_password (str): Contraseña hasheada con bcrypt
        is_active (bool): Estado activo/inactivo del usuario
        created_at (datetime): Fecha y hora de registro
        
    Relationships:
        posts: Lista de publicaciones creadas por el usuario
        following: Lista de usuarios que este usuario sigue
        followers: Lista de usuarios que siguen a este usuario (backref)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) #El nullable indica que no puede contener valores únicos 
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación uno a muchos: Un usuario puede tener múltiples posts
    posts = relationship("Post", back_populates="owner")
   

class Post(Base):
    """
    Modelo de publicación en el microblogging.
    
    Representa las publicaciones/posts creadas por los usuarios,
    incluyendo su contenido, metadatos y análisis de sentimiento.
    
    Attributes:
        id (int): Identificador único de la publicación
        title (str): Título de la publicación
        content (str): Contenido de texto de la publicación
        owner_id (int): ID del usuario propietario (clave foránea)
        created_at (datetime): Fecha y hora de creación
        sentiment (str): Análisis de sentimiento ("Positivo", "Negativo", "Neutral")
        
    Relationships:
        owner: Usuario propietario de la publicación
        comments: Lista de comentarios en esta publicación
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Campo para el análisis automático de sentimiento
    sentiment = Column(String, nullable=True) # Positivo, Negativo, Neutral

    # Relación muchos a uno: Múltiples posts pueden pertenecer a un usuario
    owner = relationship("User", back_populates="posts")
    # Relación uno a muchos: Un post puede tener múltiples comentarios
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    """
    Modelo de comentario en publicaciones.
    
    Representa los comentarios que los usuarios pueden hacer en las
    publicaciones, creando un sistema de interacción básico.
    
    Attributes:
        id (int): Identificador único del comentario
        content (str): Contenido del comentario
        post_id (int): ID de la publicación comentada (clave foránea)
        owner_id (int): ID del usuario que escribió el comentario
        created_at (datetime): Fecha y hora de creación del comentario
        
    Relationships:
        post: Publicación a la que pertenece este comentario
        owner: Usuario que escribió el comentario
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación muchos a uno: Múltiples comentarios pueden pertenecer a un post
    post = relationship("Post", back_populates="comments")
    # Relación simple con User para el propietario del comentario
    owner = relationship("User") 


class Follow(Base):
    """
    Modelo de relación de seguimiento entre usuarios.
    
    Tabla de asociación que registra las relaciones de "seguimiento"
    entre usuarios, permitiendo crear feeds personalizados y redes sociales.
    
    Attributes:
        follower_id (int): ID del usuario que sigue (parte de la clave primaria)
        followed_id (int): ID del usuario seguido (parte de la clave primaria)
        created_at (datetime): Fecha y hora cuando se inició el seguimiento
        
    Relationships:
        follower_user: Usuario que realiza el seguimiento
        followed_user: Usuario que es seguido
        
    Note:
        La clave primaria compuesta (follower_id, followed_id) previene
        que un usuario pueda seguir al mismo usuario múltiples veces.
    """
    __tablename__ = "follows"

    #AL tener una clave primaria compuesta por dos columnas nos aseguramos de que no se pueda seguir a la misma persona 2 veces
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones explícitas con el modelo User
    # Se especifican foreign_keys para evitar ambigüedad en las claves foráneas
    follower_user = relationship(
        "User",
        foreign_keys=[follower_id]
    )
    followed_user = relationship(
        "User",
        foreign_keys=[followed_id]
    )