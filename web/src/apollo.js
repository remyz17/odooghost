import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core'

export const apolloClient = new ApolloClient({
  link: createHttpLink({
    uri: 'http://localhost:8000/graphql'
  }),
  cache: new InMemoryCache()
})
