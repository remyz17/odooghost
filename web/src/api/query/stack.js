import gql from 'graphql-tag'

export const QUERY_STACK = gql`
  query getStack($name: String!) {
    stack(name: $name) {
      name
      state
      odooVersion
      dbVersion
      networkMode
      containers {
        id
        name
        image
        service
        state
      }
    }
  }
`
export const QUERY_STACKS = gql`
  query getStacks {
    stacks {
      name
      state
      odooVersion
      dbVersion
    }
  }
`

export const QUERY_CONTAINERS = gql`
  query getContainers {
    containers {
      id
      name
      image
      service
      state
    }
  }
`
