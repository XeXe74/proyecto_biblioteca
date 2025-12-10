# 1. Imagen base
FROM python:3.10-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiamos primero las dependencias
COPY requirements.txt .

# 4. Instalamos las librerías necesarias
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 5. Copiamos el código al contenedor
COPY . .

# 6. Exponemos el puerto 8000 para poder conectar desde fuera
EXPOSE 8000

# 7. Comando de arranque que lanza uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
