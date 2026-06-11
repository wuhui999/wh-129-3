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
      <el-table-column prop="acceptor_name" label="验收人" width="90" />
      <el-table-column prop="accept_opinion" label="验收意见" min-width="150" show-overflow-tooltip />
      <el-table-column label="验收结果" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.accept_result === 'accepted'" type="success" size="small">通过</el-tag>
          <el-tag v-else-if="row.accept_result === 'rejected'" type="danger" size="small">不通过</el-tag>
          <el-tag v-else type="info" size="small">待验收</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" v-if="!row.site_restored && row.restorer_id === user?.id" @click="handleConfirmRestore(row.id)">确认恢复</el-button>
          <el-button link type="primary" v-if="row.site_restored && row.accept_result === 'pending' && (user?.role === 'heritage' || user?.role === 'safety')" @click="openAcceptDialog(row)">验收</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAcceptDialog" title="拆除验收" width="450px">
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
import { ref, onMounted } from 'vue'
import { getDemolitions, confirmRestore, acceptDemolition } from '../api'
import { getUser } from '../utils/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const user = getUser()
const demolitions = ref([])
const showAcceptDialog = ref(false)
const currentDemolition = ref(null)
const acceptForm = ref({ accept_opinion: '', accept_result: 'accepted' })

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
</style>
