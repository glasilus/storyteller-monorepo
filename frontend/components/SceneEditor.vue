<template>
  <div class="bg-base-200 rounded-lg p-4 shadow-lg">
    <div class="flex justify-between items-start mb-4">
      <h3 class="text-lg font-bold">
        Сцена {{ scene.scene_number }}
        <span class="text-sm font-normal opacity-70">({{ scene.duration }} сек)</span>
      </h3>
      <button class="btn btn-ghost btn-sm" @click="$emit('delete')">✕</button>
    </div>

    <div class="form-control mb-4">
      <label class="label">
        <span class="label-text">Описание действия</span>
      </label>
      <textarea 
        v-model="localScene.action"
        class="textarea textarea-bordered h-24"
        placeholder="Что происходит в сцене?"
        @blur="saveChanges"
      ></textarea>
    </div>

    <div class="form-control mb-4" v-if="localScene.dialogues">
      <label class="label">
        <span class="label-text">Диалоги</span>
      </label>
      <div v-for="(dialogue, index) in localScene.dialogues" :key="index" class="flex gap-2 mb-2">
        <input 
          v-model="localScene.dialogues[index]"
          class="input input-bordered flex-1"
          placeholder="Реплика персонажа"
          @blur="saveChanges"
        />
        <button class="btn btn-ghost btn-sm" @click="removeDialogue(index)">✕</button>
      </div>
      <button class="btn btn-outline btn-sm mt-2" @click="addDialogue">
        + Добавить реплику
      </button>
    </div>

    <div class="form-control mb-4">
      <label class="label">
        <span class="label-text">За кадром (voiceover)</span>
      </label>
      <textarea 
        v-model="localScene.voiceover"
        class="textarea textarea-bordered h-16"
        placeholder="Текст за кадром"
        @blur="saveChanges"
      ></textarea>
    </div>

    <div class="form-control mb-4">
      <label class="label">
        <span class="label-text">Примечания</span>
      </label>
      <textarea 
        v-model="localScene.notes"
        class="textarea textarea-bordered h-16"
        placeholder="Технические примечания"
        @blur="saveChanges"
      ></textarea>
    </div>

    <div class="flex gap-2 mt-6">
      <button 
        class="btn btn-primary flex-1" 
        @click="regenerateImage"
        :disabled="isGeneratingImage"
      >
        <span class="loading loading-spinner" v-if="isGeneratingImage"></span>
        {{ isGeneratingImage ? 'Генерация...' : 'Перегенерировать изображение' }}
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

// Синхронизация при изменении props
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
    scene: localScene.value,
    style: 'cinematic' // Можно добавить выбор стиля
  })
}
</script>