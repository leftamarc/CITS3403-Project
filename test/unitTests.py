import unittest

from app import create_app, db
from app.config import TestingConfig
from app.models import User 


class BasicTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestingConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()

        return super().setUp()
    
    def test_user_creation(self):
        user = User(username='testuser')
        password = 'testpassword1!'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        return super().tearDown()