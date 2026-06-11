<template>
  <div>
    <div class="page-bar">
      <h3 style="margin:0">拆除验收</h3>
    </div>
    <el-table :data="demolitions" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="permit_id" label="许可编号" width="90" />
      <el-table-column prop="demolish_date" label="拆除日期" width="120" />
      <el-table-column label="现场恢复" width="100">
        <template #default="{ row }">
          <el-tag :type="row.site_restored ? 'success' : 'danger'" size="small">{{ row.site_restored ? '已恢复' : '未恢复' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="restorer_name" label="提交人" width="90" />
      <el-table-column label="文保验收" min-width="160">
        <template #default="{ row }">
          <div class="accept-block">
            <div class="accept-row">
              <span :class="getStatusClass(row.heritage_result)">文保员</span>
              <el-tag v-if="row.heritage_result === 'accepted'" type="success" size="small">通过</el-tag>
              <el-tag v-else-if="row.heritage_result === 'rejected'" type="danger" size="small">不通过</el-tag>
              <el-tag v-else type="info" size="small">待验收</el-tag>
            </div>
            <div v-if="row.heritage_acceptor_name" class="accept-sub">验收人：{{ row.heritage_acceptor_name }}</div>
            <div v-if="row.heritage_opinion" class="accept-sub opinion" :title="row.heritage_opinion">意见：{{ row.heritage_opinion }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="安监验收" min-width="160">
        <template #default="{ row }">
          <div class="accept-block">
            <div class="accept-row">
              <span :class="getStatusClass(row.safety_result)">安监员</span>
              <el-tag v-if="row.safety_result === 'accepted'" type="success" size="small">通过</el-tag>
              <el-tag v-else-if="row.safety_result === 'rejected'" type="danger" size="small">不通过</el-tag>
              <el-tag v-else type="info" size="small">待验收</el-tag>
            </div>
            <div v-if="row.safety_acceptor_name" class="accept-sub">验收人：{{ row.safety_acceptor_name }}</div>
            <div v-if="row.safety_opinion" class="accept-sub opinion" :title="row.safety_opinion">意见：{{ row.safety_opinion }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="整体结果" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.accept_result === 'accepted'" type="success" size="small">通过</el-tag>
          <el-tag v-else-if="row.accept_result === 'rejected'" type="danger" size="small">不通过</el-tag>
          <el-tag v-else type="info" size="small">待验收</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" v-if="!row.site_restored && row.restorer_id === user?.id" @click="handleConfirmRestore(row.id)">确认恢复</el-button>
          <el-button link type="primary" v-if="canAccept(row)" @click="openAcceptDialog(row)">验收</el-button>
          <span v-if="!canAccept(row) && row.site_restored && (user?.role === 'heritage' || user?.role === 'safety')" class="muted-text">已验收</span>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAcceptDialog" :title="acceptDialogTitle" width="450px">
      <el-form :model="acceptForm" label-width="90px">
        <el-form-item label="验收意见">
          <el-input v-model="acceptForm.accept_opinion" type="textarea" :rows="3" placeholder="请输入验收意见" />
        </el-form-item>
        <el-form-item label="验收结果">
          <el-radio-group v-model="acceptForm.accept_result">
            <el-radio value="accepted">通过</el-radio>
            <el-radio value="rejected">不通过</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAcceptDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAccept">确认验收</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDemolitions, confirmRestore, acceptDemolition } from '../api'
import { getUser, roleMap } from '../utils/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const user = getUser()
const demolitions = ref([])
const showAcceptDialog = ref(false)
const currentDemolition = ref(null)
const acceptForm = ref({ accept_opinion: '', accept_result: 'accepted' })

const acceptDialogTitle = computed(() => {
  if (!currentDemolition.value) return '拆除验收'
  const roleName = user?.role === 'heritage' ? '文保员' : '安监员'
  return `${roleName}拆除验收`
})

const getStatusClass = (result) => {
  if (result === 'accepted') return 'status-ok'
  if (result === 'rejected') return 'status-reject'
  return 'status-pending'
}

const canAccept = (row) => {
  if (!row.site_restored) return false
  if (user?.role === 'heritage') {
    return !row.heritage_result || row.heritage_result === 'pending'
  }
  if (user?.role === 'safety') {
    return !row.safety_result || row.safety_result === 'pending'
  }
  return false
}

const loadData = async () => {
  demolitions.value = await getDemolitions()
}

const handleConfirmRestore = async (id) => {
  await ElMessageBox.confirm('确认现场已恢复？', '提示')
  await confirmRestore(id)
  ElMessage.success('现场恢复已确认')
  loadData()
}

const openAcceptDialog = (d) => {
  currentDemolition.value = d
  acceptForm.value = { accept_opinion: '', accept_result: 'accepted' }
  showAcceptDialog.value = true
}

const handleAccept = async () => {
  await acceptDemolition(currentDemolition.value.id, acceptForm.value)
  ElMessage.success(acceptForm.value.accept_result === 'accepted' ? '验收通过' : '验收不通过')
  showAcceptDialog.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
.accept-block { line-height: 1.5; }
.accept-row { display: flex; align-items: center; gap: 8px; }
.accept-sub { font-size: 12px; color: #606266; margin-top: 2px; }
.accept-sub.opinion { color: #909399; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px; }
.status-ok { color: #67c23a; font-weight: 600; }
.status-reject { color: #f56c6c; font-weight: 600; }
.status-pending { color: #909399; }
.muted-text { color: #c0c4cc; font-size: 13px; }
</style>
