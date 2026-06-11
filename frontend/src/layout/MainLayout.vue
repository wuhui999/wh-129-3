<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="layout-aside">
      <div class="logo-area">
        <h3>脚手架管理</h3>
      </div>
      <el-menu :default-active="activeMenu" router class="side-menu" background-color="#1a1a2e" text-color="#ccc" active-text-color="#409eff">
        <el-menu-item v-for="item in visibleMenus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-tag v-if="overdueCount > 0" type="danger" effect="dark" class="alert-tag">
            <el-icon><Bell /></el-icon> {{ overdueCount }}条超期告警
          </el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ user?.real_name }} <el-tag size="small" type="info">{{ roleMap[user?.role] }}</el-tag>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUser, logout, roleMap } from '../utils/auth'
import { getOverdueAlert } from '../api'
import { Document, Stamp, View, Warning, Finished, List, OfficeBuilding } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const user = ref(getUser())
const overdueCount = ref(0)

const allMenus = [
  { path: '/permits', title: '许可管理', icon: Document, roles: ['constructor', 'inspector', 'heritage', 'safety'] },
  { path: '/approvals', title: '审批管理', icon: Stamp, roles: ['heritage', 'safety'] },
  { path: '/inspections', title: '巡检管理', icon: View, roles: ['inspector'] },
  { path: '/hazards', title: '隐患整改', icon: Warning, roles: ['constructor', 'inspector', 'safety'] },
  { path: '/demolitions', title: '拆除验收', icon: Finished, roles: ['constructor', 'heritage', 'safety'] },
  { path: '/buildings', title: '建筑管理', icon: OfficeBuilding, roles: ['constructor', 'inspector', 'heritage', 'safety'] },
  { path: '/audit-logs', title: '审计日志', icon: List, roles: ['heritage', 'safety'] },
]

const visibleMenus = computed(() => {
  if (!user.value?.role) return []
  return allMenus.filter(m => m.roles.includes(user.value.role))
})

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/permits')) return '/permits'
  if (path.startsWith('/inspections')) return '/inspections'
  if (path.startsWith('/hazards')) return '/hazards'
  return path
})

const currentTitle = computed(() => route.meta?.title || '')

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    logout()
    router.push('/login')
  }
}

onMounted(async () => {
  user.value = getUser()
  try {
    const res = await getOverdueAlert()
    overdueCount.value = res.alerts?.length || 0
  } catch {}
})
</script>

<style scoped>
.layout-container { height: 100vh; }
.layout-aside {
  background: #1a1a2e;
  overflow-y: auto;
}
.logo-area {
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo-area h3 {
  color: #fff;
  font-size: 18px;
  letter-spacing: 3px;
  margin: 0;
}
.side-menu {
  border-right: none;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
  height: 56px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #333;
}
.alert-tag {
  cursor: pointer;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.layout-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
