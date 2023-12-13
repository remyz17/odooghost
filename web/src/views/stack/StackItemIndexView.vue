<script setup>
import { stackStates } from '@/constant'
import { ArrowPathIcon, PlayIcon, StopIcon } from '@heroicons/vue/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/solid'
import { inject } from 'vue'

const statuses = {
  Completed: 'text-green-400 bg-green-400/10',
  Error: 'text-rose-400 bg-rose-400/10'
}
const activityItems = [
  {
    user: {
      name: 'Michael Foster',
      imageUrl:
        'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '2d89f0c8',
    branch: 'main',
    status: 'Completed',
    duration: '25s',
    date: '45 minutes ago',
    dateTime: '2023-01-23T11:00'
  },
  {
    user: {
      name: 'Lindsay Walton',
      imageUrl:
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '249df660',
    branch: 'main',
    status: 'Completed',
    duration: '1m 32s',
    date: '3 hours ago',
    dateTime: '2023-01-23T09:00'
  },
  {
    user: {
      name: 'Courtney Henry',
      imageUrl:
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '11464223',
    branch: 'main',
    status: 'Error',
    duration: '1m 4s',
    date: '12 hours ago',
    dateTime: '2023-01-23T00:00'
  },
  {
    user: {
      name: 'Courtney Henry',
      imageUrl:
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: 'dad28e95',
    branch: 'main',
    status: 'Completed',
    duration: '2m 15s',
    date: '2 days ago',
    dateTime: '2023-01-21T13:00'
  },
  {
    user: {
      name: 'Michael Foster',
      imageUrl:
        'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '624bc94c',
    branch: 'main',
    status: 'Completed',
    duration: '1m 12s',
    date: '5 days ago',
    dateTime: '2023-01-18T12:34'
  },
  {
    user: {
      name: 'Courtney Henry',
      imageUrl:
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: 'e111f80e',
    branch: 'main',
    status: 'Completed',
    duration: '1m 56s',
    date: '1 week ago',
    dateTime: '2023-01-16T15:54'
  },
  {
    user: {
      name: 'Michael Foster',
      imageUrl:
        'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '5e136005',
    branch: 'main',
    status: 'Completed',
    duration: '3m 45s',
    date: '1 week ago',
    dateTime: '2023-01-16T11:31'
  },
  {
    user: {
      name: 'Whitney Francis',
      imageUrl:
        'https://images.unsplash.com/photo-1517365830460-955ce3ccd263?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    commit: '5c1fd07f',
    branch: 'main',
    status: 'Completed',
    duration: '37s',
    date: '2 weeks ago',
    dateTime: '2023-01-09T08:45'
  }
]

const stack = inject('stack')
</script>

<template>
  <div>
    <div class="flex justify-between items-center py-4">
      <div class="flex flex-col items-start justify-between gap-x-8 gap-y-4">
        <div class="flex gap-x-2">
          <span
            class="inline-flex items-center rounded-xl 0 px-2 py-1 text-xs"
            :class="stackStates[stack.state].classes"
            >State: {{ stackStates[stack.state].label }}</span
          >
          <span
            class="inline-flex items-center rounded-xl bg-gray-400/10 px-2 py-1 text-xs text-gray-400"
            >Network: {{ stack.networkMode }}</span
          >
        </div>
        <div>
          <div class="flex items-center gap-x-3">
            <div class="flex-none rounded-full bg-green-400/10 p-1 text-green-400">
              <div class="h-2 w-2 rounded-full bg-current" />
            </div>
            <h1 class="flex gap-x-3 text-base leading-7">
              <span class="font-semibold text-white">Stacks</span>
              <span class="text-gray-600">/</span>
              <span class="font-semibold text-white">{{ stack.name }}</span>
            </h1>
          </div>
          <p class="mt-2 text-xs leading-6 text-gray-400">Deploys from GitHub via main branch</p>
        </div>
      </div>
      <div class="flex gap-x-2">
        <button class="button-circle"><ArrowDownTrayIcon class="h-5 w-5" /></button>
        <button class="button-circle bg-green-600" v-if="stack.state != 'RUNNING'">
          <PlayIcon class="h-5 w-5" />
        </button>
        <button class="button-circle bg-blue-400" v-if="stack.state != 'RESTARTING'">
          <ArrowPathIcon class="h-5 w-5" />
        </button>
        <button class="button-circle bg-red-400" v-if="stack.state != 'STOPPED'">
          <StopIcon class="h-5 w-5" />
        </button>
      </div>
    </div>

    <!-- Stats -->
    <section class="border-t border-white/10">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-x-4">
        <div>
          <dt class="truncate text-sm font-light text-neutral-400">Odoo version</dt>
          <dd class="mt-1 text-lg tracking-tight text-white">2</dd>
        </div>
        <div>
          <dt class="truncate text-sm font-light text-neutral-400">Postgres Version</dt>
          <dd class="mt-1 text-lg tracking-tight text-white">3</dd>
        </div>
        <div>
          <dt class="truncate text-sm font-light text-neutral-400">Sercices</dt>
          <dd class="mt-1 text-lg tracking-tight text-white">3</dd>
        </div>
        <div>
          <dt class="truncate text-sm font-light text-neutral-400">Containers</dt>
          <dd class="mt-1 text-lg tracking-tight text-white">3</dd>
        </div>
      </div>
    </section>

    <section>
      <h3>Containers</h3>
      <table class="mt-6 w-full whitespace-nowrap text-left -ml-4 sm:-ml-6 lg:-ml-8">
        <colgroup>
          <col class="w-full sm:w-4/12" />
          <col class="lg:w-4/12" />
          <col class="lg:w-2/12" />
          <col class="lg:w-1/12" />
          <col class="lg:w-1/12" />
        </colgroup>
        <thead class="border-b border-white/10 text-sm leading-6 text-white">
          <tr>
            <th scope="col" class="py-2 pl-4 pr-8 font-semibold sm:pl-6 lg:pl-8">User</th>
            <th scope="col" class="hidden py-2 pl-0 pr-8 font-semibold sm:table-cell">Commit</th>
            <th
              scope="col"
              class="py-2 pl-0 pr-4 text-right font-semibold sm:pr-8 sm:text-left lg:pr-20"
            >
              Status
            </th>
            <th scope="col" class="hidden py-2 pl-0 pr-8 font-semibold md:table-cell lg:pr-20">
              Duration
            </th>
            <th
              scope="col"
              class="hidden py-2 pl-0 pr-4 text-right font-semibold sm:table-cell sm:pr-6 lg:pr-8"
            >
              Deployed at
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-for="item in activityItems" :key="item.commit">
            <td class="py-4 pl-4 pr-8 sm:pl-6 lg:pl-8">
              <div class="flex items-center gap-x-4">
                <img :src="item.user.imageUrl" alt="" class="h-8 w-8 rounded-full bg-gray-800" />
                <div class="truncate text-sm font-medium leading-6 text-white">
                  {{ item.user.name }}
                </div>
              </div>
            </td>
            <td class="hidden py-4 pl-0 pr-4 sm:table-cell sm:pr-8">
              <div class="flex gap-x-3">
                <div class="font-mono text-sm leading-6 text-gray-400">{{ item.commit }}</div>
                <div
                  class="rounded-md bg-gray-700/40 px-2 py-1 text-xs font-medium text-gray-400 ring-1 ring-inset ring-white/10"
                >
                  {{ item.branch }}
                </div>
              </div>
            </td>
            <td class="py-4 pl-0 pr-4 text-sm leading-6 sm:pr-8 lg:pr-20">
              <div class="flex items-center justify-end gap-x-2 sm:justify-start">
                <time class="text-gray-400 sm:hidden" :datetime="item.dateTime">{{
                  item.date
                }}</time>
                <div :class="[statuses[item.status], 'flex-none rounded-full p-1']">
                  <div class="h-1.5 w-1.5 rounded-full bg-current" />
                </div>
                <div class="hidden text-white sm:block">{{ item.status }}</div>
              </div>
            </td>
            <td
              class="hidden py-4 pl-0 pr-8 text-sm leading-6 text-gray-400 md:table-cell lg:pr-20"
            >
              {{ item.duration }}
            </td>
            <td
              class="hidden py-4 pl-0 pr-4 text-right text-sm leading-6 text-gray-400 sm:table-cell sm:pr-6 lg:pr-8"
            >
              <time :datetime="item.dateTime">{{ item.date }}</time>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
