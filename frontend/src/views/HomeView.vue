<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Promotion } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { searchSpots } from '@/api/spot'
import type { SpotResult } from '@/api/spot'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()

const features = [
  {
    icon: '🤖',
    title: '多智能体规划',
    desc: 'LangGraph 驱动「需求解析 → 景点检索 → 天气 → 行程生成 → 路线优化」全链路自动编排。',
  },
  {
    icon: '📚',
    title: 'RAG 知识库',
    desc: '内置城市景点与攻略向量库，结合规则引擎，无 LLM Key 也能产出完整行程。',
  },
  {
    icon: '💰',
    title: '预算估算',
    desc: '按景点门票、餐饮、住宿、交通自动测算总花费与人均，提示预算是否超标。',
  },
  {
    icon: '🌤️',
    title: '天气与路线',
    desc: '结合目的地天气与地理位置最近邻排序，给出合理的每日动线与交通建议。',
  },
]

const keyword = ref('')
const city = ref('')
const searching = ref(false)
const results = ref<SpotResult[]>([])
const showSearch = computed(() => !!store.token)

async function onSearch() {
  if (!store.token) {
    router.push('/login')
    return
  }
  if (!keyword.value.trim() && !city.value.trim()) {
    ElMessage.warning('请输入关键词或城市')
    return
  }
  searching.value = true
  try {
    const { data } = await searchSpots({
      q: keyword.value.trim() || undefined,
      city: city.value.trim() || undefined,
      top_k: 12,
    })
    results.value = data
    if (!data.length) ElMessage.info('未检索到相关景点，换个关键词试试')
  } catch {
    /* 错误由拦截器统一提示 */
  } finally {
    searching.value = false
  }
}

function goCreate() {
  router.push(store.token ? '/create' : '/login')
}
</script>

<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <h1 class="hero-title">用 AI 规划一次说走就走的旅行</h1>
      <p class="hero-sub">
        TravelAI 旅行智脑 · 基于 LangGraph 多智能体 + RAG 知识库，
        一句话生成带预算、天气与每日路线的完整行程。
      </p>
      <div class="hero-actions">
        <el-button type="primary" size="large" :icon="Promotion" @click="goCreate">
          开始规划行程
        </el-button>
        <el-button size="large" @click="store.token ? onSearch() : router.push('/login')">
          体验景点检索
        </el-button>
      </div>
    </section>

    <!-- Features -->
    <section class="features">
      <div v-for="f in features" :key="f.title" class="feature card">
        <div class="feature-icon">{{ f.icon }}</div>
        <h3 class="feature-title">{{ f.title }}</h3>
        <p class="feature-desc muted">{{ f.desc }}</p>
      </div>
    </section>

    <!-- Spot search -->
    <section class="search card">
      <h2 class="page-title">探索目的地景点</h2>
      <p class="page-sub">输入城市或关键词，基于知识库为你检索热门打卡地。</p>

      <el-form v-if="showSearch" :inline="true" class="search-form" @submit.prevent="onSearch">
        <el-form-item label="城市">
          <el-input v-model="city" placeholder="如：北京 / 杭州" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="keyword"
            placeholder="如：美食 / 历史古迹 / 亲子"
            clearable
            style="width: 220px"
            @keyup.enter="onSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" :loading="searching" @click="onSearch">
            检索
          </el-button>
        </el-form-item>
      </el-form>

      <el-empty v-else description="登录后即可体验景点智能检索">
        <el-button type="primary" @click="router.push('/login')">去登录</el-button>
      </el-empty>

      <div v-if="results.length" class="spot-grid">
        <div v-for="sp in results" :key="sp.id" class="spot card">
          <div class="spot-head">
            <span class="spot-name">{{ sp.name }}</span>
            <el-tag size="small" effect="plain">{{ sp.category }}</el-tag>
          </div>
          <div class="spot-meta muted">
            <span>📍 {{ sp.city }}</span>
            <span v-if="sp.rating">⭐ {{ sp.rating }}</span>
            <span v-if="sp.ticket_info && sp.ticket_info.price != null">
              ¥{{ sp.ticket_info.price }}
            </span>
          </div>
          <p v-if="sp.description" class="spot-desc muted">{{ sp.description }}</p>
          <div v-if="sp.tags && sp.tags.length" class="spot-tags">
            <el-tag v-for="t in sp.tags" :key="t" size="small" type="info" effect="light">
              {{ t }}
            </el-tag>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 48px 16px 36px;
  background: linear-gradient(135deg, #eef3ff 0%, #f6f9ff 100%);
  border-radius: 16px;
}
.hero-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 12px;
  color: var(--text);
}
.hero-sub {
  max-width: 680px;
  margin: 0 auto 24px;
  color: var(--muted);
  line-height: 1.7;
  font-size: 15px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 28px 0;
}
.feature {
  padding: 20px;
}
.feature-icon {
  font-size: 28px;
}
.feature-title {
  font-size: 16px;
  margin: 10px 0 6px;
}
.feature-desc {
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}
.search {
  padding: 24px;
}
.search-form {
  margin-bottom: 8px;
}
.spot-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-top: 16px;
}
.spot {
  padding: 16px;
}
.spot-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.spot-name {
  font-weight: 700;
  font-size: 15px;
}
.spot-meta {
  display: flex;
  gap: 14px;
  font-size: 13px;
  margin: 8px 0;
}
.spot-desc {
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.spot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
@media (max-width: 900px) {
  .features {
    grid-template-columns: repeat(2, 1fr);
  }
  .spot-grid {
    grid-template-columns: 1fr;
  }
}
</style>
