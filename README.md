# Платформа онлайн-обучения (DRF API) <img width="137" height="41" alt="Skypro" src="https://github.com/user-attachments/assets/ac708293-d4d3-4222-980d-a89643052ae0" />

REST API для платформы онлайн-обучения на базе **Django** и **Django REST Framework**. Реализованы кастомная модель пользователя с авторизацией по `email`, CRUD для курсов, уроков и пользователей, валидация ссылок на внешние видеоресурсы, подписка на обновления курсов, пагинация, история платежей с фильтрацией, аутентификация по **JWT-токенам**, разграничение прав доступа и автоматические тесты с проверкой покрытия (`coverage`).

---

## Основной функционал

* **Аутентификация и регистрация (JWT):**
  * Регистрация новых пользователей (`POST /register/`) с проверкой уникальности `email` и безопасным хешированием пароля (`set_password`).
  * Получение пары токенов `access` и `refresh` (`POST /login/`) и обновление токена (`POST /token/refresh/`) на базе `djangorestframework-simplejwt`.
  * Все эндпоинты API закрыты для неавторизованных пользователей по умолчанию (`IsAuthenticated`), кроме `/register/`, `/login/` и `/token/refresh/`.
* **Разграничение прав доступа и роли:**
  * **Владелец (`owner`):** при создании курса или урока текущий пользователь автоматически назначается его владельцем (`perform_create`). Обычный пользователь видит в списке и может просматривать, редактировать и удалять только свои курсы и уроки (`IsOwner`).
  * **Модератор (группа `moders`):** видит и может просматривать и редактировать любые курсы и уроки (`IsModer`), но не может создавать новые или удалять существующие объекты.
  * **Защита профилей пользователей:** любой авторизованный пользователь может просматривать список и профили других пользователей, но при просмотре чужого профиля скрываются `last_name`, `payments` и пароль (`UserPublicSerializer`). Редактирование (`PUT`/`PATCH`) и удаление (`DELETE`) профиля разрешено только его владельцу (`IsCurrentUser`).
* **Учебные материалы, валидация, подписки и пагинация:**
  * Полный CRUD для курсов (`ModelViewSet`) и уроков (`GenericAPIView`) с выводом количества уроков (`lessons_count`), статуса подписки текущего пользователя (`is_subscribed`) и вложенного списка уроков в курсе.
  * **Валидация видеоссылок (`YoutubeValidator`):** при создании и редактировании уроков допускаются ссылки только на ресурс `youtube.com` (`400 Bad Request` при указании стороннего источника).
  * **Подписка на обновления курса (`Subscription`):** эндпоинт `POST /courses/subscribe/` позволяет пользователю оформить или отменить подписку на выбранный курс (`"подписка добавлена"` / `"подписка удалена"`).
  * **Постраничная пагинация (`MaterialsPagination`):** реализован пагинатор для списков курсов и уроков (`page_size = 5`, поддержка параметра запроса `?page_size=`, ограничение `max_page_size = 50`).
* **Платежи и фильтрация:**
  * История платежей (`GET /payments/`) с фильтрацией по курсу (`paid_course`), уроку (`paid_lesson`), способу оплаты (`payment_method`) и сортировкой по дате (`payment_date`).
* **Тестирование и покрытие кода:**
  * Написаны юнит- и интеграционные API-тесты (`APITestCase`) для проверки CRUD-операций уроков, валидации ссылок, ролевой модели доступа и механизма подписок с замером покрытия через `coverage`.

---

## Технологический стек

* Python 3.12+
* Django / Django REST Framework
* djangorestframework-simplejwt
* django-filter
* Pillow
* coverage
* PostgreSQL / SQLite
* Poetry

---

## Установка и запуск проекта

1. **Клонируйте репозиторий и перейдите в директорию проекта:**
   ```bash
   git clone <URL_вашего_репозитория>
   cd 32.1_Django_DZ
   ```

2. **Установите зависимости через Poetry:**
   ```bash
   poetry install
   ```

3. **Настройте переменные окружения:**
   Создайте файл `.env` в корне проекта на основе `.env.sample` и заполните `SECRET_KEY`, `DEBUG` и параметры подключения к БД.

4. **Примените миграции базы данных:**
   ```bash
   poetry run python manage.py migrate
   ```

5. **Загрузите фикстуру группы модераторов (`moders`) и тестовые платежи:**
   ```bash
   poetry run python manage.py loaddata users/fixtures/groups.json
   poetry run python manage.py loaddata payments_fixture.json
   ```

6. **Создайте суперпользователя (при необходимости) и запустите сервер:**
   ```bash
   poetry run python manage.py createsuperuser
   poetry run python manage.py runserver
   ```

