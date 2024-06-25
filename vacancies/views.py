from django.shortcuts import render
from .models import Vacancy
from django.db.models import Q

def search_vacancies(request):
    industry = request.GET.get('industry', '')
    specialization = request.GET.get('specialization', '')
    level = request.GET.get('level', '')
    site_name = request.GET.get('site_name', '')
    print(level)
    vacancies = Vacancy.objects.all()
    if industry:
        pass
        #vacancies = vacancies.filter(industry=industry)
    if specialization:
        pass
        #vacancies = vacancies.filter(specialization=specialization)
    if level:
        if level in ['Staż', 'Intern']:
            vacancies = vacancies.filter(Q(level='Staż') | Q(level='Intern'))
        else:
            vacancies = vacancies.filter(level=level)
    if site_name:
        vacancies = vacancies.filter(site_name=site_name)

    return render(request, 'vacancies/index.html', {'vacancies': vacancies})

def show_vacancies(request):
    vacancies = Vacancy.objects.all()  # Получение всех вакансий
    return render(request, 'vacancies/vacancies_list.html', {'vacancies': vacancies})
