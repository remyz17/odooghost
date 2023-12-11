import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/dashboard/DashboardView.vue')
    },
    {
      path: '/stacks',
      name: 'stacks',
      component: () => import('@/views/stack/StackView.vue')
    },
    {
      path: '/stack/:stackId',
      name: 'stack',
      component: () => import('@/views/stack/StackItemView.vue'),
      children: [
        {
          path: '',
          name: 'stackIndex',
          component: () => import('@/views/stack/StackItemIndexView.vue')
        },
        {
          path: 'services',
          name: 'stackServices',
          component: () => import('@/views/stack/StackItemServicesView.vue')
        },
        {
          path: 'containers',
          name: 'stackContainers',
          component: () => import('@/views/stack/StackItemContainersView.vue')
        },
        {
          path: 'logs',
          name: 'stackLogs',
          component: () => import('@/views/stack/StackItemLogsView.vue')
        }
      ]
    },
    {
      path: '/usage',
      name: 'usage',
      component: () => import('@/views/usage/UsageView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/settings/SettingsView.vue')
    }
  ]
})

export default router
