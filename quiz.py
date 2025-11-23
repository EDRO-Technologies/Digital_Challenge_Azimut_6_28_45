import json
import os
import random
from pathlib import Path

# Путь к JSON файлу
QUIZ_JSON_PATH = Path(__file__).parent / "quiz.json"


def load_quiz_data():
    """Загружает данные тестов из JSON файла."""
    if not QUIZ_JSON_PATH.exists():
        raise FileNotFoundError(f"Файл {QUIZ_JSON_PATH} не найден")
    
    with open(QUIZ_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Преобразуем строковые ключи в числовые для tests
    test_names = data['test_names']
    tests_raw = data['tests']
    
    # Обрабатываем структуру с версиями
    tests = {}
    for k, v in tests_raw.items():
        module_id = int(k)
        # Если это структура с версиями (для модуля 1)
        if isinstance(v, dict) and 'current_version' in v and 'versions' in v:
            current = v['current_version']
            tests[module_id] = v['versions'][str(current)]
        else:
            # Обычная структура (для остальных модулей)
            tests[module_id] = v
    
    return test_names, tests


def update_quiz_from_module(module_id: int = 1, module_name: str = None):
    """
    Обновляет quiz.json из Python модуля с тестами.
    Для модуля 1 случайно выбирает одну из 3 версий вопросов.
    
    Args:
        module_id: ID модуля для обновления (по умолчанию 1)
        module_name: Имя модуля для импорта (по умолчанию ищет quiz_module.py)
    """
    if module_name is None:
        module_name = "quiz_module"
    
    try:
        # Загружаем текущие данные
        if QUIZ_JSON_PATH.exists():
            with open(QUIZ_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {'test_names': {}, 'tests': {}}
        
        # Импортируем модуль
        import importlib
        module = importlib.import_module(module_name)
        
        # Получаем test_names и tests из модуля
        if not hasattr(module, 'test_names') or not hasattr(module, 'tests'):
            raise ValueError(f"Модуль {module_name} должен содержать test_names и tests")
        
        test_names = module.test_names
        tests_module = module.tests
        
        # Обновляем test_names
        data['test_names'] = test_names
        
        # Для модуля 1 - работаем с версиями
        if module_id == 1:
            # Проверяем, есть ли уже структура с версиями
            if str(module_id) in data['tests'] and isinstance(data['tests'][str(module_id)], dict) and 'versions' in data['tests'][str(module_id)]:
                current_version = data['tests'][str(module_id)]['current_version']
                # Выбираем случайную версию из двух других
                other_versions = [v for v in [1, 2, 3] if v != current_version]
                new_version = random.choice(other_versions)
                data['tests'][str(module_id)]['current_version'] = new_version
                print(f"🔄 Модуль {module_id}: версия {current_version} → версия {new_version}")
            else:
                # Первая инициализация - создаём структуру с версиями
                # Проверяем, есть ли в модуле tests_versions
                if hasattr(module, 'tests_versions') and module_id in module.tests_versions:
                    versions_data = module.tests_versions[module_id]
                    # Выбираем случайную версию для старта
                    start_version = random.choice([1, 2, 3])
                    data['tests'][str(module_id)] = {
                        'current_version': start_version,
                        'versions': {
                            '1': versions_data[1],
                            '2': versions_data[2],
                            '3': versions_data[3]
                        }
                    }
                    print(f"🆕 Модуль {module_id}: инициализирован с версией {start_version}")
                else:
                    # Если нет версий, используем обычную структуру
                    data['tests'][str(module_id)] = tests_module[module_id]
                    print(f"⚠️  Модуль {module_id}: версии не найдены, используется обычная структура")
        else:
            # Для остальных модулей - обычное обновление
            data['tests'][str(module_id)] = tests_module[module_id]
        
        # Сохраняем в JSON
        with open(QUIZ_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Данные обновлены из модуля {module_name} в {QUIZ_JSON_PATH}")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта модуля {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при обновлении: {e}")
        import traceback
        traceback.print_exc()
        return False