import sys
import os

# Добавляем папку src в PYTHONPATH, чтобы импорты работали корректно
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Теперь импортируем функцию запуска из src.bot
from bot import run_bot

if __name__ == "__main__":
    run_bot()