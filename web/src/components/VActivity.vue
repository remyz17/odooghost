<script setup>
const activityItems = [
  {
    user: {
      name: 'Michael Foster',
      imageUrl:
        'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
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
  <header
    class="flex items-center justify-between border-b border-white/5 px-4 py-4 sm:px-6 sm:py-6 lg:px-8"
  >
    <h5>Activity feed</h5>
    <a href="#" class="text-sm font-semibold leading-6 text-primary">View all</a>
  </header>
  <ul role="list" class="divide-y divide-white/5">
    <li v-for="item in activityItems" :key="item.commit" class="px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-x-3">
        <img
          :src="item.user.imageUrl"
          alt=""
          class="h-6 w-6 flex-none rounded-full bg-neutral-800"
        />
        <h6 class="flex-auto truncate">
          {{ item.user.name }}
        </h6>
        <time :datetime="item.dateTime" class="flex-none text-xs text-neutral-600">{{
          item.date
        }}</time>
      </div>
      <p class="mt-3 truncate text-sm text-neutral-500">
        Pushed to <span class="text-neutral-400">{{ item.projectName }}</span> (<span
          class="font-mono text-neutral-400"
          >{{ item.commit }}</span
        >
        on <span class="text-neutral-400">{{ item.branch }}</span
        >)
      </p>
    </li>
  </ul>
</template>
