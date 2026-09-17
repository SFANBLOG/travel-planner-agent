<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTrip, deleteTrip, updateTripStatus, chat } from '@/api/trip'
import type { Trip } from '@/api/trip'
import { formatRange, yuan, statusLabel, statusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Promotion, Delete, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const trip = ref<Trip | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await getTrip(id)
    trip.value = data
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function changeStatus(status: string) {
  try {
    const { data } = await updateTripStatus(id, status)
    trip.value = data
    ElMessage.success(`已更新为「${statusLabel(status)}」`)
  } catch {
    /* 拦截器已提示 */
  }
}

async function onDelete() {
  try {
    await ElMessageBox.confirm('确定删除该行程吗？', '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteTrip(id)
    ElMessage.success('已删除')
    router.push('/trips')
  } catch {
    /* 拦截器已提示 */
  }
}

const budget = computed(() => {
  const bb = trip.value?.generated_plan?.budget_breakdown
  if (!bb) return null
  return bb as Record<string, number | boolean>
})

const rawPlan = computed(() => {
  const c = trip.value?.generated_plan?.content
  return typeof c === 'string' ? c : ''
})

// ---- AI 助手 ----
interface ChatMsg {
  role: 'user' | 'ai'
  text: string
}
const messages = ref<ChatMsg[]>([])
const draft = ref('')
const chatting = ref(false)
const chatBox = ref<HTMLElement | null>(null)

async function sendChat() {
  const text = draft.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  draft.value = ''
  chatting.value = true
  await nextTick()
  scrollChat()
  try {
    const { data } = await chat(text)
    messages.value.push({ role: 'ai', text: data.response || '（暂无回复）' })
  } catch {
    messages.value.push({ role: 'ai', text: '（请求失败，请稍后重试）' })
  } finally {
    chatting.value = false
    await nextTick()
    scrollChat()
  }
}
function scrollChat() {
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}

onMounted(load)
</script>

<template>
  <div class="detail" v-loading="loading">
    <template v-if="trip">
      <!-- 概览 -->
      <div class="head-row">
        <div>
          <h1 class="page-title">{{ trip.title }}</h1>
          <p class="page-sub">
            📍 {{ trip.destination }} ｜ 🗓️ {{ formatRange(trip.start_date, trip.end_date) }}
            ｜ 💰 预算 {{ yuan(trip.budget) }}
          </p>
        </div>
        <div class="head-actions">
          <el-tag :type="statusTagType(trip.status)" effect="dark">
            {{ statusLabel(trip.status) }}
          </el-tag>
        </div>
      </div>

      <!-- 状态操作 -->
      <div class="status-bar card">
        <span class="muted">行程管理：</span>
        <el-button size="small" :disabled="trip.status === 'confirmed'" @click="changeStatus('confirmed')">
          确认行程
        </el-button>
        <el-button size="small" type="success" :disabled="trip.status === 'completed'" @click="changeStatus('completed')">
          标记完成
        </el-button>
        <el-button size="small" type="warning" :disabled="trip.status === 'cancelled'" @click="changeStatus('cancelled')">
          取消
        </el-button>
        <el-button size="small" type="danger" plain :icon="Delete" @click="onDelete">删除</el-button>
      </div>

      <div class="layout">
        <!-- 行程主体 -->
        <div class="main-col">
          <div v-for="day in trip.days" :key="day.id" class="day card">
            <div class="day-head">
              <span class="day-no">第 {{ day.day_number }} 天</span>
              <span class="day-date muted">{{ day.date }}</span>
              <el-tag v-if="day.theme" size="small" effect="plain">{{ day.theme }}</el-tag>
            </div>
            <p v-if="day.summary" class="day-summary muted">{{ day.summary }}</p>

            <div v-if="day.spots.length" class="spots">
              <div v-for="sp in day.spots" :key="sp.id" class="spot">
                <div class="spot-time">
                  <div class="time-dot" />
                  <span class="time-text">
                    {{ sp.start_time || '—' }}<template v-if="sp.end_time"> - {{ sp.end_time }}</template>
                  </span>
                </div>
                <div class="spot-body">
                  <div class="spot-name">{{ sp.name || sp.notes || '行程点' }}</div>
                  <div v-if="sp.transport_to_next" class="spot-transport muted">
                    🚦 前往下一站：{{ sp.transport_to_next }}
                  </div>
                  <div v-if="sp.notes && sp.notes !== sp.name" class="spot-note muted">
                    {{ sp.notes }}
                  </div>
                  <div class="spot-cost">
                    <el-tag v-if="sp.estimated_cost" size="small" type="info" effect="light">
                      预计花费 {{ yuan(sp.estimated_cost) }}
                    </el-tag>
                    <span v-else class="muted">免费</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="当日暂无具体景点安排（通用模板）" :image-size="60" />
          </div>

          <!-- 预算 -->
          <div v-if="budget" class="budget card">
            <h3 class="budget-title">💰 预算估算</h3>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="门票">{{ yuan(budget.ticket as number) }}</el-descriptions-item>
              <el-descriptions-item label="餐饮">{{ yuan(budget.food as number) }}</el-descriptions-item>
              <el-descriptions-item label="住宿">{{ yuan(budget.hotel as number) }}</el-descriptions-item>
              <el-descriptions-item label="市内交通">{{ yuan(budget.transport as number) }}</el-descriptions-item>
              <el-descriptions-item label="合计">
                <strong>{{ yuan(budget.total as number) }}</strong>
              </el-descriptions-item>
              <el-descriptions-item label="人均">{{ yuan(budget.per_person as number) }}</el-descriptions-item>
            </el-descriptions>
            <p
              v-if="budget.user_budget != null && budget.user_budget !== ''"
              class="budget-flag"
              :class="budget.within_budget ? 'ok' : 'over'"
            >
              {{
                budget.within_budget
                  ? `✅ 在预算（${yuan(budget.user_budget as number)}）内`
                  : `⚠️ 超出预算（${yuan(budget.user_budget as number)}），建议压缩住宿或景点`
              }}
            </p>
          </div>

          <!-- 原始行程文本 -->
          <el-collapse v-if="rawPlan" class="raw-collapse">
            <el-collapse-item title="查看完整行程文本（Markdown）">
              <pre class="raw-plan">{{ rawPlan }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- AI 助手 -->
        <div class="aside card">
          <h3 class="aside-title">💬 调整这个行程</h3>
          <p class="page-sub">把想法告诉 AI 助手，例如「第二天多加一个博物馆」「预算压到 2000」。</p>
          <div ref="chatBox" class="chat-box">
            <div v-if="!messages.length" class="chat-empty muted">
              向助手描述你的修改需求，它会给出建议（修改本身在左侧操作）。
            </div>
            <div v-for="(m, i) in messages" :key="i" class="bubble" :class="m.role">
              {{ m.text }}
            </div>
            <div v-if="chatting" class="bubble ai typing">
              <el-icon class="is-loading"><Loading /></el-icon> 思考中…
            </div>
          </div>
          <div class="chat-input">
            <el-input v-model="draft" placeholder="描述修改需求…" @keyup.enter="sendChat" />
            <el-button type="primary" :icon="Promotion" :disabled="chatting" @click="sendChat">发送</el-button>
          </div>
        </div>
      </div>
    </template>

    <el-empty v-else-if="!loading" description="行程不存在或已被删除">
      <el-button type="primary" @click="router.push('/trips')">返回我的行程</el-button>
    </el-empty>
  </div>
</template>

<style scoped>
.head-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  margin: 16px 0;
  flex-wrap: wrap;
}
.layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  align-items: start;
}
.day {
  padding: 18px;
  margin-bottom: 16px;
}
.day-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.day-no {
  font-weight: 800;
  font-size: 16px;
}
.day-summary {
  font-size: 13px;
  margin: 0 0 12px;
}
.spots {
  border-left: 2px solid var(--border);
  margin-left: 6px;
  padding-left: 14px;
}
.spot {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed var(--border);
}
.spot:last-child {
  border-bottom: none;
}
.spot-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 56px;
}
.time-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--brand);
  margin-top: 4px;
}
.time-text {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
  white-space: nowrap;
}
.spot-body {
  flex: 1;
}
.spot-name {
  font-weight: 600;
  font-size: 15px;
}
.spot-transport,
.spot-note {
  font-size: 13px;
  margin-top: 4px;
  line-height: 1.6;
}
.spot-cost {
  margin-top: 6px;
}
.budget {
  padding: 18px;
  margin-bottom: 16px;
}
.budget-title {
  margin: 0 0 12px;
}
.budget-flag {
  margin: 12px 0 0;
  font-size: 14px;
}
.budget-flag.ok {
  color: #16a34a;
}
.budget-flag.over {
  color: #dc2626;
}
.raw-collapse {
  margin-bottom: 16px;
}
.raw-plan {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.6;
  background: var(--bg);
  border-radius: 8px;
  padding: 12px;
  margin: 0;
}
.aside {
  padding: 18px;
  position: sticky;
  top: 80px;
}
.aside-title {
  margin: 0 0 4px;
}
.chat-box {
  min-height: 240px;
  max-height: 360px;
  overflow-y: auto;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  margin: 8px 0 12px;
}
.chat-empty {
  font-size: 13px;
  line-height: 1.7;
}
.bubble {
  margin-bottom: 10px;
  max-width: 90%;
  padding: 9px 11px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.bubble.user {
  margin-left: auto;
  background: var(--brand);
  color: #fff;
}
.bubble.ai {
  background: #fff;
  border: 1px solid var(--border);
}
.bubble.typing {
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.chat-input {
  display: flex;
  gap: 8px;
}
@media (max-width: 1000px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .aside {
    position: static;
  }
}
</style>
