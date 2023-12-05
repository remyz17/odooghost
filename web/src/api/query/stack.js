import gql from 'graphql-tag'

export const QUERY_STACK = gql`
  query getStack($name: Int) {
    stack(name: $name) {
      name
    }
  }
`
export const QUERY_STACKS = gql`
  query getStacks {
    stacks {
      name
    }
  }
`
