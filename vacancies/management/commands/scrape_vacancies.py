from selenium import webdriver
from selenium.webdriver.common.by import By  # Импорт класса By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from vacancies.models import Vacancy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time


class Command(BaseCommand):
    help = 'Scrape vacancies from pracuj.pl'

    def handle(self, *args, **kwargs):
        self.scrape_vacancies()
        self.stdout.write(self.style.SUCCESS('Successfully scraped vacancies'))

    def scrape_vacancies(self):
        driver = webdriver.Chrome()  # Убедитесь, что у вас установлен драйвер браузера
        driver.get("https://it.pracuj.pl/praca")

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #vacancies = soup.find_all('div', {'data-test': 'recommended-offer'})  # Пример селектора для вакансий
            vacancies = soup.find_all('h2', {'data-test': 'offer-title'})           
            print("Количество найденных вакансий:", len(vacancies))  # Отладочный вывод
            for vacancy in vacancies:
                title = vacancy.text.strip()
                #link_element = vacancy.find('a', {'data-test': 'link-offer'})
                link_element = vacancy.find('a')
                url = link_element['href'] if link_element else ''
                city = 'Unknown'
                level = 'Unknown'

                if url:
                    url_parts = url.split('/')
                    city = url_parts[-1].split(',')[0] if len(url_parts) > 1 else 'Unknown'
                    level = 'Junior' if 'junior' in url.lower() else 'Mid' if 'mid' in url.lower() else 'Intern' if 'intern' in url.lower() else 'Senior' if 'senior' in url.lower() else 'Unknown'

                if not Vacancy.objects.filter(title=title).exists():
                    try:
                        Vacancy.objects.create(title=title, url=url, level=level, city=city)
                    except Exception as e:
                        print(f"Ошибка при создании вакансии: {e}")
                else:
                    print(f"Vacancy already exists: {title}, {url}")


            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[data-test='bottom-pagination-button-next']")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)  # небольшая задержка для обновления страницы

                # Закрытие всплывающего окна, если оно есть
                try:
                    close_button = driver.find_element(By.CSS_SELECTOR, "селектор кнопки закрытия всплывающего окна")
                    close_button.click()
                except NoSuchElementException:
                    pass  # Если всплывающее окно не найдено, пропускаем

                try:
                    next_button.click()
                except ElementClickInterceptedException:
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                    except Exception as e:
                        print(f"Ошибка при клике: {e}")
                        break
                except NoSuchElementException:
                    break  # Если кнопка "следующая страница" отсутствует, завершить цикл

            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", next_button)
            except NoSuchElementException:
                break  # Если кнопка "следующая страница" отсутствует, завершить цикл

