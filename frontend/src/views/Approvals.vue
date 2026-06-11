<template>
  <div>
    <div class="page-bar">
      <h3 style="margin:0">待审批许可</h3>
    </div>
    <el-table :data="permits" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="building_name" label="建筑名称" width="140" />
      <el-table-column prop="scaffold_scope" label="搭设范围" min-width="160" show-overflow-tooltip />
      <el-table-column prop="constructor_name" label="施工单位" width="100" />
      <el-table-column prop="start_date" label="开始日期" width="110" />
      <el-table-column prop="end_date" label="结束日期" width="110" />
      <el-table-column label="审批进度" width="120">
        <template #default="{ row }">
          <span :class="row.heritage_approved ? 'text-success' : 'text-muted'">文保</span>
          <span class="text-muted">/</span>
          <span :class="row.safety_approved ? 'text-success' : 'text-muted'">安监</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openApproveDialog(row)">审批</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="审批许可" width="550px">
      <el-descriptions :column="1" border size="small" v-if="currentPermit">
        <el-descriptions-item label="建筑">{{ currentPermit.building_name }}</el-descriptions-item>
        <el-descriptions-item label="搭设范围">{{ currentPermit.scaffold_scope }}</el-descriptions-item>
        <el-descriptions-item label="工期">{{ currentPermit.start_date }} ~ {{ currentPermit.end_date }}</el-descriptions-item>
        <el-descriptions-item label="方案附件">
          <el-link v-if="currentPermit.plan_attachment" :href="currentPermit.plan_attachment" type="primary" target="_blank">查看</el-link>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form :model="approveForm" label-width="100px" style="margin-top:20px">
        <el-form-item label="审批类型">
          <el-radio-group v-model="approveForm.approval_type">
            <el-radio value="heritage" :disabled="user?.role !== 'heritage'">文保审批</el-radio>
            <el-radio value="safety" :disabled="user?.role !== 'safety'">安监审批</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批结果">
          <el-radio-group v-model="approveForm.result">
            <el-radio value="approved">通过</el-radio>
            <el-radio value="rejected">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.opinion" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
        <el-form-item label="附加条件">
          <el-input v-model="approveForm.conditions" type="textarea" :rows="2" placeholder="如需附加条件请填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleApprove" :loading="submitting">提交审批</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPermits, approvePermit } from '../api'
import { getUser } from '../utils/auth'
import { ElMessage } from 'element-plus'

const user = getUser()
const permits = ref([])
const showDialog = ref(false)
const submitting = ref(false)
const currentPermit = ref(null)
const approveForm = ref({ approval_type: user?.role === 'heritage' ? 'heritage' : 'safety', result: 'approved', opinion: '', conditions: '' })

const loadData = async () => {
  const res = await getPermits({ status: 'approving' })
  permits.value = res
}

const openApproveDialog = (permit) => {
  currentPermit.value = permit
  approveForm.value.approval_type = user?.role === 'heritage' ? 'heritage' : 'safety'
  approveForm.value.result = 'approved'
  approveForm.value.opinion = ''
  approveForm.value.conditions = ''
  showDialog.value = true
}

const handleApprove = async () => {
  if (!currentPermit.value) return
  submitting.value = true
  try {
    await approvePermit(currentPermit.value.id, approveForm.value)
    ElMessage.success('审批已提交')
    showDialog.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
.text-success { color: #67c23a; font-weight: 600; }
.text-muted { color: #c0c4cc; }
</style>
