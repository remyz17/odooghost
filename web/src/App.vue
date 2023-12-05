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
  <div>
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

    <div class="xl:pl-72">
      <div
        class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-6 border-b border-white/5 bg-neutral-900 px-4 shadow-sm sm:px-6 lg:px-8 xl:hidden"
      >
        <button type="button" class="-m-2.5 p-2.5 text-white xl:hidden" @click="sidebarOpen = true">
          <Bars3Icon class="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      <main class="lg:pr-96">
        <RouterView v-slot="{ Component }">
          <VTransitionFade>
            <component :is="Component" />
          </VTransitionFade>
        </RouterView>
      </main>

      <aside
        class="bg-black/10 lg:fixed lg:bottom-0 lg:right-0 lg:top-0 lg:w-96 lg:overflow-y-auto lg:border-l lg:border-white/5"
      >
        <VActivity />
      </aside>
    </div>
  </div>
</template>
