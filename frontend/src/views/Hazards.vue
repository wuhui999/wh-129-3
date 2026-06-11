<template>
  <div>
    <div class="page-bar">
      <div>
        <el-button type="danger" v-if="user?.role === 'inspector'" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 上报隐患
        </el-button>
      </div>
      <div>
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="loadData" style="width:120px;margin-right:8px">
          <el-option v-for="(v,k) in hazardStatusMap" :key="k" :label="v" :value="k" />
        </el-select>
        <el-select v-model="filterLevel" placeholder="等级筛选" clearable @change="loadData" style="width:120px">
          <el-option v-for="(v,k) in hazardLevelMap" :key="k" :label="v" :value="k" />
        </el-select>
      </div>
    </div>
    <el-table :data="hazards" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="permit_id" label="许可编号" width="90" />
      <el-table-column label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="hazardLevelTagType[row.level]" size="small">{{ hazardLevelMap[row.level] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="隐患描述" min-width="180" show-overflow-tooltip />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'closed' ? 'success' : 'warning'" size="small">{{ hazardStatusMap[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="assignee_name" label="整改人" width="80" />
      <el-table-column prop="rectify_result" label="整改结果" min-width="120" show-overflow-tooltip />
      <el-table-column prop="rechecker_name" label="复查人" width="80" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" v-if="row.status === 'open' && (user?.role === 'inspector' || user?.role === 'safety')" @click="openAssignDialog(row)">派单</el-button>
          <el-button link type="warning" v-if="row.status === 'assigned' && row.assigned_to === user?.id" @click="openRectifyDialog(row)">整改</el-button>
          <el-button link type="success" v-if="row.status === 'recheck' && (user?.role === 'inspector' || user?.role === 'safety')" @click="openRecheckDialog(row)">复查</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreateDialog" title="上报隐患" width="500px">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="许可编号" required>
          <el-select v-model="createForm.permit_id" placeholder="选择许可" style="width:100%">
            <el-option v-for="p in permits" :key="p.id" :label="'#' + p.id + ' ' + p.building_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="隐患等级" required>
          <el-select v-model="createForm.level" style="width:100%">
            <el-option label="一般隐患" value="minor" />
            <el-option label="较大隐患" value="major" />
            <el-option label="重大隐患" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="隐患描述" required>
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="详细描述隐患情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确认上报</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAssignDialog" title="隐患派单" width="450px">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="整改人" required>
          <el-select v-model="assignForm.assigned_to" style="width:100%">
            <el-option v-for="u in constructors" :key="u.id" :label="u.real_name + ' (' + u.org_name + ')'" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAssign">确认派单</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRectifyDialog" title="提交整改" width="450px">
      <el-form :model="rectifyForm" label-width="80px">
        <el-form-item label="整改结果" required>
          <el-input v-model="rectifyForm.rectify_result" type="textarea" :rows="3" placeholder="描述整改措施和结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRectifyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRectify">提交整改</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRecheckDialog" title="复查隐患" width="450px">
      <el-form :model="recheckForm" label-width="80px">
        <el-form-item label="复查结果" required>
          <el-radio-group v-model="recheckForm.recheck_result">
            <el-radio value="pass">通过（关闭隐患）</el-radio>
            <el-radio value="fail">不通过（重新整改）</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecheckDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRecheck">确认复查</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHazards, createHazard, assignHazard, rectifyHazard, recheckHazard, getPermits, getUsers } from '../api'
import { getUser, hazardLevelMap, hazardLevelTagType, hazardStatusMap } from '../utils/auth'
import { ElMessage } from 'element-plus'

const user = getUser()
const hazards = ref([])
const permits = ref([])
const constructors = ref([])
const filterStatus = ref('')
const filterLevel = ref('')

const showCreateDialog = ref(false)
const showAssignDialog = ref(false)
const showRectifyDialog = ref(false)
const showRecheckDialog = ref(false)

const currentHazard = ref(null)
const createForm = ref({ permit_id: '', level: 'minor', description: '' })
const assignForm = ref({ assigned_to: '' })
const rectifyForm = ref({ rectify_result: '' })
const recheckForm = ref({ recheck_result: 'pass' })

const loadData = async () => {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  if (filterLevel.value) params.level = filterLevel.value
  hazards.value = await getHazards(params)
}

const openAssignDialog = (h) => {
  currentHazard.value = h
  assignForm.value.assigned_to = ''
  showAssignDialog.value = true
}

const openRectifyDialog = (h) => {
  currentHazard.value = h
  rectifyForm.value.rectify_result = ''
  showRectifyDialog.value = true
}

const openRecheckDialog = (h) => {
  currentHazard.value = h
  recheckForm.value.recheck_result = 'pass'
  showRecheckDialog.value = true
}

const handleCreate = async () => {
  if (!createForm.value.permit_id || !createForm.value.description) {
    ElMessage.warning('请填写必填项')
    return
  }
  await createHazard(createForm.value)
  ElMessage.success('隐患已上报')
  showCreateDialog.value = false
  loadData()
}

const handleAssign = async () => {
  if (!assignForm.value.assigned_to) {
    ElMessage.warning('请选择整改人')
    return
  }
  await assignHazard(currentHazard.value.id, assignForm.value)
  ElMessage.success('已派单')
  showAssignDialog.value = false
  loadData()
}

const handleRectify = async () => {
  if (!rectifyForm.value.rectify_result) {
    ElMessage.warning('请填写整改结果')
    return
  }
  await rectifyHazard(currentHazard.value.id, rectifyForm.value)
  ElMessage.success('整改已提交')
  showRectifyDialog.value = false
  loadData()
}

const handleRecheck = async () => {
  await recheckHazard(currentHazard.value.id, recheckForm.value)
  ElMessage.success(recheckForm.value.recheck_result === 'pass' ? '隐患已关闭' : '已退回重新整改')
  showRecheckDialog.value = false
  loadData()
}

onMounted(async () => {
  await loadData()
  permits.value = await getPermits()
  constructors.value = await getUsers({ role: 'constructor' })
})
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
</style>
