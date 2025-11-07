import uuid
from datetime import datetime, timedelta

class Usuario:
    """
    Clase base que representa a cualquier persona registrada en la biblioteca.
    """

    def __init__(self, nombre: str, email: str, edad: int):
        """
        :param nombre: Nombre completo del usuario
        :param email: Correo electrónico
        :param edad: Edad del usuario
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.email = email
        self.edad = edad
        self.fecha_ingreso = datetime.now()

    def es_bibliotecario(self):
        """Indica si el usuario es bibliotecario"""
        return False

    def __str__(self):
        return (f"ID: {self.id}\nNombre: {self.nombre}\nEmail: {self.email}\n Edad: {self.edad}\nFecha de ingreso: {self.fecha_ingreso.strftime('%Y-%m-%d %H:%M:%S')}")


class Socio(Usuario):
    """Representa a un lector registrado en la biblioteca."""

    def __init__(self, nombre, email, edad):
        super().__init__(nombre, email, edad)
        self.fecha_renovacion = self.fecha_ingreso + timedelta(days=2*365)  # Renovación automática a 2 años

    def renovar_suscripcion(self):
        """Extiende la validez del carnet por otros 2 años."""
        self.fecha_renovacion += timedelta(days=2*365)

    def __str__(self):
        return (f"{super().__str__()}\nFecha de renovación: {self.fecha_renovacion.strftime('%Y-%m-%d')}")

class Bibliotecario(Usuario):
    """Representa al personal encargado de gestionar la biblioteca."""

    def __init__(self, nombre, email, edad, numero_empleado, turno, activo=True):
        super().__init__(nombre, email, edad)
        self.numero_empleado = numero_empleado
        self.turno = turno  # "Mañana" "Tarde"
        self.activo = activo

    def es_bibliotecario(self):
        return True

    def __str__(self):
        return (f"{super().__str__()}\nNúmero empleado: {self.numero_empleado}\nTurno: {self.turno}\nActivo: {self.activo}")


