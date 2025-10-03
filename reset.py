"""
Script de utilidad para resetear la base de datos en desarrollo.
⚠️ ADVERTENCIA: Este script borra TODA la base de datos.
Solo usar en entorno de desarrollo local.
"""
from app.database import engine, Base 
from sqlalchemy import text 

#Eliminar todas las tablas con CASCADE
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS comments CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS posts CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS follows CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.commit()

#Recrear todas las tablas con la nueva estructra
Base.metadata.create_all(bind=engine)

print("Base de datos reiniciada completamente")