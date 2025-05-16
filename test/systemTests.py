import threading
import unittest
import time
import os
from app import create_app, db
from app.config import TestingConfig
from app import models 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

localhost = 'http://127.0.1:5000'

class SystemTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestingConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()

        def run_app():
            testApp.run()

        self.server_thread = threading.Thread(target=run_app)
        self.server_thread.daemon = True
        self.server_thread.start()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(localhost)

    def tearDown(self):
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists('test.db'):
            os.remove('test.db')
        return super().tearDown()

    def create_user(self, username, password):
        user = models.User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def test_create_user(self):
        self.driver.get(localhost + '/register')
        WebDriverWait(self.driver, 15).until(
            expected_conditions.presence_of_element_located((By.NAME, "username"))
        )
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        confirm_input = self.driver.find_element(By.NAME, "confirm_password")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys("testuser")
        password_input.send_keys("testpassword1!")
        confirm_input.send_keys("testpassword1!")
        submit_button.click()

        WebDriverWait(self.driver, 15).until(
            expected_conditions.url_changes('/login')
        )

        WebDriverWait(self.driver, 15).until(
            expected_conditions.presence_of_element_located((By.ID, "loginBtn"))
        )

        self.assertIn('/login', self.driver.current_url)

    def test_login_user(self):
        self.create_user('testuser', 'testpassword1!')

        self.driver.get(localhost + '/login')
        WebDriverWait(self.driver, 15).until(
            expected_conditions.presence_of_element_located((By.ID, "username"))
        )

        username_input = self.driver.find_element(By.ID, "username")
        password_input = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "loginBtn")

        username_input.send_keys("testuser")
        password_input.send_keys("testpassword1!")
        submit_button.click()
        
        WebDriverWait(self.driver, 15).until(
            expected_conditions.url_changes(localhost + '/home')
        )

        self.assertIn('/home', self.driver.current_url)

    