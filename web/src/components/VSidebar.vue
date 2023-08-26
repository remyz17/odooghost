<script setup>
import {
  ChartBarSquareIcon,
  Cog6ToothIcon,
  FolderIcon,
  GlobeAltIcon,
  ServerIcon,
  SignalIcon
} from '@heroicons/vue/24/outline'
import { RouterLink } from 'vue-router'

const navigation = [
  { name: 'Dashboard', href: { name: 'dashboard' }, icon: FolderIcon, current: false },
  { name: 'Stacks', href: { name: 'stacks' }, icon: ServerIcon, current: true },
  { name: 'Usage', href: { name: 'usage' }, icon: ChartBarSquareIcon, current: false },
  { name: 'Settings', href: { name: 'settings' }, icon: Cog6ToothIcon, current: false }
]
</script>

<template>
  <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-neutral-900 px-6 ring-1 ring-white/10">
    <div class="flex h-16 shrink-0 items-center">
      <img
        class="h-8 w-auto"
        src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=500"
        alt="Your Company"
      />
    </div>
    <nav class="flex flex-1 flex-col">
      <ul role="list" class="flex flex-1 flex-col gap-y-7">
        <li>
          <ul role="list" class="-mx-2 space-y-1">
            <li v-for="item in navigation" :key="item.name">
              <RouterLink
                :to="item.href"
                class="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-neutral-400 hover:text-white hover:bg-neutral-800"
                active-class="!bg-neutral-800 !text-white"
              >
                <component :is="item.icon" class="h-6 w-6 shrink-0" aria-hidden="true" />
                {{ item.name }}
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  </div>
</template>
