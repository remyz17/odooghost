import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: import('@/views/dashboard/DashboardView.vue')
    },
    {
      path: '/stacks',
      name: 'stacks',
      component: import('@/views/stack/StackView.vue')
    },
    {
      path: '/usage',
      name: 'usage',
      component: import('@/views/usage/UsageView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: import('@/views/settings/SettingsView.vue')
    }
  ]
})

export default router
