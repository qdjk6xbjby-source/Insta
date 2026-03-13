import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_data.db")

def init_db():
    """Инициализация базы данных и создание таблиц."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                request_count INTEGER DEFAULT 0,
                is_premium BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()

def ensure_user(user_id: int):
    """Проверяет наличие пользователя и создает его, если нет."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()

def get_user_stats(user_id: int):
    """Возвращает (request_count, is_premium) для пользователя."""
    ensure_user(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT request_count, is_premium FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

def increment_request(user_id: int):
    """Увеличивает счетчик запросов пользователя."""
    ensure_user(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET request_count = request_count + 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def set_premium(user_id: int, status: bool = True):
    """Устанавливает статус премиума."""
    ensure_user(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_premium = ? WHERE user_id = ?', (1 if status else 0, user_id))
        conn.commit()

# Инициализируем при импорте
init_db()
