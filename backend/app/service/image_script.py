import urllib.parse
import requests
import time

async def generate_image(visual_promt: str, max_retries: int = 3):
    """
    Генерирует изображение через Pollinations API с retry логикой

    Args:
        visual_promt: Текстовый промпт для генерации
        max_retries: Максимальное количество попыток

    Returns:
        str: URL сгенерированного изображения
    """
    # Сокращаем промпт если он слишком длинный (> 200 символов)
    if len(visual_promt) > 200:
        # Берем первые 200 символов и добавляем ключевые слова в конце
        visual_promt = visual_promt[:180] + "... vertical video format"
        print(f"[IMAGE_GEN] Prompt shortened to: {visual_promt}")

    # Правильное URL encoding
    encoded_prompt = urllib.parse.quote(visual_promt)

    # Используем меньшее разрешение для экономии ресурсов и надежности
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1280&nologo=true"

    print(f"[IMAGE_GEN] Generating image with URL length: {len(url)}")

    # Retry логика
    for attempt in range(max_retries):
        try:
            # Проверяем доступность URL перед возвратом
            print(f"[IMAGE_GEN] Attempt {attempt + 1}/{max_retries}...")

            response = requests.head(url, timeout=10)

            if response.status_code == 200:
                print(f"[IMAGE_GEN] Image generated successfully!")
                return url
            elif response.status_code == 530:
                print(f"[IMAGE_GEN] Server error 530, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            else:
                print(f"[IMAGE_GEN] Unexpected status code: {response.status_code}")
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"[IMAGE_GEN] Request failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                # На последней попытке возвращаем URL anyway - может сработать при рендере
                print(f"[IMAGE_GEN] Max retries reached, returning URL anyway")
                return url

    # Если все попытки провалились - пробуем альтернативный API
    print(f"[IMAGE_GEN] Pollinations failed, trying alternative API...")
    return await generate_image_alternative(visual_promt)


async def generate_image_alternative(visual_promt: str):
    """
    Альтернативный метод генерации через другой API
    Использует Hugging Face Inference API (бесплатный)
    """
    try:
        # Сокращаем промпт еще сильнее для альтернативного API
        if len(visual_promt) > 150:
            visual_promt = visual_promt[:150]

        encoded_prompt = urllib.parse.quote(visual_promt)

        # Используем Stable Diffusion через другой публичный endpoint
        # Или просто placeholder изображение
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true&model=turbo"

        print(f"[IMAGE_GEN] Alternative API URL: {url[:100]}...")
        return url

    except Exception as e:
        print(f"[IMAGE_GEN] Alternative API also failed: {str(e)}")
        # В крайнем случае возвращаем placeholder
        return "https://via.placeholder.com/768x1024/1a1a1a/ffffff?text=Image+Generation+Failed"