<script setup>
import { QUERY_CONTAINERS } from '@/api/query/stack'
import VDataView from '@/components/VDataView.vue'
import VHeader from '@/components/VHeader.vue'
import VContainers from '@/components/VContainers.vue'
import { useQuery } from '@vue/apollo-composable'

const { loading, result, error } = useQuery(QUERY_CONTAINERS, null)
</script>

<template>
  <div>
    <VHeader title="Containers" />
    <section>
      <VDataView :loading="loading" :error="error" :result="result" result-key="containers" is-list>
        <VContainers :containers="result.containers" />
      </VDataView>
    </section>
  </div>
</template>
