"""
Сервис для создания видео из изображений (слайд-шоу) с фоновым видео
"""
import os
import tempfile
import uuid
import requests
from typing import List, Dict
from moviepy.editor import (
    ImageClip, VideoFileClip, concatenate_videoclips,
    AudioFileClip, CompositeVideoClip, TextClip
)
from PIL import Image, ImageDraw, ImageFont
from app.db.supa_request import supabase


def download_from_supabase_or_url(url: str, file_name_hint: str = None) -> bytes:
    """
    Скачивает файл из Supabase Storage или по прямому URL

    Args:
        url: URL файла (может быть публичный или подписанный)
        file_name_hint: Имя файла в storage (для альтернативного метода)

    Returns:
        bytes: Содержимое файла
    """
    try:
        # Сначала пробуем скачать по URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        # Если не получилось по URL - пробуем через SDK
        if file_name_hint:
            try:
                # Извлекаем имя файла из URL если не передано
                if not file_name_hint and '/videos/' in url:
                    file_name_hint = url.split('/videos/')[-1].split('?')[0]

                # Скачиваем через Supabase SDK
                file_data = supabase.storage.from_("videos").download(file_name_hint)
                return file_data
            except Exception as sdk_error:
                raise Exception(f"Failed to download file: URL method failed ({str(e)}), SDK method failed ({str(sdk_error)})")
        raise Exception(f"Failed to download file from URL: {str(e)}")


# Пути к фоновым видео
BACKGROUND_VIDEOS = {
    "minecraft": "backend/assets/backgrounds/minecraft.mp4",
    "subway": "backend/assets/backgrounds/subway.mp4",
    "abstract": "backend/assets/backgrounds/abstract.mp4",
}


