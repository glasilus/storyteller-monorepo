<template>
  <div class="bg-base-200 rounded-xl p-6 shadow-lg border-l-4 border-primary">
    <div class="flex justify-between items-start mb-4">
      <div class="flex items-center gap-3">
        <div class="bg-primary text-primary-content rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg">
          {{ scene.scene_number }}
        </div>
        <div>
          <h3 class="font-bold text-lg">Сцена {{ scene.scene_number }}</h3>
          <p class="text-xs opacity-60" v-if="isSaving">💾 Сохранение...</p>
          <p class="text-xs text-success" v-else-if="lastSaved">✓ Сохранено {{ lastSaved }}</p>
        </div>
      </div>
      <button class="btn btn-ghost btn-sm btn-circle" @click="$emit('delete', scene.id)">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Описание действия -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎬</span>
        <label class="label-text font-bold text-base">Описание действия</label>
      </div>
      <textarea 
        v-model="localScene.action"
        class="textarea textarea-bordered w-full min-h-[100px] text-sm"
        placeholder="Что происходит на экране?"
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Диалоги -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">💬</span>
        <label class="label-text font-bold text-base">Диалоги персонажей</label>
      </div>
      <textarea 
        v-model="localScene.dialogue"
        class="textarea textarea-bordered w-full min-h-[60px] text-sm"
        placeholder="Реплики персонажей..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Текст за кадром -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎙️</span>
        <label class="label-text font-bold text-base">Текст за кадром (Voiceover)</label>
      </div>
      <textarea 
        v-model="localScene.voice_over"
        class="textarea textarea-bordered w-full min-h-[80px] text-sm font-mono bg-base-300"
        placeholder="Текст для озвучки..."
        @input="debounceSave"
      ></textarea>
    </div>

    <!-- Визуальный промпт -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎨</span>
        <label class="label-text font-bold text-base">Визуальный промпт</label>
      </div>
      <textarea 
        v-model="localScene.visual_prompt"
        class="textarea textarea-bordered w-full min-h-[60px] text-xs opacity-80"
        placeholder="Описание кадра для ИИ-художника (на английском)..."
        @input="debounceSave"
      ></textarea>
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
  isGeneratingImage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update', 'delete', 'regenerate-image'])

const localScene = ref({ 
  id: props.scene.id,
  scene_number: props.scene.scene_number || 1,
  action: props.scene.action || '',
  dialogue: props.scene.dialogue || '',
  voice_over: props.scene.voice_over || '',
  visual_prompt: props.scene.visual_prompt || ''
})

const isSaving = ref(false)
const lastSaved = ref('')
let saveTimeout = null

watch(() => props.scene, (newVal) => {
  localScene.value = { 
    id: newVal.id,
    scene_number: newVal.scene_number || 1,
    action: newVal.action || '',
    dialogue: newVal.dialogue || '',
    voice_over: newVal.voice_over || '',
    visual_prompt: newVal.visual_prompt || ''
  }
}, { deep: true })

const debounceSave = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  isSaving.value = true
  saveTimeout = setTimeout(() => {
    saveChanges()
  }, 800)
}

const saveChanges = () => {
  emit('update', {
    id: localScene.value.id,
    scene_number: localScene.value.scene_number,
    action: localScene.value.action,
    dialogue: localScene.value.dialogue,
    voice_over: localScene.value.voice_over,
    visual_prompt: localScene.value.visual_prompt
  })
  
  isSaving.value = false
  lastSaved.value = new Date().toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
  
  setTimeout(() => {
    lastSaved.value = ''
  }, 3000)
}
</script>