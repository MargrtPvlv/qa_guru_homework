#команда для запуска pytest .\test_login.py -v
import time

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Локаторы элементов формы на странице
LOGIN_INPUT     = (By.ID, "login-input")
PASSWORD_INPUT  = (By.ID, "password-input")
SUBMIT_BUTTON   = (By.ID, "submit-button")
STATUS_MESSAGE  = (By.ID, "error-message")
WELCOME_MESSAGE = (By.ID, "welcome-message")


@pytest.fixture
def driver():
    """Фикстура для инициализации и закрытия браузера."""
    #options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  # Фоновый режим для CI/CD
    #options.add_argument("--window-size=1920,1080")    
    #driver = webdriver.Chrome(options=options)

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(3)

    yield driver

    driver.quit()


# Реализация DDT подхода через параметризацию pytest
@pytest.mark.parametrize(
    "email, password, scenario_type, expected_text",
    [
        # --- ПОЗИТИВНЫЕ СЦЕНАРИИ ---
        ("user1", "password1", "positive", "Welcome, user1!"),
        
        # --- НЕГАТИВНЫЕ СЦЕНАРИИ ---
        ("USER1", "password1", "negative", "Welcome, user1!"),
        ("qaguru@qa.guru", "wrong_pass", "negative", "Неверный пароль"),
        ("unknown@qa.guru", "qaguru", "negative", "Такого пользователя не существует"),
        ("", "qaguru", "negative", "Заполните поле Email"),
        ("qaguru@qa.guru", "", "negative", "Заполните поле Пароль"),
        ("", "", "negative", "Заполните поля"),
        ("qaguruqa.guru", "qaguru", "negative", "Email должен содержать символ @"),
        ("qaguru@", "qaguru", "negative", "Введен некорректный Email"),
        ("@qa.guru", "qaguru", "negative", "Введен некорректный Email"),
        ("qaguru' OR '1'='1", "' OR '1'='1", "negative", "Некорректные данные"),
    ]
)
def test_login_form(driver, email, password, scenario_type, expected_text):
    """Тест кейс, принимающий наборы данных (DDT)."""
    
    # 1. Открытие тестируемой страницы
    driver.get("https://qa-guru.github.io/one-page-form/login.html")
    
    # 2. Поиск элементов формы
    email_field = driver.find_element(*LOGIN_INPUT)    
    password_field = driver.find_element(*PASSWORD_INPUT)    
    submit_button = driver.find_element(*SUBMIT_BUTTON)
    
    # 3. Очистка полей и ввод тестовых данных
    email_field.clear()
    email_field.send_keys(email)
    
    password_field.clear()
    password_field.send_keys(password)
    
    # 4. Клик по кнопке отправки формы
    submit_button.click()
    
    # 5. Ожидание появления ответа
    actual_result = ""

    time.sleep(1)

    # NOTE: как минимум по трем причинам это анти подход 
    # 5. Ожидание появления ответа (алерта или текста на экране)
    # ПРИМЕЧАНИЕ: Данный блок адаптируется под логику страницы (JS-alert или блок текста).
        #ждем Welcome message, если успех
    if scenario_type == "positive":
        try:
            locator = WELCOME_MESSAGE
            success_login = (WebDriverWait(driver, 3).
                    until(EC.visibility_of_element_located(WELCOME_MESSAGE)))
            actual_result = success_login.text
        except:
            print(f"Ожидался успешный вход, но получено: '{actual_result}'")

        assert expected_text in actual_result

    elif scenario_type == "negative":
    #если Welcome message не появился, ожидаем ошибку
        try:
            locator = STATUS_MESSAGE
            invalid_login = (WebDriverWait(driver, 3).
                        until(EC.visibility_of_element_located(STATUS_MESSAGE)))
            actual_result = invalid_login.text
        except:
            print(f"Форма пропустила некорректные данные: Email='{email}', Pass='{password}'")

        assert expected_text in actual_result or driver.current_url != "success_url"

#NOTE: мне кажется, я что-то набедокурила тут с логикой, но не могу понять что
#########