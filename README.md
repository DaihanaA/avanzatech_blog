Avanzatech Blog
Es una plataforma de blogs, donde puedes crear, leer y editar posts.Tambien puedes dejar comentarios y dar like a los posts de tu preferiencia. 

1. Para comenzar necesitaras clonar este repositorio:
    $git clone https://github.com/DaihanaA/avanzatech_blog.git

2. Crea tu base de datos:
     CREATE DATABASE avanzatech_blog;
  y configura el archivo se settings.py:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'avanzatech_blog',
            'USER': '####',
            'PASSWORD': '###',
            'HOST': 'localhost',  # O la IP de tu servidor si no es local
            'PORT': '5432',  # El puerto por defecto de PostgreSQL
        }
    }

3. Configura tu entorno virtual
   python3 venv env
   
4. Incializa tu entorno virtual
   source env/bin/activate
   
5. Instala el archivo de requerimientos con:
   pip install -r requeriments.txt
   (Confirma que tienes instalado pipenv)

6. Realiza las migraciones
   python3 manage.py makemigrations
   python3 manage.py migrate

7. Crea tu superusuario:
  python3 manage.py createsuperuser
(te pedira un nombre, mail y contraseña)

8. Ya puedes correr el programa:
   python3 manage.py runserver

10. Para correr los tests:
    python3 manage.py test posts


Desde el admin site podrás: ('/admin/')
1. Crear los usuarios(estos los maneja User django)
2. Crear Teams (igualmente los maneja Groups django)
3. Asignar un perfil para los usuarios como admin o blogger

Dentro del api/posts podrás:
1. Crear posts con un usuario autenticado ('api/posts/create/)
2. Visualizar los posts con los permisos requeridos ('/api/posts/')
3. Actualizar tus porpios posts o los que pertenezcan a tu equipo('/api/posts/update/')
4. Borrar tus propios posts o los que pertenezcan a tu equipo('/api/posts/delete')

Dentro de api/comments podrás:
1. Crear comentarios en el posts a los que tengas acceso('api/comments/')
2. Lista los comentarios a los que que tengas acceso('/api/comments/<int:post_id>/')
3. Borrar un comentario en un post especifo ('/api/comments/<int:comment_id>/delete/')

Dentro de api/likes podrás:
1. Dar like a los posts a los que tengas acceso('/api/likes/<int:post_id>/')
2. Listar los likes de los posts a los que tengas acceso('/api/likes/')
3. Eliminar un like de un post ('/api/likes/<int:post_id>')



 
 
