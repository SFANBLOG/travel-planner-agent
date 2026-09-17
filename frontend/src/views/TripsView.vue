<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listTrips, deleteTrip } from '@/api/trip'
import type { TripListItem } from '@/api/trip'
import { formatRange, yuan, statusLabel, statusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Promotion, Delete, View } from '@element-plus/icons-vue'

const router = useRouter()
const trips = ref<TripListItem[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await listTrips()
    trips.value = data
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function onDelete(t: TripListItem) {
  try {
    await ElMessageBox.confirm(`确定删除行程「${t.title}」吗？此操作不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteTrip(t.id)
    ElMessage.success('已删除')
    await load()
  } catch {
    /* 拦截器已提示 */
  }
}

onMounted(load)
</script>

<template>
  <div class="trips">
    <div class="trips-head">
      <div>
        <h1 class="page-title">我的行程</h1>
        <p class="page-sub">查看、管理你用 TravelAI 生成的全部行程。</p>
      </div>
      <el-button type="primary" :icon="Promotion" @click="router.push('/create')">
        新建行程
      </el-button>
    </div>

    <div v-loading="loading" class="trip-grid">
      <el-empty v-if="!loading && !trips.length" description="还没有行程，去生成第一个吧">
        <el-button type="primary" @click="router.push('/create')">生成行程</el-button>
      </el-empty>

      <div v-for="t in trips" :key="t.id" class="trip-card card">
        <div class="trip-card-head">
          <span class="trip-title">{{ t.title }}</span>
          <el-tag :type="statusTagType(t.status)" size="small" effect="light">
            {{ statusLabel(t.status) }}
          </el-tag>
        </div>
        <div class="trip-meta muted">
          <span>📍 {{ t.destination }}</span>
          <span>🗓️ {{ formatRange(t.start_date, t.end_date) }}</span>
          <span>💰 {{ yuan(t.budget) }}</span>
        </div>
        <div class="trip-actions">
          <el-button :icon="View" @click="router.push(`/trips/${t.id}`)">查看</el-button>
          <el-button type="danger" plain :icon="Delete" @click="onDelete(t)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trips-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 16px;
}
.trip-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  min-height: 120px;
}
.trip-card {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.trip-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.trip-title {
  font-weight: 700;
  font-size: 16px;
}
.trip-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}
.trip-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}
@media (max-width: 1000px) {
  .trip-grid {
    grid-template-columns: 1fr;
  }
}
</style>
