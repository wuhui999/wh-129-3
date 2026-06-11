import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUser } from '../utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/permits',
    children: [
      { path: 'permits', name: 'Permits', component: () => import('../views/Permits.vue'), meta: { title: '许可管理', icon: 'Document', roles: ['constructor', 'inspector', 'heritage', 'safety'] } },
      { path: 'permits/create', name: 'PermitCreate', component: () => import('../views/PermitForm.vue'), meta: { title: '新建许可', roles: ['constructor'] } },
      { path: 'permits/:id', name: 'PermitDetail', component: () => import('../views/PermitDetail.vue'), meta: { title: '许可详情', roles: ['constructor', 'inspector', 'heritage', 'safety'] } },
      { path: 'approvals', name: 'Approvals', component: () => import('../views/Approvals.vue'), meta: { title: '审批管理', icon: 'Stamp', roles: ['heritage', 'safety'] } },
      { path: 'inspections', name: 'Inspections', component: () => import('../views/Inspections.vue'), meta: { title: '巡检管理', icon: 'View', roles: ['inspector'] } },
      { path: 'inspections/create', name: 'InspectionCreate', component: () => import('../views/InspectionForm.vue'), meta: { title: '新建巡检', roles: ['inspector'] } },
      { path: 'hazards', name: 'Hazards', component: () => import('../views/Hazards.vue'), meta: { title: '隐患整改', icon: 'Warning', roles: ['constructor', 'inspector', 'safety'] } },
      { path: 'demolitions', name: 'Demolitions', component: () => import('../views/Demolitions.vue'), meta: { title: '拆除验收', icon: 'Finished', roles: ['constructor', 'heritage', 'safety'] } },
      { path: 'audit-logs', name: 'AuditLogs', component: () => import('../views/AuditLogs.vue'), meta: { title: '审计日志', icon: 'List', roles: ['heritage', 'safety'] } },
      { path: 'buildings', name: 'Buildings', component: () => import('../views/Buildings.vue'), meta: { title: '建筑管理', icon: 'OfficeBuilding', roles: ['constructor', 'inspector', 'heritage', 'safety'] } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function getRoleDefaultPath(role) {
  const defaults = {
    constructor: '/permits',
    inspector: '/inspections',
    heritage: '/approvals',
    safety: '/approvals',
  }
  return defaults[role] || '/permits'
}

function hasPermission(route, role) {
  const roles = route.meta?.roles
  if (!roles) return true
  return roles.includes(role)
}

router.beforeEach((to, from, next) => {
  if (to.path === '/login') {
    next()
    return
  }
  const token = getToken()
  if (!token) {
    next('/login')
    return
  }
  const user = getUser()
  if (!user) {
    next('/login')
    return
  }
  if (to.matched.some(record => !hasPermission(record, user.role))) {
    next(getRoleDefaultPath(user.role))
    return
  }
  next()
})

export default router
export { getRoleDefaultPath, hasPermission }
