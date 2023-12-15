<script setup>
import { QUERY_STACK } from '@/api/query/stack'
import VLoading from '@/components/VLoading.vue'
import VNav from '@/components/VNav.vue'
import VErrorAlert from '@/components/alerts/VErrorAlert.vue'
import VWarningAlert from '@/components/alerts/VWarningAlert.vue'
import VTransitionFade from '@/components/transitions/VTransitionFade.vue'
import { stackStates } from '@/constant'
import { ArrowPathIcon, PlayIcon, StopIcon } from '@heroicons/vue/24/outline'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/solid'
import { useQuery } from '@vue/apollo-composable'
import { computed, provide, reactive, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'

const route = useRoute()
const params = reactive({
  name: route.params.stackId
})

watch(
  () => route.params.stackId,
  (newId) => {
    if (newId === undefined) return
    params.name = newId
  }
)

const { result, loading, error } = useQuery(QUERY_STACK, params)

const stack = computed(() => result.value?.stack ?? null)
const navigation = computed(() => [
  {
    name: 'Overview',
    to: { name: 'stackIndex', params: { stackId: params.name } }
  }
  // {
  //   name: 'Services',
  //   to: { name: 'stackServices', params: { stackId: params.name } }
  // },
  // {
  //   name: 'Containers',
  //   to: { name: 'stackContainers', params: { stackId: params.name } }
  // },
  // {
  //   name: 'Logs',
  //   to: { name: 'stackLogs', params: { stackId: params.name } }
  // }
])

provide('stack', stack)
</script>

<template>
  <div>
    <div class="py-20" v-if="loading">
      <VLoading />
    </div>
    <div v-else-if="error" class="py-20 max-w-xl mx-auto">
      <VErrorAlert
        title="Une erreur est survenue !"
        text="Veuillez réessayer plus tard. Si le problème persiste, contactez votre administrateur."
      />
    </div>
    <div v-else-if="stack">
      <VNav :title="params.name" :navigation="navigation" :backlink="{ name: 'stacks' }"
        ><div class="flex gap-x-2">
          <button class="button-circle"><ArrowDownTrayIcon class="h-5 w-5" /></button>
          <button class="button-circle bg-green-600" v-if="stack.state != 'RUNNING'">
            <PlayIcon class="h-5 w-5" />
          </button>
          <button class="button-circle bg-blue-400" v-if="stack.state == 'RUNNING'">
            <ArrowPathIcon class="h-5 w-5" />
          </button>
          <button class="button-circle bg-red-400" v-if="stack.state != 'STOPPED'">
            <StopIcon class="h-5 w-5" />
          </button></div
      ></VNav>
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
      <RouterView v-slot="{ Component }">
        <VTransitionFade>
          <component :is="Component" />
        </VTransitionFade>
      </RouterView>
    </div>
    <div v-else class="py-20 max-w-xl mx-auto">
      <VWarningAlert
        title="Aucun résultat !"
        text="Si vous pensez que c'est une erreur, contactez votre administrateur."
      />
    </div>
  </div>
</template>
