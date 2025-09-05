# Развертывание Mibiri на Railway

## Пошаговая инструкция

### 1. Создайте аккаунт на Railway
- Зайдите на [railway.app](https://railway.app)
- Войдите через GitHub (рекомендуется)

### 2. Создайте новый проект
- Нажмите "New Project"
- Выберите "Deploy from GitHub repo"
- Подключите ваш GitHub аккаунт

### 3. Выберите репозиторий
- Найдите ваш репозиторий с кодом Mibiri
- Нажмите "Deploy Now"

### 4. Railway автоматически:
- ✅ Определит Python проект
- ✅ Установит зависимости из `requirements.txt`
- ✅ Запустит сервер на порту из переменной `PORT`
- ✅ Даст вам публичный URL

### 5. Получите URL сервера
После деплоя Railway покажет вам URL типа:
```
https://your-app-name.up.railway.app
```

### 6. Использование с новым URL
Замените `127.0.0.1:5555` на ваш Railway URL:

```bash
# Регистрация
python client.py register --server your-app-name.up.railway.app:443 --username алиса

# Отправка сообщения
python client.py send --server your-app-name.up.railway.app:443 --from алиса --to боб --message "Привет!"
```

## Важные замечания:
- Railway автоматически использует HTTPS на порту 443
- Сервер будет работать 24/7 (не спит)
- Бесплатный план: 500 часов в месяц
- Все файлы готовы для деплоя!

## Troubleshooting:
Если что-то не работает:
1. Проверьте логи в Railway Dashboard
2. Убедитесь, что все файлы загружены
3. Проверьте, что `requirements.txt` содержит все зависимости
