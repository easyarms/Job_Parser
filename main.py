from classes import HeadHunterAPI, SupperJob, Connector


def main():
    vacancies_json = []

    keyword = "Python"
    hh = HeadHunterAPI(keyword)
    sj = SupperJob(keyword)
    for api in (hh, sj):
        api.get_vacancies(pages_count=1)
        vacancies_json.extend(api.get_formatted_vacancies())

    connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input(
            "1 - Вывести список вакансий; \n"
            "2 - Сортировка по минимальной зарплате; \n"
            "3 - Сортировка по минимальной зарплате (DESC); \n"
            "4 - Сортировка по максимальной зарплате; \n"
            "exit - Выйти. \n"
        )
        if command.lower() == 'exit':
            break
        elif command.lower() == '1':
            vacancies = connector.select()
        elif command.lower() == '2':
            vacancies = connector.sorted_vacancies_by_salary_from_asc()
        elif command.lower() == '3':
            vacancies = connector.sorted_vacancies_by_salary_from_desc()
        elif command.lower() == '4':
            vacancies = connector.sorted_vacancies_by_salary_to_asc()

        for vacancy in vacancies:
            print(vacancy, end='\n\n')


if __name__ == '__main__':
    main()
