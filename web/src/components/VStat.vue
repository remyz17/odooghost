<script setup>
const props = defineProps({
  name: String,
  stat: String
})
</script>

<template>
  <div class="card">
    <p class="text-sm font-medium leading-6 text-primary">{{ props.name }}</p>
    <p class="mt-2 flex items-baseline gap-x-2">
      <span class="text-3xl font-medium tracking-tight text-white">{{ props.stat }}</span>
    </p>
  </div>
</template>
