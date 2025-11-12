<template>
  <div class="bg-base-200 rounded-lg p-4 shadow-lg h-full flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <span class="text-sm font-bold">Сцена {{ scene.scene_number }}</span>
      <div class="flex gap-2">
        <select v-model="selectedStyle" class="select select-bordered select-sm">
          <option value="">Стандартный</option>
          <option value="cinematic">Кинематографичный</option>
          <option value="cartoon">Мультфильм</option>
          <option value="pixel art">Пиксель-арт</option>
          <option value="realistic">Реалистичный</option>
          <option value="minimalist">Минимализм</option>
        </select>
        <button 
          class="btn btn-primary btn-sm" 
          @click="regenerateWithStyle"
          :disabled="isGenerating"
        >
          <span class="loading loading-spinner loading-xs" v-if="isGenerating"></span>
          🔄
        </button>
      </div>
    </div>

    <div class="flex-1 flex items-center justify-center bg-base-300 rounded-lg overflow-hidden">
      <!-- Загрузка -->
      <div v-if="isGenerating" class="text-center p-8">
        <span class="loading loading-spinner loading-lg text-primary mb-4"></span>
        <p class="text-sm opacity-70">Генерирую изображение...</p>
        <p class="text-xs opacity-50 mt-2">{{ progressText }}</p>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="text-center p-8">
        <div class="text-error text-6xl mb-4">⚠️</div>
        <p class="text-error mb-4">{{ error }}</p>
        <button class="btn btn-outline btn-error" @click="regenerateWithStyle">
          Попробовать снова
        </button>
      </div>

      <!-- Нет изображения -->
      <div v-else-if="!scene.generated_image_url" class="text-center p-8">
        <div class="text-6xl mb-4 opacity-30">🎨</div>
        <p class="text-sm opacity-70">Изображение еще не сгенерировано</p>
      </div>

      <!-- Изображение -->
      <img 
        v-else 
        :src="scene.generated_image_url" 
        :alt="`Сцена ${scene.scene_number}`"
        class="max-h-full max-w-full object-contain"
      />
    </div>

    <!-- Промпт -->
    <div v-if="scene.visual_prompt" class="mt-3 p-3 bg-base-300 rounded text-xs opacity-70 max-h-24 overflow-y-auto">
      <strong>Промпт:</strong> {{ scene.visual_prompt }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  scene: {
    type: Object,
    required: true
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['regenerate'])

const selectedStyle = ref('')
const progressText = ref('Обрабатываю запрос...')
const error = ref(null)

watch(() => props.isGenerating, (newVal) => {
  if (newVal) {
    error.value = null
    const progress = ['Анализ сцены...', 'Создание промпта...', 'Генерация изображения...', 'Обработка...']
    let i = 0
    const interval = setInterval(() => {
      progressText.value = progress[i % progress.length]
      i++
    }, 800)
    
    setTimeout(() => clearInterval(interval), 60000)
  }
})

const regenerateWithStyle = () => {
  error.value = null
  emit('regenerate', {
    sceneId: props.scene.id,  // ИСПРАВЛЕНО: передаём id вместо номера
    style: selectedStyle.value || null
  })
}
</script>