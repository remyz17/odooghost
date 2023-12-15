import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core'

export const apolloClient = new ApolloClient({
  link: createHttpLink({
    uri: import.meta.env.VITE_API_URL
  }),
  cache: new InMemoryCache()
})
