// composables/useApi.js
export const useApi = () => {
  const config = useRuntimeConfig()
  const supabase = useSupabaseClient() 

  const getAuthHeader = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.access_token) return {}
    return { Authorization: `Bearer ${session.access_token}` }
  }

  const apiFetch = async (endpoint, options = {}) => {
    const headers = await getAuthHeader()
    let baseUrl = config.public.apiBase
    
    if (!baseUrl.endsWith('/api/v1')) {
        if (baseUrl.endsWith('/')) {
            baseUrl = baseUrl.slice(0, -1)
        }
        baseUrl = baseUrl + '/api/v1'
    }
    
    const finalEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const fullUrl = baseUrl + finalEndpoint
    
    const response = await $fetch(fullUrl, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
      onResponseError({ response }) {
        if (response.status === 401) {
          navigateTo('/login')
        }
      }
    })

    return response
  }

  // ========== ГЕНЕРАЦИЯ СЦЕНАРИЯ ==========
  const generateScript = async (request) => {
    const payload = {
      prompt: request.prompt,
      genre: request.genre || null,
      style: request.style || 'cinematic',
      time: request.time || 30
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

  // ========== ПОЛУЧЕНИЕ ПРОЕКТОВ ==========
  const getUserProjects = async () => {
    return await apiFetch('/projects')
  }

  // ========== ПОЛУЧЕНИЕ ПРОЕКТА ==========
  const getProject = async (id) => {
    return await apiFetch(`/projects/${id}`)
  }

  // ========== ГЕНЕРАЦИЯ ВСЕХ ИЗОБРАЖЕНИЙ (НОВОЕ!) ==========
  const generateImages = async (projectId) => {
    try {
      return await apiFetch(`/generate-image/${projectId}`, {
        method: 'POST'
      })
    } catch (error) {
      console.error('Ошибка генерации изображений:', error)
      throw new Error(error.data?.detail || 'Не удалось сгенерировать изображения')
    }
  }

  // ========== ОБНОВЛЕНИЕ СЦЕНЫ (НОВОЕ!) ==========
  const updateScene = async (sceneId, updates) => {
    try {
      return await apiFetch(`/scenes/${sceneId}`, {
        method: 'PUT',
        body: updates
      })
    } catch (error) {
      console.error('Ошибка обновления сцены:', error)
      throw new Error(error.data?.detail || 'Не удалось обновить сцену')
    }
  }

  // ========== ПЕРЕГЕНЕРАЦИЯ СЦЕНЫ (НОВОЕ!) ==========
  const regenerateScene = async (sceneId, style = null) => {
    try {
      const body = style ? { style } : {}
      return await apiFetch(`/regenerate-scene/${sceneId}`, {
        method: 'POST',
        body
      })
    } catch (error) {
      console.error('Ошибка перегенерации сцены:', error)
      throw new Error(error.data?.detail || 'Не удалось перегенерировать изображение')
    }
  }

  // ========== ОБНОВЛЕНИЕ МЕТАДАННЫХ ПРОЕКТА (НОВОЕ!) ==========
  const updateProject = async (projectId, updates) => {
    try {
      return await apiFetch(`/projects/${projectId}`, {
        method: 'PUT',
        body: updates
      })
    } catch (error) {
      console.error('Ошибка обновления проекта:', error)
      throw new Error(error.data?.detail || 'Не удалось обновить проект')
    }
  }

  // ========== УДАЛЕНИЕ ПРОЕКТА (НОВОЕ!) ==========
  const deleteProject = async (projectId) => {
    try {
      // TODO: Добавить DELETE /projects/{project_id} на бэкенде
      console.warn('DELETE endpoint не реализован на бэкенде')
      throw new Error('Функция удаления пока не реализована')
    } catch (error) {
      throw new Error(error.message || 'Не удалось удалить проект')
    }
  }

  // ========== РЕНДЕРИНГ (для будущего Модуля 2) ==========
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
  
  const getRenderStatus = async (projectId) => {
    try {
      return await apiFetch(`/projects/${projectId}/status`)
    } catch (error) {
      throw new Error(error.data?.detail || 'Не удалось получить статус')
    }
  }

  return {
    generateScript,
    getUserProjects,
    getProject,
    generateImages,        // НОВОЕ
    updateScene,          // НОВОЕ
    regenerateScene,      // НОВОЕ
    updateProject,        // НОВОЕ
    deleteProject,        // НОВОЕ
    generateVoiceover,
    startRender,
    getRenderStatus
  }
}