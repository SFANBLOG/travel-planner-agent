<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { generateTrip, chat } from '@/api/trip'
import { TRAVEL_STYLES, toDateStr } from '@/utils/format'
import { ElMessage } from 'element-plus'
import { Loading, Promotion } from '@element-plus/icons-vue'

const router = useRouter()
const store = useUserStore()

const generating = ref(false)

const form = reactive({
  user_message: '',
  destination: '',
  dateRange: [] as (Date | string)[],
  budget: undefined as number | undefined,
  travelers: 1,
  travel_style: 'relaxed',
})

const example =
  '我想去杭州玩 3 天，预算 3000 元，两个人，亲子游，多安排一些自然风光和美食。'

async function onSubmit() {
  if (!form.user_message.trim() && !form.destination.trim()) {
    ElMessage.warning('请填写自然语言需求或目的地')
    return
  }
  generating.value = true
  try {
    const { data } = await generateTrip({
      user_message: form.user_message.trim() || form.destination.trim(),
      destination: form.destination.trim() || undefined,
      start_date: toDateStr(form.dateRange[0]),
      end_date: toDateStr(form.dateRange[1]),
      budget: form.budget,
      travelers: form.travelers,
      travel_style: form.travel_style,
    })
    ElMessage.success('行程已生成')
    router.push(`/trips/${data.id}`)
  } catch {
    /* 拦截器已提示 */
  } finally {
    generating.value = false
  }
}

// ---- AI 助手（对话式预规划）----
interface ChatMsg {
  role: 'user' | 'ai'
  text: string
  actions?: string[]
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
    messages.value.push({
      role: 'ai',
      text: data.response || '（暂无回复）',
      actions: data.suggested_actions || [],
    })
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

function useSuggestion(s: string) {
  draft.value = s
}
</script>

<template>
  <div class="create">
    <h1 class="page-title">生成我的行程</h1>
    <p class="page-sub">
      用一句话描述你的旅行想法，TravelAI 会解析需求、检索景点、估算预算并生成每日路线。
    </p>

    <div class="layout">
      <!-- 表单 -->
      <div class="form-col card">
        <el-form label-position="top">
          <el-form-item label="自然语言需求">
            <el-input
              v-model="form.user_message"
              type="textarea"
              :rows="4"
              :placeholder="example"
            />
          </el-form-item>

          <div class="grid-2">
            <el-form-item label="目的地（可选）">
              <el-input v-model="form.destination" placeholder="如：杭州" clearable />
            </el-form-item>
            <el-form-item label="出行日期（可选）">
              <el-date-picker
                v-model="form.dateRange"
                type="daterange"
                range-separator="~"
                start-placeholder="开始"
                end-placeholder="结束"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </div>

          <div class="grid-2">
            <el-form-item label="预算（元，可选）">
              <el-input-number v-model="form.budget" :min="0" :step="500" controls-position="right" style="width: 100%" />
            </el-form-item>
            <el-form-item label="出行人数">
              <el-input-number v-model="form.travelers" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </div>

          <el-form-item label="旅行风格">
            <el-select v-model="form.travel_style" style="width: 100%">
              <el-option
                v-for="s in TRAVEL_STYLES"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="full"
            :loading="generating"
            :icon="Promotion"
            @click="onSubmit"
          >
            {{ generating ? '规划中…' : '一键生成行程' }}
          </el-button>
        </el-form>
      </div>

      <!-- AI 助手 -->
      <div class="chat-col card">
        <h3 class="chat-title">💬 先和 AI 助手聊聊</h3>
        <p class="page-sub">不确定怎么描述？先用对话梳理想法，再把结论填到左侧表单。</p>
        <div ref="chatBox" class="chat-box">
          <div v-if="!messages.length" class="chat-empty muted">
            例如：「带孩子去成都三天怎么安排？」「杭州美食之旅预算多少合适？」
          </div>
          <div
            v-for="(m, i) in messages"
            :key="i"
            class="bubble"
            :class="m.role"
          >
            <div class="bubble-text">{{ m.text }}</div>
            <div v-if="m.actions && m.actions.length" class="bubble-actions">
              <el-tag
                v-for="a in m.actions"
                :key="a"
                size="small"
                type="info"
                effect="plain"
                class="action-tag"
                @click="useSuggestion(a)"
              >
                {{ a }}
              </el-tag>
            </div>
          </div>
          <div v-if="chatting" class="bubble ai typing">
            <el-icon class="is-loading"><Loading /></el-icon> 思考中…
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="draft"
            placeholder="向 AI 助手提问…"
            @keyup.enter="sendChat"
          />
          <el-button type="primary" :icon="Promotion" :disabled="chatting" @click="sendChat">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  align-items: start;
}
.form-col {
  padding: 24px;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.full {
  width: 100%;
}
.chat-col {
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.chat-title {
  margin: 0 0 4px;
  font-size: 16px;
}
.chat-box {
  flex: 1;
  min-height: 280px;
  max-height: 420px;
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
  margin-bottom: 12px;
  max-width: 88%;
  padding: 10px 12px;
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
.bubble-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.action-tag {
  cursor: pointer;
}
.chat-input {
  display: flex;
  gap: 8px;
}
@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
