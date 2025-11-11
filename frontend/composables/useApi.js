// composables/useApi.js
import { z } from 'zod'

// Схемы валидации ответов
const SceneSchema = z.object({
  scene_number: z.number(),
  action: z.string(),
  dialogues: z.array(z.string()).optional(),
  voiceover: z.string().optional(),
  notes: z.string().optional(),
  duration: z.number().optional()
})

const ScriptSchema = z.object({
  title: z.string(),
  description: z.string(),
  tone: z.string(),
  target_audience: z.string().optional(),
  scenes: z.array(SceneSchema)
})

const ImageGenerationSchema = z.object({
  scene_id: z.number(),
  image_url: z.string(),
  prompt: z.string(),
  style: z.string()
})

export const useApi = () => {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient() 

  const getAuthHeader = async () => {
    // Получаем сессию через auth клиент
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return {}
    return { Authorization: `Bearer ${session.access_token}` }
  }

  /*const apiFetch = async (endpoint, options = {}) => {
    const headers = await getAuthHeader()
    
    return $fetch(`${config.public.apiBase}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
        ...options.headers
      }
    })
  }*/

  const apiFetch = async (endpoint, options = {}) => { //ВРЕМЕННАЯ МЕРА
    const headers = await getAuthHeader()

    // ❗ 1. Получаем базовый URL (например, 'https://storyteller-monorepo.onrender.com')
    let baseUrl = config.public.apiBase;
    
    // ❗ 2. ГАРАНТИРУЕМ ПРИСУТСТВИЕ ПРЕФИКСА: Добавляем '/api/v1', ес
    if (!baseUrl.endsWith('/api/v1')) {
        // Убеждаемся, что baseUrl не заканчивается на слэш, чтобы избежать двойного слэша
        if (baseUrl.endsWith('/')) {
            baseUrl = baseUrl.slice(0, -1);
        }
        baseUrl = baseUrl + '/api/v1';
    }
    
    // 3. Убеждаемся, что endpoint начинается со слэша
    const finalEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    // 4. Формируем полный URL для запроса
    const fullUrl = baseUrl + finalEndpoint
    
    const response = await $fetch(fullUrl, {
      // Использование fullUrl вместо baseURL
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
      // Обработка ошибок
      onResponseError({ response }) {
        if (response.status === 401) {
          // Если 401 Unauthorized, перенаправляем на логин
          navigateTo('/login');
        }
      }
    })

    return response
  }

  // Генерация сценария
  const generateScript = async (idea, options = {}) => {

    const payload = {
      prompt: idea,                             // твоя идея текста
      genre: options.genre || null,            // если не нужно — можно null
      style: options.style || 'cinematic',
      time: options.duration || 30             // длительность в секундах (float)
    }

    try {
      return await apiFetch('/generate-script', {
        method: 'POST',
        body: payload
      })
    } catch (error) {
      console.error('Ошибка генерации сценария:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать сценарий')
    }
  }

  // Генерация изображения для сцены
  const generateSceneImage = async (scene, style = 'cinematic') => {
    try {
      return await apiFetch('/image/generate', {
        method: 'POST',
        body: {
          scene_description: scene.action,
          style,
          scene_number: scene.scene_number
        }
      })
    } catch (error) {
      console.error('Ошибка генерации изображения:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать изображение')
    }
  }

  // Сохранение проекта
  const saveProject = async (projectData) => {
    return await apiFetch('/projects', {
      method: 'POST',
      body: projectData
    })
  }

  // Получение проектов пользователя
  const getUserProjects = async () => {
    return await apiFetch('/projects')
  }

  // Получение конкретного проекта
  const getProject = async (id) => {
    return await apiFetch(`/projects/${id}`)
  }

  // Генерация озвучки
  const generateVoiceover = async (projectId, scenes) => {
    try {
      return await apiFetch(`/projects/${projectId}/voiceover`, {
        method: 'POST',
        body: { scenes }
      })
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось сгенерировать озвучку')
    }
  }
  
  // Запуск рендеринга видео
  const startRender = async (projectId, settings) => {
    try {
      return await apiFetch(`/projects/${projectId}/render`, {
        method: 'POST',
        body: settings
      })
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось запустить рендеринг')
    }
  }
  
  // Получение статуса рендеринга
  const getRenderStatus = async (projectId) => {
    try {
      return await apiFetch(`/projects/${projectId}/status`)
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось получить статус')
    }
  }

  return {
    generateScript,
    generateSceneImage,
    saveProject,
    getUserProjects,
    getProject,
    generateVoiceover,
    startRender,
    getRenderStatus
  }
}