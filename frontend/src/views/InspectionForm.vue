<template>
  <div>
    <div class="page-bar">
      <el-page-header @back="$router.push('/inspections')" content="新建巡检记录" />
    </div>
    <el-card>
      <el-form :model="form" label-width="100px" style="max-width:600px">
        <el-form-item label="许可编号" required>
          <el-select v-model="form.permit_id" placeholder="选择使用中的许可" style="width:100%">
            <el-option v-for="p in permits" :key="p.id" :label="'#' + p.id + ' ' + p.building_name + ' (' + p.scaffold_scope?.substring(0,20) + ')'" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查项" required>
          <el-checkbox-group v-model="checkItems">
            <el-checkbox label="扣件紧固" value="扣件紧固" />
            <el-checkbox label="荷载合规" value="荷载合规" />
            <el-checkbox label="警示标识" value="警示标识" />
            <el-checkbox label="立杆垂直" value="立杆垂直" />
            <el-checkbox label="连墙件" value="连墙件" />
            <el-checkbox label="扫地杆" value="扫地杆" />
            <el-checkbox label="防护栏杆" value="防护栏杆" />
            <el-checkbox label="脚手板" value="脚手板" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="检查结果">
          <el-radio-group v-model="form.result">
            <el-radio value="normal">正常</el-radio>
            <el-radio value="abnormal">异常</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="隐患等级" v-if="form.result === 'abnormal'">
          <el-select v-model="form.hazard_level" style="width:100%">
            <el-option label="一般隐患" value="minor" />
            <el-option label="较大隐患" value="major" />
            <el-option label="重大隐患" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="照片链接">
          <el-input v-model="form.photos" placeholder="巡检照片链接，多个用逗号分隔" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="巡检备注信息" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">提交巡检</el-button>
          <el-button @click="$router.push('/inspections')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createInspection, getPermits } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const permits = ref([])
const checkItems = ref([])
const form = ref({
  permit_id: route.query.permit_id ? Number(route.query.permit_id) : '',
  check_items: '',
  result: 'normal',
  photos: '',
  hazard_level: 'none',
  remark: '',
})

const handleSubmit = async () => {
  if (!form.value.permit_id || !checkItems.value.length) {
    ElMessage.warning('请填写必填项')
    return
  }
  form.value.check_items = checkItems.value.join('、')
  if (form.value.result === 'normal') form.value.hazard_level = 'none'
  loading.value = true
  try {
    await createInspection(form.value)
    ElMessage.success('巡检记录已提交')
    router.push('/inspections')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  permits.value = await getPermits({ status: 'in_use' })
})
</script>

<style scoped>
.page-bar { margin-bottom: 16px; }
</style>
