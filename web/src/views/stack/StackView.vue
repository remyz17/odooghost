<script setup>
import { QUERY_STACKS } from '@/api/query/stack'
import VDataView from '@/components/VDataView.vue'
import VHeader from '@/components/VHeader.vue'
import { stackStates } from '@/constant'
import { useQuery } from '@vue/apollo-composable'

const { loading, result, error } = useQuery(QUERY_STACKS, null)
</script>

<template>
  <div>
    <VHeader title="Stacks" />
    <section>
      <VDataView :loading="loading" :error="error" :result="result" result-key="stacks" is-list>
        <dl role="list" class="grid grid-cols-1 gap-x-2 gap-y-4 lg:grid-cols-3 xl:gap-x-4">
          <RouterLink
            v-for="stack in result.stacks"
            :key="stack.name"
            :to="{ name: 'stackIndex', params: { stackId: stack.name } }"
            class="card flex flex-col space-y-6 hover:border-primary hover:cursor-pointer transition-all"
          >
            <div class="flex justify-between">
              <h5>{{ stack.name }}</h5>
              <span
                class="inline-flex items-center rounded-xl 0 px-2 py-1 text-xs"
                :class="stackStates[stack.state].classes"
                >{{ stackStates[stack.state].label }}</span
              >
            </div>
            <div class="grid grid-cols-2 gap-x-4">
              <div>
                <dt class="truncate text-sm font-light text-neutral-400">Services</dt>
                <dd class="mt-1 text-lg tracking-tight text-white">2</dd>
              </div>
              <div>
                <dt class="truncate text-sm font-light text-neutral-400">Containers</dt>
                <dd class="mt-1 text-lg tracking-tight text-white">3</dd>
              </div>
            </div>
          </RouterLink>
        </dl>
      </VDataView>
    </section>
  </div>
</template>
