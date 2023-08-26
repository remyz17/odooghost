<script setup>
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import VAlert from './components/VAlert.vue'

const props = defineProps({
  title: String,
  text: String
})
</script>
<template>
  <VAlert
    :data="{
      title: props.title,
      text: props.text,
      bgColor: 'bg-yellow-400/10',
      ringColor: 'ring-yellow-400/20',
      iconColor: 'text-yellow-500',
      titleColor: 'text-yellow-500',
      textColor: 'text-yellow-500',
      icon: ExclamationTriangleIcon
    }"
  />
</template>
