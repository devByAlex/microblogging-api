"""
Configuración de la base de datos para mi API de microblogging.

Desde este módulo manejo la configuración de SQLAlchemy, incluyendo:
- Configuración del motor de base de datos
- Configuración de sesiones
- Clase base para modelos ORM
- Función de dependencia para inyección de sesiones de base de datos
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv

#Carga las variables de entorno del archivo .env
load_dotenv()

#Obtengo la URL de la base de datos desde las variables de entorno
#Formateo esperado: postgresql://user:password@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el motor de SQLAlchemy
# echo=True muestra las consultas SQL en la consola 
engine = create_engine(DATABASE_URL, echo = True)

# Configura el factory de sesiones de SQLAlchemy
# autocommit=False: Las transacciones deben confirmarse manualmente
# autoflush=False: Los objetos no se envían automáticamente a la DB antes de consultas
SessionLocal = sessionmaker(autocommit= False, autoflush= False, bind= engine)

# Clase base para todos los modelos ORM
# Todos los modelos heredarán de esta clase
Base = declarative_base()

def get_db():
    """
    Función de dependencia para obtener una sesión de base de datos.
    
    Esta función la utilizaré como dependencia en FastAPI para inyectar
    una sesión de base de datos en los endpoints. Asegura que la sesión
    se cierre correctamente después de cada petición.
    
    Yields:
        Session: Sesión de SQLAlchemy para interactuar con la base de datos
        
    Note:
        Utiliza un bloque try-finally para garantizar que la sesión
        se cierre incluso si ocurre una excepción.
    """
    
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()