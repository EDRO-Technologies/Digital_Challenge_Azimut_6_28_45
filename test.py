import requests
import json

# Базовый URL API
BASE_URL = "http://5.53.21.135:8021"

# Тестовые данные
TEST_USER_ID = 1
TEST_MODULE_ID = 1
TEST_QUESTION = "хала привеn?"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_get_answer():
    """Тест эндпоинта /get_answer"""
    print_separator("ТЕСТ: /get_answer")
    
    url = f"{BASE_URL}/get_answer"
    payload = {
        "question": TEST_QUESTION,
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Ответ: {data.get('answer', 'N/A')}")
            print(f"   Метаданные: {data.get('metadata', 'N/A')}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_get_module():
    """Тест эндпоинта /get_module/{module_id}"""
    print_separator("ТЕСТ: /get_module/{module_id}")
    
    url = f"{BASE_URL}/get_module/{TEST_MODULE_ID}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   ID модуля: {data.get('module_id', 'N/A')}")
            print(f"   Название модуля: {data.get('module_name', 'N/A')}")
            print(f"   Количество вопросов: {data.get('total_questions', 'N/A')}")
            print(f"   Вопросы: {len(data.get('questions', []))}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_get_quiz():
    """Тест эндпоинта /get_quiz"""
    print_separator("ТЕСТ: /get_quiz")
    
    url = f"{BASE_URL}/get_quiz"
    payload = {
        "id": str(TEST_USER_ID)
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Викторина: {len(data.get('quiz', []))} вопросов")
            for i, question in enumerate(data.get('quiz', []), 1):
                print(f"   Вопрос {i}: {question.get('question', 'N/A')}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_analyze_calibration():
    """Тест эндпоинта /analyze_calibration"""
    print_separator("ТЕСТ: /analyze_calibration")
    
    url = f"{BASE_URL}/analyze_calibration"
    
    # Тестовые ответы на калибровочный тест
    test_answers = {
        "question1": "ответ1",
        "question2": "ответ2",
        "question3": "ответ3"
    }
    
    payload = {
        "answers": test_answers
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Пропущенные модули: {data.get('skipped_modules', [])}")
            print(f"   Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_db_create_user():
    """Тест создания пользователя через /db/users/"""
    print_separator("ТЕСТ: /db/users/ (создание пользователя)")
    
    url = f"{BASE_URL}/db/users/"
    payload = {
        "name": "Тестовый Пользователь",
        "role": "студент",
        "mentor": "Иванов И.И.",
        "lvl": "начальный"
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   ID пользователя: {data.get('id', 'N/A')}")
            print(f"   Сообщение: {data.get('message', 'N/A')}")
            return data.get('id')  # Возвращаем ID для использования в других тестах
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
    return None

def test_db_get_user(user_id):
    """Тест получения пользователя через /db/users/{user_id}"""
    print_separator("ТЕСТ: /db/users/{user_id} (получение пользователя)")
    
    url = f"{BASE_URL}/db/users/{user_id}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Пользователь: {data}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_db_update_user_level(user_id):
    """Тест обновления уровня пользователя"""
    print_separator("ТЕСТ: /db/users/{user_id}/level (обновление уровня)")
    
    url = f"{BASE_URL}/db/users/{user_id}/level"
    payload = {
        "new_lvl": "продвинутый"
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.put(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_db_create_test(user_id):
    """Тест создания теста"""
    print_separator("ТЕСТ: /db/tests/ (создание теста)")
    
    url = f"{BASE_URL}/db/tests/"
    payload = {
        "user_id": user_id,
        "module_id": TEST_MODULE_ID,
        "corrects": 8
    }
    
    print(f"URL: {url}")
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   ID теста: {data.get('id', 'N/A')}")
            print(f"   Сообщение: {data.get('message', 'N/A')}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_db_analytics_general():
    """Тест общей аналитики"""
    print_separator("ТЕСТ: /db/analytics/general")
    
    url = f"{BASE_URL}/db/analytics/general"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Общая статистика: {data}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_db_analytics_user(user_id):
    """Тест аналитики пользователя"""
    print_separator("ТЕСТ: /db/analytics/user/{user_id}")
    
    url = f"{BASE_URL}/db/analytics/user/{user_id}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕШНЫЙ ОТВЕТ:")
            print(f"   Статистика пользователя: {data}")
        else:
            print(f"❌ ОШИБКА: {response.status_code}")
            print(f"   Текст ошибки: {response.text}")
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_get_answer_empty_question():
    """Тест с пустым вопросом"""
    print_separator("ТЕСТ: /get_answer (пустой вопрос)")
    
    url = f"{BASE_URL}/get_answer"
    payload = {
        "question": ""
    }
    
    print(f"Данные запроса: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_wrong_endpoint():
    """Тест несуществующего эндпоинта"""
    print_separator("ТЕСТ: Несуществующий эндпоинт")
    
    url = f"{BASE_URL}/wrong_endpoint"
    payload = {
        "question": TEST_QUESTION
    }
    
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_wrong_method():
    """Тест неправильного HTTP метода"""
    print_separator("ТЕСТ: Неправильный HTTP метод (GET вместо POST)")
    
    url = f"{BASE_URL}/get_answer"
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def test_multiple_questions():
    """Тест нескольких разных вопросов"""
    print_separator("ТЕСТ: Несколько разных вопросов")
    
    questions = [
        "Что такое технологический парк?",
        "Как создать стартап?",
        "Какие программы поддержки существуют для предпринимателей?",
        "Расскажи об инновациях в IT"
    ]
    
    url = f"{BASE_URL}/get_answer"
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Вопрос {i}: {question} ---")
        
        payload = {
            "question": question
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Статус код: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ответ получен (длина: {len(data.get('answer', ''))} символов)")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")

def test_multiple_modules():
    """Тест нескольких модулей"""
    print_separator("ТЕСТ: Несколько модулей")
    
    module_ids = [0, 1, 2, 3]  # Тестируем разные модули
    
    for module_id in module_ids:
        print(f"\n--- Модуль {module_id} ---")
        
        url = f"{BASE_URL}/get_module/{module_id}"
        
        try:
            response = requests.get(url)
            print(f"Статус код: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Модуль получен: {data.get('module_name', 'N/A')}")
                print(f"   Вопросов: {data.get('total_questions', 0)}")
            elif response.status_code == 404:
                print(f"⚠️  Модуль {module_id} не найден")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")

def main():
    """Основная функция запуска тестов"""
    print("🚀 ЗАПУСК ТЕСТОВ API TECHNOPARK ASSISTANT")
    print("Предварительное условие: сервер должен быть запущен на localhost:8021")
    
    # Основные тесты API
    # test_get_answer()
    # test_get_module()
    # test_get_quiz()
    # test_analyze_calibration()
    
    # # Тесты базы данных
    user_id = test_db_create_user()
    if user_id:
        test_db_get_user(user_id)
        # test_db_update_user_level(user_id)
        test_db_create_test(user_id)
        test_db_get_user(user_id)

    #     test_db_analytics_user(user_id)
    
    # test_db_analytics_general()
    
    # # Тесты ошибок
    # test_get_answer_empty_question()
    # test_wrong_endpoint()
    # test_wrong_method()
    
    # # Дополнительные тесты
    # test_multiple_questions()
    # test_multiple_modules()
    
    print_separator("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    main()