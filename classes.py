import json
import os
from abc import ABC, abstractmethod

import requests


class ParsingError(Exception):
    def __str__(self):
        return 'Ошибка получения данных по API'


class Vacancy:
    __slots__ = ('id', 'title', 'url', 'salary_from', 'salary_to', 'employer', 'api')

    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer, api):
        self.id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.employer = employer
        self.api = api

    def __gt__(self, other):
        if not other.salary_min:
            return True
        elif not self.salary_min:
            return True
        return self.salary_min >= other.salary_min

    def __str__(self):
        salary_from = f'Oт {self.salary_from}' if self.salary_from else ''
        salary_to = f'До {self.salary_to}' if self.salary_to else ''
        if self.salary_from is None and self.salary_to is None:
            salary_from = 'Не указана'

        return f'Вакансия: \"{self.title} \" ' \
               f'\nКомпания: \"{self.employer} \" ' \
               f'\nЗарплата: {salary_from} {salary_to} ' \
               f'\nURL: {self.url}'


class Connector:
    def __init__(self, keyword, vacancies_json):
        self.__filename = f"{keyword.title()}.json"
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.__filename, encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def select(self):
        with open(self.__filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancies = [Vacancy(x['id'],
                             x['title'],
                             x['url'],
                             x['salary_from'],
                             x['salary_to'],
                             x['employer'],
                             x['api']) for x in data]
        return vacancies


class Engine(ABC):

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunterAPI(Engine):

    def __init__(self, keyword):
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        }

        self.__params = {
            "text": keyword,
            "page": 0,
            "per_page": 100
        }

        self.__vacancies = []

    @staticmethod
    def get_salary(salary):
        formatted_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formatted_salary = salary['from'] if salary['currency'].lower() == 'rur' else salary['from'] * 78
        if salary and salary['to'] and salary['to'] != 0:
            formatted_salary = salary['to'] if salary['currency'].lower() == 'rur' else salary['to'] * 78
        return formatted_salary

    def get_request(self):
        response = requests.get('https://api.hh.ru/vacancies',
                                headers=self.__headers,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        else:
            return response.json()['items']

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            formatted_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['name'],
                'url': vacancy['alternate_url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer': vacancy['employer']['name'],
                'api': vacancy['HeadHunter']
            })
        return formatted_vacancies

    def get_vacancies(self, pages_count=1):
        while self.__params['page'] < pages_count:
            print(f"HeadHunter, парсинг страницы {self.__params['page'] + 1}", end=": ")

            try:
                values = self.get_request()
            except ParsingError:
                print('Ошибка получения данных!')
                break
            print(f"Найдено: {len(values)} вакансий.")
            self.__vacancies.extend(values)
            self.__params['page'] += 1


class Supperjob(Engine):

    def __init__(self, keyword):
        self.__headers = {"X-Api-App-Id": os.getenv("SJ_API_KEY")}

        self.__params = {
            "keyword": keyword,
            "page": 0,
            "count": 100
        }

        self.__vacancies = []

    @staticmethod
    def get_salary(salary, currency):
        formatted_salary = None

        if salary and salary != 0:
            formatted_salary = salary if currency == 'rub' else salary * 78
        return formatted_salary

    def get_request(self):
        response = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                headers=self.__headers,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        else:
            return response.json()['items']

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            formatted_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['profession'],
                'url': vacancy['link'],
                'salary_from': self.get_salary(vacancy['payment_from'], vacancy['currency']),
                'salary_to': self.get_salary(vacancy['payment_to'], vacancy['currency']),
                'employer': vacancy['firm_name'],
                'api': 'Superjob'
            })
        return formatted_vacancies

    def get_vacancies(self, pages_count=1):
        while self.__params['page'] < pages_count:
            print(f"SuperJob, парсинг страницы {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_request()
            except ParsingError:
                print('Ошибка получения данных!')
                break
            print(f"Найдено: {len(values)} вакансий.")
            self.__vacancies.extend(values)
            self.__params['page'] += 1
