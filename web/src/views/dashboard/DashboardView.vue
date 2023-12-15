<script setup>
import { QUERY_DASHBOARD } from '@/api/query/dashboard'
import VContainers from '@/components/VContainers.vue'
import VDataView from '@/components/VDataView.vue'
import VHeader from '@/components/VHeader.vue'
import VStat from '@/components/VStat.vue'
import { useQuery } from '@vue/apollo-composable'

const { result, loading, error } = useQuery(QUERY_DASHBOARD)
</script>

<template>
  <div>
    <VHeader title="Dashboard" />

    <VDataView :loading="loading" :error="error" :result="result" result-key="version">
      <section>
        <div class="mx-auto max-w-7xl">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <VStat name="Odooghost version" :stat="result.version" />
            <VStat name="Docker version" :stat="result.dockerVersion" />
            <VStat name="Stacks count" :stat="result.stackCount" />
          </div>
        </div>
      </section>
      <section>
        <h3>Running Containers</h3>
        <VContainers :containers="result.containers" />
      </section>
    </VDataView>
  </div>
</template>
