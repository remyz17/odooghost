<script setup>
import { XCircleIcon } from '@heroicons/vue/24/solid'
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
      bgColor: 'bg-red-400/10',
      ringColor: 'ring-red-400/20',
      iconColor: 'text-red-400',
      titleColor: 'text-red-400',
      textColor: 'text-red-400',
      icon: XCircleIcon
    }"
  />
</template>
