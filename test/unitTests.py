import unittest

from app import create_app
from app.config import TestingConfig 


class UnitTests(unittest.TestCase):
    def Setup(self):
        testApp = create_app(TestingConfig)
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()