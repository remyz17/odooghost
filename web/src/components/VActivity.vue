<script setup>
const activityItems = [
  {
    user: {
      name: 'Stack: opennet17'
    },
    projectName: 'ios-app',
    commit: '2d89f0c8',
    branch: 'main',
    date: '1h',
    dateTime: '2023-01-23T11:00'
  }
  // More items...
]
</script>

<template>
  <header class="flex items-center justify-between px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
    <h5>Events feed</h5>
    <a href="#" class="text-sm font-semibold leading-6 text-primary">View all</a>
  </header>
  <ul role="list" class="divide-y divide-white/5">
    <li v-for="item in activityItems" :key="item.commit" class="px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-x-3">
        <h6 class="flex-auto truncate text-neutral-200">
          {{ item.user.name }}
        </h6>
        <time :datetime="item.dateTime" class="flex-none text-xs text-neutral-600">{{
          item.date
        }}</time>
      </div>
      <!-- <p class="mt-3 truncate text-sm text-neutral-500">
        Started stack services <span class="text-neutral-400">{{ item.projectName }}</span> (<span
          class="font-mono text-neutral-400"
          >{{ item.commit }}</span
        >
        on <span class="text-neutral-400">{{ item.branch }}</span
        >)
      </p> -->
      <p class="mt-3 truncate text-sm text-neutral-500">Started stack services</p>
    </li>
  </ul>
</template>
