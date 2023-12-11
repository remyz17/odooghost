<script setup>
const props = defineProps({
  title: String
})
</script>

<template>
  <header class="flex items-center justify-end sm:justify-between">
    <h1>{{ props.title }}</h1>
    <slot></slot>
  </header>
</template>
