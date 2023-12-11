<script setup>
import VHeader from '@/components/VHeader.vue'
</script>

<template>
  <div>
    <VHeader title="Dashboard" />
    <section>
      <div class="mx-auto max-w-7xl">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div class="card">
            <p class="text-sm font-medium leading-6 text-primary">Number of stacks</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-3xl font-medium tracking-tight text-white">2</span>
            </p>
          </div>
          <div class="card">
            <p class="text-sm font-medium leading-6 text-primary">Docker version</p>
            <p class="mt-2 flex items-baseline gap-x-2">
              <span class="text-3xl font-medium tracking-tight text-white">17.3.65</span>
            </p>
          </div>
          <div class="card">
            <p class="text-sm font-medium leading-6 text-primary">Odooghost version</p>
            <p class="mt-2 flex items-medium gap-x-2">
              <span class="text-3xl font-medium tracking-tight text-white">0.5.0</span>
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
