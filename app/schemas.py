from pydantic import BaseModel, EmailStr, SecretStr
from fastapi import FastAPI
from datetime import datetime

# Estos esquemas de Pydantic definen la estructura de los datos
# que se reciben y se envían en la API 
class UserCreate(BaseModel):
    """"
     Esquema para la creación de un nuevo usuario.
    
    Define los campos requeridos para el registro de un usuario en el sistema.
    Utilizado en el endpoint POST /users para validar los datos de entrada.
    
    Attributes:
        username (str): Nombre de usuario único en el sistema
        email (EmailStr): Dirección de correo electrónico válida del usuario
        password (str): Contraseña en texto plano (será hasheada antes del almacenamiento) 
    """
    username : str 
    email: EmailStr #Uso EmailStr para una validación automatica de email
    password: str
    
    class Config:
        from_attributes = True  

class UserResponse(BaseModel):
    """
    Esquema para la respuesta de datos de un usuario.
    
    Devuelve los campos públicos del usuario sin información sensible
    como la contraseña hasheada. Utilizado en respuestas de endpoints
    que devuelven información de usuario.
    
    Attributes:
        id (int): Identificador único del usuario en la base de datos
        username (str): Nombre de usuario único
        email (EmailStr): Dirección de correo electrónico del usuario
        is_active (bool): Indica si la cuenta del usuario está activa
        created_at (datetime): Fecha y hora de creación de la cuenta
    """
    id: int
    username: str
    email: EmailStr 
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class PostCreate(BaseModel): 
    """
    Esquema para la creación de una nueva publicación.
    
    Solo requiere el contenido del post, ya que otros campos como
    el ID, fecha de creación y propietario son generados automáticamente
    por el backend.
    
    Attributes:
        content (str): Contenido de texto de la publicaciónmáticamente por backend
    """
    content:str
    
class UserPostResponse(BaseModel):
    """
    Esquema simplificado para la respuesta de un usuario dentro de una publicación.
    
    Versión reducida del esquema UserResponse para evitar devolver datos
    sensibles como el email cuando se incluye información del propietario
    en las respuestas de publicaciones.
    
    Attributes:
        id (int): Identificador único del usuario
        username (str): Nombre de usuario único
    """
    id: int
    username: str
    
    class Config:
        from_attributes = True  

#Esquema para la respuesta de una publicación: incluye toda la información.
class PostResponse(BaseModel):
    """
Esquema completo para la respuesta de una publicación.
    
    Incluye toda la información relevante de un post junto con
    los datos básicos del propietario. Utilizado en endpoints
    que devuelven información completa de publicaciones.
    
    Attributes:
        id (int): Identificador único de la publicación
        content (str): Contenido de texto de la publicación
        created_at (datetime): Fecha y hora de creación de la publicación
        owner (UserPostResponse): Información básica del propietario de la publicación
    """
    id: int
    content: str
    created_at: datetime
    #Se añade el propietario del post usando el esquema de respuesta del usuario.
    owner: UserPostResponse
    
    class Config:
        from_attributes = True
    
        

     
    