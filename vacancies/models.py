from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=255)  # Название вакансии
    industry = models.CharField(max_length=100)  # Отрасль
    specialization = models.CharField(max_length=100)  # Специализация
    level = models.CharField(max_length=50)  # Уровень (например, Junior, Middle, Senior)
    city = models.CharField(max_length=50)  # Город
    url = models.URLField(max_length=200)  # URL вакансии
    site_name = models.CharField(max_length=50)

    def __str__(self):
        return self.title
