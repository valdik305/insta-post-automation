
from pollinations import Pollinations  # type: ignore

def generate_daily_quotes():
    client = Pollinations()
    prompt = (
        "Сгенерируй 5 коротких философских или психологических цитат на русском языке. "
        "Формат вывода строго такой, каждая с новой строки: Текст цитаты | АВТОР. "
        "Без лишних слов, без нумерации. Автор может быть известным (Юнг, Сенека) или если автора нет ставим прочерк '_'."
    )

    print("Запрос к ИИ для генерации новых цитат...")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai",
        temperature=0.8
    )

    text = response.choices[0].message.content.strip()

    # Очищаем от возможных артефактов markdown
    text = text.replace("```text", "").replace("```", "").strip()

    file_path = "data/quotes.txt"  # <-- Изменено
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    print(f"✅ Сгенерировано и сохранено в quotes.txt:\n{text}\n")


if __name__ == "__main__":
    generate_daily_quotes()