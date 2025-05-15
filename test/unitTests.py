import unittest

from app import create_app, db
from app.config import TestingConfig
from app import models 
from app import security


class BasicTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestingConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()

        return super().setUp()
    
    def create_user(self, username, password):
        user = models.User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def test_user_creation(self):
        user = self.create_user('testuser', 'testpassword1!')
        self.assertIsNotNone(user)

    def test_user_login(self):
        self.create_user('testuser2', 'testpassword2!')
        password = 'testpassword2!'

        logged_in_user = models.User.query.filter_by(username='testuser2').first()
        self.assertIsNotNone(logged_in_user)
        self.assertFalse(logged_in_user.check_password(password + 'willywonka'))
        self.assertTrue(logged_in_user.check_password(password))

    def test_password_hashing(self):
        user = models.User(username='anotheruser')
        user.set_password('securepassword1!')
        self.assertTrue(user.check_password('securepassword1!'))
        self.assertFalse(user.check_password('wrongpassword1!'))

    def test_user_query(self):
        user = models.User(username='queryuser')
        user.set_password('password1!')
        db.session.add(user)
        db.session.commit()
        queried = models.User.query.filter_by(username='queryuser').first()
        self.assertIsNotNone(queried)
        self.assertEqual(queried.username, 'queryuser')

    def test_password_strength(self):
        self.assertTrue(security.is_strong_password('StrongPass1!'))
        self.assertFalse(security.is_strong_password('weakpass'))
        self.assertFalse(security.is_strong_password('12345678'))
        self.assertFalse(security.is_strong_password('NoSpecialChar1'))
        self.assertFalse(security.is_strong_password('!@#$%^&*()'))


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        return super().tearDown()