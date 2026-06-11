<template>
  <div>
    <div class="page-bar">
      <el-page-header @back="$router.push('/permits')" content="新建许可申请" />
    </div>
    <el-card>
      <el-form :model="form" label-width="110px" style="max-width:600px">
        <el-form-item label="建筑点位" required>
          <el-select v-model="form.building_id" placeholder="选择建筑" style="width:100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name + ' - ' + b.address" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="搭设范围" required>
          <el-input v-model="form.scaffold_scope" type="textarea" :rows="3" placeholder="描述搭设范围、高度、面积等" />
        </el-form-item>
        <el-form-item label="开始日期" required>
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" placeholder="选择开始日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择结束日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="方案附件地址">
          <el-input v-model="form.plan_attachment" placeholder="搭设方案PDF/文档链接地址" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">提交申请</el-button>
          <el-button @click="$router.push('/permits')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createPermit, getBuildings } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const buildings = ref([])
const form = ref({ building_id: '', scaffold_scope: '', start_date: '', end_date: '', plan_attachment: '' })

const handleSubmit = async () => {
  if (!form.value.building_id || !form.value.scaffold_scope || !form.value.start_date || !form.value.end_date) {
    ElMessage.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    await createPermit(form.value)
    ElMessage.success('许可申请已提交')
    router.push('/permits')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  buildings.value = await getBuildings()
})
</script>

<style scoped>
.page-bar { margin-bottom: 16px; }
</style>
