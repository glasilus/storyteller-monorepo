<template>
  <div>
    <AppHeader />
    
    <main class="container mx-auto px-4 py-4 max-w-5xl">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">
          Рендеринг: {{ project?.title }}
        </h1>
        <NuxtLink 
          :to="`/project/${route.params.id}`"
          class="btn btn-outline"
        >
          ← Назад к сценарию
        </NuxtLink>
      </div>
      
      <!-- Шаги процесса -->
      <RenderSteps :current-status="renderStatus" class="mb-6" />
      
      <!-- Шаг 1: Озвучка -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6">
        <h2 class="text-xl font-bold mb-4">Шаг 1: Генерация озвучки</h2>
        
        <button 
          v-if="!audioUrl && !isGeneratingAudio"
          class="btn btn-primary"
          @click="generateVoiceover"
          :disabled="!project.script"
        >
          🎙️ Сгенерировать озвучку
        </button>
        
        <AppLoader 
          v-else-if="isGeneratingAudio"
          title="Генерируется озвучка..."
          subtitle="Это может занять до 30 секунд"
        />
        
        <AudioPlayer 
          v-else-if="audioUrl"
          :audio-url="audioUrl"
          title="Готовая озвучка"
        />
        
        <!-- Субтитры -->
        <div v-if="subtitles" class="mt-4 p-4 bg-base-300 rounded">
          <h4 class="font-semibold mb-2">Сгенерированные субтитры:</h4>
          <pre class="text-xs whitespace-pre-wrap">{{ subtitles }}</pre>
        </div>
      </div>
      
      <!-- Шаг 2: Выбор фона -->
      <BackgroundSelector 
        v-model="renderSettings.background"
        class="mb-6"
      />
      
      <!-- Шаг 3: Сборка видео -->
      <div class="bg-base-200 rounded-lg p-6 shadow-lg mb-6">
        <h2 class="text-xl font-bold mb-4">Шаг 3: Сборка видео</h2>
        
        <button 
          v-if="!videoUrl && status !== 'processing'"
          class="btn btn-primary btn-lg"
          @click="startRender"
          :disabled="!audioUrl || status === 'pending'"
        >
          🎬 Собрать видео
        </button>
        
        <AppLoader 
          v-else-if="status === 'processing'"
          title="Собираем ваше видео..."
          subtitle="Это может занять до 2 минут"
        />
        
        <VideoPlayer 
          v-else-if="videoUrl"
          :video-url="videoUrl"
          title="Готовое видео готово!"
        />
        
        <div v-if="error" class="alert alert-error mt-4">
          <span>❌ {{ error }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const route = useRoute()
const { generateVoiceover: apiGenerateVoiceover, startRender: apiStartRender, getRenderStatus } = useApi()
const { user } = useSupabaseAuth()

const project = ref(null)
const audioUrl = ref(null)
const subtitles = ref(null)
const isGeneratingAudio = ref(false)
const videoUrl = ref(null)
const status = ref('pending') // pending, voiceover, processing, done, failed
const error = ref(null)

const renderSettings = ref({
  background: 'minecraft'
})

// Проверка статуса при монтировании
onMounted(async () => {
  const projectId = route.params.id
  
  // Загружаем проект
  project.value = await $fetch(`/api/v1/projects/${projectId}`)
  
  // Проверяем, есть ли уже готовые файлы
  if (project.value.voiceover_url) {
    audioUrl.value = project.value.voiceover_url
    subtitles.value = project.value.subtitle_url ? await fetch(project.value.subtitle_url).then(r => r.text()) : null
    status.value = 'voiceover'
  }
  
  if (project.value.final_video_url) {
    videoUrl.value = project.value.final_video_url
    status.value = 'done'
  } else if (project.value.render_status === 'processing') {
    status.value = 'processing'
    pollStatus(projectId)
  }
})

const generateVoiceover = async () => {
  if (!project.value.script) return
  
  isGeneratingAudio.value = true
  
  try {
    const result = await apiGenerateVoiceover(route.params.id, project.value.script.scenes)
    audioUrl.value = result.audio_url
    subtitles.value = result.subtitles
    status.value = 'voiceover'
  } catch (err) {
    error.value = err.message
  } finally {
    isGeneratingAudio.value = false
  }
}

const startRender = async () => {
  status.value = 'processing'
  error.value = null
  
  try {
    await apiStartRender(route.params.id, renderSettings.value)
    pollStatus(route.params.id)
  } catch (err) {
    error.value = err.message
    status.value = 'failed'
  }
}

const pollStatus = async (projectId) => {
  const { start, stop } = usePolling(async () => {
    const result = await getRenderStatus(projectId)
    status.value = result.status
    
    if (result.status === 'done') {
      videoUrl.value = result.final_video_url
      stop()
    } else if (result.status === 'failed') {
      error.value = result.error
      stop()
    }
  }, 3000)
  
  start()
}
</script>