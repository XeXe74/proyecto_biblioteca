from typing import List
from datetime import datetime, timedelta
from models.Producto import Producto, DVD
from models.Usuario import Usuario, Socio, Bibliotecario
from models.Prestamo import Prestamo


class Biblioteca:
    """Clase que centraliza la gestión de usuarios, productos y préstamos."""

    def __init__(self):
        self.usuarios: List[Usuario] = []
        self.productos: List[Producto] = []
        self.prestamos: List[Prestamo] = []

    # -------------------- USUARIOS --------------------
    def registrar_usuario(self, usuario: Usuario):
        """
        Registra un usuario existente en la biblioteca.
        """
        # Comprobar campos vacíos
        if not usuario.nombre or not usuario.email or usuario.edad is None:
            print("Todos los campos obligatorios del usuario deben completarse (nombre, email, edad).")
            return None

        # Comprobar duplicados por correo
        for u in self.usuarios:
            if u.email == usuario.email:
                print(f"Ya existe un usuario con el correo {usuario.email}.")
                return None

        # Añadir usuario
        self.usuarios.append(usuario)
        #print(f"Usuario {usuario.nombre} registrado correctamente.")
        return usuario

    def dar_de_baja_usuario(self, usuario_id: str):
        """Elimina un usuario existente."""
        for u in self.usuarios:
            if u.id == usuario_id:
                self.usuarios.remove(u)
                return f"Usuario {u.nombre} eliminado correctamente."

        return "Usuario no encontrado."

    def renovar_socio(self, socio_id: str):
        """Renueva la fecha de validez de un socio sumando 2 años."""
        for u in self.usuarios:
            if isinstance(u, Socio) and u.id == socio_id:
                u.renovar_suscripcion()
                return f"Suscripción de {u.nombre} renovada hasta {u.fecha_renovacion}"

        return "Socio no encontrado."

    def ampliar_fecha_renovacion(self, socio_id: str, dias: int):
        """Permite extender manualmente la fecha de renovación de un socio."""
        for u in self.usuarios:
            if isinstance(u, Socio) and u.id == socio_id:
                u.fecha_renovacion += timedelta(days=dias)
                return f"Fecha de renovación de {u.nombre} ampliada hasta {u.fecha_renovacion}"

        return "Socio no encontrado."

    # -------------------- PRODUCTOS --------------------
    def añadir_producto(self, producto: Producto):
        if not producto.titulo or not producto.autor:
            return "Error: el producto debe tener título y autor"

        for p in self.productos:
            if p.titulo.lower() == producto.titulo.lower() and p.autor.lower() == producto.autor.lower():
                p.cantidad += producto.cantidad
                return f"Stock actualizado para {p.titulo}"

        self.productos.append(producto)

        return f"Producto {producto.titulo} añadido al inventario"

    def eliminar_producto(self, producto_id: str):
        """Elimina un producto del inventario por su ID."""
        for p in self.productos:
            if p.id == producto_id:
                self.productos.remove(p)
                return f"Producto {p.titulo} eliminado correctamente."

        return "Producto no encontrado."

    def ajustar_stock(self, producto_id: str, cantidad: int):
        """Función que elimina cierta cantidad de stock de un producto"""
        for p in self.productos:
            if p.id == producto_id:
                if cantidad > p.cantidad:
                    return "No hay suficiente stock para ajustar"
                p.cantidad += cantidad
                return f"Stock ajustado, quedan {p.cantidad} ejemplares"

        return "Producto no encontrado"

    def listar_productos(self):
        """Lista los productos agrupados por tipo."""
        categorias = {}

        for p in self.productos:
            tipo = type(p).__name__
            categorias.setdefault(tipo, []).append(p)

        for tipo, lista in categorias.items():
            print(f"\n--- {tipo}s ---")
            for prod in lista:
                print(prod)
                print("---")

    def buscar_producto(self, titulo: str):
        """Busca productos por título."""
        encontrados = []
        for p in self.productos:
            if titulo.lower() in p.titulo.lower():
                encontrados.append(p)

        if not encontrados:
            print("No se encontraron productos con ese título.")

        for prod in encontrados:
            print(prod)
            print("---")

        return encontrados

    # -------------------- PRÉSTAMOS --------------------
    def registrar_prestamo(self, usuario: Usuario, productos: List[tuple[Producto, int]], dias: int = 14):
        """Crea un préstamo y actualiza el stock de los productos prestados."""

        productos_validos = []

        if usuario not in self.usuarios:
            print(f"El usuario {usuario.nombre} no está registrado en la biblioteca. No se puede crear el préstamo.")
            return None

        if isinstance(usuario, Socio) and usuario.fecha_renovacion < datetime.now():
            print(f"La suscripción de {usuario.nombre} ha expirado. No puede realizar préstamos.")
            return None

        # Verificar disponibilidad
        for prod, cant in productos:
            if cant <= 0:
                print(f"La cantidad para {prod.titulo} debe ser mayor que 0. Se omitirá este producto.")
                continue

            if not prod.esta_disponible(cant):
                print(f"No hay suficiente stock de {prod.titulo}. Se omitirá este producto.")
                continue

            # Validación de edad solo para DVDs
            if isinstance(prod, DVD) and isinstance(usuario, Socio):
                edad_min = int(prod.clasificacion.lstrip("+"))
                if usuario.edad < edad_min:
                    print(f"{usuario.nombre} no tiene la edad mínima para alquilar {prod.titulo}. Se omitirá este producto.")
                    continue  # Saltar este producto

            productos_validos.append((prod, cant))

        if not productos_validos:
            print(f"No se pudo crear el préstamo para {usuario.nombre}: ningún producto disponible o válido.")
            return None

        # Crear el préstamo
        prestamo = Prestamo(usuario, productos_validos, dias)
        self.prestamos.append(prestamo)

        # Actualizar stock
        for prod, cant in productos:
            prod.actualizar_stock(prod.cantidad - cant)

        return prestamo

    def marcar_devuelto(self, prestamo_id: str):
        """Marca un préstamo como devuelto y recupera el stock."""
        for prestamo in self.prestamos:
            if prestamo.id == prestamo_id:
                mensaje = prestamo.registrar_devolucion()
                return mensaje
        return "Préstamo no encontrado."

    def ampliar_prestamo_socio(self, prestamo_id: str, dias: int):
        """Amplía la fecha de devolución de un préstamo."""
        for prestamo in self.prestamos:
            if prestamo.id == prestamo_id:
                prestamo.ampliar_prestamo(dias)
                return f"Préstamo de {prestamo.socio.nombre} ampliado hasta {prestamo.fecha_devolucion}"
        return "Préstamo no encontrado."

    def listar_prestamos_por_usuario(self, usuario_id):
        """Lista todos los préstamos de un usuario, ordenados por fecha."""
        prestamos_usuario = []

        usuario_registrado = next((u for u in self.usuarios if u.id == usuario_id), None)

        if not usuario_registrado:
            print("El usuario no está registrado en la biblioteca.")
            return

        for prestamo in self.prestamos:
            if prestamo.socio.id == usuario_id:
                prestamos_usuario.append(prestamo)

        if not prestamos_usuario:
            print("El usuario no tiene préstamos.")
            return

        # Ordenamos por fecha de inicio
        prestamos_usuario.sort(key=lambda p: p.fecha_inicio)

        for p in prestamos_usuario:
            print(p)
            print("---")
