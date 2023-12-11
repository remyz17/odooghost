<script setup>
import { ChevronLeftIcon } from '@heroicons/vue/20/solid'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: String,
  navigation: Object,
  hasBack: {
    type: Boolean,
    default: true
  },
  backlink: [Object, String]
})

const router = useRouter()

const goBack = () => {
  if (props.backlink) router.push(props.backlink)
  else router.go(-1)
}
</script>

<template>
  <nav class="flex items-center justify-between border-b border-black/10">
    <div class="overflow-x-auto flex-1 flex items-center gap-6">
      <div v-if="props.hasBack">
        <button @click="goBack" class="flex items-center text-sm font-medium group">
          <ChevronLeftIcon
            class="flex-shrink-0 h-5 w-5 text-neutral-400 group-hover:text-primary"
            aria-hidden="true"
          />
        </button>
      </div>
      <h3 class="hidden sm:block">{{ props.title }}</h3>
      <ul
        role="list"
        class="flex items-center flex-none gap-x-6 text-sm font-semibold leading-6 text-neutral-400 sm:border-l sm:border-neutral-700 sm:pl-6 sm:leading-7"
      >
        <li v-for="item in props.navigation" :key="item.name">
          <router-link :to="item.to" exact-active-class="!text-primary">{{
            item.name
          }}</router-link>
        </li>
      </ul>
    </div>
    <div class="">
      <slot></slot>
    </div>
  </nav>
</template>
