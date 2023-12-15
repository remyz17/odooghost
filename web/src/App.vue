<script setup>
import VActivity from '@/components/VActivity.vue'
import VTransitionFade from '@/components/transitions/VTransitionFade.vue'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { Bars3Icon } from '@heroicons/vue/20/solid'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import VSidebar from './components/VSidebar.vue'

const sidebarOpen = ref(false)
</script>

<template>
  <TransitionRoot as="template" :show="sidebarOpen">
    <Dialog as="div" class="relative z-50 xl:hidden" @close="sidebarOpen = false">
      <TransitionChild
        as="template"
        enter="transition-opacity ease-linear duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="transition-opacity ease-linear duration-300"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-neutral-900/80" />
      </TransitionChild>

      <div class="fixed inset-0 flex">
        <TransitionChild
          as="template"
          enter="transition ease-in-out duration-300 transform"
          enter-from="-translate-x-full"
          enter-to="translate-x-0"
          leave="transition ease-in-out duration-300 transform"
          leave-from="translate-x-0"
          leave-to="-translate-x-full"
        >
          <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
            <TransitionChild
              as="template"
              enter="ease-in-out duration-300"
              enter-from="opacity-0"
              enter-to="opacity-100"
              leave="ease-in-out duration-300"
              leave-from="opacity-100"
              leave-to="opacity-0"
            >
              <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                <button type="button" class="-m-2.5 p-2.5" @click="sidebarOpen = false">
                  <XMarkIcon class="h-6 w-6 text-white" aria-hidden="true" />
                </button>
              </div>
            </TransitionChild>
            <VSidebar />
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>

  <div class="hidden xl:fixed xl:inset-y-0 xl:z-50 xl:flex xl:w-72 xl:flex-col">
    <VSidebar />
  </div>

  <div class="xl:pl-72 h-full">
    <div
      class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-6 bg-neutral-900 px-4 shadow-sm sm:px-6 lg:px-8 xl:hidden"
    >
      <button type="button" class="-m-2.5 p-2.5 text-white xl:hidden" @click="sidebarOpen = true">
        <Bars3Icon class="h-5 w-5" aria-hidden="true" />
      </button>
    </div>

    <div class="lg:pr-96 h-full flex flex-col">
      <div class="relative h-full flex flex-col shell-space bg-neutral-950">
        <main class="flex-1">
          <RouterView v-slot="{ Component }">
            <VTransitionFade>
              <component :is="Component" />
            </VTransitionFade>
          </RouterView>
        </main>
        <footer class="mx-auto w-full max-w-2xl space-y-10 lg:max-w-5xl">
          <div
            class="flex flex-col items-center justify-between gap-5 border-t pt-8 border-white/5 sm:flex-row"
          >
            <p class="text-xs text-neutral-400">
              &copy; Copyright {{ new Date().getFullYear() }}. All rights reserved.
            </p>
            <div class="flex gap-4">
              <a href="https://github.com/remyz17/odooghost" target="_blank">
                <svg
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                  class="h-5 w-5 fill-neutral-700 transition group-hover:fill-neurtral-500"
                >
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M10 1.667c-4.605 0-8.334 3.823-8.334 8.544 0 3.78 2.385 6.974 5.698 8.106.417.075.573-.182.573-.406 0-.203-.011-.875-.011-1.592-2.093.397-2.635-.522-2.802-1.002-.094-.246-.5-1.005-.854-1.207-.291-.16-.708-.556-.01-.567.656-.01 1.124.62 1.281.876.75 1.292 1.948.93 2.427.705.073-.555.291-.93.531-1.143-1.854-.213-3.791-.95-3.791-4.218 0-.929.322-1.698.854-2.296-.083-.214-.375-1.09.083-2.265 0 0 .698-.224 2.292.876a7.576 7.576 0 0 1 2.083-.288c.709 0 1.417.096 2.084.288 1.593-1.11 2.291-.875 2.291-.875.459 1.174.167 2.05.084 2.263.53.599.854 1.357.854 2.297 0 3.278-1.948 4.005-3.802 4.219.302.266.563.78.563 1.58 0 1.143-.011 2.061-.011 2.35 0 .224.156.491.573.405a8.365 8.365 0 0 0 4.11-3.116 8.707 8.707 0 0 0 1.567-4.99c0-4.721-3.73-8.545-8.334-8.545Z"
                  />
                </svg>
              </a>
            </div>
          </div>
        </footer>
      </div>
    </div>

    <aside class="bg-black/10 lg:fixed lg:bottom-0 lg:right-0 lg:top-0 lg:w-96 lg:overflow-y-auto">
      <VActivity />
    </aside>
  </div>
</template>
