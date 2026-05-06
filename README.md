# Мой code runner

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

Реализовал достаточно легковесную и безопасную платформу для выполнения кода прямо в браузере. Это облачная песочница, где можно писать, запускать и делиться кодом на разных языках программирования.

## Плюшки

- **Мультиязычность:** Поддержка Python 3.11, C++ 17, C (GCC 12) и Node.js 18.
- **Изоляция:** Весь пользовательский код выполняется во временных, изолированных Docker-контейнерах, по сути docker in docker.
- **Ограничение ресурсов:** Контейнеры запускаются без доступа к сети (`--network=none`), с файловой системой read-only и жестким лимитом памяти (256 MB).
- **Асинхронность:** Еще и redis тут.
- **UI:** Встроенный редактор на базе CodeMirror.

## Архитектура

... TODO ...

## Стек

- FastAPI
- Docker
- Redis
- PostgreSQL

## Как работает

Принимает код через REST API, ставит задачу в очередь, исполняет в изолированном Docker-песочнице и сохраняет результат в БД.
