from django.test import TestCase
from .models import User

class UserModelTests(TestCase):

    def test_user_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass'))
