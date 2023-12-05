<script setup>
import VHeader from '@/components/VHeader.vue'
</script>

<template>
  <div>
    <VHeader title="Dashboard" />
    <section>
      <div class="mx-auto max-w-7xl">
        <div class="grid grid-cols-1 gap-px sm:grid-cols-2 lg:grid-cols-4">
          <div class="bg-neutral-900 px-4 py-6 sm:px-6 lg:px-8">
            <p class="text-sm font-medium leading-6 text-gray-400">Number of deploys</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-4xl font-semibold tracking-tight text-white">405</span>
            </p>
          </div>
          <div class="bg-neutral-900 px-4 py-6 sm:px-6 lg:px-8">
            <p class="text-sm font-medium leading-6 text-gray-400">Average deploy time</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-4xl font-semibold tracking-tight text-white">3.65</span>
              <span class="text-sm text-gray-400">mins</span>
            </p>
          </div>
          <div class="bg-neutral-900 px-4 py-6 sm:px-6 lg:px-8">
            <p class="text-sm font-medium leading-6 text-gray-400">Number of servers</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-4xl font-semibold tracking-tight text-white">3</span>
            </p>
          </div>
          <div class="bg-neutral-900 px-4 py-6 sm:px-6 lg:px-8">
            <p class="text-sm font-medium leading-6 text-gray-400">Success rate</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-4xl font-semibold tracking-tight text-white">98.5%</span>
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
