<script setup>
const props = defineProps({
  data: Object
})
</script>

<template>
  <div :class="['rounded-md p-4 ring-1 ring-inset', props.data.bgColor, props.data.ringColor]">
    <div class="flex">
      <div class="flex-shrink-0">
        <component
          :is="props.data.icon"
          :class="['h-5 w-5', props.data.iconColor]"
          aria-hidden="true"
        />
      </div>
      <div class="ml-3">
        <span :class="['text-base font-medium', props.data.titleColor]">{{
          props.data.title
        }}</span>
        <div>
          <p :class="['mt-2 text-sm', props.data.textColor]">
            {{ props.data.text }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
