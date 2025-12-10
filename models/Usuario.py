import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

class Usuario:
    """
    Clase base que representa a cualquier persona registrada en la biblioteca.
    """
    def __init__(self, nombre: str, email: str, edad: int, contrasena: str):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.email = email
        self.edad = edad
        self.contrasena = contrasena # Propiedad obligatoria
        self.fecha_ingreso = datetime.now()

    def es_bibliotecario(self):
        """Indica si el usuario es bibliotecario"""
        return False

    def __str__(self):
        return (f"ID: {self.id}\nNombre: {self.nombre}\nEmail: {self.email}\nEdad: {self.edad}\nFecha de ingreso: {self.fecha_ingreso.strftime('%Y-%m-%d %H:%M:%S')}")

class Socio(Usuario):
    """Representa a un lector registrado en la biblioteca."""
    # AÑADIDO: contrasena
    def __init__(self, nombre, email, edad, contrasena):
        # AÑADIDO: contrasena al super()
        super().__init__(nombre, email, edad, contrasena)
        self.fecha_renovacion = self.fecha_ingreso + timedelta(days=2*365) 

    def renovar_suscripcion(self):
        """Extiende la validez del carnet por otros 2 años."""
        self.fecha_renovacion += timedelta(days=2*365)

    def __str__(self):
        return (f"{super().__str__()}\nFecha de renovación: {self.fecha_renovacion.strftime('%Y-%m-%d')}")

class Bibliotecario(Usuario):
    """Representa al personal encargado de gestionar la biblioteca."""
    # AÑADIDO: contrasena
    def __init__(self, nombre, email, edad, contrasena, numero_empleado, turno, activo=True):
        # AÑADIDO: contrasena al super()
        super().__init__(nombre, email, edad, contrasena)
        self.numero_empleado = numero_empleado
        self.turno = turno 
        self.activo = activo

    def es_bibliotecario(self):
        return True

    def __str__(self):
        return (f"{super().__str__()}\nNúmero empleado: {self.numero_empleado}\nTurno: {self.turno}\nActivo: {self.activo}")

# Pydantic modelos (estos estaban bien)

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    edad: int
    contrasena: str
    tipo: str
    numero_empleado: Optional[str] = None
    turno: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Ana Pérez",
                "email": "ana@email.com",
                "edad": 25,
                "contrasena": "claveSegura123",
                "tipo": "socio"
            }
        }

class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    es_bibliotecario: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Ana Pérez",
                "email": "ana@email.com",
                "es_bibliotecario": False
            }
        }
