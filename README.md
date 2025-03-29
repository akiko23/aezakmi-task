# Notification Service
Тестовое задание для компании Aezakmi group

## 📜 Функционал
Реалзован весь основной функционал, представленны в ТЗ

Бонусные задания:
- Реализовать WebSocket API для получения уведомлений в реальном времени ❌
- Добавить метрики и мониторинг (Prometheus + Grafana) ✅
- Реализовать rate limiting для API ✅
- Создать простой веб-интерфейс для просмотра уведомлений ❌

## 🔧 Стек технологий

- **FastAPI** — фреймворк для создания веб API серверной части приложения.
- **Redis** — хранилище данных в памяти для кэширования уведомлений.
- **SQLAlchemy** — библиотека для работой с СУБД на уровне ЯП.
- **Pydantic** — валидация и сериализация данных.
- **celery** - таск менеджер, для упрощенного межсервисного взаимодействия.
- **toml** — конфигурация сервиса.
- **PostgreSQL** — реляционная СУБД.
- **pytest** - Фрейиворк для создания тестов любого типа на python.
- **Unittest** - Стандартная библиотека python для написания unit тестов.
- **3 Layer Architecture** - набор принципов по написанию легко поддерживаемого и устойчивого к разного рода изменениям ПО (services, controllers, repositories)
- **Prometheus** - создание и сбор метрик.
- **dishka** - DI фреймворк для внедрения зависимостей через ioc_container в различные компоненты приложения.
- **Grafana** - визуализация метрик в виде дашбордов.
- **uv** - all in one утилита для python проектов (virtual-venv, pip, setup-tools)

## Установка

1. Склонируйте репозиторий
```bash
git clone https://github.com/akiko23/aezakmi-task
cd aezakmi-task
```

1.1 (Optional) Запустите теты
```bash
AEZAKMI_TEST_CONFIG_PATH=configs/app_test.toml uv run pytest
```

2. Запустите проект с помощью docker compose
```bash
docker compose up -d
```

3. После запуска можно зайти в Swagger, либо Grafana
   
![image](https://github.com/user-attachments/assets/25db73cc-b242-4201-8a81-73cf967bc508)

![image](https://github.com/user-attachments/assets/6935ae4c-6313-431e-be6a-9a0e5494cc9e)
