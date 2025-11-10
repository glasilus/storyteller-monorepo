<template>
  <div class="bg-base-200 rounded-xl p-6 shadow-lg border-l-4 border-primary">
    <div class="flex justify-between items-start mb-4">
      <div class="flex items-center gap-3">
        <div class="bg-primary text-primary-content rounded-full w-12 h-12 flex items-center justify-center font-bold text-lg">
          {{ scene.scene_number }}
        </div>
        <div>
          <h3 class="font-bold text-lg">Сцена {{ scene.scene_number }}</h3>
          <span class="text-sm opacity-70">{{ scene.duration }} секунд</span>
        </div>
      </div>
      <button class="btn btn-ghost btn-sm btn-circle" @click="$emit('delete')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- БЛОК: Описание действия -->
    <div class="mb-5">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎬</span>
        <label class="label-text font-bold text-base">Описание действия</label>
      </div>
      <textarea 
        v-model="localScene.action"
        class="textarea textarea-bordered w-full min-h-[100px] text-sm"
        placeholder="Что происходит на экране? Подробно опишите действия, выражения, движения..."
        @blur="saveChanges"
      ></textarea>
    </div>

    <!-- БЛОК: Диалоги -->
    <div class="mb-5" v-if="localScene.dialogues !== undefined">
      <div class="flex items-center gap-2 mb-3">
        <span class="text-2xl">💬</span>
        <label class="label-text font-bold text-base">Диалоги персонажей</label>
      </div>
      <div class="space-y-3 pl-6 border-l-2 border-base-300">
        <div 
          v-for="(dialogue, index) in localScene.dialogues" 
          :key="index"
          class="flex gap-2 items-center"
        >
          <div class="flex-1 relative">
            <input 
              v-model="localScene.dialogues[index]"
              class="input input-bordered w-full pl-8 text-sm"
              placeholder="Реплика персонажа..."
              @blur="saveChanges"
            />
            <span class="absolute left-2 top-3 text-base">🗣️</span>
          </div>
          <button 
            class="btn btn-ghost btn-circle btn-sm" 
            @click="removeDialogue(index)"
          >
            ✕
          </button>
        </div>
        <button 
          class="btn btn-outline btn-sm btn-block justify-start gap-2"
          @click="addDialogue"
        >
          <span class="text-xl">+</span>
          Добавить реплику
        </button>
      </div>
    </div>

    <!-- БЛОК: Текст за кадром (VOICEOVER) -->
    <div class="mb-5" v-if="localScene.voiceover !== undefined">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">🎙️</span>
        <label class="label-text font-bold text-base">Текст за кадром (Voiceover)</label>
      </div>
      <textarea 
        v-model="localScene.voiceover"
        class="textarea textarea-bordered w-full min-h-[80px] text-sm font-mono bg-base-300"
        placeholder="Текст, который будет озвучен поверх видео..."
        @blur="saveChanges"
      ></textarea>
    </div>

    <!-- БЛОК: Технические заметки -->
    <div class="mb-5" v-if="localScene.notes !== undefined">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-2xl">📝</span>
        <label class="label-text font-bold text-base">Технические заметки</label>
      </div>
      <textarea 
        v-model="localScene.notes"
        class="textarea textarea-bordered w-full min-h-[60px] text-xs opacity-80"
        placeholder="Примечания для режиссера: ракурс, свет, эффекты..."
        @blur="saveChanges"
      ></textarea>
    </div>

    <!-- КНОПКИ ДЕЙСТВИЙ -->
    <div class="flex gap-2 mt-6 pt-4 border-t border-base-300">
      <button 
        class="btn btn-primary flex-1 btn-sm" 
        @click="regenerateImage"
        :disabled="props.isGeneratingImage"
      >
        <span class="loading loading-spinner" v-if="props.isGeneratingImage"></span>
        {{ props.isGeneratingImage ? 'Генерация...' : '🎨 Перегенерить картинку' }}
      </button>
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

const localScene = ref({ ...props.scene })

watch(() => props.scene, (newVal) => {
  localScene.value = { ...newVal }
}, { deep: true })

const saveChanges = () => {
  emit('update', localScene.value)
}

const addDialogue = () => {
  if (!localScene.value.dialogues) {
    localScene.value.dialogues = []
  }
  localScene.value.dialogues.push('')
  saveChanges()
}

const removeDialogue = (index) => {
  localScene.value.dialogues.splice(index, 1)
  saveChanges()
}

const regenerateImage = () => {
  emit('regenerate-image', {
    sceneNumber: localScene.value.scene_number,
    style: 'cinematic'
  })
}
</script>