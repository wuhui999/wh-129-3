<template>
  <div>
    <div class="page-bar">
      <el-button type="primary" @click="$router.push('/permits/create')" v-if="user?.role === 'constructor'">
        <el-icon><Plus /></el-icon> 新建许可申请
      </el-button>
      <div>
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="loadData" style="width:140px">
          <el-option v-for="(v,k) in statusMap" :key="k" :label="v" :value="k" />
        </el-select>
      </div>
    </div>
    <el-table :data="permits" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="building_name" label="建筑名称" width="140" />
      <el-table-column prop="scaffold_scope" label="搭设范围" min-width="160" show-overflow-tooltip />
      <el-table-column prop="constructor_name" label="施工单位" width="100" />
      <el-table-column prop="start_date" label="开始日期" width="110" />
      <el-table-column prop="end_date" label="结束日期" width="110" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType[row.status]" size="small">{{ statusMap[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审批" width="120">
        <template #default="{ row }">
          <span :class="row.heritage_approved ? 'text-success' : 'text-muted'">文保</span>
          <span class="text-muted">/</span>
          <span :class="row.safety_approved ? 'text-success' : 'text-muted'">安监</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/permits/${row.id}`)">详情</el-button>
          <el-button link type="warning" v-if="row.status === 'applied' && user?.role === 'constructor' && row.constructor_id === user?.id" @click="handleSubmit(row.id)">提交审批</el-button>
          <el-button link type="success" v-if="row.status === 'can_scaffold' && user?.role === 'constructor' && row.constructor_id === user?.id" @click="handleStartUse(row.id)">开始使用</el-button>
          <el-button link type="danger" v-if="row.status === 'in_use' && user?.role === 'constructor' && row.constructor_id === user?.id" @click="handleRequestDemolish(row.id)">申请拆除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPermits, submitPermit, startUsePermit, requestDemolish } from '../api'
import { getUser, statusMap, statusTagType } from '../utils/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const user = getUser()
const permits = ref([])
const filterStatus = ref('')

const loadData = async () => {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  permits.value = await getPermits(params)
}

const handleSubmit = async (id) => {
  await ElMessageBox.confirm('确认提交审批？', '提示')
  await submitPermit(id)
  ElMessage.success('已提交审批')
  loadData()
}

const handleStartUse = async (id) => {
  await ElMessageBox.confirm('确认开始使用？脚手架已搭设完毕', '提示')
  await startUsePermit(id)
  ElMessage.success('已开始使用')
  loadData()
}

const handleRequestDemolish = async (id) => {
  await ElMessageBox.confirm('确认申请拆除？需确保无未关闭重大隐患', '提示')
  try {
    await requestDemolish(id)
    ElMessage.success('已申请拆除')
    loadData()
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.data-table { background: #fff; border-radius: 8px; }
.text-success { color: #67c23a; font-weight: 600; }
.text-muted { color: #c0c4cc; }
</style>
