<template>
  <div>
    <div class="page-bar">
      <h3 style="margin:0">建筑管理</h3>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> 新增建筑
      </el-button>
    </div>
    <el-table :data="buildings" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="name" label="建筑名称" width="140" />
      <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="heritage_level" label="保护级别" width="100">
        <template #default="{ row }">
          <el-tag :type="levelTagType(row.heritage_level)" size="small">{{ row.heritage_level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
    </el-table>

    <el-dialog v-model="showCreateDialog" title="新增建筑" width="500px">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="建筑名称" required>
          <el-input v-model="createForm.name" placeholder="请输入建筑名称" />
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="createForm.address" placeholder="请输入建筑地址" />
        </el-form-item>
        <el-form-item label="保护级别">
          <el-select v-model="createForm.heritage_level" style="width:100%">
            <el-option label="国家级" value="国家级" />
            <el-option label="省级" value="省级" />
            <el-option label="市级" value="市级" />
            <el-option label="区级" value="区级" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="建筑描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确认新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBuildings, createBuilding } from '../api'
import { ElMessage } from 'element-plus'

const buildings = ref([])
const showCreateDialog = ref(false)
const createForm = ref({ name: '', address: '', heritage_level: '市级', description: '' })

const levelTagType = (level) => {
  const map = { '国家级': 'danger', '省级': 'warning', '市级': '', '区级': 'info' }
  return map[level] || 'info'
}

const loadData = async () => {
  buildings.value = await getBuildings()
}

const handleCreate = async () => {
  if (!createForm.value.name || !createForm.value.address) {
    ElMessage.warning('请填写必填项')
    return
  }
  await createBuilding(createForm.value)
  ElMessage.success('建筑已新增')
  showCreateDialog.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
</style>
