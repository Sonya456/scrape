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



    def get_vacancy_details(self, url):
        driver = webdriver.Chrome()
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            city_element = soup.find('div', {'data-test': 'text-benefit'})
            city = city_element.text.strip() if city_element else 'Unknown'

            level_element = soup.find('div', {'data-test': 'sections-benefit-employment-type-name-text'})
            if level_element:
                level_text = level_element.get_text(strip=True).lower()  # Получение текста элемента и приведение к нижнему регистру
                print(level_text)
                if 'junior' in level_text:
                    level = 'Junior'
                elif 'senior' in level_text:
                    level = 'Senior'
                elif 'mid' in level_text or 'specjalista' in level_text:
                    level = 'Mid'
                elif 'intern' in level_text:
                    level = 'Intern'
                else:
                    level = 'Unknown'  # Неизвестный уровень, если не найдено соответствий
            else:
                print("Элемент с уровнем специализации не найден.")
                level = 'Unknown'


        except Exception as e:
            print(f"Ошибка при извлечении деталей вакансии: {e}")
            city, level = 'Unknown', 'Unknown'
        finally:
            driver.quit()

        return city, level



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
                link_element = vacancy.find('a')
                url = link_element['href'] if link_element else ''
                city = 'Unknown'
                level = 'Unknown'
                k = 0
                i = 0
                if url:
                    city, level = self.get_vacancy_details(url)
                if not url:
                    pass
                if not Vacancy.objects.filter(title=title).exists() and k == 0:
                    try:
                        Vacancy.objects.create(title=title, url=url, level=level, city=city)
                    except Exception as e:
                        print(f"Ошибка при создании вакансии: {e}")
                else:
                    print(f"Vacancy already exists: {title}, {url}")
    
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[data-test='bottom-pagination-button-next']")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)

                try:
                    close_button = driver.find_element(By.CSS_SELECTOR, "селектор кнопки закрытия всплывающего окна")
                    close_button.click()
                except NoSuchElementException:
                    pass
                try:
                    next_button.click()
                except ElementClickInterceptedException:
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                    except Exception as e:
                        print(f"Ошибка при клике: {e}")
                        break
                except NoSuchElementException:
                    break

            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", next_button)
            except NoSuchElementException:
                break

def extract_vacancy_data(vacancy_block, i, soup):
    link_elements = vacancy_block.find_all('a', {'data-test': 'link-offer'})
    print(i)
    level_element = soup.find_all('div', {'link-offer': 'tiles_bt5eb'})
    print(level_element)
    for link in link_elements:
        city = link.text.strip()
        url = link['href']
        print(f"Город: {city}, URL: {url}")
