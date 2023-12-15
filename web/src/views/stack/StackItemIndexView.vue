<script setup>
import VContainers from '@/components/VContainers.vue'
import VStat from '@/components/VStat.vue'
import { inject } from 'vue'

const stack = inject('stack')
</script>

<template>
  <div>
    <!-- Stats -->
    <section>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <VStat name="Odoo version" :stat="stack.odooVersion" />
        <VStat name="PostgresQL version" :stat="stack.dbVersion" />
      </div>
    </section>

    <section>
      <h3>Containers</h3>
      <VContainers :containers="stack.containers" />
    </section>
  </div>
</template>
