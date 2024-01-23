from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from vacancies.models import Vacancy

class Command(BaseCommand):
    help = 'Scrape vacancies from solid.jobs for different experience levels'

    def handle(self, *args, **kwargs):
        experience_levels = ['Staż', 'Junior', 'Regular', 'Senior']
        for level in experience_levels:
            self.scrape_vacancies(level)
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped {level} vacancies'))

    def scrape_vacancies(self, level):
        driver = webdriver.Chrome()
        url = f"https://solid.jobs/offers/it;experiences={level}"
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "offer-list-item"))
            )
        except TimeoutException:
            print("Страница не загрузилась вовремя.")
            driver.quit()
            return

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        vacancies = soup.find_all("offer-list-item", class_="ng-star-inserted")

        for vacancy in vacancies:
            title = None
            location = None
            link = None

            try:
                title = vacancy.select_one("h2.font-weight-500.h5 > a").text.strip()
                location = vacancy.find("i", class_="fa-location-dot").next_sibling.strip()
                link = "https://solid.jobs" + vacancy.select_one("a")['href']
            except (AttributeError, NoSuchElementException):
                link = "Link not found"
            #print(f"Название: {title}, Местоположение: {location}, Ссылка: {link}")

            if not Vacancy.objects.filter(url=link).exists():
                try:
                    Vacancy.objects.create(title=title, url=link, level=level, city=location, site_name="solid.jobs")
                except Exception as e:
                    print(f"Ошибка при создании вакансии: {e}")

        driver.quit()
