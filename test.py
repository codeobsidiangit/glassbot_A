print("Тест: Python работает!")
import os
print(f"Токен из переменных: {'Есть' if os.environ.get('BOT_TOKEN') else 'Нет'}")
print("Скрипт завершил работу")