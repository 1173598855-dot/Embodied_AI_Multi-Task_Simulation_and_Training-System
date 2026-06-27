import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/tasks', name: 'Tasks', component: () => import('../views/TaskList.vue') },
  { path: '/training/:id', name: 'Training', component: () => import('../views/Training.vue') },
  { path: '/logs', name: 'Logs', component: () => import('../views/Logs.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
