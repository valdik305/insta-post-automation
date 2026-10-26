import subprocess
import sys
import os
import logging

# Создаем папку logs, если её нет
os.makedirs("logs", exist_ok=True)

# Настройка логирования в файл
logging.basicConfig(
    filename='logs/pipeline.log', # <-- Изменено
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def run_step(script_name):
    logging.info(f"--- Запуск: {script_name} ---")
    print(f"🚀 Запуск: {script_name}")
    try:
        # sys.executable — это путь к Python в твоем venv
        subprocess.check_call([sys.executable, script_name])
        logging.info(f"✅ Успешно: {script_name}")
        print(f"✅ {script_name} завершен.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Ошибка в {script_name}: {e}")
        print(f"❌ Ошибка в {script_name}. Пайплайн остановлен.")
        sys.exit(1)  # Останавливаем выполнение


if __name__ == "__main__":
    # Убедимся, что скрипт запускается из своей папки
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    scripts = [
        "generate_quotes.py",
        "main.py",
        "poster.py"
    ]

    for script in scripts:
        run_step(script)

    print("🎉 Весь пайплайн выполнен успешно!")
    logging.info("=== Пайплайн завершен ===")
