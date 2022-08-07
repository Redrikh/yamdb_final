# YaMDb API
[![Django-app workflow](https://github.com/Redrikh/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/Redrikh/yamdb_final/actions/workflows/yamdb_workflow.yml)
***
Тестовый проект доступен по адресу: http://130.193.52.11/
***
Проект YaMDb собирает отзывы пользователей на произведения. Через API администратор может создавать произведения для отзывов, категории и жанры произведений. Пользователям предоставляется возможность писать отзывы на произведения и комментировать их.

## Workflow состоит из следущих этапов:
- tests - проверка кода на соответствие PEP8 и прохождение автотестов pytest.
- build_and_push_to_docker_hub - запускается только при успешном прохождении tests, собирает и заливает образ на DockerHub
- deploy - запускается только при успешном прохождении build_and_push_to_docker_hub. Создаёт файл с переменными окружения и запускает docker-compose
- send_message - запускается только при успешном прохождении deploy. Отправляет сообщение о успешном запуске в telegram

### Запуск workflow:
#### Подготовка сервера:
- На боевой сервер нужно установить nginx, docker и docker-compose:
```
sudo apt install nginx
sudo apt install docker-io
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- Создать файлы:
```
/home/isturnell/docker-compose.yaml
/home/isturnell/nginx/default.conf
Можно скопировать их из репозитория /infra/
```
- Разрешить фаерволле подключение к SSH и web:
```
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH 
```
- Остановить nginx:
```
sudo sysmctl stop nginx
```
#### Подготовка переменных окружения:
В репозитории добавить `Settings -> Secrets -> Actions secrets`:
```
DB_ENGINE - используемая СУБД (по-умолчанию django.db.backends.postgresql)
DB_HOST - адрес сервера БД
DB_NAME - имя БД
DB_PORT - порт для подключения к БД
DOCKER_PASSWORD - пароль пользователя DockerHub
DOCKER_REPOSITORY - имя репозитория DockerHub
DOCKER_USERNAME - имя пользователя DockerHub
HOST - адрес удалённого сервера
POSTGRES_PASSWORD - пароль пользователя базы данных PostgreSQL
POSTGRES_USER - имя пользователя базы данных PostgreSQL
SSH_KEY - закрытый ключ для подключения к серверу по SSH
TELEGRAM_TO - ID пользователя telegram, которому будут приходить оповещения
TELEGRAM_TOKEN - токен бота telegram, который будет рассылать оповещения
USER - логин пользователя боевого сервера
```
##### Ключ SSH:
```
Скопировать ключ можно с сервера из файла ~/.ssh/id_rsa
Если его там нет, нужно сгенерировать ключ:
ssh-keygen
Открытый ключ из ~/.ssh/id_rsa.pub нужно скопировать в ~/.ssh/authorized_keys не удаляя оттуда уже имеющихся ключей
```
### При первом запуске после успешного деплоя нужно сделать миграции, создать суперюзера и собрать статику:
```
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic --no-input
```

## Пользовательские роли
```
Anonymous
Может просматривать описания произведений, читать отзывы и комментарии.
User
Может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
Moderator
Те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
Admin
Полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям
Суперюзер Django
Обладет правами администратора
```


### Регистрация нового пользователя
```
1. Отправить POST-запрос с параметрами email и username на эндпоинт /api/v1/auth/signup/.
2. YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на указанный адрес email.
3. Отправить POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос приходит token (JWT-токен).
```

### Создание категории
```POST /api/v1/categories/```
```json
{
    "name": "string",
    "slug": "string"
}
```

### Добавление произведения
```GET /api/v1/titles/```
```json
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

### Добавление нового отзыва
```GET /api/v1/titles/```
```json
{
  "text": "string",
  "score": 1
}
```
## Используемые технологии
- Python
- Django Rest Framework
- Joser
- Simple JWT
## Автор
Скворцов Евгений, Родителев Андрей, Кожевников Алексей