<template>
  <div v-loading="loading">
    <div class="page-bar">
      <el-page-header @back="$router.push('/permits')" :content="'许可详情 #' + permit?.id" />
    </div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="statusTagType[permit?.status]" size="large">{{ statusMap[permit?.status] }}</el-tag>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="建筑名称">{{ permit?.building_name }}</el-descriptions-item>
            <el-descriptions-item label="施工单位">{{ permit?.constructor_name }}</el-descriptions-item>
            <el-descriptions-item label="搭设范围" :span="2">{{ permit?.scaffold_scope }}</el-descriptions-item>
            <el-descriptions-item label="开始日期">{{ permit?.start_date }}</el-descriptions-item>
            <el-descriptions-item label="结束日期">{{ permit?.end_date }}</el-descriptions-item>
            <el-descriptions-item label="方案附件" :span="2">
              <el-link v-if="permit?.plan_attachment" :href="permit.plan_attachment" type="primary" target="_blank">查看方案</el-link>
              <span v-else class="text-muted">未上传</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ permit?.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ permit?.updated_at }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card">
          <template #header><span>审批记录</span></template>
          <el-timeline v-if="approvals.length">
            <el-timeline-item v-for="a in approvals" :key="a.id" :timestamp="a.created_at" placement="top">
              <el-card shadow="never">
                <p><strong>{{ a.approval_type === 'heritage' ? '文保审批' : '安监审批' }}</strong>
                  <el-tag :type="a.result === 'approved' ? 'success' : 'danger'" size="small" style="margin-left:8px">
                    {{ a.result === 'approved' ? '通过' : '驳回' }}
                  </el-tag>
                </p>
                <p>审批人：{{ a.approver_name }}</p>
                <p v-if="a.opinion">意见：{{ a.opinion }}</p>
                <p v-if="a.conditions">附加条件：{{ a.conditions }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无审批记录" />
        </el-card>

        <el-card class="detail-card">
          <template #header><span>巡检记录</span></template>
          <el-table :data="inspections" stripe border size="small" v-if="inspections.length">
            <el-table-column prop="inspector_name" label="巡检员" width="80" />
            <el-table-column prop="check_items" label="检查项" show-overflow-tooltip />
            <el-table-column prop="result" label="结果" width="80" />
            <el-table-column prop="hazard_level" label="隐患等级" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.hazard_level !== 'none'" :type="hazardLevelTagType[row.hazard_level]" size="small">{{ hazardLevelMap[row.hazard_level] }}</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="inspected_at" label="时间" width="160" />
          </el-table>
          <el-empty v-else description="暂无巡检记录" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="detail-card">
          <template #header><span>状态操作</span></template>
          <div class="action-area">
            <el-button v-if="permit?.status === 'applied' && user?.role === 'constructor' && permit?.constructor_id === user?.id" type="warning" @click="handleSubmit" style="width:100%">提交审批</el-button>
            <el-button v-if="permit?.status === 'can_scaffold' && user?.role === 'constructor' && permit?.constructor_id === user?.id" type="success" @click="handleStartUse" style="width:100%">开始使用</el-button>
            <el-button v-if="permit?.status === 'in_use' && user?.role === 'constructor' && permit?.constructor_id === user?.id" type="danger" @click="handleRequestDemolish" style="width:100%">申请拆除</el-button>
            <el-button v-if="permit?.status === 'in_use' && user?.role === 'inspector'" type="primary" @click="$router.push({ path: '/inspections/create', query: { permit_id: permit?.id } })" style="width:100%">新建巡检</el-button>
            <el-button v-if="permit?.status === 'pending_demolish' && user?.role === 'constructor'" type="primary" @click="showDemolishDialog = true" style="width:100%">提交拆除验收</el-button>
          </div>
        </el-card>

        <el-card class="detail-card">
          <template #header><span>隐患汇总</span></template>
          <div v-if="hazards.length">
            <div v-for="h in hazards" :key="h.id" class="hazard-item">
              <el-tag :type="hazardLevelTagType[h.level]" size="small">{{ hazardLevelMap[h.level] }}</el-tag>
              <span class="hazard-desc">{{ h.description }}</span>
              <el-tag size="small" :type="h.status === 'closed' ? 'success' : 'warning'">{{ hazardStatusMap[h.status] }}</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无隐患" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showDemolishDialog" title="拆除验收" width="500px">
      <el-form :model="demolishForm" label-width="100px">
        <el-form-item label="拆除日期" required>
          <el-date-picker v-model="demolishForm.demolish_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="现场恢复">
          <el-switch v-model="demolishForm.site_restored" :active-value="1" :inactive-value="0" active-text="已恢复" inactive-text="未恢复" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDemolishDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateDemolition">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getPermit, getApprovals, getInspections, getHazards, submitPermit, startUsePermit, requestDemolish, createDemolition } from '../api'
import { getUser, statusMap, statusTagType, hazardLevelMap, hazardLevelTagType, hazardStatusMap } from '../utils/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const user = getUser()
const permit = ref(null)
const approvals = ref([])
const inspections = ref([])
const hazards = ref([])
const loading = ref(true)
const showDemolishDialog = ref(false)
const demolishForm = ref({ demolish_date: '', site_restored: 0 })

const loadData = async () => {
  const id = route.params.id
  permit.value = await getPermit(id)
  approvals.value = await getApprovals(id)
  inspections.value = await getInspections({ permit_id: id })
  hazards.value = await getHazards({ permit_id: id })
  loading.value = false
}

const handleSubmit = async () => {
  await ElMessageBox.confirm('确认提交审批？', '提示')
  await submitPermit(permit.value.id)
  ElMessage.success('已提交审批')
  loadData()
}

const handleStartUse = async () => {
  await ElMessageBox.confirm('确认开始使用？', '提示')
  await startUsePermit(permit.value.id)
  ElMessage.success('已开始使用')
  loadData()
}

const handleRequestDemolish = async () => {
  await ElMessageBox.confirm('确认申请拆除？', '提示')
  try {
    await requestDemolish(permit.value.id)
    ElMessage.success('已申请拆除')
    loadData()
  } catch {}
}

const handleCreateDemolition = async () => {
  if (!demolishForm.value.demolish_date) {
    ElMessage.warning('请选择拆除日期')
    return
  }
  await createDemolition({ ...demolishForm.value, permit_id: permit.value.id })
  ElMessage.success('拆除验收已提交')
  showDemolishDialog.value = false
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-bar { margin-bottom: 16px; }
.detail-card { margin-bottom: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.action-area { display: flex; flex-direction: column; gap: 10px; }
.hazard-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f0f0f0; }
.hazard-desc { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.text-muted { color: #c0c4cc; }
</style>
