<script setup>
import { QUERY_STACK } from '@/api/query/stack'
import VLoading from '@/components/VLoading.vue'
import VNav from '@/components/VNav.vue'
import VErrorAlert from '@/components/alerts/VErrorAlert.vue'
import VWarningAlert from '@/components/alerts/VWarningAlert.vue'
import VTransitionFade from '@/components/transitions/VTransitionFade.vue'
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
  },
  {
    name: 'Services',
    to: { name: 'stackServices', params: { stackId: params.name } }
  },
  {
    name: 'Containers',
    to: { name: 'stackContainers', params: { stackId: params.name } }
  },
  {
    name: 'Logs',
    to: { name: 'stackLogs', params: { stackId: params.name } }
  }
])

provide('stack', stack)
</script>

<template>
  <div>
    <VNav :title="params.name" :navigation="navigation" :backlink="{ name: 'stacks' }" />
    <div class="py-20" v-if="loading">
      <VLoading />
    </div>
    <div v-else-if="error" class="py-20 max-w-xl mx-auto">
      <VErrorAlert
        title="Une erreur est survenue !"
        text="Veuillez réessayer plus tard. Si le problème persiste, contactez votre administrateur."
      />
    </div>
    <div v-else-if="stack" class="py-5">
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
