// composables/useConfirm.js
import { ref } from 'vue'

const isOpen = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const resolveCallback = ref(null)

export const useConfirm = () => {
  const confirm = (title, message) => {
    return new Promise((resolve) => {
      dialogTitle.value = title
      dialogMessage.value = message
      isOpen.value = true
      resolveCallback.value = resolve
    })
  }

  const handleConfirm = () => {
    isOpen.value = false
    if (resolveCallback.value) {
      resolveCallback.value(true)
      resolveCallback.value = null
    }
  }

  const handleCancel = () => {
    isOpen.value = false
    if (resolveCallback.value) {
      resolveCallback.value(false)
      resolveCallback.value = null
    }
  }

  return {
    isOpen,
    dialogTitle,
    dialogMessage,
    confirm,
    handleConfirm,
    handleCancel
  }
}
