import gql from 'graphql-tag'

export const MUTATION_START_STACK = gql`
  mutation startStack($name: String!) {
    startStack(name: $name) {
      ... on StartStackSuccess {
        name
      }
      ... on StartStackError {
        message
      }
    }
  }
`

export const MUTATION_STOP_STACK = gql`
  mutation stopStack($name: String!) {
    stopStack(name: $name) {
      ... on StopStackSuccess {
        name
      }
      ... on StopStackError {
        message
      }
    }
  }
`

export const MUTATION_RESTART_STACK = gql`
  mutation restartStack($name: String!) {
    restartStack(name: $name) {
      ... on RestartStackSuccess {
        name
      }
      ... on RestartStackError {
        message
      }
    }
  }
`
