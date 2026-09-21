<script setup lang="ts">
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

const props = withDefaults(
  defineProps<{
    /** Markdown 原文 */
    source?: string
    /** 紧凑模式：用于聊天气泡等窄容器 */
    compact?: boolean
  }>(),
  { source: '', compact: false },
)

/** 渲染结果已由 renderMarkdown 做 HTML 转义，可安全绑定 */
const html = computed(() => renderMarkdown(props.source || ''))
</script>

<template>
  <div class="md" :class="{ 'md--compact': compact }" v-html="html" />
</template>

<style scoped>
/* 容器：Markdown 自己管理块级间距，故不再使用 pre-wrap */
.md {
  font-size: 14px;
  line-height: 1.75;
  color: var(--text);
  word-break: break-word;
  overflow-wrap: anywhere;
}
.md--compact {
  font-size: 13.5px;
  line-height: 1.7;
}

/* ---------- 标题：靠字号 + 字重 + 分隔线建立层次 ---------- */
.md :deep(.md-heading) {
  font-weight: 700;
  line-height: 1.4;
  color: #111827;
}
.md :deep(.md-h1) {
  font-size: 1.35em;
  margin: 18px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.md :deep(.md-h2) {
  font-size: 1.18em;
  margin: 16px 0 8px;
  padding-left: 9px;
  border-left: 3px solid var(--brand);
}
.md :deep(.md-h3) {
  font-size: 1.06em;
  margin: 14px 0 6px;
  color: var(--brand-dark);
}
.md :deep(.md-h4),
.md :deep(.md-h5),
.md :deep(.md-h6) {
  font-size: 1em;
  margin: 12px 0 6px;
  color: var(--muted);
}

/* 首个元素不留上边距，避免气泡顶部空一块 */
.md :deep(> :first-child) {
  margin-top: 0;
}
.md :deep(> :last-child) {
  margin-bottom: 0;
}

/* ---------- 段落 ---------- */
.md :deep(.md-p) {
  margin: 0 0 10px;
}

/* ---------- 列表 ---------- */
.md :deep(.md-list) {
  margin: 6px 0 10px;
  padding-left: 22px;
}
.md :deep(.md-list .md-list) {
  margin: 4px 0 2px;
}
.md :deep(.md-list > li) {
  margin: 3px 0;
  padding-left: 2px;
}
.md :deep(.md-list > li)::marker {
  color: var(--brand);
  font-weight: 600;
}
.md :deep(.md-list > li > .md-list > li) {
  color: var(--muted);
}
.md :deep(.md-task) {
  margin-right: 6px;
  color: var(--brand);
}

/* ---------- 强调 ---------- */
.md :deep(strong) {
  font-weight: 700;
  color: var(--brand-dark);
}
.md :deep(em) {
  font-style: italic;
  color: var(--muted);
}
.md :deep(del) {
  color: var(--muted);
}

/* ---------- 代码 ---------- */
.md :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.9em;
  background: #eef2ff;
  color: #3730a3;
  padding: 1px 5px;
  border-radius: 4px;
}
.md :deep(.md-pre) {
  margin: 8px 0 10px;
  padding: 10px 12px;
  background: #f6f8fa;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow-x: auto;
  line-height: 1.6;
}
.md :deep(.md-pre code) {
  display: block;
  background: none;
  color: inherit;
  padding: 0;
  font-size: 12.5px;
  white-space: pre;
}

/* ---------- 引用 ---------- */
.md :deep(.md-quote) {
  margin: 8px 0 10px;
  padding: 6px 12px;
  border-left: 3px solid var(--brand);
  background: #f3f6ff;
  border-radius: 0 6px 6px 0;
  color: var(--muted);
}
.md :deep(.md-quote .md-p) {
  margin: 4px 0;
}

/* ---------- 分隔线 ---------- */
.md :deep(.md-hr) {
  margin: 14px 0;
  border: 0;
  border-top: 1px dashed var(--border);
}

/* ---------- 表格 ---------- */
.md :deep(.md-table-wrap) {
  margin: 8px 0 12px;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
}
.md :deep(.md-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95em;
}
.md :deep(.md-table th) {
  background: #f6f8fa;
  font-weight: 600;
  white-space: nowrap;
  text-align: left;
}
.md :deep(.md-table th),
.md :deep(.md-table td) {
  padding: 6px 10px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
}
.md :deep(.md-table tr:last-child td) {
  border-bottom: 0;
}
.md :deep(.md-table th:last-child),
.md :deep(.md-table td:last-child) {
  border-right: 0;
}
.md :deep(.md-table tbody tr:nth-child(even)) {
  background: #fafbfc;
}

/* ---------- 链接 ---------- */
.md :deep(a) {
  color: var(--brand);
  text-decoration: none;
  border-bottom: 1px solid rgba(47, 111, 237, 0.35);
}
.md :deep(a:hover) {
  color: var(--brand-dark);
  border-bottom-color: var(--brand-dark);
}
</style>
