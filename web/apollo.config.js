module.exports = {
  client: {
    service: {
      name: 'odoogghost',
      // URL to the GraphQL API
      url: 'http://localhost:8000/graphql'
    },
    // Files processed by the extension
    includes: ['src/**/*.vue', 'src/**/*.js']
  }
}
