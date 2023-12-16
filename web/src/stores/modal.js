import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
  const data = ref({})
  const open = ref(false)

  const openModal = (modalData) => {
    data.value = modalData
    open.value = true
  }

  const closeModal = () => {
    open.value = false
    setTimeout(() => (data.value = {}), 1000)
  }

  const runCallbackModal = (args = null) => {
    if (args) data.value.callback(args)
    else data.value.callback()
    closeModal()
  }

  return {
    data,
    open,
    openModal,
    closeModal,
    runCallbackModal
  }
})
