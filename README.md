# AvanzaTech Blog  
**AvanzaTech Blog** is a blogging platform where you can create, read, edit and delete posts. You can also interact by leaving comments and liking posts of your choice.

---

## **Installation and Configuration Guide** **Installation Guide

### **1. Clone this repository**
```bash
    git clone https://github.com/DaihanaA/avanzatech_blog.git
```

### **2. Create the database**
Log into your PostgreSQL environment and run the following command to create the database:
```bash
     CREATE DATABASE avanzatech_blog;
```
Then configure the settings.py file:
```bash
    DATABASES = {
        default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'avanzatech_blog',
            'USER': '####',
            'PASSWORD': '###',
            'HOST': 'localhost', # Or your server IP if not local
            'PORT': '5432', # The default port of PostgreSQL
        }
    }
```
### **3. Set up your virtual environment**
Create a virtual environment to handle project dependencies:
```bash
   python3 -m venv env
```
### **4. Activate the virtual environment**   
```bash
   source env/bin/activate
   ```
### **5. Install the dependencies**  
Make sure you have pip installed, then run:
```bash
   pip install -r requeriments.txt
   ```

### **6. Perform the migrations**  
Apply the migrations to configure the database:

```bash

   python3 manage.py makemigrations
   python3 manage.py migrate
```
### **7. Create a superuser**  
Generate a superuser to administer the site:
```bash
  python3 manage.py createsuperuser
```
You will be prompted to provide a username, email and password.

### **8. Run the tests**
Verify that everything is working correctly by running the project tests:
```bash
    python3 manage.py test posts
```

### **9. Run the server**
Start the development server:
```bash
   python3 manage.py runserver
```

## Functions of the Administration Panel (/admin/)
From the Admin Site, you can:

### 1. Manage users: 
Create and modify users (managed by the Django user model).
### 2. Manage teams: 
Create and assign teams to users (managed by groups in Django).
### 3. Assign roles: 
Define whether a user is “admin” or “blogger”.

### API endpoints
### Posts API (/api/posts/)

#### 1.Create posts as an authenticated user: 
    /api/posts/posts/create/

#### 2. Display posts with permissions: 
    /api/posts/
#### 3. Update your posts or your team's posts: 
    /api/posts/update/<int:post_id>/

#### 4. Delete your posts or your team's posts: 
    /api/posts/delete/<int:post_id>/

### Comments API (/api/comments/)
#### 1. Create comments on posts with access: 
    /api/comments/create/<int:post_id>/
#### 2. List comments on a specific post: 
    /api/comments/<int:post_id>/
#### 3.Delete a comment: 
    /api/comments/delete/<int:comment_id>/

### Likes API (/api/likes/)

#### 1.Like posts with access: 
    /api/likes/create/<int:post_id>/
#### 2. List “likes” of posts: 
    /api/likes/
#### 3. Remove a “like” from a post: 
    /api/likes/delete/<int:post_id>/   

