from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import BlogPost, Comment
from rest_framework.test import APIClient
from django.urls import reverse
import random
import string
from rest_framework.test import APITestCase
from rest_framework import status

def generate_unique_username():
    return 'testuser_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

class BlogPostModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title='Test Post', content='This is a test post', author=self.user)
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author.username, 'testuser')

class CommentModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title='Test Post', content='This is a test post', author=self.user)
        self.comment = Comment.objects.create(content='This is a comment', blog_post=self.post, user=self.user)
        
    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'This is a comment')
        self.assertEqual(self.comment.blog_post, self.post)


class PostLikeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')
        self.post = BlogPost.objects.create(title="Test Post", content="This is a test post", author=self.user)

    def test_like_post(self):
        response = self.client.post(reverse('post-like-list', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 201)


class BlogPostPermissionsTest(APITestCase):

    def setUp(self):
        # Create a test user and login
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        # Create a post
        self.post = BlogPost.objects.create(title='Test Post', content='Test content')

    def test_authenticated_post_access(self):
        # Test access to a post for authenticated users
        response = self.client.get(f'/posts/{self.post.id}/')  # Match the URL pattern
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_post_access(self):
        # Test access for the post author
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)