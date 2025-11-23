# EffectiveMobileTestTask

## Система аутентификации и авторизации
Система авторизации основана на таблице 'access-rules' со столбцами create_permission, read_permission, 
read_all_permission, update_permission, update_all_permission, delete_permission, delete_all_permission, role_id,
business_object_id, где permission без 'all' - разрешение на работу с объектами, созданными пользователем, а без 'all' -
разрешение на работу со всеми объектами.

В приложении существуют три роли - ADMIN, SUPERUSER, USER. USER имеет доступ только к своим ресурсам,
SUPERUSER - ко своим, а также ко всем продуктам (/products), ADMIN - ко всем ресурсам.
Для проверки прав доступа к ресурсу используется функция check_access_rights в auth_utils.py. У каждой группы ресурсов 
есть свой tag в APIRouter, который хранится в таблице BusinessObject. Также для авторизации используется url с '/my' для 
доступа к ресурсам, созданным пользователем.

Для logout используется БД Redis, в которой хранятся все неиспользующиеся токены до момента истечения срока годности.


## Для запуска приложения нужен запущенный Docker!

## Инструкция по запуску приложения
1. Скопируйте проект
```bash
git clone {url}
```

2. Перейдите в корневую папку
```bash
cd EffectiveMobileTestTask
```

3. Заполните файл .env
```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pass

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1

SECRET_KEY=blabla
ALGORITHM=HS256
TOKEN_EXPIRE_SECONDS=3600
```

4. Запустите сборку docker-контейнеров
```bash
docker compose up -d
```

5. Примените миграции к БД
```bash
docker exec -it app python -m alembic upgrade head
```

6. (Опционально) Инициализируйте базу данных начальными значениями
```bash
docker exec -it app python -m static.fill_db_data
```

7. Введите в браузер 'http://localhost:8000/docs' для доступа к Swagger UI
