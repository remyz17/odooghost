<script setup>
import { computed, toRefs } from 'vue'

const props = defineProps({
  animationDuration: {
    type: Number,
    default: 1000
  },
  dotSize: {
    type: Number,
    default: 15
  },
  dotsNum: {
    type: Number,
    default: 3
  },
  color: {
    type: String,
    default: '#714B67'
  }
})

const { animationDuration, dotSize, dotsNum, color } = toRefs(props)

const horizontalMargin = computed(() => dotSize.value)

const spinnerStyle = computed(() => {
  return {
    height: `${dotSize.value}px`,
    width: `${(dotSize.value + horizontalMargin.value * 2) * dotsNum.value}px`
  }
})

const dotStyle = computed(() => {
  return {
    animationDuration: `${animationDuration.value}ms`,
    width: `${dotSize.value}px`,
    height: `${dotSize.value}px`,
    margin: `0 ${horizontalMargin.value}px`,
    borderWidth: `${dotSize.value / 5}px`,
    borderColor: color.value
  }
})

const dotsStyles = computed(() => {
  const dotsStyles = []
  const delayModifier = 0.3
  const basicDelay = 1000
  for (let i = 1; i <= dotsNum.value; i++) {
    const style = Object.assign(
      {
        animationDelay: `${basicDelay * i * delayModifier}ms`
      },
      dotStyle.value
    )
    dotsStyles.push(style)
  }
  return dotsStyles
})
</script>

<template>
  <div class="hollow-dots-spinner mx-auto" :style="spinnerStyle">
    <div v-for="(ds, index) in dotsStyles" :key="index" class="dot" :style="ds"></div>
  </div>
</template>

<style scoped>
.hollow-dots-spinner,
.hollow-dots-spinner * {
  box-sizing: border-box;
}
.hollow-dots-spinner {
  height: 15px;
  width: calc(30px * 3);
}
.hollow-dots-spinner .dot {
  width: 15px;
  height: 15px;
  margin: 0 calc(15px / 2);
  border: calc(15px / 5) solid #ff1d5e;
  border-radius: 50%;
  float: left;
  transform: scale(0);
  animation: hollow-dots-spinner-animation 1000ms ease infinite 0ms;
}
.hollow-dots-spinner .dot:nth-child(1) {
  animation-delay: calc(300ms * 1);
}
.hollow-dots-spinner .dot:nth-child(2) {
  animation-delay: calc(300ms * 2);
}
.hollow-dots-spinner .dot:nth-child(3) {
  animation-delay: calc(300ms * 3);
}
@keyframes hollow-dots-spinner-animation {
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>
