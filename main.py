import os
import sys
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

# --- НАСТРОЙКИ ДИЗАЙНА ---
# Список фонов. Скрипт будет менять их каждые 5 картинок.
# --- НАСТРОЙКИ ДИЗАЙНА ---
# Список фонов. Скрипт будет менять их каждые 5 картинок.
# В будущем просто добавляй новые строки в этот список, код сам их подхватит!
BACKGROUND_PROMPTS = [
    # Фон 1 (картинки 1-5): Темный графит / Ночное небо
    "abstract dark obsidian texture, midnight black and deep grey tones, soft elegant highlights, minimalist, no text, empty space",

    # Фон 2 (картинки 6-10): Глубокий черный / Угольный
    "abstract deep charcoal black texture, subtle dark grey fluid waves, moody cinematic lighting, minimalist dark luxury, no text, empty space",

    # Фон 3 (картинки 11-15): Глубокий синий/вода
    "abstract dark blue fluid texture, deep water waves, soft cinematic lighting, minimalist, no text, empty space",

    # Фон 4 (картинки 16-20): Мягкий бежевый/песочный
    "abstract soft beige texture, warm sand tones, elegant minimalist, soft light, no text, empty space"

    # СЮДА МОЖЕШЬ ДОБАВЛЯТЬ НОВЫЕ ФОНЫ (не забудь запятую в конце предыдущей строки):
    # "твой новый промпт...",
]

ACCENT_COLOR = (242, 187, 174)  # Персиково-розовый
TEXT_COLOR = (255, 255, 255)  # Белый
HEADER_TEXT = "ЦИТАТЫ СО СМЫСЛОМ"
WIDTH, HEIGHT = 1080, 1080


def download_background(prompt, filename):
    print(f"Генерация фона для {filename}...")
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={WIDTH}&height=1120&nologo=true&model=flux"

    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Ошибка при генерации фона: {response.status_code}")
        return False


def draw_centered_text(draw, text, font, y_pos, color, max_width=None):
    if max_width:
        avg_char_width = font.getlength("А")
        chars_per_line = int(max_width / avg_char_width)
        lines = textwrap.wrap(text, width=chars_per_line)
    else:
        lines = text.split('\n')

    line_height = font.getbbox("А")[3] + 15
    total_height = len(lines) * line_height
    current_y = y_pos - (total_height / 2)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_pos = (WIDTH - text_width) / 2
        draw.text((x_pos, current_y), line, font=font, fill=color)
        current_y += line_height


def create_post(quote_text, author_text, output_filename, prompt):
    temp_bg = "temp_bg.jpg"
    if not download_background(prompt, temp_bg):
        return False

    img = Image.open(temp_bg).convert("RGB")

    # Отрезаем логотип
    img = img.crop((0, 0, img.width, img.height - 40))
    # Делаем квадрат
    img = ImageOps.fit(img, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)

    # Делаем светлее
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.3)

    # Темная вуаль для контраста текста
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 80))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 30)
        font_quote = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 55)
        font_author = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 28)
        font_quotes_icon = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 180)
    except IOError as e:
        print(f"ВНИМАНИЕ: Не найдены файлы шрифтов!{e}")
        return False

    # Рисуем элементы
    draw_centered_text(draw, "“", font_quotes_icon, 180, ACCENT_COLOR)
    draw_centered_text(draw, HEADER_TEXT, font_header, 280, TEXT_COLOR)

    rect_x1, rect_y1, rect_x2, rect_y2 = 120, 340, 960, 740
    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline=ACCENT_COLOR, width=3)

    draw_centered_text(draw, quote_text, font_quote, 540, TEXT_COLOR, max_width=780)
    draw_centered_text(draw, author_text.upper(), font_author, 860, TEXT_COLOR)

    img = img.convert("RGB")
    img.save(output_filename, "JPEG", quality=95)
    print(f"✅ Пост сохранен: {output_filename}")

    if os.path.exists(temp_bg):
        os.remove(temp_bg)

    return True


def main():
    quotes_file = "data/quotes.txt"
    index_file = "data/bg_index.txt"  # Файл, который будет помнить номер фона

    if not os.path.exists(quotes_file):
        print(f"❌ Ошибка: Файл {quotes_file} не найден!")
        sys.exit(1)

    os.makedirs("ready_img", exist_ok=True)

    # 1. Читаем, какой фон использовать (если файла нет, начинаем с 0)
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            current_bg_index = int(f.read().strip())
    else:
        current_bg_index = 0

    # Выбираем фон для текущего запуска
    current_prompt = BACKGROUND_PROMPTS[current_bg_index % len(BACKGROUND_PROMPTS)]
    print(f"🎨 Используется фон №{current_bg_index + 1} из {len(BACKGROUND_PROMPTS)}")

    with open(quotes_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for i, line in enumerate(lines[:5]):
        if not line.strip():
            continue

        if '|' in line:
            parts = line.split('|')
            quote_text = parts[0].strip()
            author_text = parts[1].strip()

            output_name = os.path.join("ready_img", f"post_{i + 1}.jpg")

            # Передаем один и тот же фон для всех 5 картинок этого запуска
            success = create_post(quote_text, author_text, output_name, current_prompt)
            if success:
                count += 1
        else:
            print(f"⚠️ Пропущена строка {i + 1}: {line.strip()}")

    print(f"\n🎉 Готово! Сгенерировано {count} постов в папке 'ready_img'.")

    if count == 0:
        sys.exit(1)

    # 2. Сохраняем индекс следующего фона для будущего запуска
    next_bg_index = (current_bg_index + 1) % len(BACKGROUND_PROMPTS)
    with open(index_file, "w") as f:
        f.write(str(next_bg_index))
    print(f"💾 Следующий запуск будет использовать фон №{next_bg_index + 1}")


if __name__ == "__main__":
    main()