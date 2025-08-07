# 🚀 Инструкция по развертыванию YouTube Downloader в продакшн

## 📋 Предварительные требования

На вашем Ubuntu VPS должны быть установлены:

- Docker
- Docker Compose
- Git
- Доменное имя (ytubik.sarsembai.com)

## 🔧 Шаг 1: Подготовка сервера

### 1.1 Установка Docker (если не установлен)

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
sudo apt install docker.io docker-compose -y

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Перезаходим или выполняем
newgrp docker

# Проверяем установку
docker --version
docker-compose --version
```

### 1.2 Настройка домена

В вашем Fastpanel или панели управления DNS:

1. Создайте A-запись для `ytubik.sarsembai.com` → IP вашего сервера
2. Подождите распространения DNS (5-30 минут)

## 🚀 Шаг 2: Развертывание проекта

### 2.1 Загрузка кода

```bash
# Переходим в папку для проектов
cd /var/www

# Клонируем репозиторий
sudo git clone https://github.com/timursarsembai/ytubik.git
cd ytubik

# Даем права пользователю на папку проекта
sudo chown -R $USER:$USER /var/www/ytubik
```

### 2.2 Настройка переменных окружения

```bash
# Копируем пример настроек
cp .env.example .env

# Редактируем настройки
nano .env
```

**Заполните .env файл:**

```bash
# База данных - ОБЯЗАТЕЛЬНО смените пароль!
DB_PASSWORD=your_very_secure_password_123456

# Секретный ключ - сгенерируйте случайный, минимум 32 символа
SECRET_KEY=your_super_secret_key_min_32_chars_long_change_this

# Домен
DOMAIN=ytubik.sarsembai.com

# Окружение
ENVIRONMENT=production
DEBUG=false
```

**💡 Для генерации секретного ключа:**

```bash
# Генерируем случайный ключ
openssl rand -base64 32
```

### 2.3 Запуск проекта

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем развертывание
./deploy.sh
```

### 2.4 Проверка развертывания

```bash
# Проверяем статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Смотрим логи
docker-compose -f docker-compose.prod.yml logs -f

# Проверяем работу сайта
curl http://localhost
```

## 🌐 Шаг 3: Настройка Nginx и SSL

### 3.1 Установка Nginx (через Fastpanel или вручную)

В Fastpanel:

1. Создайте новый сайт для домена `ytubik.sarsembai.com`
2. Настройте проксирование на `localhost:80`

Или вручную:

```bash
# Устанавливаем Nginx
sudo apt install nginx -y

# Создаем конфигурацию сайта
sudo nano /etc/nginx/sites-available/ytubik
```

**Содержимое файла /etc/nginx/sites-available/ytubik:**

```nginx
server {
    listen 80;
    server_name ytubik.sarsembai.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

```bash
# Активируем сайт
sudo ln -s /etc/nginx/sites-available/ytubik /etc/nginx/sites-enabled/

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
```

### 3.2 Установка SSL сертификата

```bash
# Устанавливаем Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получаем сертификат
sudo certbot --nginx -d ytubik.sarsembai.com

# Проверяем автообновление
sudo systemctl status certbot.timer
```

## 🔄 Шаг 4: Настройка автоматических обновлений

### 4.1 Создание скрипта обновления

```bash
# Создаем скрипт обновления
nano /var/www/ytubik/update.sh
```

**Содержимое update.sh:**

```bash
#!/bin/bash

cd /var/www/ytubik

echo "🔄 Обновляем код из Git..."
git pull origin main

echo "🚀 Перезапускаем сервисы..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Обновление завершено!"
```

```bash
# Делаем скрипт исполняемым
chmod +x update.sh
```

### 4.2 Мониторинг и логи

```bash
# Просмотр логов в реальном времени
docker-compose -f docker-compose.prod.yml logs -f

# Просмотр логов отдельного сервиса
docker-compose -f docker-compose.prod.yml logs -f backend

# Статус всех сервисов
docker-compose -f docker-compose.prod.yml ps

# Перезапуск всех сервисов
docker-compose -f docker-compose.prod.yml restart

# Перезапуск отдельного сервиса
docker-compose -f docker-compose.prod.yml restart backend
```

## 🛡️ Шаг 5: Безопасность

### 5.1 Настройка фаервола

```bash
# Настраиваем UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 5.2 Резервное копирование

```bash
# Создаем бэкап базы данных
docker-compose -f docker-compose.prod.yml exec db pg_dump -U ytubik_user ytubik > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
docker-compose -f docker-compose.prod.yml exec -T db psql -U ytubik_user ytubik < backup_20250808.sql
```

## ✅ Шаг 6: Проверка работы

После успешного развертывания:

1. **Откройте в браузере:** https://ytubik.sarsembai.com
2. **Попробуйте загрузить видео** с YouTube
3. **Проверьте разделы:**
   - 📁 Мои загрузки (ваши личные загрузки)
   - 🌍 Глобальная активность (общая активность)

## 🚨 Устранение проблем

### Проблема: Контейнеры не запускаются

```bash
# Смотрим логи
docker-compose -f docker-compose.prod.yml logs

# Проверяем .env файл
cat .env

# Пересобираем образы
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Проблема: База данных не подключается

```bash
# Проверяем статус PostgreSQL
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Создаем таблицы вручную
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
"
```

### Проблема: Сайт недоступен

```bash
# Проверяем Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверяем порты
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

## 📞 Поддержка

После развертывания сайт будет доступен по адресу:
**https://ytubik.sarsembai.com**

Основные команды управления:

- Остановка: `docker-compose -f docker-compose.prod.yml down`
- Запуск: `docker-compose -f docker-compose.prod.yml up -d`
- Обновление: `./update.sh`
- Логи: `docker-compose -f docker-compose.prod.yml logs -f`
