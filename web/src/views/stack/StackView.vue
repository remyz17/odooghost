<script setup>
import { QUERY_STACKS } from '@/api/query/stack'
import VHeader from '@/components/VHeader.vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { EllipsisHorizontalIcon } from '@heroicons/vue/20/solid'
import { useQuery } from '@vue/apollo-composable'

const { loading, result, error } = useQuery(QUERY_STACKS, null)

const statuses = {
  Paid: 'text-green-700 bg-transparent ring-green-600/20',
  Withdraw: 'text-gray-600 bg-transparent ring-gray-500/10',
  Overdue: 'text-red-700 bg-transparent ring-red-600/10'
}
const clients = [
  {
    id: 1,
    name: 'Tuple',
    imageUrl: 'https://tailwindui.com/img/logos/48x48/tuple.svg',
    lastInvoice: {
      date: 'December 13, 2022',
      dateTime: '2022-12-13',
      amount: '$2,000.00',
      status: 'Overdue'
    }
  },
  {
    id: 2,
    name: 'SavvyCal',
    imageUrl: 'https://tailwindui.com/img/logos/48x48/savvycal.svg',
    lastInvoice: {
      date: 'January 22, 2023',
      dateTime: '2023-01-22',
      amount: '$14,000.00',
      status: 'Paid'
    }
  },
  {
    id: 3,
    name: 'Reform',
    imageUrl: 'https://tailwindui.com/img/logos/48x48/reform.svg',
    lastInvoice: {
      date: 'January 23, 2023',
      dateTime: '2023-01-23',
      amount: '$7,600.00',
      status: 'Paid'
    }
  }
]
</script>

<template>
  <div>
    <VHeader title="Stacks" />
    <section class="shell-space">
      <ul
        v-if="!loading && !error"
        role="list"
        class="grid grid-cols-1 gap-x-2 gap-y-4 lg:grid-cols-3 xl:gap-x-4"
      >
        <li
          v-for="stack in result.stacks"
          :key="stack.name"
          class="overflow-hidden rounded-xl border border-white/5"
        >
          <div class="flex items-center gap-x-4 border-b border-white/5 p-3">
            <div class="text-sm font-medium leading-6 text-white">{{ stack.name }}</div>
            <Menu as="div" class="relative ml-auto">
              <MenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
                <span class="sr-only">Open options</span>
                <EllipsisHorizontalIcon class="h-5 w-5" aria-hidden="true" />
              </MenuButton>
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems
                  class="absolute right-0 z-10 mt-0.5 w-32 origin-top-right rounded-md bg-neutral-900 py-2 shadow-lg ring-1 ring-white/5 focus:outline-none"
                >
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[
                        active ? 'bg-gray-50' : '',
                        'block px-3 py-1 text-sm leading-6 text-gray-900'
                      ]"
                      >View</a
                    >
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[
                        active ? 'bg-gray-50' : '',
                        'block px-3 py-1 text-sm leading-6 text-gray-900'
                      ]"
                      >Edit</a
                    >
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
          <!-- <dl class="-my-3 divide-y divide-white/5 px-3 py-4 text-sm leading-6">
            <div class="flex justify-between gap-x-2 py-2">
              <dt class="text-neutral-400">Last invoice</dt>
              <dd class="text-white text-sm">
                <time :datetime="client.lastInvoice.dateTime">{{ client.lastInvoice.date }}</time>
              </dd>
            </div>
            <div class="flex justify-between gap-x-2 py-2">
              <dt class="text-neutral-400">Amount</dt>
              <dd class="flex items-start gap-x-2">
                <div class="text-white">{{ client.lastInvoice.amount }}</div>
                <div
                  :class="[
                    statuses[client.lastInvoice.status],
                    'rounded-md py-1 px-2 text-xs font-medium ring-1 ring-inset'
                  ]"
                >
                  {{ client.lastInvoice.status }}
                </div>
              </dd>
            </div>
          </dl> -->
        </li>
      </ul>
    </section>
  </div>
</template>