* Главная страница API: http://127.0.0.1:8000/
* Административная панель Django: http://127.0.0

---

## Тестирование и проверка покрытия (Coverage)

1. **Запуск автотестов с замером покрытия:**
   ```bash
   poetry run coverage run --source='.' manage.py test
   ```

2. **Вывод отчета о покрытии в консоль:**
   ```bash
   poetry run coverage report
   ```

3. **Генерация и сохранение HTML-отчета о покрытии (`htmlcov/index.html`):**
   ```bash
   poetry run coverage html
   ```

---

## Основные эндпоинты API

### Авторизация и пользователи
* `POST /register/` — регистрация нового пользователя (`AllowAny`)
* `POST /login/` — получение JWT-токенов `access` и `refresh` (`AllowAny`)
* `POST /token/refresh/` — обновление `access`-токена (`AllowAny`)
* `GET /users/` — список пользователей (публичные данные без фамилии и платежей)
* `GET /users/<id>/` — просмотр профиля (полные данные для владельца, сокращенные для остальных)
* `PUT / PATCH /users/<id>/` — редактирование профиля (только владелец профиля)
* `DELETE /users/delete/<id>/` — удаление профиля (только владелец профиля)

### Курсы, уроки, подписки и платежи
* `GET / POST /courses/` — список курсов с пагинацией (своих или всех для модератора) и создание курса (запрещено модераторам)
* `GET / PUT / PATCH / DELETE /courses/<id>/` — просмотр (с полем `is_subscribed`), редактирование и удаление курса (удаление запрещено модераторам)
* `POST /courses/subscribe/` — добавление или удаление подписки текущего пользователя на обновления курса (в теле запроса передается `{"course_id": <id>}`)
* `GET /lessons/` — список уроков с пагинацией (поддерживает `?page=` и `?page_size=`)
* `POST /lessons/create/` — создание урока с валидацией ссылки на `youtube.com` (запрещено модераторам)
* `GET /lessons/<id>/` — просмотр урока
* `PUT / PATCH /lessons/update/<id>/` — редактирование урока
* `DELETE /lessons/delete/<id>/` — удаление урока (только владелец)
* `GET /payments/` — список платежей (поддерживает `?paid_course=`, `?paid_lesson=`, `?payment_method=`, `?ordering=-payment_date`)
---

## Структура проекта

