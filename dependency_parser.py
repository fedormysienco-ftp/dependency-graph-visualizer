import urllib.request
import json


class DependencyParser:
    # конструктор
    def __init__(self, config):
        self.config = config

    #получает информацию о пакете из npm registry
    def get_package_info(self, package_name: str, version: str = None) -> dict:
        try:
            if self.config.params['test_mode']:
                return self._load_test_package_info(package_name)
            else:
                base_url = self.config.params['repo_url'].rstrip('/')
                package_name = package_name.strip()
                version = (version or 'latest').strip()

                url = f"{base_url}/{package_name}/{version}"
                print(f'Загрузка информации о пакете: {url}')

                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.URLError as e:
            print(f"Ошибка сети при получении пакета {package_name}: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при получении информации о пакете {package_name}: {e}")
            return None

    # загружает тестовую информацию о пакете из файла
    def _load_test_package_info(self, package_name: str) -> dict:
        try:
            with open(self.config.params['repo_url'], 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            return test_data.get(package_name, {})
        except Exception as e:
            print(f"Ошибка загрузки тестовых данных: {e}")
            return {}

    # извлекает прямые зависимости пакета
    def get_dependencies(self, package_name: str, version: str = None) -> set:
        package_info = self.get_package_info(package_name, version) # получает информацию о пакете

        if not package_info:
            print(f"Не удалось получить информацию о пакете {package_name}")
            return set() # вернем пустое множество


        # зависимости находятся прямо в корне (тут извлекаем)
        dependencies = package_info.get('dependencies', {})

        print(f"\nПрямые зависимости пакета {package_name}:")
        deps_set = set()

        if dependencies:
            for dep_name, dep_version in dependencies.items():
                print(f"  - {dep_name}: {dep_version}")
                deps_set.add(dep_name)
        else:
            print("  - Зависимости не найдены")
            print(f"\nПоиск зависимостей в альтернативных полях:")


            peer_deps = package_info.get('peerDependencies', {})
            if peer_deps:
                print(f"  Найдены peerDependencies:")
                for dep_name, dep_version in peer_deps.items():
                    print(f"    - {dep_name}: {dep_version}")
                    deps_set.add(dep_name)

            dev_deps = package_info.get('devDependencies', {})
            if dev_deps:
                print(f"  Найдены devDependencies:")
                for dep_name, dep_version in dev_deps.items():
                    print(f"    - {dep_name}: {dep_version}")
                    deps_set.add(dep_name)

        print(f"\nВсего прямых зависимостей: {len(deps_set)}")
        return deps_set


if __name__ == "__main__":
    class TestConfig:
        def __init__(self):
            self.params = {
                'package_name': 'express',
                'repo_url': 'https://registry.npmjs.org',
                'test_mode': False
            }


    print("=== Демонстрация Этапа 2 ===")
    parser = DependencyParser(TestConfig()) # создали парсер
    dependencies = parser.get_dependencies('express') # нашли зависимости