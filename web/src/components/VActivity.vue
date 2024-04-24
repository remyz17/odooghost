<script setup>
import { SUBSCRIBE_EVEMTS } from '@/api/subscription'
import { useSubscription } from '@vue/apollo-composable'
import { ref, watch } from 'vue'
import VErrorAlert from './alerts/VErrorAlert.vue'

const events = ref([])
const statuses = {
  die: { classes: 'text-neutral-400 bg-neutral-100/10', text: 'stopped' },
  start: { classes: 'text-emerald-400 bg-emerald-400/10', text: 'started' },
  kill: { classes: 'text-rose-400 bg-rose-400/10', text: 'killed' },
  stop: { classes: 'text-yellow-500 bg-yellow-400/10', text: 'stopping' }
}

const { result, error, loading } = useSubscription(SUBSCRIBE_EVEMTS, null, {
  fetchPolicy: 'no-cache'
})

watch(
  result,
  (data) => {
    events.value.unshift(data.events)
  },
  {
    lazy: true // Don't immediately execute handler
  }
)

const clearEvents = () => (events.value = [])
</script>

<template>
  <header class="flex items-center justify-between px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
    <h4>Events feed</h4>
    <button @click="clearEvents()" class="text-sm font-semibold leading-6 text-primary">
      Clear
    </button>
  </header>
  <div v-if="error">
    <div class="py-20 max-w-xl mx-auto">
      <VErrorAlert
        title="Une erreur est survenue !"
        text="Veuillez réessayer plus tard. Si le problème persiste, contactez votre administrateur."
      />
    </div>
  </div>
  <ul
    role="list"
    class="divide-y divide-white/5"
    v-else-if="!loading && events && events.length > 0"
  >
    <li v-for="event in events" :key="event.id" class="px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-x-3 justify-between">
        <h5 class="min-w-0 text-sm font-semibold leading-6 text-white">
          <a class="flex gap-x-2">
            <span class="truncate">{{ event.stackName }}</span>
            <span class="text-neutral-400">/</span>
            <span class="whitespace-nowrap">{{ event.serviceName }}</span>
          </a>
        </h5>
        <div :class="[statuses[event.action].classes, 'flex-none rounded-full p-1']">
          <div class="h-2 w-2 rounded-full bg-current" />
        </div>
      </div>
      <p class="mt-3 truncate text-sm">{{ event.containerName }}</p>
      <p class="mt-1 truncate text-sm">Container {{ statuses[event.action].text }}</p>
    </li>
  </ul>
  <div v-else class="py-20 px-4 sm:px-6 lg:px-8">
    <div class="text-center">
      <svg
        class="mx-auto h-12 w-12 text-primary"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          vector-effect="non-scaling-stroke"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
        />
      </svg>
      <h5>No events</h5>
      <p class="mt-1 text-sm">There is no container events to show for the moment !</p>
    </div>
  </div>
</template>
