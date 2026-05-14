# Организационная структура API

## Описание проекта

API для управления организационной структурой компании.

Система позволяет:
- создавать подразделения (дерево отделов)
- управлять иерархией отделов
- добавлять сотрудников в отделы
- перемещать сотрудников между отделами
- удалять отделы (cascade / reassign)
- получать дерево подразделений с контролем глубины
---

## Основные возможности

- CRUD для подразделений
- Вложенная структура отделов (дерево)
- Ограничение глубины дерева (depth до 5)
- Управление сотрудниками внутри отделов
- Переназначение сотрудников при удалении отдела
- Защита от циклов в дереве
- Валидация уникальности названий в рамках родителя
- Swagger документация API

---

## Стек технологий

### Backend
- Python 3.12
- Django
- Django REST Framework
- drf-spectacular (Swagger)

### База данных
- PostgreSQL

### DevOps
- Docker
- Docker Compose
---

## 🚀 Запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/organization-api.git
cd organization-api
```

### 2. Настройка переменных окружения
Пример .env лежит в .env.example

### 3. Запуск через Docker
```bash
docker compose up --build
```

## Доступ к сервису

| Сервис | URL |
|--------|-----|
| API | http://localhost:8000/api/ |
| Swagger | http://localhost:8000/api/docs/ |
| Admin | http://localhost:8000/admin/ |

## Основные endpoints
### Создание подразделения
```http
POST /api/departments/
```
```json
{
  "name": "Backend",
  "parent": 1
}
```
### Получение дерева подразделений
```http
GET /api/departments/{id}/?depth=2&include_employees=true
```
### Обновление подразделения
```http
PATCH /api/departments/{id}/
```
```json
{
  "name": "Developer",
  "parent": 2
}
```

### Удаление подразделения
#### Каскадное удаление:
```http
DELETE /api/departments/{id}/?mode=cascade
```

#### Удаление с переносом сотрудников:
```http
DELETE /api/departments/{id}/?mode=reassign&reassign_to_department_id=2
```

### Создание сотрудника в подразделении
```http
POST /api/departments/{id}/employees/
```
```json
{
  "full_name": "Иван Иванов",
  "position": "Backend Developer",
  "hired_at": "2026-05-12"
}
```
