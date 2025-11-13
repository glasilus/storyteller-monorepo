// composables/useConfirm.js
let resolveCallback = null

export const useConfirm = () => {
  const isOpen = useState('confirm-dialog-open', () => false)
  const dialogTitle = useState('confirm-dialog-title', () => '')
  const dialogMessage = useState('confirm-dialog-message', () => '')

  const confirm = (title, message) => {
    return new Promise((resolve) => {
      dialogTitle.value = title
      dialogMessage.value = message
      isOpen.value = true
      resolveCallback = resolve
    })
  }

  const handleConfirm = () => {
    isOpen.value = false
    if (resolveCallback) {
      resolveCallback(true)
      resolveCallback = null
    }
  }

  const handleCancel = () => {
    isOpen.value = false
    if (resolveCallback) {
      resolveCallback(false)
      resolveCallback = null
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
