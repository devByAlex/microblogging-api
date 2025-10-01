"""
Módulo de autenticación y autorización para la API de microblogging.

Este módulo maneja:
- Hashing y verificación de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Autenticación de usuarios mediante dependencias de FastAPI
- Configuración de esquemas OAuth2
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User as UserModel    
import bcrypt
import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

# Configuración del esquema OAuth2 para autenticación con tokens Bearer
# tokenUrl="login" especifica la URL donde los clientes pueden obtener tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Carga las variables de entorno
load_dotenv()

# Configuración de JWT desde variables de entorno con valores por defecto
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de una contraseña utilizando bcrypt.
    
    Toma una contraseña en texto plano y la convierte en un hash
    seguro utilizando bcrypt con salt automático. El hash resultante
    puede ser almacenado de forma segura en la base de datos.
    
    Args:
        password (str): Contraseña en texto plano a hashear
        
    Returns:
        str: Hash de la contraseña codificado en UTF-8
        
    Note:
        bcrypt.gensalt() genera automáticamente un salt único
        para cada contraseña, aumentando la seguridad.
    """
    # Codifico la contraseña a bytes
    encoded_password = password.encode('utf-8')
    
    # Genera el hash con salt automático
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    
    # Retorna el hash decodificado a string
    return hashed_password.decode('utf-8')
    
def verify_password(password: str, hashed_passowrd: str) -> bool: 
    """
    Verifica si una contraseña coincide con su hash.
    
    Compara una contraseña en texto plano con su hash almacenado
    utilizando bcrypt para determinar si coinciden.
    
    Args:
        password (str): Contraseña en texto plano a verificar
        hashed_password (str): Hash almacenado de la contraseña
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
        
    Note:
        bcrypt.checkpw() maneja automáticamente la extracción del salt
        del hash y realiza la comparación segura.
    """
    # Codifica ambas contraseñas a bytes
    encoded_password = password.encode('utf-8')
    encoded_hashed_password = hashed_passowrd.encode('utf-8')
    
    # Verifica la contraseña usando bcrypt
    return bcrypt.checkpw(encoded_password, encoded_hashed_password)

#----------- FUNCIÓN CREACIÓN DEL TOKEN -----------
def create_access_token(data: dict):
    """
    Crea un token de acceso JWT firmado.
    
    Genera un token JWT que contiene la información del usuario
    y una fecha de expiración. El token está firmado con la clave
    secreta del servidor.
    
    Args:
        data (dict): Datos a incluir en el payload del token.
                    Típicamente contiene {"sub": username}
                    
    Returns:
        str: Token JWT firmado codificado como string
        
    Note:
        El token incluye automáticamente un campo "exp" (expiration)
        basado en ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    # Copia los datos del usuario para el token
    to_encode= data.copy()
    
    # Calculo la fecha de expiración
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update ({"exp": expire})
    
    #Uso la libreria jose.jwt para firmar el token con la clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

#------------- FUNCIÓN QUE VERIFICARÁ EL TOKEN DE ACCESO -------------
def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)): 
    """
    Dependencia de FastAPI para obtener el usuario actual autenticado.
    
    Esta función se utiliza como dependencia en endpoints protegidos.
    Decodifica y valida el token JWT, luego busca y retorna el usuario
    correspondiente de la base de datos.
    
    Args:
        token (str): Token JWT obtenido del header Authorization
        db (Session): Sesión de base de datos inyectada como dependencia
        
    Returns:
        UserModel: Objeto del usuario autenticado
        
    Raises:
        HTTPException: 401 Unauthorized si:
            - El token es inválido o ha expirado
            - El token no contiene un username válido  
            - El usuario no existe en la base de datos
            
    Note:
        Esta función se ejecuta automáticamente en endpoints que la
        incluyen como dependencia, proporcionando autenticación automática.
    """
    # Preparo la excepción para credenciales inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate:" "Bearer"},
    )
    
    try:
       # Decodifica el token JWT
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       # Obtengo el username del payload del token
       username: str = payload.get("sub")
       if username is None:
            # Token inválido, expirado, o malformado
            raise credentials_exception
    except JWTError:
        # Si la decodificación falla (token expirado, inválido, etc.), levanto la excepción
        raise credentials_exception
       
    # Valido al usuario
    # Busco al usuario en la base de datos usando el username del payload
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        # Si el usuario no existe en la base de datos, levanto la excepción
        raise credentials_exception
    
    # Si todo es correcto, devuelvo el objeto de usuario de la base de datos
    return user