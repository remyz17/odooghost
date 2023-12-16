<script setup>
import { useModalStore } from '@/stores/modal'
import { DialogPanel } from '@headlessui/vue'
import { ExclamationCircleIcon } from '@heroicons/vue/24/outline'

const store = useModalStore()

const refreshPage = () => {
  store.closeModal()
  location.reload(true)
}
</script>

<template>
  <DialogPanel
    class="relative transform overflow-hidden rounded-lg bg-neutral-950 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6"
  >
    <div>
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-600/10">
        <ExclamationCircleIcon class="h-6 w-6 text-rose-500" aria-hidden="true" />
      </div>
      <div class="mt-3 text-center sm:mt-5">
        <h2>Error</h2>
        <div class="mt-2">
          <p>
            An error has occured while querying the server. Make sur odooghost web server is running
            !
          </p>
        </div>
      </div>
    </div>
    <div class="mt-5 sm:mt-6 flex justify-center">
      <button type="button" class="button-primary" @click="refreshPage()">Refresh page</button>
    </div>
  </DialogPanel>
</template>
