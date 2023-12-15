<script setup>
import { ChevronRightIcon } from '@heroicons/vue/20/solid'
const props = defineProps({ containers: Array })

const statuses = {
  STOPPED: 'text-neutral-400 bg-neutral-100/10',
  RUNNING: 'text-emerald-400 bg-emerald-400/10',
  EXITED: 'text-rose-400 bg-rose-400/10',
  PAUSED: 'text-purple-400 bg-purple-400/10',
  RESTARTING: 'text-yellow-500 bg-yellow-400/10'
}
const services = {
  odoo: 'text-primary bg-primary/10 ring-primary/20',
  db: 'text-indigo-400 bg-indigo-400/10 ring-indigo-400/30'
}
</script>

<template>
  <ul role="list" class="divide-y divide-white/5">
    <li v-for="c in props.containers" :key="c.id" class="relative flex items-center space-x-4 py-4">
      <div class="min-w-0 flex-auto">
        <div class="flex items-center gap-x-3">
          <div :class="[statuses[c.state], 'flex-none rounded-full p-1']">
            <div class="h-2 w-2 rounded-full bg-current" />
          </div>
          <h2 class="min-w-0 text-sm font-semibold leading-6 text-white">
            <a class="flex gap-x-2">
              <span class="truncate">{{ c.name }}</span>
              <span class="text-gray-400">/</span>
              <span class="whitespace-nowrap">{{ c.image }}</span>
              <span class="absolute inset-0" />
            </a>
          </h2>
        </div>
        <div class="mt-3 flex items-center gap-x-2.5 text-xs leading-5 text-gray-400">
          <p class="truncate">{{ c.id }}</p>
          <svg viewBox="0 0 2 2" class="h-0.5 w-0.5 flex-none fill-gray-300">
            <circle cx="1" cy="1" r="1" />
          </svg>
          <p class="whitespace-nowrap">{{ c.id }}</p>
        </div>
      </div>
      <div
        :class="[
          services[c.service],
          'rounded-full flex-none py-1 px-2 text-xs font-medium ring-1 ring-inset'
        ]"
      >
        {{ c.service }}
      </div>
      <ChevronRightIcon class="h-5 w-5 flex-none text-gray-400" aria-hidden="true" />
    </li>
  </ul>
</template>
