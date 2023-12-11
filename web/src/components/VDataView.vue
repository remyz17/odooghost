<script setup>
import VLoading from './VLoading.vue'
import VErrorAlert from './alerts/VErrorAlert.vue'
import VWarningAlert from './alerts/VWarningAlert.vue'

const props = defineProps({
  result: Object,
  loading: Boolean,
  error: Boolean,
  resultKey: String,
  isList: {
    type: Boolean,
    default: false
  }
})

const hasData = (result, key) => {
  return result && result[key] && (!props.isList || (props.isList && result[key].length > 0))
}
</script>

<template>
  <div class="py-20" v-if="props.loading">
    <slot name="loading">
      <VLoading />
    </slot>
  </div>
  <div v-else-if="props.error">
    <slot name="error">
      <div class="py-20 max-w-xl mx-auto">
        <VErrorAlert
          title="Une erreur est survenue !"
          text="Veuillez réessayer plus tard. Si le problème persiste, contactez votre administrateur."
        />
      </div>
    </slot>
  </div>
  <div v-else-if="!props.loading && hasData(props.result, props.resultKey)">
    <slot></slot>
  </div>
  <div v-else>
    <slot name="empty">
      <div class="py-20 max-w-xl mx-auto">
        <VWarningAlert
          title="Aucun résultat !"
          text="Si vous pensez que c'est une erreur, contactez votre administrateur."
        />
      </div>
    </slot>
  </div>
</template>
