Dependency Graph Visualizer
Инструмент для визуализации графа зависимостей пакетов из npm registry.

📁 Project Structure
Core Files:

cli.py - Основное приложение с парсером зависимостей

csv_config.csv - Конфигурационный файл параметров

Development Stages:

Stage 1: CLI Configuration System

Конфигурация через CSV файл или аргументы командной строки

Валидация всех параметров и обработка ошибок

Вывод параметров в формате ключ-значение

Stage 2: Dependency Analysis

Получение данных о пакетах из npm registry

Анализ зависимостей (dependencies, peerDependencies, devDependencies)

Вывод списка прямых зависимостей в консоль

🛠️ Features
CLI Configuration:

Поддержка CSV конфигурации и аргументов командной строки

Параметры: имя пакета, URL репозитория, тестовый режим, глубина анализа

Комплексная валидация и обработка ошибок

Dependency Parser:

Запросы к npm registry (https://registry.npmjs.org)

Извлечение зависимостей из package metadata

Поддержка тестового режима с локальными данными

Рекурсивный анализ до указанной глубины

Implemented Commands:

Автоматическая загрузка конфигурации

Анализ зависимостей npm пакетов

Демонстрация обработки ошибок

Вывод метаданных пакетов
