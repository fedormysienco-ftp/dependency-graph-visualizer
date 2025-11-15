import argparse
import sys
import csv
import urllib.request
import json


class DependencyParser:
    def __init__(self, config):
        self.config = config

    def get_package_info(self, package_name: str, version: str = None) -> dict:
        try:
            # формируем базовый url репозитория
            base_url = self.config.params['repo_url'].rstrip('/')
            # очищаем имя пакета от пробелов
            package_name = package_name.strip()
            version = (version or 'latest').strip()

            # создаем полный url для запроса
            url = f"{base_url}/{package_name}"
            print(f"запрос к: {url}")
            # выполняем http get запрос
            with urllib.request.urlopen(url) as response:
                # парсим json данные в python словарь
                data = json.loads(response.read().decode('utf-8'))
            return data
        except Exception as e:
            print(f"Ошибка при получении информации о пакете {package_name}: {e}")
            return None

    # получает инфу о пакете через гет инфо, собирает и выводит зависимости
    def get_dependencies(self, package_name: str, version: str = None):
        package_info = self.get_package_info(package_name, version)

        if not package_info:
            print(f"Не удалось получить информацию о пакете {package_name}")
            return {}

        # отладочная информация (как в вашем CLI)
        print(f"получены данные о пакете: {package_info.get('name')}")
        print(f"последняя версия: {package_info['dist-tags']['latest']}")

        latest_version = package_info['dist-tags']['latest']
        version_data = package_info['versions'][latest_version]

        print(f"все поля в версии {latest_version}: {list(version_data.keys())}")

        # парсим зависимости из всех источников
        dependencies = {}
        dependencies.update(version_data.get('dependencies', {}))
        dependencies.update(version_data.get('peerDependencies', {}))
        dependencies.update(version_data.get('devDependencies', {}))

        # Выводим зависимости в формате парсера
        print(f"\nПрямые зависимости пакета {package_name}:")
        if dependencies:
            for dep_name, dep_version in dependencies.items():
                print(f"  - {dep_name}: {dep_version}")
            print(f"\nВсего прямых зависимостей: {len(dependencies)}")
        else:
            print("  - Зависимости не найдены")

        return dependencies



class CLIConfig:
    def __init__(self):
        try:
            self.params = self.csv_file()
            self.input_type = 'csv_file'
        except FileNotFoundError:
            self.params = self.command_line()
            self.input_type = 'command_line'
        except ValueError as e:
            print(f"ошибка в csv конфигурации: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ошибка чтения csv: {e}")
            sys.exit(1)

        self.validate_params()
        self.print_params()

    def validate_params(self):
        if not self.params['package_name'] or not self.params['package_name'].strip():
            print("ошибка: имя пакета не может быть пустым")
            sys.exit(1)

        if not self.params['repo_url'] or not self.params['repo_url'].strip():
            print("ошибка: url репозитория не может быть пустым")
            sys.exit(1)

        if self.params['max_depth'] < 0:
            print("ошибка: максимальная глубина не может быть отрицательной")
            sys.exit(1)

        if not self.params['output_file'] or not self.params['output_file'].strip():
            print("ошибка: имя выходного файла не может быть пустым")
            sys.exit(1)

    def print_params(self):
        print(f"имя пакета: {self.params['package_name']}")
        print(f"репозиторий: {self.params['repo_url']}")
        print(f"тестовый режим: {self.params['test_mode']}")
        print(f"имя файла с изображением: {self.params['output_file']}")
        print(f"максимальная глубина: {self.params['max_depth']}")
        print(f"подстрока для фильтрации: {self.params['filter_substring']}")

    def csv_file(self):
        params = {}
        try:
            with open('csv_config.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parameter = row['parameter']
                    value = row['value']
                    params[parameter] = value.strip()

            if not params['package_name']:
                raise ValueError('package_name cannot be empty')

            if not params['repo_url']:
                raise ValueError('repo_url cannot be empty')

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
            raise

    def command_line(self):
        params = {}

        parser = argparse.ArgumentParser(
            description='cli-приложение для анализа пакетов'
        )

        parser.add_argument('--package-name', '-p',
                            type=str,
                            required=True,
                            help='имя анализируемого пакета')

        parser.add_argument('--repo-url', '-r',
                            type=str,
                            required=True,
                            help='url-адрес репозитория или путь к файлу тестового репозитория')

        parser.add_argument('--test-mode', '-t',
                            action='store_true',
                            default=False,
                            help='режим работы с тестовым репозиторием (по умолчанию: false)')

        parser.add_argument('--output-file', '-o',
                            type=str,
                            default='dependency_graph.png',
                            help='имя сгенерированного файла с изображением графа')

        parser.add_argument('--max-depth', '-d',
                            type=int,
                            default=10,
                            help='максимальная глубина анализа зависимостей')

        parser.add_argument('--filter-substring', '-f',
                            type=str,
                            default='',
                            help='подстрока для фильтрации пакетов')

        args = parser.parse_args()

        params['package_name'] = args.package_name
        params['repo_url'] = args.repo_url
        params['test_mode'] = args.test_mode
        params['output_file'] = args.output_file
        params['max_depth'] = args.max_depth
        params['filter_substring'] = args.filter_substring

        return params


def demonstrate_error_handling():
    print("\nдемонстрация обработки ошибок: ")

    test_cases = [
        {
            'name': 'test 1: пустое имя пакета',
            'test': lambda: test_empty_package_name(),
            'expected_error': 'package_name cannot be empty'
        },
        {
            'name': 'test 2: отрицательная максимальная глубина',
            'test': lambda: test_negative_max_depth(),
            'expected_error': 'max_depth cannot be negative'
        },
        {
            'name': 'test 3: пустой url репозитория',
            'test': lambda: test_invalid_repo_url(),
            'expected_error': 'repo_url cannot be empty'
        },
        {
            'name': 'test 4: пустое имя выходного файла',
            'test': lambda: test_empty_output_file(),
            'expected_error': 'имя выходного файла не может быть пустым'
        }
    ]

    passed_tests = 0
    for test_case in test_cases:
        print(f"\n {test_case['name']}")
        try:
            test_case['test']()
            print("    тест не пройден: ожидалась ошибка, но ее не было")
        except Exception as e:
            if test_case['expected_error'] in str(e):
                print(f"    тест пройден: {e}")
                passed_tests += 1
            else:
                print(f"    тест не пройден: получена ошибка '{e}', но ожидалась '{test_case['expected_error']}'")

    print(f"\n результаты: {passed_tests}/{len(test_cases)} тестов пройдено")


def test_empty_package_name():
    test_config = {
        'package_name': '',
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
        'max_depth': -1,
        'filter_substring': ''
    }
    if test_config['max_depth'] < 0:
        raise ValueError("max_depth cannot be negative")


def test_empty_output_file():
    test_config = {
        'package_name': 'react',
        'repo_url': 'https://registry.npmjs.org',
        'test_mode': False,
        'output_file': '',
        'max_depth': 5,
        'filter_substring': ''
    }
    if not test_config['output_file'] or not test_config['output_file'].strip():
        raise ValueError("имя выходного файла не может быть пустым")


def test_invalid_repo_url():
    test_config = {
        'package_name': 'react',
        'repo_url': '',
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

        # используем DependencyParser вместо NpmDependencyAnalyzer
        parser = DependencyParser(cli)
        parser.get_dependencies(cli.params['package_name'])

    except Exception as e:
        print(f"ошибка: {e}")
        sys.exit(1)