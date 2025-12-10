from typing import List, Tuple
from datetime import datetime, timedelta
from passlib.context import CryptContext  # pip install passlib[bcrypt]

from models.Producto import Producto, DVD
from models.Usuario import Usuario, Socio, Bibliotecario
from models.Prestamo import Prestamo

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Biblioteca:
    """Clase que centraliza la gestión de usuarios, productos y préstamos para la API REST."""

    def __init__(self):
        self.usuarios: List[Usuario] = []
        self.productos: List[Producto] = []
        self.prestamos: List[Prestamo] = []

    # ==================== USUARIOS ====================

    def registrar_usuario(self, tipo: str, nombre: str, email: str, edad: int, 
                          contrasena: str, numero_empleado: str = None, turno: str = None) -> Usuario:
        """Registra un nuevo usuario hasheando su contraseña."""
        
        # Validaciones básicas
        if not nombre or not email or edad is None or not contrasena:
            raise ValueError("Faltan campos obligatorios (nombre, email, edad, contraseña).")

        # Comprobar duplicados
        for u in self.usuarios:
            if u.email == email:
                raise ValueError(f"Ya existe un usuario con el correo {email}.")

        # Hashear contraseña
        contrasena_hash = pwd_context.hash(contrasena)

        if tipo.lower() == "socio":
            usuario = Socio(nombre, email, edad, contrasena_hash)
        elif tipo.lower() == "bibliotecario":
            if not numero_empleado or not turno:
                raise ValueError("Faltan número de empleado o turno para bibliotecario.")
            usuario = Bibliotecario(nombre, email, edad, contrasena_hash, numero_empleado, turno)
        else:
            raise ValueError("Tipo de usuario no válido. Debe ser 'socio' o 'bibliotecario'.")

        self.usuarios.append(usuario)
        return usuario

    def autenticar_usuario(self, email: str, contrasena_plana: str) -> Usuario | None:
        """Verifica credenciales para el login."""
        for u in self.usuarios:
            # Verificamos hash
            if pwd_context.verify(contrasena_plana, u.contrasena):
                return u
        return None

    def dar_de_baja_usuario(self, usuario_id: str):
        """Elimina un usuario por ID."""
        for u in self.usuarios:
            if u.id == usuario_id:
                self.usuarios.remove(u)
                return True # Éxito
        return False # No encontrado

    def renovar_socio(self, socio_id: str):
        """Renueva suscripción de socio (lógica de negocio)."""
        for u in self.usuarios:
            if isinstance(u, Socio) and u.id == socio_id:
                u.renovar_suscripcion()
                return u # Devolvemos el usuario actualizado
        raise ValueError("Socio no encontrado")

    def buscar_usuario_por_id(self, usuario_id: str):
        for u in self.usuarios:
            if u.id == usuario_id:
                return u
        return None

    def listar_usuarios(self):
        return self.usuarios

    # ==================== PRODUCTOS ====================

    def añadir_producto(self, producto: Producto):
        """Añade producto o suma stock si ya existe."""
        if not producto.titulo or not producto.autor:
            raise ValueError("El producto debe tener título y autor")

        for p in self.productos:
            # Comprobamos por título, autor y tipo
            if (p.titulo.lower() == producto.titulo.lower() and 
                p.autor.lower() == producto.autor.lower() and 
                type(p) == type(producto)):
                
                p.cantidad += producto.cantidad
                return p # Devolvemos el producto actualizado

        self.productos.append(producto)
        return producto

    def eliminar_producto(self, producto_id: str):
        for p in self.productos:
            if p.id == producto_id:
                self.productos.remove(p)
                return True
        return False

    def ajustar_stock(self, producto_id: str, cantidad: int):
        for p in self.productos:
            if p.id == producto_id:
                if cantidad < 0 and abs(cantidad) > p.cantidad:
                     raise ValueError("No hay suficiente stock para reducir")
                p.cantidad += cantidad
                return p
        raise ValueError("Producto no encontrado")

    def listar_productos(self):
        """Devuelve la lista pura de productos."""
        return self.productos

    def buscar_producto_por_id(self, producto_id: str):
        for p in self.productos:
            if p.id == producto_id:
                return p
        return None
    
    def buscar_productos_por_titulo(self, titulo: str):
        encontrados = []
        for p in self.productos:
            if titulo.lower() in p.titulo.lower():
                encontrados.append(p)
        return encontrados

    # ==================== PRÉSTAMOS ====================

    def registrar_prestamo(self, usuario_id: str, items: List[Tuple[Producto, int]], dias: int = 14):
        """Crea préstamo validando reglas de negocio."""
        usuario = self.buscar_usuario_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado.")

        if isinstance(usuario, Socio) and usuario.fecha_renovacion < datetime.now():
            raise ValueError(f"La suscripción de {usuario.nombre} ha expirado.")

        productos_validos = []

        for prod, cant in items:
            if cant <= 0: continue
            
            # Validación Stock
            if not prod.esta_disponible(cant):
                raise ValueError(f"Sin stock para '{prod.titulo}'.")

            # Validación Edad (DVD)
            if isinstance(prod, DVD) and isinstance(usuario, Socio):
                try:
                    edad_min = int(prod.clasificacion.lstrip("+"))
                    if usuario.edad < edad_min:
                        raise ValueError(f"Edad insuficiente para '{prod.titulo}' (+{edad_min}).")
                except ValueError:
                    pass

            productos_validos.append((prod, cant))

        if not productos_validos:
            raise ValueError("No hay productos válidos para el préstamo.")

        prestamo = Prestamo(usuario, productos_validos, dias)
        self.prestamos.append(prestamo)

        # Restar stock
        for prod, cant in productos_validos:
            prod.actualizar_stock(prod.cantidad - cant)

        return prestamo

    def marcar_devuelto(self, prestamo_id: str):
        for prestamo in self.prestamos:
            if prestamo.id == prestamo_id:
                try:
                    mensaje = prestamo.registrar_devolucion() # Esto suma el stock
                    return mensaje
                except Exception as e:
                    return str(e)
        raise ValueError("Préstamo no encontrado")

    def ampliar_prestamo_socio(self, prestamo_id: str, dias: int):
        for prestamo in self.prestamos:
            if prestamo.id == prestamo_id:
                prestamo.ampliar_prestamo(dias)
                return prestamo
        raise ValueError("Préstamo no encontrado")

    def listar_prestamos_por_usuario(self, usuario_id: str):
        """Devuelve lista de préstamos de un usuario."""
        resultado = []
        for p in self.prestamos:
            if p.socio.id == usuario_id:
                resultado.append(p)
        return resultado
