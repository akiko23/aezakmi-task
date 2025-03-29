# Notification Service
Тестовое задание для компании Aezakmi group

## 📜 Функционал
Реализован весь основной функционал, представленный в ТЗ, в который входит 
- Создание нового уведомления
- Получение списка уведомлений с фильтрацией и пагинацией
- Получение детальной информации об уведомлении
- Отметка уведомления как прочитанного.
- Интеграция с внешним API (в данном случае мок) для анализа текста уведомления

А также бонусные задания:
- Реализовать WebSocket API для получения уведомлений в реальном времени ✅
- Добавить метрики и мониторинг (Prometheus + Grafana) ✅
- Реализовать rate limiting для API ✅
- Создать простой веб-интерфейс для просмотра уведомлений ✅

## 🔧 Стек технологий

- **FastAPI** — фреймворк для создания веб API серверной части приложения.
- **Redis** — хранилище данных в памяти для кэширования уведомлений.
- **SQLAlchemy** — библиотека для работы с СУБД на уровне ЯП.
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

1.1 (Optional) Запустите тесты
```bash
AEZAKMI_TEST_CONFIG_PATH=configs/app_test.toml uv run pytest
```

2. Запустите проект с помощью docker compose
```bash
docker compose up -d
```

3. После запуска можно зайти на клиентскую часть (http://localhost:8000)
   
   ![image](https://github.com/user-attachments/assets/0ef909d7-db25-4e67-97b1-83927421d573)
   ![image](https://github.com/user-attachments/assets/66d6a7ec-d828-4502-8a68-2fc63931bc7a)

   Swagger (http://localhost:8000/docs)

   ![image](https://github.com/user-attachments/assets/25db73cc-b242-4201-8a81-73cf967bc508)

   или Grafana (http://localhost:3000). Логин - admin; Пароль - admin

   ![image](https://github.com/user-attachments/assets/6935ae4c-6313-431e-be6a-9a0e5494cc9e)
