<script setup>
const props = defineProps({
  title: String
})
</script>

<template>
  <header
    class="flex items-center justify-end sm:justify-between border-b border-white/5 shell-space"
  >
    <h2 class="hidden sm:block">{{ props.title }}</h2>
    <slot></slot>
  </header>
</template>
