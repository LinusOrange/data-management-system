import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from './views/DashboardView.vue'
import UploadView from './views/UploadView.vue'
import DatabaseView from './views/DatabaseView.vue'
import FileManagementView from './views/FileManagementView.vue'
import ReconciliationView from './views/ReconciliationView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: DashboardView },
  { path: '/upload', component: UploadView },
  { path: '/database', component: DatabaseView },
  { path: '/files', component: FileManagementView },
  { path: '/reconciliation', component: ReconciliationView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
