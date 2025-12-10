import uuid
from datetime import datetime, timedelta
from typing import List, Tuple
from pydantic import BaseModel
from typing import Optional

from models.Producto import Producto
from models.Usuario import Usuario, Socio


class Prestamo:
    """Representa un préstamo de productos a un socio de la biblioteca."""

    def __init__(self, usuario: Usuario, productos: List[Tuple[Producto, int]], dias_prestamo: int = 14):
        """
        :param socio: Socio que realiza el préstamo
        :param productos: Lista de tuplas (Producto, cantidad)
        :param dias_prestamo: Duración en días del préstamo (por defecto 14)
        """
        self.id = str(uuid.uuid4())
        self.socio = usuario
        self.productos = productos
        self.fecha_inicio = datetime.now()
        self.fecha_devolucion = self.fecha_inicio + timedelta(days=dias_prestamo)
        self.devuelto = False  # Indica si el préstamo ya se ha completado

    def esta_vigente(self) -> bool:
        """Devuelve True si el préstamo aún está vigente."""
        if self.devuelto:
            return False
        return datetime.now() <= self.fecha_devolucion

    def registrar_devolucion(self):
        """Marca el préstamo como devuelto y actualiza el stock de los productos."""
        if self.devuelto:
            return "El prestamo ya había sido devuelto"
        self.devuelto = True

        for producto, cantidad in self.productos:
            producto.actualizar_stock(producto.cantidad + cantidad)

        return f"Préstamo de {self.socio.nombre} devuelto correctamente."

    def ampliar_prestamo(self, dias_extra: int):
        """Amplía la fecha de devolución del préstamo."""
        if self.devuelto:
            raise ValueError("No se puede ampliar un préstamo ya devuelto.")
        self.fecha_devolucion += timedelta(days=dias_extra)

    def __str__(self) -> str:
        productos_str = ""
        for producto, cantidad in self.productos:
            productos_str += f"  - {producto.titulo} x {cantidad}\n"

        return (f"ID: {self.id}\nSocio: {self.socio.nombre}\n"
                f"Fecha de inicio: {self.fecha_inicio.strftime('%Y-%m-%d')}\n"
                f"Fecha de devolución: {self.fecha_devolucion.strftime('%Y-%m-%d')}\n"
                f"Productos:\n{productos_str}"
                f"Devuelto: {self.devuelto}")
        
class PrestamoItemCreate(BaseModel):
    producto_id: str
    cantidad: int

class PrestamoCreate(BaseModel):
    usuario_id: str
    items: List[PrestamoItemCreate]
    dias: int = 14

    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": "id-del-socio-123",
                "items": [
                    {"producto_id": "id-del-libro-1984", "cantidad": 1},
                    {"producto_id": "id-del-dvd-matrix", "cantidad": 1}
                ],
                "dias": 14
            }
        }

class PrestamoItemRead(BaseModel):
    producto_id: str
    titulo: str
    cantidad: int
    tipo: str

class PrestamoRead(BaseModel):
    id: str
    usuario_id: str
    nombre_usuario: str
    fecha_inicio: str
    fecha_devolucion: str
    devuelto: bool
    items: List[PrestamoItemRead]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "prestamo-999",
                "usuario_id": "socio-123",
                "nombre_usuario": "Ana Pérez",
                "fecha_inicio": "2025-12-10",
                "fecha_devolucion": "2025-12-24",
                "devuelto": False,
                "items": [
                    {"producto_id": "p1", "titulo": "1984", "cantidad": 1, "tipo": "Libro"}
                ]
            }
        }
