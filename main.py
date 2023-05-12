from classes import HeadHunterAPI, Supperjob, Connector


def main():
    keyword = "Python"
    hh = HeadHunterAPI(keyword)
    sj = Supperjob(keyword)
    for api in (hh, sj):
        api.get_vacancies(pages_count=1)
        vacancies_json.extend(api.get_formatted_vacancies())

    connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input(
            "1 - Вывести список вакансий; \n"
            "exit - Выйти. \n"
        )
        if command.lower() == 'exit':
            break
        elif command.lower() == '1':
            vacancies = connector.select()

        for vacancy in vacancies:
            print(vacancy, end='\n\n')


if __name__ == '__main__':
    main()
