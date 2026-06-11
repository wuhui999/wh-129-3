<template>
  <div>
    <div class="page-bar">
      <h3 style="margin:0">审计日志</h3>
      <div>
        <el-select v-model="filterType" placeholder="类型筛选" clearable @change="loadData" style="width:140px">
          <el-option label="许可" value="permit" />
          <el-option label="审批" value="approval" />
          <el-option label="巡检" value="inspection" />
          <el-option label="隐患" value="hazard" />
          <el-option label="拆除验收" value="demolition" />
        </el-select>
      </div>
    </div>
    <el-table :data="logs" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="user_name" label="操作人" width="90" />
      <el-table-column prop="action" label="操作" width="160" />
      <el-table-column prop="target_type" label="目标类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ targetTypeMap[row.target_type] || row.target_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_id" label="目标ID" width="80" />
      <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="170" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAuditLogs } from '../api'

const logs = ref([])
const filterType = ref('')

const targetTypeMap = {
  permit: '许可',
  approval: '审批',
  inspection: '巡检',
  hazard: '隐患',
  demolition: '拆除验收',
}

const loadData = async () => {
  const params = {}
  if (filterType.value) params.target_type = filterType.value
  logs.value = await getAuditLogs(params)
}

onMounted(loadData)
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
</style>
