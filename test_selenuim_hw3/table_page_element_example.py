import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# TODO: 4) Переписать используя PageFactory (Lesson 5)

#TODO: 2) Добавить работу с таблицей 2 done
#TODO: 3) Добавить TC в которых идет работа сразу с 2-я таблицами done

# 1. Реализация Page Element для таблицы
class TableElement:
    def __init__(self, driver, locator):
        self.driver = driver
        self.locator = locator

    @property
    def element(self):
        return self.driver.find_element(*self.locator)

    def get_headers(self) -> list[str]:
        """Возвращает список заголовков таблицы."""
        header_elements = self.element.find_elements(By.CSS_SELECTOR, "thead th")
        return [header.text for header in header_elements]

    def get_row_data(self, row_index: int) -> list[str]:
        """Возвращает данные конкретной строки по её индексу (начиная с 0)."""
        rows = self.element.find_elements(By.CSS_SELECTOR, "tbody tr")
        cells = rows[row_index].find_elements(By.TAG_NAME, "td")
        return [cell.text for cell in cells]

    def get_cell_value(self, row_index: int, column_index: int) -> str:
        """Возвращает значение конкретной ячейки."""
        # TODDO: 1) как переписать используя вызов get_row_data ? Done
        return self.get_row_data(row_index)[column_index]

    def get_column_data(self, column_index: int) -> list[str]:
        rows = self.element.find_elements(By.CSS_SELECTOR, "tbody tr")
        return [row.find_elements(By.TAG_NAME, "td")[column_index].text
        for row in rows]

        # 2. Пример использования (Скрипт теста)
if __name__ == "__main__":
    # Инициализация драйвера
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(5)

    try:
        driver.get("https://the-internet.herokuapp.com/tables")

        # Инициализация таблицы 1
        table1_locator = (By.ID, "table1")
        table1 = TableElement(driver, table1_locator)

        # Инициализация таблицы 2
        table2_locator = (By.ID, "table2")
        table2 = TableElement(driver, table2_locator)

        # Тест с таблицей 1
        print("\n--Тест с таблицей 1--")
        headers1 = table1.get_headers()
        first_row = table1.get_row_data(0)
        specific_cell = table1.get_cell_value(row_index=2, column_index=3)  # Строка 3, Колонка 4 (Due)

        # Вывод результатов в консоль
        print("Заголовки таблицы:", headers1)
        print("Первая строка данных:", first_row)
        print(f"Значение в строке 3, колонке 'Due': {specific_cell}")

        # Простые проверки (Assertions)
        assert "Last Name" in headers1, "Заголовок 'Last Name' не найден"
        assert "Smith" in first_row, "Фамилия 'Smith' должна быть в первой строке"
        assert specific_cell == "$100.00", f"Ожидалось $100.00, но получено {specific_cell}"

        print("\n✅ Тест с таблицей 1 успешно пройден!")

        # Тест с таблицей 2
        print("\n--Тест с таблицей 2--")
        headers2 = table2.get_headers()
        second_column2 = table2.get_column_data(1)
        specific_cell2 = table2.get_cell_value(row_index=1, column_index=2)

        print(f'''Заголовки таблицы: {headers2}
Вторая колонка: {second_column2}
Значение в строке 2, колонке "Email": {specific_cell2}''')

        assert "Due" in headers2, "Заголовок 'Due' не найден"
        assert "Jason" in second_column2, "Фамилия 'Jason' должна быть во второй колонке"
        assert specific_cell2 == "fbach@yahoo.com", f"Ожидалось fbach@yahoo.com, но получено {specific_cell2}"

        print("\n✅ Тест с таблицей 2 успешно пройден!")

        #Тест с обеими таблицами
        print("\n--Тест с таблицами 1 и 2--")
        last_name1 = table1.get_cell_value(row_index=0, column_index=0)
        last_name2 = table2.get_cell_value(row_index=0, column_index=0)

        print(f'''Первая фамилия в таблице 1: {last_name1}
Первая фамилия в таблице 2: {last_name2}''')

        assert headers1 == headers2, "Шапки таблиц отличаются"
        assert last_name1 == last_name2, "Фамилии в первых строках различаются"

        print("\n✅ Тест с обеими таблицами успешно пройден!")
        time.sleep(1)

    finally:
        driver.quit()