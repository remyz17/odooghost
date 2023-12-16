import gql from 'graphql-tag'

export const SUBSCRIBE_EVEMTS = gql`
  subscription subscribeEvents {
    events {
      id
      action
      imageFrom
      containerId
      containerName
      stackName
      serviceName
    }
  }
`
