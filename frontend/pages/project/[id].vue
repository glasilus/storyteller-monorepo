<template>
  <div>
    <AppHeader />
    
    <main class="container mx-auto px-4 py-4 max-w-7xl">
      <!-- Шапка проекта -->
      <div class="bg-base-200 rounded-lg p-4 mb-4 shadow-lg">
        <input 
          v-model="project.title"
          class="input input-ghost text-2xl font-bold w-full mb-2"
          placeholder="Название проекта"
          @blur="saveProject"
        />
        <textarea 
          v-model="project.description"
          class="textarea textarea-ghost w-full"
          placeholder="Опишите вашу идею для видео..."
          rows="2"
          @blur="saveProject"
        ></textarea>
        
        <div class="flex gap-4 mt-4 flex-wrap">
          <select v-model="project.settings.tone" class="select select-bordered select-sm" @change="saveProject">
            <option value="humorous">Юмористический</option>
            <option value="formal">Формальный</option>
            <option value="friendly">Дружелюбный</option>
            <option value="dramatic">Драматичный</option>
            <option value="educational">Образовательный</option>
          </select>
          
          <select v-model="project.settings.style" class="select select-bordered select-sm" @change="saveProject">
            <option value="cinematic">Кинематографичный</option>
            <option value="cartoon">Мультфильм</option>
            <option value="pixel-art">Пиксель-арт</option>
            <option value="realistic">Реалистичный</option>
            <option value="minimalist">Минимализм</option>
          </select>
          
          <input 
            v-model.number="project.settings.duration"
            type="number"
            class="input input-bordered input-sm w-24"
            placeholder="Длительность"
            @blur="saveProject"
          />
          <span class="self-center text-sm">секунд</span>
        </div>
        
        <div class="flex gap-2 mt-4">
          <button 
            class="btn btn-primary" 
            @click="handleGenerateScript"
            :disabled="generatingScript"
          >
            <span class="loading loading-spinner" v-if="generatingScript"></span>
            {{ generatingScript ? 'Генерирую...' : '📝 Сгенерировать сценарий' }}
          </button>
          
          <button 
            class="btn btn-secondary" 
            @click="generateAllImages"
            :disabled="generatingImages || !project.script?.scenes?.length"
          >
            <span class="loading loading-spinner" v-if="generatingImages"></span>
            {{ generatingImages ? 'Генерирую...' : '🎨 Сгенерировать все изображения' }}
          </button>
        </div>
      </div>

      <!-- Редактор сцен -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="space-y-4">
          <h2 class="text-xl font-bold flex items-center gap-2">
            📋 Сцены
            <span class="badge badge-primary" v-if="project.script?.scenes?.length">
              {{ project.script.scenes.length }}
            </span>
          </h2>
          
          <div v-if="!project.script?.scenes?.length" class="bg-base-200 rounded-lg p-8 text-center">
            <div class="text-4xl mb-4 opacity-30">📝</div>
            <p class="opacity-70">Сценарий еще не сгенерирован</p>
            <p class="text-sm opacity-50 mt-2">Нажмите кнопку выше</p>
          </div>
          
          <SceneEditor 
            v-for="scene in project.script?.scenes || []"
            :key="scene.scene_number"
            :scene="scene"
            :is-generating-image="imageGenerationStates[scene.scene_number]?.isGenerating"
            @update="updateScene"
            @delete="deleteScene(scene.scene_number)"
            @regenerate-image="handleRegenerateSingleImage"
          />
        </div>
        
        <div>
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
            🖼️ Раскадровка
            <span class="badge badge-secondary" v-if="project.script?.scenes?.length">
              {{ project.script.scenes.length }}
            </span>
          </h2>
          
          <div class="space-y-4 max-h-screen overflow-y-auto">
            <div 
              v-for="scene in project.script?.scenes || []" 
              :key="`image-${scene.scene_number}`"
              class="h-64"
            >
              <ImageGenerator
                :scene-number="scene.scene_number"
                :image-url="project.images[scene.scene_number]"
                :prompt="project.imagePrompts[scene.scene_number]"
                :is-generating="imageGenerationStates[scene.scene_number]?.isGenerating"
                @regenerate="handleRegenerateSingleImage"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const { generateScript, generateSceneImage, saveProject: apiSaveProject, getProject } = useApi()
