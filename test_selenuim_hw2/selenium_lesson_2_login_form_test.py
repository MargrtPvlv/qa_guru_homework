import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class TestLoginForm:
    URL = "https://qa-guru.github.io/one-page-form/login.html"

    LOGIN_FIELD = (By.ID, "login-input")
    PASSWORD_FIELD = (By.ID, "password-input")
    LOGIN_BUTTON = (By.ID, "submit-button")
    LOGOUT_BUTTON = (By.ID, "logout-button")
    WELCOME_MESSAGE = (By.ID, "welcome-message")
    ERROR_MESSAGE = (By.ID, "error-message")

    @pytest.fixture(scope="function")
    def setup(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.URL)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 5)
        yield
        self.driver.quit()

    def field_login(self, login):
        self.driver.find_element(*self.LOGIN_FIELD).send_keys(login)

    def field_password(self, password):
        self.driver.find_element(*self.PASSWORD_FIELD).send_keys(password)

    def login_button(self):
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def logout_button(self):
        self.driver.find_element(*self.LOGOUT_BUTTON).click()

    def welcome_message_text(self):
        self.wait.until(ec.visibility_of_element_located(self.WELCOME_MESSAGE))
        return self.driver.find_element(*self.WELCOME_MESSAGE).text

    def error_message_text(self):
        self.wait.until(ec.visibility_of_element_located(self.ERROR_MESSAGE))
        return self.driver.find_element(*self.ERROR_MESSAGE).text

    @pytest.mark.parametrize("login, password, expected", [
        ("user1", "password1", f"Welcome, user1!")
    ])
    def test_valid_data_login(self, login, password, expected):
        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.welcome_message_text() == expected

    @pytest.mark.parametrize("login, password, expected", [
        ("user2", "password1", "Wrong login or password"),
        ("user1", "password2", "Wrong login or password"),
    ])
    def test_invalid_login(self, login, password, expected):
        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.error_message_text() == expected

    def test_empty_fields(self):
        self.login_button()
        assert self.error_message_text() == "Login and password are required (minimum 3 and 6 characters)"

    def test_invalid_password(self):
        login = "user1"
        password = "password2"

        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.error_message_text() == "Wrong login or password"


    #Тест на логаут
    def test_logout_button(self):
        login = "user1"
        password = "password1"

        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.welcome_message_text() == "Welcome, user1!"

        self.logout_button()

        field_login = self.wait.until(ec.visibility_of_element_located(self.LOGIN_FIELD))
        field_password = self.wait.until(ec.visibility_of_element_located(self.PASSWORD_FIELD))

        assert field_login.get_attribute("value") == ""
        assert field_password.get_attribute("value") == ""


    #Негативные тесты
    #Поле логин должно быть более 3х и менее 100 (допустим) символов включительно
    #Поле пароль должно быть более 6 и менее 100 (допустим) символов включительно
    @pytest.mark.parametrize("login, password, expected", [
        ("lo", "password1", "Login must be at least 3 characters"),
        ("user1", "12345", "Password must be at least 6 characters"),
        ("l" * 101, "password1", "Wrong login or password"),
        ("user1", "p" * 101, "Wrong login or password"),
    ])
    def test_boundary_values(self, login, password, expected):
        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.error_message_text() == expected


    #Тест на sql инъекции
    @pytest.mark.parametrize("login, password, expected", [
        ("admin' --, OR 1=1", "", "Wrong login or password"),
        ("user1", "OR 1=1", "Wrong login or password"),
    ])
    def test_sql_injections(self, login, password, expected):
        self.field_login(login)
        self.field_login(login)
        self.field_password(password)
        self.login_button()

        assert self.error_message_text() == expected
