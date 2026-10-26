import os
import random
import sys
import time
from pollinations import Pollinations


def generate_daily_quotes():
    # Передаем ключ для использования персонального шлюза
    client = Pollinations(
        api_key=os.getenv("POLLINATIONS_API_KEY"),
        timeout=90  # Увеличиваем таймаут
    )

    random_seed = random.randint(1000, 999999)

    prompt = (
        f"Сгенерируй 5 коротких философских или психологических цитат на русском языке (итерация {random_seed}). "
        "Формат вывода строго такой, каждая с новой строки: Текст цитаты | АВТОР. "
        "Обязательно указывай реальных известных авторов (например: Карл Юнг, Сенека, Фрейд, Ницше, Шопенгауэр). "
        "Если цитата действительно безымянная (народная мудрость), то в качестве автора напиши просто длинный прочерк '—'. "
        "Без лишних слов, без нумерации, без кавычек. Только текст в формате 'Цитата | Автор'."
    )

    max_retries = 3

    for attempt in range(max_retries):
        print(f"Запрос к ИИ для генерации новых цитат (попытка {attempt + 1} из {max_retries})...")
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai",
                temperature=1.0
            )

            text = response.choices[0].message.content.strip()
            if not text:
                raise ValueError("ИИ вернул пустой ответ")

            text = text.replace("```text", "").replace("```", "").strip()

            cleaned_lines = []
            for line in text.split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    quote = parts[0].strip()
                    author = parts[1].strip() if len(parts) > 1 else ""

                    unknown_authors = ["_", "-", "—", "НЕИЗВЕСТНЫЙ АВТОР", "Неизвестный автор", ""]

                    if author in unknown_authors or author.lower() == "неизвестный автор":
                        author = "—"

                    cleaned_lines.append(f"{quote} | {author}")
                elif line.strip():
                    cleaned_lines.append(line.strip())

            final_text = "\n".join(cleaned_lines[:5])

            # ЖЕСТКАЯ ПРОВЕРКА: если текст пустой или в нем нет символа "|", кидаем ошибку
            if not final_text.strip() or "|" not in final_text:
                raise ValueError("ИИ вернул текст в неверном формате (нет разделителя |)")

            os.makedirs("data", exist_ok=True)
            file_path = "data/quotes.txt"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text + "\n")

            print(f"✅ Сгенерировано и сохранено в {file_path}:\n{final_text}\n")
            return

        except Exception as e:
            print(f"⚠️ Попытка {attempt + 1} не удалась: {e}")
            if attempt < max_retries - 1:
                print("Ждем 15 секунд и пробуем снова...\n")
                time.sleep(15)
            else:
                print("❌ Все попытки исчерпаны. Сервер Pollinations не отвечает или выдает ошибку.")
                sys.exit(1)


if __name__ == "__main__":
    generate_daily_quotes()