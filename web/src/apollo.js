import { ApolloClient, ApolloLink, HttpLink, InMemoryCache, split } from '@apollo/client/core'
import { onError } from '@apollo/client/link/error'
import { GraphQLWsLink } from '@apollo/client/link/subscriptions' // <-- This one uses graphql-ws
import { getMainDefinition } from '@apollo/client/utilities'
import { createClient } from 'graphql-ws'
import { markRaw } from 'vue'
import VNetworkError from './components/modals/VNetworkError.vue'
import { useModalStore } from './stores/modal'

const wsLink = new GraphQLWsLink(
  createClient({
    url: 'ws://localhost:8000/graphql'
  })
)

const errorLink = onError(({ networkError }) => {
  const store = useModalStore()
  if (networkError && (networkError.statusCode >= 500 || networkError.statusCode == undefined)) {
    store.openModal({
      title: 'Voulez-vous continuer ?',
      message: 'Vous êtes sur le point de fermer un ticket. Celui-ci ne pourra pas être réouvert.',
      callback: null,
      component: markRaw(VNetworkError)
    })
  }
})

const httpLink = new HttpLink({
  uri: import.meta.env.VITE_API_URL
})

const link = split(
  // split based on operation type
  ({ query }) => {
    const definition = getMainDefinition(query)
    return definition.kind === 'OperationDefinition' && definition.operation === 'subscription'
  },
  wsLink,
  httpLink
)

export const apolloClient = new ApolloClient({
  link: ApolloLink.from([errorLink, link]),
  cache: new InMemoryCache()
})
