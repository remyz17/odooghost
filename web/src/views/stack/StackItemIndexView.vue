<script setup>
import { inject } from 'vue'
const stats = [
  { name: 'Number of deploys', value: '405' },
  { name: 'Average deploy time', value: '3.65', unit: 'mins' },
  { name: 'Number of servers', value: '3' },
  { name: 'Success rate', value: '98.5%' }
]

const stack = inject('stack')
</script>

<template>
  <div>
    <div
      class="flex flex-col items-start justify-between gap-x-8 gap-y-4 py-4 sm:flex-row sm:items-center"
    >
      <div>
        <div class="flex items-center gap-x-3">
          <div class="flex-none rounded-full bg-green-400/10 p-1 text-green-400">
            <div class="h-2 w-2 rounded-full bg-current" />
          </div>
          <h1 class="flex gap-x-3 text-base leading-7">
            <span class="font-semibold text-white">Odooghost</span>
            <span class="text-gray-600">/</span>
            <span class="font-semibold text-white">{{ stack.name }}</span>
          </h1>
        </div>
        <p class="mt-2 text-xs leading-6 text-gray-400">Deploys from GitHub via main branch</p>
      </div>
      <div
        class="order-first flex-none rounded-full bg-indigo-400/10 px-2 py-1 text-xs font-medium text-indigo-400 ring-1 ring-inset ring-indigo-400/30 sm:order-none"
      >
        Production
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="(stat, statIdx) in stats"
        :key="stat.name"
        :class="[statIdx % 2 === 1 ? '' : statIdx === 2 ? '' : '', ' py-6 px-4 sm:px-6 lg:px-8']"
      >
        <p class="text-sm font-medium leading-6 text-gray-400">{{ stat.name }}</p>
        <p class="mt-2 flex items-baseline gap-x-2">
          <span class="text-4xl font-semibold tracking-tight text-white">{{ stat.value }}</span>
          <span v-if="stat.unit" class="text-sm text-gray-400">{{ stat.unit }}</span>
        </p>
      </div>
    </div>
  </div>
</template>
