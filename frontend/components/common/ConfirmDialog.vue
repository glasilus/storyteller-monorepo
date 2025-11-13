<template>
  <div v-if="isOpen" class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">{{ dialogTitle }}</h3>
      <p class="py-4">{{ dialogMessage }}</p>
      <div class="modal-action">
        <button class="btn btn-ghost" @click="handleCancel">
          Отмена
        </button>
        <button class="btn btn-error" @click="handleConfirm">
          Удалить
        </button>
      </div>
    </div>
    <div class="modal-backdrop bg-black bg-opacity-50" @click="handleCancel"></div>
  </div>
</template>

<script setup>
import { useConfirm } from '~/composables/useConfirm'

const { isOpen, dialogTitle, dialogMessage, handleConfirm, handleCancel } = useConfirm()
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}
</style>
