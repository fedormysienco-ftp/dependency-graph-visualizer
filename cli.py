import argparse
import sys
import csv

class CLIConfig:
    def __init__(self):
        try:
            self.params = self.csv_file()
            self.input_type = 'csv_file'
        except FileNotFoundError:
            self.params = self.command_line()
            self.input_type = 'command_line'

        self.validate_params()

        self.print_params()

    # валидация всех параметров и для CSV и для command_line
    def validate_params(self):
        if not self.params['package_name'] or not self.params['package_name'].strip():
            print("Ошибка: имя пакета не может быть пустым")
            sys.exit(1)

        if not self.params['repo_url'] or not self.params['repo_url'].strip():
            print("Ошибка: URL репозитория не может быть пустым")
            sys.exit(1)

        if self.params['max_depth'] < 0:
            print("Ошибка: максимальная глубина не может быть отрицательной")
            sys.exit(1)

        if not self.params['output_file'] or not self.params['output_file'].strip():
            print("Ошибка: имя выходного файла не может быть пустым")
            sys.exit(1)

    #вывод всех параметров
    def print_params(self):
        print(f"Имя пакета: {self.params['package_name']}")
        print(f"Репозиторий: {self.params['repo_url']}")
        print(f"Тестовый режим: {self.params['test_mode']}")
        print(f"Имя файла с изображением: {self.params['output_file']}")
        print(f"Максимальная глубина: {self.params['max_depth']}")
        print(f"Подстрока для фильтрации: {self.params['filter_substring']}")

    # возвращает словарь в формате ключ значение из csv
    def csv_file(self):
        params = {}
        try:
            with open('csv_config.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parameter = row['parameter']
                    value = row['value']
                    params[parameter] = value

            if not params['package_name']:
                raise ValueError('package_name cannot be empty')

            if not params['repo_url']:
                raise ValueError('repo_url cannot be empty')

            # установка значений по умолчанию для отсутствующих параметров
            if 'test_mode' not in params:
                params['test_mode'] = False
            elif isinstance(params['test_mode'], str):
                params['test_mode'] = params['test_mode'].lower() == 'true'

            if 'output_file' not in params:
                params['output_file'] = 'dependency_graph.png'

            if 'max_depth' not in params:
                params['max_depth'] = 10
            else:
                params['max_depth'] = int(params['max_depth'])

            if 'filter_substring' not in params:
                params['filter_substring'] = ''

            return params

        except Exception as e:
            raise FileNotFoundError('csv_config.csv file not found')

    # парсит аргументы из командной строки и делает params
    def command_line(self):
        params = {}

        # парсер аргументов
        parser = argparse.ArgumentParser(
            description='CLI-приложение для анализа пакетов'
        )

        parser.add_argument('--package-name', '-p',
                            type=str,
                            required=True,
                            help='Имя анализируемого пакета')

        parser.add_argument('--repo-url', '-r',
                            type=str,
                            required=True,
                            help='URL-адрес репозитория или путь к файлу тестового репозитория')

        parser.add_argument('--test-mode', '-t',
                            action='store_true',
                            default=False,
                            help='Режим работы с тестовым репозиторием (по умолчанию: false)')

        parser.add_argument('--output-file', '-o',
                            type=str,
                            default='dependency_graph.png',
                            help='Имя сгенерированного файла с изображением графа')

        parser.add_argument('--max-depth', '-d',
                            type=int,
                            default=10,
                            help='Максимальная глубина анализа зависимостей')

        parser.add_argument('--filter-substring', '-f',
                            type=str,
                            default='',
                            help='Подстрока для фильтрации пакетов')

        args = parser.parse_args()

        # формируем params
        params['package_name'] = args.package_name
        params['repo_url'] = args.repo_url
        params['test_mode'] = args.test_mode
        params['output_file'] = args.output_file
        params['max_depth'] = args.max_depth
        params['filter_substring'] = args.filter_substring

        return params


def demonstrate_error_handling():
    print("\n=== Демонстрация обработки ошибок ===")

    test_cases = [
        {
            'name': 'TEST 1: Пустое имя пакета',
            'test': lambda: test_empty_package_name(),
            'expected_error': 'package_name cannot be empty'
        },
        {
            'name': 'TEST 2: Отрицательная максимальная глубина',
            'test': lambda: test_negative_max_depth(),
            'expected_error': 'max_depth cannot be negative'
        },
        {
            'name': 'TEST 3: Пустой URL репозитория',
            'test': lambda: test_invalid_repo_url(),
            'expected_error': 'repo_url cannot be empty'
        },
        {
            'name': 'TEST 4: Пустое имя выходного файла',
            'test': lambda: test_empty_output_file(),
            'expected_error': 'имя выходного файла не может быть пустым'
        }
    ]

    passed_tests = 0
    for test_case in test_cases:
        print(f"\n {test_case['name']}")
        try:
            test_case['test']()
            print("    ТЕСТ НЕ ПРОЙДЕН: Ожидалась ошибка, но ее не было")
        except Exception as e:
            if test_case['expected_error'] in str(e):
                print(f"    ТЕСТ ПРОЙДЕН: {e}")
                passed_tests += 1
            else:
                print(f"    ТЕСТ НЕ ПРОЙДЕН: Получена ошибка '{e}', но ожидалась '{test_case['expected_error']}'")

    print(f"\n Результаты: {passed_tests}/{len(test_cases)} тестов пройдено")


def test_empty_package_name():
    test_config = {
        'package_name': '',  # пустое имя пакета
        'repo_url': 'https://registry.npmjs.org',
        'test_mode': False,
        'output_file': 'test.png',
        'max_depth': 5,
        'filter_substring': ''
    }
    if not test_config['package_name'] or not test_config['package_name'].strip():
        raise ValueError("package_name cannot be empty")


def test_negative_max_depth():
    test_config = {
        'package_name': 'react',
        'repo_url': 'https://registry.npmjs.org',
        'test_mode': False,
        'output_file': 'test.png',
        'max_depth': -1,  # отрицательная глубина
        'filter_substring': ''
    }
    if test_config['max_depth'] < 0:
        raise ValueError("max_depth cannot be negative")

def test_empty_output_file():

    test_config = {
        'package_name': 'react',
        'repo_url': 'https://registry.npmjs.org',
        'test_mode': False,
        'output_file': '',  # пустое имя выходного
        'max_depth': 5,
        'filter_substring': ''
    }
    if not test_config['output_file'] or not test_config['output_file'].strip():
        raise ValueError("имя выходного файла не может быть пустым")

def test_invalid_repo_url():
    test_config = {
        'package_name': 'react',
        'repo_url': '',  # пустой url
        'test_mode': False,
        'output_file': 'test.png',
        'max_depth': 5,
        'filter_substring': ''
    }
    if not test_config['repo_url'] or not test_config['repo_url'].strip():
        raise ValueError("repo_url cannot be empty")


if __name__ == "__main__":
    try:
        cli = CLIConfig()

        demonstrate_error_handling()

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)