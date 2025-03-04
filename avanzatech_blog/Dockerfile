# Usa una imagen oficial de Python
FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios para instalar dependencias
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código del backend
COPY . .

# Expone el puerto 8000 para el backend de Django
EXPOSE 8000

# Comando para iniciar el servidor con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "avanzatech_blog.wsgi:application"]
