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

        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome()
        self.driver.get(localhost)

    def tearDown(self):
        try:
            self.driver.quit()
        except Exception:
            pass
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
            expected_conditions.url_contains('/home')
        )
        self.assertIn('/home', self.driver.current_url)

        # Navigate to profile page before trying to logout
        self.driver.get(localhost + '/profile')

        # Click logout button by button text if no ID is present
        logout_button = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "button.btn.btn-danger[type='submit']")
            )
        )
        logout_button.click()

        WebDriverWait(self.driver, 15).until(
            expected_conditions.url_contains('/login')
        )
        self.assertIn('/login', self.driver.current_url)

    def test_logout_user(self):
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
            expected_conditions.url_contains('/home')
        )
        self.assertIn('/home', self.driver.current_url)
        
        self.driver.get(localhost + '/profile')
        WebDriverWait(self.driver, 15).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Log Out')]"))
        )

        logout_button = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
            (By.XPATH, "//button[contains(@class, 'btn-danger') and normalize-space()='Log Out']")
            )
        )
        logout_button.click()
        WebDriverWait(self.driver, 15).until(
            expected_conditions.url_contains('/login')
        )
        self.assertIn('/login', self.driver.current_url)

    def test_password_strength(self):
        self.driver.get(localhost + '/register')
        WebDriverWait(self.driver, 15).until(
            expected_conditions.presence_of_element_located((By.NAME, "username"))
        )
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        confirm_input = self.driver.find_element(By.NAME, "confirm_password")
        submit_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='Register']")

        username_input.send_keys("testuser")
        password_input.send_keys("weakpass")
        confirm_input.send_keys("weakpass")
        submit_button.click()

        # If registration fails, URL should not change to /login
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "autoDismissAlert"))
        )
        self.assertNotIn('/login', self.driver.current_url)


    def test_basic_navigation(self):
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
        current_url = self.driver.current_url
        submit_button.click()
        WebDriverWait(self.driver, 15).until(
            expected_conditions.url_changes(current_url)
        )
        WebDriverWait(self.driver, 10).until(
            expected_conditions.url_contains('/home')
        )
        self.assertIn('/home', self.driver.current_url)

        # Click "Get"
        get_header = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "//*[contains(@class, 'clickable-text') and contains(text(), 'Get')]")
            )
        )
        get_header.click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.url_contains('/get')
        )
        self.assertIn('/get', self.driver.current_url)

        # Click "SteamWrapped" (Home)
        home_header = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'clickable-text') and contains(text(), 'SteamWrapped')]")
            )
        )
        home_header.click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.url_contains('/home')
        )
        self.assertIn('/home', self.driver.current_url)

        # Click Profile (username in uppercase)
        profile_header = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "//span[contains(@class, 'clickable-text') and contains(text(), '{}')]".format('TESTUSER'))
            )
        )
        profile_header.click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.url_contains('/profile')
        )
        self.assertIn('/profile', self.driver.current_url)