```text
31_Django_DZ/                       # 31 Корневая директория проекта (платформа онлайн-обучения на DRF с JWT и правами доступа)
│
├── config/                         # 30.1 Главная конфигурационная папка проекта Django
│   ├── __init__.py                 # 30.1 Инициализация пакета конфигурации проекта
│   ├── asgi.py                     # 30.1 Асинхронный интерфейс веб-сервера
│   ├── settings.py                 # 31 Настройки проекта: подключен SimpleJWT, глобальный доступ IsAuthenticated, время жизни токенов
│   ├── urls.py                     # 30.1 Главный файл маршрутизации (пути admin, приложений materials и users, медиафайлы)
│   └── wsgi.py                     # 30.1 Синхронный интерфейс веб-сервера
│
├── materials/                      # 30.1 Приложение «Учебные материалы» (Курсы и уроки)
│   ├── migrations/                 # 30.1 Папка миграций приложения в базе данных
│   ├── __init__.py                 # 30.1 Инициализация пакета приложения materials
│   ├── admin.py                    # 31 Регистрация Course и Lesson в админке с выводом и фильтрацией по владельцу (owner)
│   ├── apps.py                     # 30.1 Конфигурация приложения materials
│   ├── models.py                   # 31 Модели БД: добавлена связь owner (ForeignKey на User) в Course и Lesson
│   ├── serializers.py              # 30.2 Сериализаторы DRF: LessonSerializer и CourseSerializer
│   ├── tests.py                    # 30.1 Модуль для написания автотестов приложения
│   ├── urls.py                     # 30.1 Маршруты API (DefaultRouter для курсов и path для Generic-уроков)
│   └── views.py                    # 31 Контроллеры курсов и уроков: автопривязка owner (perform_create), фильтрация и права IsModer / IsOwner
│
├── users/                          # 30.1 Приложение «Пользователи» (Кастомная модель, профиль, авторизация и платежи)
│   ├── fixtures/                   # 31 Директория для хранения фикстур приложения users
│   │   └── groups.json             # 31 Выгруженная фикстура группы модераторов (moders)
│   ├── management/                 # 30.2 Пакет для пользовательских management-команд Django
│   ├── migrations/                 # 30.1 Папка миграций пользователей в базе данных
│   ├── __init__.py                 # 30.1 Инициализация пакета приложения users
│   ├── admin.py                    # 30.2 Регистрация моделей User и Payment в административной панели Django
│   ├── apps.py                     # 30.1 Конфигурация приложения users
│   ├── models.py                   # 30.2 Модели User (вход по email, phone, city, avatar) и Payment (история оплат)
│   ├── permissions.py              # 31 Кастомные классы прав доступа: IsModer, IsOwner и IsCurrentUser
│   ├── serializers.py              # 31 Сериализаторы UserRegisterSerializer, UserSerializer, UserPublicSerializer и PaymentSerializer
│   ├── tests.py                    # 30.1 Модуль для написания автотестов пользователей
│   ├── urls.py                     # 31 Маршруты JWT-токенов (login, token/refresh), полного CRUD пользователей и списка платежей
│   └── views.py                    # 31 Контроллеры полного CRUD пользователей (с разделением прав/сериализаторов профиля) и платежей
│
├── media/                          # 30.1 Динамическая папка проекта (Загружаемые медиафайлы)
├── .env.sample                     # 30.1 Шаблон файла с переменными окружения
├── .gitignore                      # 30.1 Список файлов и папок, игнорируемых системой Git
├── manage.py                       # 30.1 Главный управляющий скрипт Django-проекта
├── payments_fixture.json           # 30.2 Фикстура с выгруженными тестовыми данными модели Payment
├── pyproject.toml                  # 31 Конфигурационный файл Poetry со списком зависимостей (включая djangorestframework-simplejwt)
├── poetry.lock                     # 31 Зафиксированные версии установленных библиотек Poetry
└── README.md                       # 31 Документация проекта и инструкция по запуску для проверки ДЗ



32.1_Django_DZ/                     # 32.1 Корневая директория проекта (платформа онлайн-обучения на DRF с валидаторами, подписками, пагинацией и тестами)
│
├── config/                         # 30.1 Главная конфигурационная папка проекта Django
│   ├── __init__.py                 # 30.1 Инициализация пакета конфигурации проекта
│   ├── asgi.py                     # 30.1 Асинхронный интерфейс веб-сервера
│   ├── settings.py                 # 31 Настройки проекта: подключен SimpleJWT, глобальный доступ IsAuthenticated, время жизни токенов
│   ├── urls.py                     # 30.1 Главный файл маршрутизации (пути admin, приложений materials и users, медиафайлы)
│   └── wsgi.py                     # 30.1 Синхронный интерфейс веб-сервера
│
├── materials/                      # 30.1 Приложение «Учебные материалы» (Курсы, уроки и подписки)
│   ├── migrations/                 # 32.1 Папка миграций приложения в базе данных
│   │   ├── 0001_initial.py                      # 30.1 Начальная миграция создания моделей Course и Lesson
│   │   ├── 0002_course_owner_lesson_owner.py    # 31 Миграция добавления поля owner в модели Course и Lesson
│   │   ├── 0003_subscription.py                 # 32.1 Миграция создания модели подписки Subscription с уникальным ограничением
│   │   └── __init__.py             # 30.1 Инициализация пакета миграций приложения materials
│   ├── __init__.py                 # 30.1 Инициализация пакета приложения materials
│   ├── admin.py                    # 32.1 Регистрация Course, Lesson и Subscription в админке с фильтрацией
│   ├── apps.py                     # 30.1 Конфигурация приложения materials
│   ├── models.py                   # 32.1 Модели БД: Course, Lesson (с owner) и модель подписки Subscription (уникальность пары user и course)
│   ├── paginators.py               # 32.1 Класс постраничной пагинации MaterialsPagination (page_size, page_size_query_param, max_page_size)
│   ├── serializers.py              # 32.1 Сериализаторы DRF: LessonSerializer (с YoutubeValidator) и CourseSerializer (с полем is_subscribed)
│   ├── tests.py                    # 32.1 Автотесты APITestCase (LessonTestCase и SubscriptionTestCase) для проверки CRUD уроков, прав и подписок
│   ├── urls.py                     # 32.1 Маршруты API (DefaultRouter для курсов, Generic-уроки и эндпоинт подписки courses/subscribe/)
│   ├── validators.py               # 32.1 Кастомный валидатор YoutubeValidator для проверки ссылок на ресурс youtube.com
│   └── views.py                    # 32.1 Контроллеры курсов и уроков (с пагинацией MaterialsPagination) и контроллер подписки SubscriptionAPIView
│
├── users/                          # 30.1 Приложение «Пользователи» (Кастомная модель, профиль, авторизация и платежи)
│   ├── fixtures/                   # 31 Директория для хранения фикстур приложения users
│   │   └── groups.json             # 31 Выгруженная фикстура группы модераторов (moders)
│   ├── management/                 # 30.2 Пакет для пользовательских management-команд Django
│   ├── migrations/                 # 30.1 Папка миграций пользователей в базе данных
│   │   ├── 0001_initial.py         # 30.1 Начальная миграция создания модели пользователя
│   │   ├── 0002_alter_user_options_remove_user_username_user_avatar_and_more.py # 30.1 Миграция настройки авторизации по email и доп. полей профиля
│   │   ├── 0003_payment.py         # 30.2 Миграция создания модели платежей Payment
│   │   └── __init__.py             # 30.1 Инициализация пакета миграций приложения users
│   ├── __init__.py                 # 30.1 Инициализация пакета приложения users
│   ├── admin.py                    # 30.2 Регистрация моделей User и Payment в административной панели Django
│   ├── apps.py                     # 30.1 Конфигурация приложения users
│   ├── models.py                   # 30.2 Модели User (вход по email, phone, city, avatar) и Payment (история оплат)
│   ├── permissions.py              # 32.1 Кастомные классы прав доступа: IsModer (с has_object_permission), IsOwner и IsCurrentUser
│   ├── serializers.py              # 31 Сериализаторы UserRegisterSerializer, UserSerializer, UserPublicSerializer и PaymentSerializer
│   ├── tests.py                    # 30.1 Модуль для написания автотестов пользователей
│   ├── urls.py                     # 31 Маршруты JWT-токенов (login, token/refresh), полного CRUD пользователей и списка платежей
│   └── views.py                    # 31 Контроллеры полного CRUD пользователей (с разделением прав/сериализаторов профиля) и платежей
│
├── htmlcov/                        # 32.1 Сохраненный HTML-отчет о проверке покрытия кода тестами (coverage html)
├── media/                          # 30.1 Динамическая папка проекта (Загружаемые медиафайлы)
├── .coverage                       # 32.1 Служебный файл с результатами замера покрытия тестами
├── .env.sample                     # 30.1 Шаблон файла с переменными окружения
├── .gitignore                      # 30.1 Список файлов и папок, игнорируемых системой Git
├── manage.py                       # 30.1 Главный управляющий скрипт Django-проекта
├── payments_fixture.json           # 30.2 Фикстура с выгруженными тестовыми данными модели Payment
├── pyproject.toml                  # 32.1 Конфигурационный файл Poetry со списком зависимостей (включая coverage)
├── poetry.lock                     # 32.1 Зафиксированные версии установленных библиотек Poetry
└── README.md                       # 32.1 Документация проекта, инструкции по запуску и проверке тестов/покрытия
```
### Основные команды
#### 30.1 инициализируем новый проект Poetry в текущей директории (если pyproject.toml еще не создан)
poetry init -n

