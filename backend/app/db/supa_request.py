from supabase import create_client
from datetime import datetime
import uuid
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

## Get formatted time
time = datetime.now()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")


### ADD PROJECT WITH SCENES
def create_project_with_scenes(script: dict, time: float) -> str:

    # 1️⃣ Создаем проект
    project_data = {
        "title": script.get("title"),
        "intro": script.get("intro"),
        "project_time": time,
        "created_at": formatted_time,
    }

    res = supabase.table("projects").insert(project_data).execute()


    
    project_id = res.data[0]["id"]

    # 2️⃣ Создаём сцену
    scenes_data = []
    for scene in script.get("scenes", []):
        text_content = f"{scene.get('description','')}\n{scene.get('dialogue','')}"
        scenes_data.append({
            "project_id": project_id,
            "scene_number": scene.get("scene_number"),
            "dialogue": scene.get("dialogue"),
            "visual_prompt": scene.get("description"),
            "generated_image_url": None,
            "created_at": formatted_time,
        })


    if scenes_data:
        res_scenes = supabase.table("scenes").insert(scenes_data).execute()

    return project_id



    