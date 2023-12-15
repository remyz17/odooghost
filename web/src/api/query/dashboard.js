import gql from 'graphql-tag'

export const QUERY_DASHBOARD = gql`
  query getDashboard {
    version
    dockerVersion
    stackCount
    containers(stopped: false) {
      id
      name
      image
      service
      state
    }
  }
`
