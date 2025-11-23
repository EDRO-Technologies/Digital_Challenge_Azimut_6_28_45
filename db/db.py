import mysql.connector
from typing import Optional, Dict, List

from config import CONFIG


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = mysql.connector.connect(**CONFIG)
        except mysql.connector.Error as e:
            print(f"❌ Ошибка подключения: {e}")

    def create_tables(self):
        """Создание таблиц users и tests (без created_at, lvl как TEXT)"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    mentor VARCHAR(100) NULL,
                    lvl TEXT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    module_id INT NOT NULL,
                    corrects INT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            cursor.close()
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при создании таблиц: {e}")

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()

    def create_user(self, name: str, role: str, mentor: str = None, lvl: str = None) -> Optional[int]:
        """Создать пользователя"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO users (name, role, mentor, lvl) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, role, mentor, lvl))
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при создании пользователя: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, name, role, mentor, lvl FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при поиске пользователя: {e}")
            return None

    def create_test(self, user_id: int, module_id: int, corrects: int) -> Optional[int]:
        """Создать результат теста"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не существует")
                return None

            cursor = self.connection.cursor()
            query = "INSERT INTO tests (user_id, module_id, corrects) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, module_id, corrects))
            test_id = cursor.lastrowid
            cursor.close()
            return test_id
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при создании теста: {e}")
            return None

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            cursor.close()
            return True
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при удалении пользователя: {e}")
            return False

    def update_user_lvl(self, user_id: int, new_lvl: str) -> bool:
        """Обновить уровень (lvl) пользователя по ID"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return False

            cursor = self.connection.cursor()
            query = "UPDATE users SET lvl = %s WHERE id = %s"
            cursor.execute(query, (new_lvl, user_id))
            cursor.close()
            print(f"✅ Уровень пользователя ID {user_id} обновлён на: {new_lvl or '—'}")
            return True
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при обновлении lvl: {e}")
            return False

    def get_all_users(self) -> list:
        """Получить всех пользователей"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, name, role, mentor, lvl FROM users ORDER BY id"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при получении пользователей: {e}")
            return []

    # === СТАТИСТИКА ===

    def get_general_statistics(self) -> Dict:
        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    module_id,
                    COUNT(DISTINCT user_id) as successful_users
                FROM tests 
                WHERE corrects = 5 
                GROUP BY module_id 
                ORDER BY module_id
            """)
            module_stats = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']

            cursor.execute("SELECT COUNT(*) as total_tests FROM tests")
            total_tests = cursor.fetchone()['total_tests']

            cursor.execute("SELECT COUNT(*) as successful_tests FROM tests WHERE corrects = 5")
            successful_tests = cursor.fetchone()['successful_tests']

            cursor.close()

            success_rate = round((successful_tests / total_tests * 100), 2) if total_tests > 0 else 0

            return {
                'total_users': total_users,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': success_rate,
                'module_statistics': module_stats
            }
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при получении общей статистики: {e}")
            return {}

    def get_user_statistics(self, user_id: int) -> Dict:
        """Статистика по конкретному пользователю (безопасна даже при отсутствии тестов)"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {}

            cursor = self.connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    module_id,
                    COUNT(*) as total_attempts,
                    MIN(corrects) as worst_score,
                    MAX(corrects) as best_score
                FROM tests 
                WHERE user_id = %s 
                GROUP BY module_id 
                ORDER BY module_id
            """, (user_id,))
            module_progress = cursor.fetchall()

            successful_modules = [mod['module_id'] for mod in module_progress if mod.get('best_score', 0) == 5]

            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tests,
                    AVG(corrects) as avg_score,
                    MAX(corrects) as max_score,
                    MIN(corrects) as min_score
                FROM tests 
                WHERE user_id = %s
            """, (user_id,))
            res = cursor.fetchone()
            cursor.close()

            # 🛡️ Защита от отсутствия тестов (res может быть None)
            if res and res['total_tests'] > 0:
                total_tests = res['total_tests']
                avg_score = round(res['avg_score'], 2) if res['avg_score'] is not None else 0.0
                max_score = res['max_score'] if res['max_score'] is not None else 0
                min_score = res['min_score'] if res['min_score'] is not None else 0
            else:
                total_tests = 0
                avg_score = 0.0
                max_score = 0
                min_score = 0

            return {
                'user_info': user,
                'total_tests': total_tests,
                'average_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'successful_modules': successful_modules,
                'module_progress': module_progress
            }
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при получении статистики пользователя: {e}")
            return {}
        
    def get_total_tests_correct(self, user_id: int) -> int:
        """Получить общее количество тестов с corrects=5 для указанного пользователя"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM tests WHERE user_id = %s AND corrects = 5"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при получении количества успешных тестов: {e}")
            return 0

    def get_mentor_statistics(self, mentor_name: str) -> Dict:
        """Статистика по ментору (устойчива к пустым данным)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM users WHERE mentor = %s", (mentor_name,))
            mentor_users = cursor.fetchall()
            cursor.close()

            if not mentor_users:
                return {
                    'mentor_name': mentor_name,
                    'total_users': 0,
                    'total_successful_modules': 0,
                    'average_success_rate': 0.0,
                    'users': []
                }

            user_stats = []
            for user_row in mentor_users:
                stat = self.get_user_statistics(user_row['id'])
                if stat:
                    user_stats.append(stat)

            total_users = len(mentor_users)
            total_successful_modules = sum(len(s['successful_modules']) for s in user_stats)

            # Считаем средний балл только по тем, у кого есть тесты (чтобы не делить на 0)
            scores = [s['average_score'] for s in user_stats if s['total_tests'] > 0]
            avg_success_rate = round(sum(scores) / len(scores), 2) if scores else 0.0

            return {
                'mentor_name': mentor_name,
                'total_users': total_users,
                'total_successful_modules': total_successful_modules,
                'average_success_rate': avg_success_rate,
                'users': user_stats
            }
        except mysql.connector.Error as e:
            print(f"❌ Ошибка при получении статистики ментора: {e}")
            return {}
        
        
        
db_1 = DatabaseManager()
db_1.connect()
db_1.create_tables()