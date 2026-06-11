<template>
  <div>
    <div class="page-bar">
      <div>
        <el-button type="primary" v-if="user?.role === 'inspector'" @click="$router.push('/inspections/create')">
          <el-icon><Plus /></el-icon> 新建巡检
        </el-button>
      </div>
      <div>
        <el-select v-model="filterPermitId" placeholder="筛选许可" clearable @change="loadData" style="width:160px">
          <el-option v-for="p in allPermits" :key="p.id" :label="'#' + p.id + ' ' + p.building_name" :value="p.id" />
        </el-select>
        <el-button type="warning" @click="checkOverdue" style="margin-left:8px">
          <el-icon><Bell /></el-icon> 超期告警
        </el-button>
      </div>
    </div>
    <el-table :data="inspections" stripe border class="data-table">
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="permit_id" label="许可编号" width="90" />
      <el-table-column prop="inspector_name" label="巡检员" width="80" />
      <el-table-column prop="check_items" label="检查项" min-width="180" show-overflow-tooltip />
      <el-table-column prop="result" label="结果" width="80">
        <template #default="{ row }">
          <el-tag :type="row.result === 'normal' ? 'success' : 'danger'" size="small">{{ row.result === 'normal' ? '正常' : '异常' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="hazard_level" label="隐患等级" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.hazard_level !== 'none'" :type="hazardLevelTagType[row.hazard_level]" size="small">{{ hazardLevelMap[row.hazard_level] }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column prop="inspected_at" label="巡检时间" width="160" />
    </el-table>

    <el-dialog v-model="showOverdueDialog" title="超期告警" width="600px">
      <el-table :data="overdueAlerts" stripe border size="small">
        <el-table-column prop="permit_id" label="许可编号" width="90" />
        <el-table-column prop="building_name" label="建筑名称" width="140" />
        <el-table-column prop="last_inspected" label="上次巡检" width="180" />
        <el-table-column label="超期时长" width="100">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.overdue_hours }}小时</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!overdueAlerts.length" description="暂无超期告警" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInspections, getPermits, getOverdueAlert } from '../api'
import { getUser, hazardLevelMap, hazardLevelTagType } from '../utils/auth'

const user = getUser()
const inspections = ref([])
const allPermits = ref([])
const filterPermitId = ref('')
const showOverdueDialog = ref(false)
const overdueAlerts = ref([])

const loadData = async () => {
  const params = {}
  if (filterPermitId.value) params.permit_id = filterPermitId.value
  inspections.value = await getInspections(params)
}

const checkOverdue = async () => {
  const res = await getOverdueAlert()
  overdueAlerts.value = res.alerts || []
  showOverdueDialog.value = true
}

onMounted(async () => {
  await loadData()
  allPermits.value = await getPermits()
})
</script>

<style scoped>
.page-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.data-table { background: #fff; border-radius: 8px; }
</style>
