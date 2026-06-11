<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>古建筑修缮</h1>
        <h2>脚手架许可与巡检系统</h2>
      </div>
      <el-form :model="form" @submit.prevent="handleLogin" class="login-form">
        <el-form-item>
          <el-input v-model="form.username" prefix-icon="User" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" prefix-icon="Lock" placeholder="密码" type="password" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width:100%">登 录</el-button>
        </el-form-item>
      </el-form>
      <div class="demo-accounts">
        <p class="demo-title">演示账号（密码均为 123456）</p>
        <div class="demo-grid">
          <el-tag @click="fillAccount('constructor1')" class="demo-tag">施工单位 - 张建国</el-tag>
          <el-tag @click="fillAccount('inspector1')" type="warning" class="demo-tag">巡检员 - 王巡检</el-tag>
          <el-tag @click="fillAccount('heritage1')" type="success" class="demo-tag">文保员 - 陈文保</el-tag>
          <el-tag @click="fillAccount('safety1')" type="danger" class="demo-tag">安监员 - 刘安监</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'
import { setToken, setUser } from '../utils/auth'
import { getRoleDefaultPath } from '../router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const fillAccount = (username) => {
  form.value.username = username
  form.value.password = '123456'
}

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await login(form.value)
    setToken(res.access_token)
    setUser(res.user)
    ElMessage.success('登录成功')
    router.push(getRoleDefaultPath(res.user.role))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
.login-card {
  width: 420px;
  padding: 48px 40px 32px;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-header {
  text-align: center;
  margin-bottom: 36px;
}
.login-header h1 {
  font-size: 28px;
  color: #1a1a2e;
  margin: 0 0 8px;
  font-weight: 700;
  letter-spacing: 4px;
}
.login-header h2 {
  font-size: 16px;
  color: #666;
  margin: 0;
  font-weight: 400;
  letter-spacing: 2px;
}
.login-form { margin-bottom: 24px; }
.demo-accounts {
  border-top: 1px solid #eee;
  padding-top: 20px;
}
.demo-title {
  font-size: 12px;
  color: #999;
  margin: 0 0 12px;
  text-align: center;
}
.demo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.demo-tag {
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.demo-tag:hover { transform: scale(1.05); }
</style>
