# API Documentation

## Base URL
```
http://5.53.21.135:8021
```

## Endpoints

### 1. Получение ответа на вопрос

**Endpoint:** `POST /get_answer`

**Description:** Отвечает на вопрос пользователя с использованием RAG и LLM

**cURL:**
```bash
curl -X POST "http://5.53.21.135:8021/get_answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "хала привет?"
  }'
```

**Response:**
```json
{
  "answer": "Привет! Я - виртуальный ассистент технологического парка. Чем могу помочь?",
  "metadata": []
}
```

### 2. Получение модуля с вопросами

**Endpoint:** `GET /get_module/{module_id}`

**Description:** Возвращает вопросы конкретного модуля

**cURL:**
```bash
curl -X GET "http://5.53.21.135:8021/get_module/1"
```

**Response:**
```json
{
  "module_id": 1,
  "module_name": "История и миссия",
  "questions": [
    {
      "question": "Вопрос 1",
      "options": ["Вариант 1", "Вариант 2", "Вариант 3"],
      "correct_answer": 0
    }
  ],
  "total_questions": 10
}
```

**Endpoint:** `POST /get_quiz`

### 4. Анализ калибровочного теста

**Endpoint:** `POST /analyze_calibration`

**Description:** Анализирует результаты калибровочного теста и рекомендует модули для пропуска

**cURL:**
```bash
curl -X POST "http://5.53.21.135:8021/analyze_calibration" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "question1": "ответ1",
      "question2": "ответ2",
      "question3": "ответ3"
    }
  }'
```

**Response:**
```json
{
  "skipped_modules": [2, 5, 7],
  "message": "Рекомендуется пропустить модули 2, 5 и 7 на основе ваших знаний"
}
```

## Database Endpoints

### 5. Создание пользователя

**Endpoint:** `POST /db/users/`

**cURL:**
```bash
curl -X POST "http://5.53.21.135:8021/db/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовый Пользователь",
    "role": "студент",
    "mentor": "Иванов И.И.",
    "lvl": "начальный"
  }'
```

**Response:**
```json
{
  "id": 12,
  "message": "Пользователь успешно создан"
}
```

### 6. Получение пользователя

**Endpoint:** `GET /db/users/{user_id}`

**cURL:**
```bash
curl -X GET "http://5.53.21.135:8021/db/users/12"
```

**Response:**
```json
{
  "id": 12,
  "name": "Тестовый Пользователь",
  "role": "студент",
  "mentor": "Иванов И.И.",
  "lvl": "начальный",
  "created_at": "2024-01-15 10:30:00"
}
```

### 7. Обновление уровня пользователя

**Endpoint:** `PUT /db/users/{user_id}/level`

**cURL:**
```bash
curl -X PUT "http://5.53.21.135:8021/db/users/12/level" \
  -H "Content-Type: application/json" \
  -d '{
    "new_lvl": "продвинутый"
  }'
```

**Response:**
```json
{
  "message": "Уровень пользователя успешно обновлен"
}
```

### 8. Создание теста

**Endpoint:** `POST /db/tests/`

**cURL:**
```bash
curl -X POST "http://5.53.21.135:8021/db/tests/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12,
    "module_id": 1,
    "corrects": 8
  }'
```

**Response:**
```json
{
  "id": 456,
  "message": "Тест успешно создан"
}
```

### 9. Общая аналитика

**Endpoint:** `GET /db/analytics/general`

**cURL:**
```bash
curl -X GET "http://5.53.21.135:8021/db/analytics/general"
```

**Response:**
```json
{
  "total_users": 150,
  "total_tests": 450,
  "average_score": 78.5,
  "most_popular_module": 3
}
```

### 10. Аналитика пользователя

**Endpoint:** `GET /db/analytics/user/{user_id}`

**cURL:**
```bash
curl -X GET "http://5.53.21.135:8021/db/analytics/user/12"
```

**Response:**
```json
{
  "user_id": 12,
  "tests_completed": 15,
  "average_score": 85.2,
  "completed_modules": [1, 2, 3, 4],
  "current_level": "продвинутый"
}
```

### 11. Преобразование речи в текст

**Endpoint:** `POST /speech_to_text`

**Description:** Конвертирует аудиофайл в текст

**cURL:**
```bash
curl -X POST "http://5.53.21.135:8021/speech_to_text" \
  -F "file=@audio.wav"
```

**Response:**
```json
{
  "text": "Привет, это тестовое аудиосообщение"
}
```

### 12. Проверка здоровья API

**Endpoint:** `GET /`

**cURL:**
```bash
curl -X GET "http://5.53.21.135:8021/"
```

**Response:**
```json
{
  "result": "it's healthy"
}
```

## Error Responses

### Common Error Codes:

- `400` - Bad Request (неверные данные запроса)
- `404` - Not Found (ресурс не найден)
- `500` - Internal Server Error (внутренняя ошибка сервера)

**Example Error Response:**
```json
{
  "detail": "Пользователь не найден"
}
```

## Testing the API

You can use the provided Python test script to test all endpoints:

```bash
python test_api.py
```

Or test individual endpoints using curl commands above.

## Notes

- Все запросы к эндпоинтам (кроме GET) должны отправляться с заголовком `Content-Type: application/json`
- Для работы с аудиофайлами используйте `multipart/form-data`
- API поддерживает CORS для кросс-доменных запросов
- Базовая аутентификация не требуется (может быть добавлена в будущем)