const { requireAuth } = useSupabaseAuth()
const route = useRoute()
const router = useRouter()

// Состояние проекта
const project = ref({
  title: 'Новый проект',
  description: '',
  settings: {
    tone: 'friendly',
    style: 'cinematic',
    duration: 30
  },
  script: null,
  images: {},
  imagePrompts: {}
})

const imageGenerationStates = ref({})
const generatingScript = ref(false)
const generatingImages = ref(false)

// Проверка авторизации
onMounted(async () => {
  if (!requireAuth()) return
  
  if (route.params.id !== 'new') {
    await loadProject(route.params.id)
  }
})

const loadProject = async (id) => {
  try {
    const loadedProject = await getProject(id)
    project.value = {
      ...loadedProject,
      settings: loadedProject.settings || {
        tone: 'friendly',
        style: 'cinematic',
        duration: 30
      }
    }
  } catch (error) {
    console.error('Ошибка загрузки проекта:', error)
    alert('Не удалось загрузить проект')
  }
}

const handleGenerateScript = async () => {
  if (!project.value.description.trim()) {
    alert('Опишите вашу идею для видео')
    return
  }

  generatingScript.value = true
  
  try {
    const result = await generateScript(project.value.description, {
      tone: project.value.settings.tone,
      duration: project.value.settings.duration,
      style: project.value.settings.style
    })
    
    project.value.script = result.script
    project.value.title = result.script.title || project.value.title
    
    // Сбросить старые изображения
    project.value.images = {}
    project.value.imagePrompts = {}
    
    await saveProject()
  } catch (error) {
    alert(error.message)
  } finally {
    generatingScript.value = false
  }
}

const updateScene = (updatedScene) => {
  const index = project.value.script.scenes.findIndex(s => s.scene_number === updatedScene.scene_number)
  if (index !== -1) {
    project.value.script.scenes[index] = updatedScene
    saveProject()
  }
}

const deleteScene = (sceneNumber) => {
  if (!confirm('Удалить сцену?')) return
  
  project.value.script.scenes = project.value.script.scenes.filter(s => s.scene_number !== sceneNumber)
  // Перенумеровать сцены
  project.value.script.scenes.forEach((scene, index) => {
    scene.scene_number = index + 1
  })
  saveProject()
}

const handleRegenerateSingleImage = async ({ sceneNumber, style }) => {
  const scene = project.value.script.scenes.find(s => s.scene_number === sceneNumber)
  if (!scene) return

  imageGenerationStates.value[sceneNumber] = { isGenerating: true }
  
  try {
    const result = await generateSceneImage(scene, style || project.value.settings.style)
    project.value.images[sceneNumber] = result.image_url
    project.value.imagePrompts[sceneNumber] = result.prompt
  } catch (error) {
    alert(`Ошибка генерации изображения: ${error.message}`)
  } finally {
    imageGenerationStates.value[sceneNumber].isGenerating = false
    saveProject()
  }
}

const generateAllImages = async () => {
  if (!project.value.script?.scenes?.length) return
  
  generatingImages.value = true
  
  for (const scene of project.value.script.scenes) {
    await handleRegenerateSingleImage({ 
      sceneNumber: scene.scene_number, 
      style: project.value.settings.style 
    })
  }
  
  generatingImages.value = false
}

const saveProject = async () => {
  try {
    const result = await apiSaveProject(project.value)
    // Обновить ID если это новый проект
    if (route.params.id === 'new' && result.id) {
      router.replace(`/project/${result.id}`)
    }
  } catch (error) {
    console.error('Ошибка сохранения проекта:', error)
  }
}
</script>