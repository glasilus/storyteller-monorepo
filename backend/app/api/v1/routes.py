from fastapi import APIRouter, HTTPException, Depends
from app.service.gemini_script import generate_script
from app.service.image_script import generate_image
from .shemas import ScriptRequest, SceneListResponse, SceneUpdateRequest
from app.db.supa_request import (
    
    create_project_with_scenes, 
    get_project, 
    get_project_scenes, 
    get_all_projects, 
    get_visual_promt_by_project, 
    update_scene_image_url, 
    update_scene, 
    get_scenes_by_project,
    delete_project_by_id,
    supabase
)
from app.db.auth import get_current_user

router = APIRouter()

# ========== ГЕНЕРАЦИЯ СЦЕНАРИЯ ==========
@router.post("/generate-script")
async def generate_script_endpoint(request: ScriptRequest, 
    user_id: str = Depends(get_current_user)):
    
    result = await generate_script(request.prompt, request.genre, request.style, request.time)
    
    if not result:
        raise HTTPException(status_code=500, detail="Script generation failed")

    try:
        project_id = create_project_with_scenes(
            script=result, 
            user_prompt=request.prompt,
            time=request.time, 
            genre=request.genre, 
            style=request.style,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

    return {
        "project_id": project_id,
        "script": result
    }


# ========== ПОЛУЧЕНИЕ ПРОЕКТОВ ==========
@router.get("/projects")
async def get_all_projects_endpoint(user_id: str = Depends(get_current_user)):
    try:
        projects = get_all_projects(user_id) 
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load projects: {str(e)}")


# ========== ПОЛУЧЕНИЕ ПРОЕКТА (ИСПРАВЛЕНО!) ==========
@router.get("/projects/{project_id}")
async def get_project_endpoint(project_id: str, user_id: str = Depends(get_current_user)):
    """
    ИЗМЕНЕНИЕ: Возвращает scenes на верхнем уровне с id и generated_image_url
    """
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    scenes = get_project_scenes(project_id) or []

    return {
        "id": project_id,
        "title": project.get("title"),
        "description": project.get("description"),
        "intro": project.get("intro"),
        "settings": {
            "tone": project.get("tone") or "",     
            "style": project.get("style") or "",   
            "duration": project.get("project_time") or 30 
        },
        "scenes": [
            {
                "id": s.get("id"),                              # ← ДОБАВЛЕНО
                "scene_number": s.get("scene_number"),
                "action": s.get("action") or "",
                "dialogue": s.get("dialogue") or "",
                "voice_over": s.get("voice_over") or "",
                "visual_prompt": s.get("visual_prompt") or "",
                "generated_image_url": s.get("generated_image_url")  # ← ДОБАВЛЕНО
            } for s in scenes
        ]
    }


# ========== ГЕНЕРАЦИЯ ВСЕХ ИЗОБРАЖЕНИЙ ==========
@router.post("/generate-image/{project_id}")
async def generate_images(project_id: str, user_id: str = Depends(get_current_user)):
    scenes = get_visual_promt_by_project(project_id)

    if not scenes:
        raise HTTPException(status_code=404, detail="No scenes found for this project")
    
    result = []

    for scene in scenes:
        promt = scene.get("visual_prompt")
        image_url = await generate_image(promt)
        update_scene_image_url(scene["id"], image_url)
        result.append({
            "scene_id": scene["id"],
            "promt": promt,
            "generated_image_url": image_url
        })

    return {
        "project_id": project_id,
        "scenes": result
    }


# ========== ОБНОВЛЕНИЕ ОДНОЙ СЦЕНЫ (НОВЫЙ РОУТ!) ==========
@router.put("/scenes/{scene_id}")
async def update_scene_endpoint(
    scene_id: str, 
    updates: dict,
    user_id: str = Depends(get_current_user)
):
    """
    НОВЫЙ РОУТ для автосохранения SceneEditor.
    Принимает: {"action": "...", "dialogue": "...", "voice_over": "...", "visual_prompt": "..."}
    """
    try:
        allowed_fields = {"action", "dialogue", "voice_over", "visual_prompt"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered_updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        res = supabase.table("scenes").update(filtered_updates).eq("id", scene_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Scene not found")
        
        return {"success": True, "scene_id": scene_id, "updated": res.data[0]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update scene: {str(e)}")


# ========== ПЕРЕГЕНЕРАЦИЯ ОДНОГО ИЗОБРАЖЕНИЯ (НОВЫЙ РОУТ!) ==========
@router.post("/regenerate-scene/{scene_id}")
async def regenerate_scene_endpoint(
    scene_id: str,
    request: dict = None,
    user_id: str = Depends(get_current_user)
):
    """
    НОВЫЙ РОУТ для перегенерации одной сцены.
    Опционально: {"style": "pixel art"} для изменения стиля
    """
    try:
        scene = supabase.table("scenes").select("visual_prompt").eq("id", scene_id).single().execute()
        if not scene.data:
            raise HTTPException(status_code=404, detail="Scene not found")
        
        visual_prompt = scene.data.get("visual_prompt", "")
        
        # Если передан модификатор стиля
        if request and request.get("style"):
            visual_prompt = f"{request['style']}, {visual_prompt}"
        
        image_url = await generate_image(visual_prompt)
        update_scene_image_url(scene_id, image_url)
        
        return {
            "success": True,
            "scene_id": scene_id,
            "generated_image_url": image_url
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate: {str(e)}")


# ========== ОБНОВЛЕНИЕ МЕТАДАННЫХ ПРОЕКТА (НОВЫЙ РОУТ!) ==========
@router.put("/projects/{project_id}")
async def update_project_metadata(
    project_id: str,
    updates: dict,
    user_id: str = Depends(get_current_user)
):
    """
    НОВЫЙ РОУТ для обновления title, description, tone, style, project_time
    """
    try:
        allowed_fields = {"title", "description", "intro", "tone", "style", "project_time"}
        filtered = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        res = supabase.table("projects").update(filtered).eq("id", project_id).eq("user_id", user_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        return {"success": True, "updated": res.data[0]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


# ========== СТАРЫЕ РОУТЫ (для обратной совместимости) ==========

@router.get("/{project_id}/scenes", response_model=SceneListResponse)
async def get_project_scenes_legacy(project_id: str):
    """[DEPRECATED] Используйте GET /projects/{project_id}"""
    try:
        scenes = get_scenes_by_project(str(project_id))
        if not scenes:
            raise HTTPException(status_code=404, detail="Scenes not found")
        return {"project_id": project_id, "scenes": scenes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scenes: {str(e)}")


@router.put("/{project_id}/scenes")
async def update_project_scenes(project_id: str, request: SceneUpdateRequest):
    """[DEPRECATED] Используйте PUT /scenes/{scene_id}"""
    try:
        updated_scenes = []
        for scene in request.scenes:
            update_data = scene.dict(exclude_unset=True)
            updated = update_scene(project_id, scene.scene_number, update_data)
            updated_scenes.append(updated)
        return {"message": "Scenes updated successfully", "updated_scenes": updated_scenes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update scenes: {str(e)}")


@router.put("/regenerate_images/{project_id}")
async def regenerate_images(project_id: str, user_id: str = Depends(get_current_user)):
    """[DEPRECATED] Используйте POST /regenerate-scene/{scene_id}"""
    try:
        scenes = get_visual_promt_by_project(project_id)
        if not scenes:
            raise HTTPException(status_code=404, detail="No scenes found")
        
        result = []
        for scene in scenes:
            promt = scene.get("visual_prompt")
            image_url = await generate_image(promt)
            update_scene_image_url(scene["id"], image_url)
            result.append({
                "scene_id": scene["id"],
                "promt": promt,
                "generated_image_url": image_url
            })
        
        return {"project_id": project_id, "scenes": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate images: {str(e)}")
    

## Delete scene by scene_id
@router.delete("/scenes/{scene_id}")
async def delete_scene_endpoint(scene_id: str, user_id: str = Depends(get_current_user)):
    """
    Delete a scene by ID
    """
    try:
        res = supabase.table("scenes").delete().eq("id", scene_id).execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Scene not found or already deleted")

        return {"success": True, "message": "Scene deleted successfully", "scene_id": scene_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete scene: {str(e)}")


## Delete project by project_id
@router.delete("/projects/{project_id}")
async def delete_project_endpoint(project_id: str, user_id: str = Depends(get_current_user)):

    res = delete_project_by_id(project_id)

    if not res:
        raise HTTPException(status_code=404, detail="Project not found or already deleted")

    return {"success": True, "message": "Project and scenes deleted successfully", "project_id": project_id}