async def create_slideshow_video(
    scenes: List[Dict],
    voiceover_url: str = None,
    subtitle_content: str = None,
    total_duration: float = 30.0,
    background_style: str = "minecraft"
) -> str:
    """
    Создает слайд-шоу видео из изображений сцен с фоновым видео

    Args:
        scenes: Список сцен с generated_image_url
        voiceover_url: URL аудио озвучки (опционально)
        subtitle_content: Содержимое субтитров в формате SRT (опционально)
        total_duration: Общая длительность видео в секундах
        background_style: Стиль фонового видео ('minecraft', 'subway', 'abstract')

    Returns:
        str: Публичный URL загруженного видео
    """
    print(f"[VIDEO_SERVICE] Starting video creation")
    print(f"[VIDEO_SERVICE] Scenes: {len(scenes)}, Duration: {total_duration}, Background: {background_style}")

    temp_files = []
    clips = []

    try:
        # Фильтруем сцены с изображениями
        valid_scenes = [s for s in scenes if s.get("generated_image_url")]
        print(f"[VIDEO_SERVICE] Valid scenes with images: {len(valid_scenes)}")

        if not valid_scenes:
            raise ValueError("No scenes with generated images found")

        # Рассчитываем длительность для каждого изображения
        duration_per_scene = total_duration / len(valid_scenes)
        print(f"[VIDEO_SERVICE] Duration per scene: {duration_per_scene}s")

        # Размеры для вертикального видео 9:16 (1080x1920)
        video_width = 1080
        video_height = 1920

        # Проверяем наличие фонового видео
        background_path = BACKGROUND_VIDEOS.get(background_style)
        print(f"[VIDEO_SERVICE] Background path: {background_path}")
        background_clip = None

        if background_path and os.path.exists(background_path):
            print(f"[VIDEO_SERVICE] Loading background video: {background_path}")
            # Загружаем фоновое видео
            background_clip = VideoFileClip(background_path)

            # Зацикливаем фоновое видео если оно короче нужной длительности
            if background_clip.duration < total_duration:
                num_loops = int(total_duration / background_clip.duration) + 1
                background_clip = background_clip.loop(n=num_loops)

            # Обрезаем до нужной длительности
            background_clip = background_clip.subclip(0, total_duration)
        else:
            # Если нет фонового видео - создаем черный фон
            black_bg_path = create_solid_color_image(video_width, video_height, (0, 0, 0))
            temp_files.append(black_bg_path)
            background_clip = ImageClip(black_bg_path, duration=total_duration)

        # Создаем клипы из каждого изображения
        for i, scene in enumerate(valid_scenes):
            print(f"[VIDEO_SERVICE] Processing scene {i+1}/{len(valid_scenes)}")
            image_url = scene.get("generated_image_url")
            print(f"[VIDEO_SERVICE] Scene {i+1} image URL: {image_url}")

            # Скачиваем изображение (безопасным способом)
            print(f"[VIDEO_SERVICE] Downloading image for scene {i+1}...")
            img_content = download_from_supabase_or_url(image_url)
            print(f"[VIDEO_SERVICE] Downloaded {len(img_content)} bytes for scene {i+1}")

            # Сохраняем во временный файл
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_img.write(img_content)
            temp_img.close()
            temp_files.append(temp_img.name)
            print(f"[VIDEO_SERVICE] Saved scene {i+1} to temp file: {temp_img.name}")

            # Обрабатываем изображение - делаем меньше для наложения на фон
            img = Image.open(temp_img.name)
            # Размещаем картинку в верхней части экрана (занимает 60% высоты)
            overlay_height = int(video_height * 0.6)
            overlay_width = int(overlay_height * img.width / img.height)
            print(f"[VIDEO_SERVICE] Scene {i+1} original size: {img.width}x{img.height}, resizing to: {overlay_width}x{overlay_height}")

            img_resized = img.resize((overlay_width, overlay_height), Image.Resampling.LANCZOS)

            # Сохраняем обработанное изображение
            temp_processed = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img_resized.save(temp_processed.name, quality=95)
            temp_processed.close()
            temp_files.append(temp_processed.name)
            print(f"[VIDEO_SERVICE] Saved processed scene {i+1} to: {temp_processed.name}")

            # Создаем видео клип из изображения
            start_time = i * duration_per_scene
            clip = (ImageClip(temp_processed.name)
                   .set_duration(duration_per_scene)
                   .set_start(start_time)
                   .set_position(("center", 50)))  # Центрируем по горизонтали, сверху
            clips.append(clip)
            print(f"[VIDEO_SERVICE] Created clip for scene {i+1}, start_time: {start_time}s, duration: {duration_per_scene}s")

        # Накладываем все клипы на фоновое видео
        print(f"[VIDEO_SERVICE] Compositing {len(clips)} clips onto background...")
        final_video = CompositeVideoClip([background_clip] + clips, size=(video_width, video_height))
        print(f"[VIDEO_SERVICE] Video composition complete, duration: {final_video.duration}s")

        # Добавляем аудио озвучку, если есть
        if voiceover_url:
            print(f"[VIDEO_SERVICE] Adding voiceover from: {voiceover_url}")
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

            try:
                # Скачиваем аудио безопасным способом
                print(f"[VIDEO_SERVICE] Downloading voiceover...")
                audio_content = download_from_supabase_or_url(voiceover_url)
                print(f"[VIDEO_SERVICE] Downloaded {len(audio_content)} bytes of audio")
                audio_temp.write(audio_content)
                audio_temp.close()
                temp_files.append(audio_temp.name)

                audio_clip = AudioFileClip(audio_temp.name)
                print(f"[VIDEO_SERVICE] Audio clip loaded, duration: {audio_clip.duration}s")
            except Exception as e:
                # Если не удалось скачать - пропускаем озвучку
                audio_temp.close()
                if os.path.exists(audio_temp.name):
                    os.unlink(audio_temp.name)
                print(f"[VIDEO_SERVICE] Warning: Could not download voiceover: {str(e)}")
                audio_clip = None

            # Подгоняем длительность видео под аудио (если аудио длиннее)
            if audio_clip and audio_clip.duration > final_video.duration:
                print(f"[VIDEO_SERVICE] Extending video duration to match audio: {audio_clip.duration}s")
                final_video = final_video.set_duration(audio_clip.duration)

            if audio_clip:
                print(f"[VIDEO_SERVICE] Setting audio on video...")
                final_video = final_video.set_audio(audio_clip)
                print(f"[VIDEO_SERVICE] Audio added successfully")
        else:
            print(f"[VIDEO_SERVICE] No voiceover URL provided, skipping audio")

        # Добавляем субтитры, если есть
        if subtitle_content:
            print(f"[VIDEO_SERVICE] Adding subtitles...")
            final_video = add_subtitles_to_video(final_video, subtitle_content)
            print(f"[VIDEO_SERVICE] Subtitles added")
        else:
            print(f"[VIDEO_SERVICE] No subtitles provided, skipping")

        # Экспортируем финальное видео
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_temp.close()
        temp_files.append(output_temp.name)
        print(f"[VIDEO_SERVICE] Starting video export to: {output_temp.name}")
        print(f"[VIDEO_SERVICE] Export settings: fps=24, codec=libx264, preset=medium, threads=4")

        final_video.write_videofile(
            output_temp.name,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4
        )
        print(f"[VIDEO_SERVICE] Video export complete!")

        # Загружаем в Supabase Storage
        file_name = f"video_{uuid.uuid4()}.mp4"
        print(f"[VIDEO_SERVICE] Uploading video to Supabase: {file_name}")

        with open(output_temp.name, "rb") as f:
            file_data = f.read()
        print(f"[VIDEO_SERVICE] Read {len(file_data)} bytes from exported video")

        # Используем upsert для перезаписи файла если он уже существует
        print(f"[VIDEO_SERVICE] Uploading to Supabase Storage...")
        res = supabase.storage.from_("videos").upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": "video/mp4", "upsert": "true"}
        )
        print(f"[VIDEO_SERVICE] Upload complete!")

        # Получаем публичный URL
        try:
            public_url = supabase.storage.from_("videos").get_public_url(file_name)
            print(f"[VIDEO_SERVICE] Got public URL: {public_url}")
            return public_url
        except Exception as e:
            # Fallback: создаем signed URL на 1 год
            print(f"[VIDEO_SERVICE] get_public_url failed ({str(e)}), falling back to signed URL")
            signed_url = supabase.storage.from_("videos").create_signed_url(
                file_name,
                expires_in=31536000  # 1 год в секундах
            )
            print(f"[VIDEO_SERVICE] Got signed URL: {signed_url['signedURL']}")
            return signed_url['signedURL']

    except Exception as e:
        print(f"[VIDEO_SERVICE] ERROR during video creation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to create video: {str(e)}")

    finally:
        # Очищаем все временные файлы
        print(f"[VIDEO_SERVICE] Cleaning up {len(temp_files)} temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                    print(f"[VIDEO_SERVICE] Deleted temp file: {temp_file}")
                except Exception as cleanup_error:
                    print(f"[VIDEO_SERVICE] Failed to delete temp file {temp_file}: {str(cleanup_error)}")
        print(f"[VIDEO_SERVICE] Cleanup complete")


def create_solid_color_image(width: int, height: int, color: tuple) -> str:
    """
    Создает изображение сплошного цвета и возвращает путь к временному файлу

    Args:
        width: Ширина изображения
        height: Высота изображения
        color: RGB цвет (r, g, b)

    Returns:
        str: Путь к временному файлу
    """
    img = Image.new('RGB', (width, height), color)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    img.save(temp_file.name, quality=95)
    temp_file.close()
    return temp_file.name


def resize_and_crop(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Изменяет размер и обрезает изображение до целевого соотношения сторон

    Args:
        img: PIL Image объект
        target_width: Целевая ширина
        target_height: Целевая высота

    Returns:
        Image.Image: Обработанное изображение
    """
    target_ratio = target_width / target_height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Изображение шире целевого - обрезаем по ширине
        new_height = target_height
        new_width = int(new_height * img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Обрезаем по центру
        left = (new_width - target_width) // 2
        img_cropped = img_resized.crop((left, 0, left + target_width, target_height))
    else:
        # Изображение выше целевого - обрезаем по высоте
        new_width = target_width
        new_height = int(new_width / img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Обрезаем по центру
        top = (new_height - target_height) // 2
        img_cropped = img_resized.crop((0, top, target_width, top + target_height))

    return img_cropped


def add_subtitles_to_video(video_clip, srt_content: str):
    """
    Добавляет субтитры на видео (упрощенная версия)

    Args:
        video_clip: VideoClip объект
        srt_content: Содержимое SRT файла

    Returns:
        CompositeVideoClip с субтитрами
    """
    # Парсим SRT контент
    subtitles = parse_srt(srt_content)

    text_clips = []

    for subtitle in subtitles:
        text_clip = TextClip(
            subtitle["text"],
            fontsize=40,
            color="white",
            bg_color="black",
            size=(video_clip.w - 100, None),
            method="caption"
        ).set_position(("center", "bottom")).set_start(subtitle["start"]).set_duration(
            subtitle["end"] - subtitle["start"]
        )

        text_clips.append(text_clip)

    # Комбинируем видео с текстовыми клипами
    if text_clips:
        return CompositeVideoClip([video_clip] + text_clips)

    return video_clip


def parse_srt(srt_content: str) -> List[Dict]:
    """
    Парсит SRT контент в список субтитров

    Args:
        srt_content: Содержимое SRT файла

    Returns:
        List[Dict]: Список с временем и текстом субтитров
    """
    subtitles = []
    blocks = srt_content.strip().split("\n\n")

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            # Парсим временные метки
            time_line = lines[1]
            start_str, end_str = time_line.split(" --> ")

            start_seconds = parse_srt_time(start_str)
            end_seconds = parse_srt_time(end_str)

            # Текст субтитра
            text = "\n".join(lines[2:])

            subtitles.append({
                "start": start_seconds,
                "end": end_seconds,
                "text": text
            })

    return subtitles


def parse_srt_time(time_str: str) -> float:
    """Парсит время из SRT формата в секунды"""
    time_str = time_str.strip()
    # Формат: HH:MM:SS,mmm
    hours, minutes, seconds = time_str.split(":")
    seconds, millis = seconds.split(",")

    total_seconds = (
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds) +
        int(millis) / 1000
    )

    return total_seconds
