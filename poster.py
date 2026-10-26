import os
import sys
import glob
import random
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# --- НАСТРОЙКИ (берутся из .env) ---
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
CAPTION = os.getenv("CAPTION", "Размышления о психологии и жизни. Свайп 👉\n\n#психология #философия")
SESSION_FILE = "session.json"

# Проверка, что данные вообще загрузились
if not IG_USERNAME or not IG_PASSWORD:
    print("❌ Ошибка: Не найдены IG_USERNAME или IG_PASSWORD в файле .env")
    exit(1)

# Список поисковых запросов для выбора музыки
MUSIC_QUERIES = [
    "calm piano",
    "ambient meditation",
    "soft acoustic",
    "peaceful instrumental",
    "cinematic ambient"
]


def get_all_posts() -> list[Path]:
    files = glob.glob("ready_img/post_*.jpg")
    def get_num(filepath):
        filename = os.path.basename(filepath)
        return int(filename.split('_')[1].split('.')[0])
    files.sort(key=get_num)
    return [Path(f) for f in files]


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_random_music(cl):
    print("Поиск спокойной музыки...")
    query = random.choice(MUSIC_QUERIES)
    print(f"Поисковый запрос: '{query}'")

    try:
        tracks = cl.search_music(query)
        if not tracks:
            query = random.choice(MUSIC_QUERIES)
            tracks = cl.search_music(query)

        if tracks:
            track = random.choice(tracks[:10])
            print(f"Выбран трек (ID): {track.pk if hasattr(track, 'pk') else 'unknown'}")
            music_feed = cl.music_in_feed_audio_browser()
            session_id = music_feed.get("alacorn_session_id")
            return track, session_id
        else:
            return None, None
    except Exception as e:
        print(f"⚠️ Ошибка при поиске музыки: {e}")
        return None, None


def post_to_instagram():
    all_posts = get_all_posts()

    if not all_posts:
        print("❌ Нет картинок для публикации.")
        sys.exit(1)
        return

    print(f"Всего найдено картинок: {len(all_posts)}")

    cl = Client()

    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        print("Загружена сохраненная сессия.")

    try:
        print("Авторизация в Instagram...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("✅ Успешный вход!")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return

    groups = list(chunk_list(all_posts, 5))
    print(f"Будет опубликовано каруселей: {len(groups)}")

    for idx, group in enumerate(groups, start=1):
        print(f"\n--- Публикация карусели {idx} из {len(groups)} ---")
        print(f"Картинки: {[p.name for p in group]}")

        track, session_id = get_random_music(cl)

        try:
            if track and session_id:
                media = cl.album_upload_with_music(
                    paths=group,
                    caption=CAPTION,
                    track=track,
                    alacorn_session_id=session_id
                )
                print("✅ Опубликовано с музыкой.")
            else:
                media = cl.album_upload(paths=group, caption=CAPTION)
                print("✅ Опубликовано без музыки (трек не найден).")

            print(f"🎉 Ссылка: https://www.instagram.com/p/{media.code}/")

            os.makedirs("archive", exist_ok=True)
            for path in group:
                os.rename(path, os.path.join("archive", path.name))
            print("Картинки перемещены в archive.")

        except Exception as e:
            print(f"❌ Ошибка при публикации: {e}")


if __name__ == "__main__":
    post_to_instagram()