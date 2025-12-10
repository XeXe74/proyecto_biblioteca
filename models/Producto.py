import uuid
from typing import Optional
from pydantic import BaseModel

class Producto:
    """Clase base para todos los productos de la biblioteca."""

    def __init__(self, titulo: str, autor: str, cantidad: int):
        """
        :param titulo: Título del producto
        :param autor: Autor o responsable del producto
        :param cantidad: Cantidad disponible en stock
        """
        self.id = str(uuid.uuid4())
        self.titulo = titulo
        self.autor = autor
        self.cantidad = cantidad

    def esta_disponible(self, cantidad_solicitada: int = 1) -> bool:
        """Devuelve True si hay suficientes ejemplares disponibles."""
        return self.cantidad >= cantidad_solicitada

    def actualizar_stock(self, cantidad_nueva: int):
        """Actualiza la cantidad disponible del producto."""
        self.cantidad = cantidad_nueva

    def __str__(self) -> str:
        return f"Título: {self.titulo}\nAutor: {self.autor}\nCantidad disponible: {self.cantidad}"


class Libro(Producto):
    """Clase que representa un libro."""

    def __init__(self, titulo: str, autor: str, cantidad: int, num_paginas: int, genero: str, isbn: str):
        super().__init__(titulo, autor, cantidad)
        self.num_paginas = num_paginas
        self.genero = genero
        self.isbn = isbn

    def __str__(self) -> str:
        return (f"{super().__str__()}\nPáginas: {self.num_paginas}\nGénero: {self.genero}\nISBN: {self.isbn}")


class DVD(Producto):
    """Clase que representa un DVD."""

    def __init__(self, titulo: str, autor: str, cantidad: int, duracion_min: int, clasificacion: str):
        super().__init__(titulo, autor, cantidad)
        self.duracion_min = duracion_min
        self.clasificacion = clasificacion

    def __str__(self) -> str:
        return (f"{super().__str__()}\nDuración: {self.duracion_min} min\nClasificación: {self.clasificacion}")


class CD(Producto):
    """Clase que representa materiales de audio como un CD o un audiolibro."""

    def __init__(self, titulo: str, autor: str, cantidad: int, duracion_total: int, genero: str, codigo_upc: str):
        super().__init__(titulo, autor, cantidad)
        self.duracion_total = duracion_total
        self.genero = genero
        self.codigo_upc = codigo_upc

    def __str__(self) -> str:
        return (f"{super().__str__()}\nDuración total: {self.duracion_total} min\nGénero: {self.genero}\nCódigo UPC: {self.codigo_upc}")


class Ebook(Producto):
    """Clase que representa un libro digital."""

    def __init__(self, titulo: str, autor: str, cantidad: int, formato: str, tamaño_mb: float):
        super().__init__(titulo, autor, cantidad)
        self.formato = formato
        self.tamaño_mb = tamaño_mb

    def __str__(self) -> str:
        return (f"{super().__str__()}\nFormato: {self.formato}\nTamaño: {self.tamaño_mb} MB")

# Pydantic modelos

class ProductoCreate(BaseModel):
    tipo: str # "libro", "dvd", "cd", "ebook"
    titulo: str
    autor: str
    cantidad: int
    
    # Campos opcionales según el tipo
    num_paginas: Optional[int] = None
    genero: Optional[str] = None
    isbn: Optional[str] = None
    
    duracion_min: Optional[int] = None # Para DVD
    clasificacion: Optional[str] = None # Para DVD
    
    duracion_total: Optional[int] = None # Para CD
    codigo_upc: Optional[str] = None # Para CD
    
    formato: Optional[str] = None # Para Ebook
    tamaño_mb: Optional[float] = None # Para Ebook

    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "libro",
                "titulo": "1984",
                "autor": "George Orwell",
                "cantidad": 5,
                "num_paginas": 328,
                "genero": "Distopía",
                "isbn": "9780451524935"
            }
        }

class ProductoRead(BaseModel):
    id: str
    tipo: str
    titulo: str
    autor: str
    cantidad: int
    
    # Devolvemos también los detalles opcionales para que se vean en el JSON
    num_paginas: Optional[int] = None
    genero: Optional[str] = None
    isbn: Optional[str] = None
    duracion_min: Optional[int] = None
    clasificacion: Optional[str] = None
    duracion_total: Optional[int] = None
    codigo_upc: Optional[str] = None
    formato: Optional[str] = None
    tamaño_mb: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-123",
                "tipo": "libro",
                "titulo": "1984",
                "autor": "George Orwell",
                "cantidad": 5,
                "genero": "Distopía"
            }
        }