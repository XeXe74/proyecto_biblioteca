from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from contextlib import asynccontextmanager

from services.Biblioteca import Biblioteca
from models.Usuario import Usuario, UsuarioCreate, UsuarioRead
from models.Producto import (
    Producto, Libro, DVD, CD, Ebook,
    ProductoCreate, ProductoRead
)
from models.Prestamo import PrestamoCreate, PrestamoRead, PrestamoItemRead

# --- CONFIGURACIÓN JWT ---
SECRET_KEY = "clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="API Gestión de Biblioteca")
biblioteca = Biblioteca() # Instancia única del servicio

# Configuración de seguridad (OAuth2)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- UTILIDADES JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Buscamos el usuario por email manualmente en la lista
    user = next((u for u in biblioteca.usuarios if u.email == email), None)
    if user is None:
        raise credentials_exception
    return user

# ============================= ENDPOINTS AUTENTICACIÓN =============================

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login para obtener el token JWT."""
    user = biblioteca.autenticar_usuario(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "rol": "bibliotecario" if user.es_bibliotecario() else "socio"}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UsuarioRead)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """Ver mis datos (Protegido)."""
    return UsuarioRead(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        edad=current_user.edad,
        es_bibliotecario=current_user.es_bibliotecario()
    )

# ============================= ENDPOINTS USUARIOS =============================

@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def registrar_usuario(usuario: UsuarioCreate):
    try:
        nuevo = biblioteca.registrar_usuario(
            tipo=usuario.tipo,
            nombre=usuario.nombre,
            email=usuario.email,
            edad=usuario.edad,
            contrasena=usuario.contrasena,
            numero_empleado=usuario.numero_empleado,
            turno=usuario.turno
        )
        return UsuarioRead(
            id=nuevo.id, nombre=nuevo.nombre, email=nuevo.email, 
            edad=nuevo.edad, es_bibliotecario=nuevo.es_bibliotecario()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/usuarios", response_model=List[UsuarioRead])
def listar_usuarios():
    usuarios = biblioteca.listar_usuarios()
    return [
        UsuarioRead(id=u.id, nombre=u.nombre, email=u.email, edad=u.edad, es_bibliotecario=u.es_bibliotecario())
        for u in usuarios
    ]
    
@app.delete("/usuarios/{usuario_id}", status_code=204)
def dar_de_baja_usuario(usuario_id: str, current_user: Usuario = Depends(get_current_user)):
    """
    Elimina un usuario del sistema.
    Solo un bibliotecario puede realizar esta acción.
    """
    if not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="Permiso denegado: Solo bibliotecarios pueden eliminar usuarios.")
    
    exito = biblioteca.dar_de_baja_usuario(usuario_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    return

@app.put("/usuarios/{socio_id}/renovar", response_model=UsuarioRead)
def renovar_suscripcion(socio_id: str, current_user: Usuario = Depends(get_current_user)):
    """
    Renueva la suscripción de un socio por 2 años más.
    Solo bibliotecarios pueden hacerlo.
    """
    if not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="Solo bibliotecarios pueden renovar suscripciones.")

    try:
        socio_actualizado = biblioteca.renovar_socio(socio_id)
        return UsuarioRead(
            id=socio_actualizado.id,
            nombre=socio_actualizado.nombre,
            email=socio_actualizado.email,
            edad=socio_actualizado.edad,
            es_bibliotecario=False
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



# ============================= ENDPOINTS PRODUCTOS =============================

def mapear_producto(prod):
    """Auxiliar para convertir objeto Producto a Schema."""
    tipo = "generico"
    extra = {}
    
    if isinstance(prod, Libro): 
        tipo = "libro"; extra = {"num_paginas": prod.num_paginas, "genero": prod.genero, "isbn": prod.isbn}
    elif isinstance(prod, DVD): 
        tipo = "dvd"; extra = {"duracion_min": prod.duracion_min, "clasificacion": prod.clasificacion}
    elif isinstance(prod, CD): 
        tipo = "cd"; extra = {"duracion_total": prod.duracion_total, "genero": prod.genero, "codigo_upc": prod.codigo_upc}
    elif isinstance(prod, Ebook): 
        tipo = "ebook"; extra = {"formato": prod.formato, "tamaño_mb": prod.tamaño_mb}

    return ProductoRead(
        id=prod.id, tipo=tipo, titulo=prod.titulo, autor=prod.autor, cantidad=prod.cantidad,
        **extra # Desempaquetamos los campos extra
    )

@app.get("/productos", response_model=List[ProductoRead])
def listar_productos():
    prods = biblioteca.listar_productos()
    return [mapear_producto(p) for p in prods]

@app.post("/productos", response_model=ProductoRead, status_code=201)
def crear_producto(p: ProductoCreate, current_user: Usuario = Depends(get_current_user)):
    """Solo bibliotecarios pueden añadir productos."""
    if not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="Permiso denegado: Solo bibliotecarios.")
    
    try:
        nuevo_prod = None
        if p.tipo.lower() == "libro":
            nuevo_prod = Libro(p.titulo, p.autor, p.cantidad, p.num_paginas, p.genero, p.isbn)
        elif p.tipo.lower() == "dvd":
            nuevo_prod = DVD(p.titulo, p.autor, p.cantidad, p.duracion_min, p.clasificacion)
        elif p.tipo.lower() == "cd":
            nuevo_prod = CD(p.titulo, p.autor, p.cantidad, p.duracion_total, p.genero, p.codigo_upc)
        elif p.tipo.lower() == "ebook":
            nuevo_prod = Ebook(p.titulo, p.autor, p.cantidad, p.formato, p.tamaño_mb)
        else:
            nuevo_prod = Producto(p.titulo, p.autor, p.cantidad)
            
        biblioteca.añadir_producto(nuevo_prod)
        return mapear_producto(nuevo_prod)
    except Exception as e: # Capturamos cualquier error de validación manual
         raise HTTPException(status_code=400, detail=str(e))
     
@app.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: str, current_user: Usuario = Depends(get_current_user)):
    """
    Elimina un producto del catálogo.
    Solo bibliotecarios.
    """
    if not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="Permiso denegado.")
    
    exito = biblioteca.eliminar_producto(producto_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return

# ============================= ENDPOINTS PRÉSTAMOS =============================

@app.post("/prestamos", response_model=PrestamoRead, status_code=201)
def crear_prestamo(prestamo_data: PrestamoCreate, current_user: Usuario = Depends(get_current_user)):
    """Crea un préstamo. Verifica que seas tú mismo o un bibliotecario."""
    
    # Seguridad: Solo puedes pedir préstamos para ti mismo (salvo que seas bibliotecario)
    if current_user.id != prestamo_data.usuario_id and not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="No puedes crear préstamos para otros usuarios.")

    try:
        # Recuperar objetos producto reales
        items_obj = []
        for item in prestamo_data.items:
            prod = biblioteca.buscar_producto_por_id(item.producto_id)
            if not prod:
                raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")
            items_obj.append((prod, item.cantidad))
            
        nuevo_prestamo = biblioteca.registrar_prestamo(prestamo_data.usuario_id, items_obj, prestamo_data.dias)
        
        # Mapeo de respuesta
        items_res = [
            PrestamoItemRead(producto_id=p.id, titulo=p.titulo, cantidad=c, tipo=type(p).__name__)
            for p, c in nuevo_prestamo.productos
        ]
        
        return PrestamoRead(
            id=nuevo_prestamo.id,
            usuario_id=nuevo_prestamo.socio.id,
            nombre_usuario=nuevo_prestamo.socio.nombre,
            fecha_inicio=nuevo_prestamo.fecha_inicio.strftime('%Y-%m-%d'),
            fecha_devolucion=nuevo_prestamo.fecha_devolucion.strftime('%Y-%m-%d'),
            devuelto=nuevo_prestamo.devuelto,
            items=items_res
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/me/prestamos", response_model=List[PrestamoRead])
def mis_prestamos(current_user: Usuario = Depends(get_current_user)):
    """Ver mis propios préstamos."""
    prestamos = biblioteca.listar_prestamos_por_usuario(current_user.id)
    
    resultado = []
    for p in prestamos:
        items_res = [
            PrestamoItemRead(producto_id=pr.id, titulo=pr.titulo, cantidad=c, tipo=type(pr).__name__)
            for pr, c in p.productos
        ]
        resultado.append(PrestamoRead(
            id=p.id,
            usuario_id=p.socio.id,
            nombre_usuario=p.socio.nombre,
            fecha_inicio=p.fecha_inicio.strftime('%Y-%m-%d'),
            fecha_devolucion=p.fecha_devolucion.strftime('%Y-%m-%d'),
            devuelto=p.devuelto,
            items=items_res
        ))
    return resultado

@app.put("/prestamos/{prestamo_id}/devolver")
def devolver_prestamo(prestamo_id: str, current_user: Usuario = Depends(get_current_user)):
    """
    Marca un préstamo como devuelto y recupera el stock.
    Accesible para el propio usuario o bibliotecarios.
    """

    try:
        mensaje = biblioteca.marcar_devuelto(prestamo_id)
        return {"mensaje": mensaje}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@app.put("/prestamos/{prestamo_id}/ampliar")
def ampliar_prestamo(prestamo_id: str, dias: int, current_user: Usuario = Depends(get_current_user)):
    """
    Amplía la fecha de devolución de un préstamo.
    Query param: ?dias=7
    """
    if not current_user.es_bibliotecario():
        raise HTTPException(status_code=403, detail="Permiso denegado.")

    try:
        prestamo = biblioteca.ampliar_prestamo_socio(prestamo_id, dias)
        return {
            "mensaje": "Préstamo ampliado",
            "nueva_fecha": prestamo.fecha_devolucion.strftime('%Y-%m-%d')
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


