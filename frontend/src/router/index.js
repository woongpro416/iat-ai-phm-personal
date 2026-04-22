import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '../views/DashboardView.vue'
import SafetyEventView from '../views/SafetyEventView.vue'
import AlertView from '../views/AlertView.vue'
import DeviceStatusView from '../views/DeviceStatusView.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
  },
  {
    path: '/safety-events',
    name: 'SafetyEvents',
    component: SafetyEventView,
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: AlertView,
  },
  {
    path: '/device-status',
    name: 'DeviceStatus',
    component: DeviceStatusView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router