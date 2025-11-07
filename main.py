from models.Producto import Libro, DVD, CD, Ebook
from models.Usuario import Socio, Bibliotecario
from services.Biblioteca import Biblioteca

# Crear la biblioteca
biblioteca = Biblioteca()

# -------------------- REGISTRO DE USUARIOS --------------------
socio1 = Socio("Ana Pérez", "ana@email.com", 25)
socio2 = Socio("Luis Gómez", "luis@email.com", 12)
socio3 = Socio("Carla Ruiz", "carla@email.com", 30)
socio4 = Socio("Ana Pérez", "ana@email.com", 25)
socio5 = Socio("", "jose@email.com", 34)

bibliotecario = Bibliotecario("Jorge Díaz", "jorge@email.com", 40, "001", "Mañana")

for u in [socio1, socio2, socio3, socio4, socio5, bibliotecario]:
    biblioteca.registrar_usuario(u)

# -------------------- CREACIÓN DE PRODUCTOS --------------------
libro = Libro("1984", "George Orwell", 5, 328, "Distopía", "9780451524935")
dvd = DVD("Matrix", "Hermanas Wachowski", 3, 136, "+16")
cd = CD("Thriller", "Michael Jackson", 4, 42, "Pop", "07464381122")
ebook = Ebook("Python Básico", "Guido van Rossum", 10, "PDF", 5.2)
libro2 = Libro("El Principito", "Antoine de Saint-Exupéry", 2, 96, "Infantil", "9780156012195")
libro3 = Libro("1984", "George Orwell", 1, 328, "Distopía", "9780451524935")
producto_malo = Libro("", "", 1, 23, "Hola", "123")

for p in [libro, dvd, cd, ebook, libro2, libro3, producto_malo]:
    print(biblioteca.añadir_producto(p))

# -------------------- MOSTRAR INVENTARIO --------------------
print("\nInventario inicial:")
biblioteca.listar_productos()

# -------------------- REGISTRAR PRÉSTAMOS --------------------
biblioteca.registrar_prestamo(socio1, [(libro, 1), (dvd, 1)])
biblioteca.registrar_prestamo(socio2, [(dvd, 1), (cd, 1)])  # Debería avisar de edad para DVD +16
biblioteca.registrar_prestamo(socio3, [(ebook, 1), (libro2, 1)])
biblioteca.registrar_prestamo(socio4, [(ebook, 1), (libro3, 1)])
biblioteca.registrar_prestamo(bibliotecario, [(dvd, 1)])  # Bibliotecario no tiene restricción de edad
biblioteca.registrar_prestamo(socio1, [(libro, -1)])

# -------------------- LISTAR PRÉSTAMOS POR USUARIO --------------------
for socio in [socio1, socio2, socio3, socio4, bibliotecario]:
    print(f"\nHistorial de préstamos de {socio.nombre}:")
    biblioteca.listar_prestamos_por_usuario(socio.id)

# -------------------- DEVOLUCIONES --------------------
# Devolver un préstamo
prestamo_a_devolver = biblioteca.prestamos[0].id
print("\nDevolviendo un préstamo:")
print(biblioteca.marcar_devuelto(prestamo_a_devolver))

# Intentar devolver nuevamente el mismo préstamo
print(biblioteca.marcar_devuelto(prestamo_a_devolver))

# -------------------- AMPLIAR PRÉSTAMO --------------------
prestamo_a_ampliar = biblioteca.prestamos[1].id
print("\nAmpliando préstamo:")
print(biblioteca.ampliar_prestamo_socio(prestamo_a_ampliar, 7))

# -------------------- RENOVAR SOCIO --------------------
print("\nRenovando suscripción de socio1:")
print(biblioteca.renovar_socio(socio1.id))

# -------------------- DAR DE BAJA USUARIO --------------------
print("\nDando de baja al socio2:")
print(biblioteca.dar_de_baja_usuario(socio2.id))

# -------------------- AJUSTAR STOCK --------------------
print("\nAjustando stock de libro 1984:")
print(biblioteca.ajustar_stock(libro.id, -2))

# -------------------- BUSCAR PRODUCTO --------------------
print("\nBuscando productos con '1984':")
biblioteca.buscar_producto("1984")