#### 30.1 устанавливаем Django, Django REST Framework и библиотеку Pillow через Poetry
poetry add django djangorestframework pillow

#### 30.1 создаем новый Django-проект с именем config внутри виртуального окружения Poetry
poetry run django-admin startproject config .

#### 30.1 создаем приложение users для модели кастомного пользователя
poetry run python manage.py startapp users

#### 30.1 создаем приложение materials для моделей курса и урока
poetry run python manage.py startapp materials

#### 30.1 запускаем тестовый сервер Django через Poetry для проверки работоспособности проекта
poetry run python manage.py runserver

#### 30.1 генерируем файлы миграций для созданных моделей в приложениях users и materials
poetry run python manage.py makemigrations

#### 30.1 применяем все миграции и создаем таблицы в базе данных
poetry run python manage.py migrate

#### 30.2 запускаем кастомную команду для наполнения таблицы платежей тестовыми данными
poetry run python manage.py fill_payments

#### 30.2 выгружаем данные платежей напрямую в файл payments_fixture.json
poetry run python -Xutf8 manage.py dumpdata users.Payment --indent 2 -o payments_fixture.json

#### 30.2 устанавливаем библиотеку django-filter через Poetry для фильтрации и сортировки в DRF
poetry add django-filter

#### 31 устанавливаем библиотеку djangorestframework-simplejwt для работы с JWT-токенами
poetry add djangorestframework-simplejwt

#### 31 создаем директорию fixtures внутри приложения users
mkdir users\fixtures

#### 31 выгружаем группы пользователей в fixtures
poetry run python -Xutf8 manage.py dumpdata auth.group --indent 2 -o users/fixtures/groups.json

#### 32.1 устанавливаем библиотеку coverage, через Poetry
poetry add --group dev coverage

#### 32.1 Запускаем все тесты с подсчетом покрытия
poetry run coverage run --source='.' manage.py test

#### 32.1 выводим таблицу покрытия в терминал
poetry run coverage report

#### 32.1 Сохраните результат проверки покрытия в HTML-папку htmlcov/ (и/или в файл coverage_report.txt для сдачи ДЗ):bash
poetry run coverage html
