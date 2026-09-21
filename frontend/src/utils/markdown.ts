/**
 * 轻量 Markdown 渲染器（零依赖，纯函数）
 *
 * 设计要点
 * - **先转义、后转换**：原文先做 HTML 实体转义，再做 Markdown 规则替换，
 *   因此模型输出中的任何标签都无法注入 → 天然免疫 XSS，无需额外 sanitizer。
 * - 链接协议白名单（http/https/mailto/tel/相对路径/锚点），阻断 `javascript:`、`data:`。
 * - 覆盖 LLM 常见输出：标题、粗体、斜体、删除线、行内代码、围栏代码块、链接、
 *   有序/无序列表（按缩进嵌套）、任务列表、引用、分隔线、表格（含对齐）。
 * - 输出统一带 `md-*` 类名，排版样式由 `components/MarkdownView.vue` 提供。
 */

const HTML_ESCAPE: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}

function escapeHtml(input: string): string {
  return input.replace(/[&<>"']/g, (ch) => HTML_ESCAPE[ch])
}

/** 仅放行安全协议，其余一律置为 `#`，防止 javascript:/data: 注入 */
function safeUrl(raw: string): string {
  const url = raw.trim()
  return /^(https?:\/\/|mailto:|tel:|\/|#)/i.test(url) ? url : '#'
}

/** 行内语法：代码 / 链接 / 粗体 / 斜体 / 删除线 */
function renderInline(text: string): string {
  let out = escapeHtml(text)

  // 先抽出「行内代码」与「链接」为占位符：它们生成的 HTML 含 `_`、`*` 等字符
  // （如 target="_blank"），若留在文本里会被后续强调规则二次改写。
  const stash: string[] = []
  const keep = (html: string): string => {
    stash.push(html)
    return `\u0001${stash.length - 1}\u0001`
  }

  // 行内代码
  out = out.replace(/`([^`]+)`/g, (_m, code: string) => keep(`<code>${code}</code>`))

  // 链接 [文本](地址)
  out = out.replace(/\[([^\]\n]+)\]\(([^)\s]+)\)/g, (_m, label: string, url: string) =>
    keep(`<a href="${safeUrl(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`),
  )

  // 粗体 → 删除线 → 斜体（顺序不可换，否则 ** 会被 * 规则先吃掉）
  out = out.replace(/\*\*([^\n]+?)\*\*/g, '<strong>$1</strong>')
  out = out.replace(/__([^\n]+?)__/g, '<strong>$1</strong>')
  out = out.replace(/~~([^\n]+?)~~/g, '<del>$1</del>')
  out = out.replace(/(^|[^*\w])\*([^*\n]+?)\*/g, '$1<em>$2</em>')
  out = out.replace(/(^|[^_\w])_([^_\n]+?)_/g, '$1<em>$2</em>')

  // 还原占位符
  return out.replace(/\u0001(\d+)\u0001/g, (_m, idx: string) => stash[Number(idx)])
}

// ---------------------------------------------------------------- 列表

interface ListItem {
  indent: number
  ordered: boolean
  content: string
}

interface ListNode {
  ordered: boolean
  items: { content: string; children: ListNode | null }[]
}

/** `- [x] 内容` → 带勾选框的条目 */
function renderListItemContent(content: string): string {
  const task = content.match(/^\[([ xX])\]\s+(.*)$/)
  if (task) {
    const checked = task[1].toLowerCase() === 'x'
    return `<span class="md-task">${checked ? '☑' : '☐'}</span>${renderInline(task[2])}`
  }
  return renderInline(content)
}

function serializeList(node: ListNode): string {
  const tag = node.ordered ? 'ol' : 'ul'
  const items = node.items
    .map((item) => {
      const nested = item.children ? serializeList(item.children) : ''
      return `<li>${renderListItemContent(item.content)}${nested}</li>`
    })
    .join('')
  return `<${tag} class="md-list">${items}</${tag}>`
}

/**
 * 解析连续列表行 → 按缩进建树 → 输出嵌套 <ul>/<ol>。
 * 用缩进栈而非固定 2/4 空格阶数，兼容模型输出的不同缩进习惯。
 */
function renderList(lines: string[], start: number): { html: string; next: number } {
  const items: ListItem[] = []
  let i = start

  while (i < lines.length) {
    const line = lines[i]
    if (!line.trim()) {
      // 列表项之间的单个空行不结束列表，但空行后必须是列表项
      const nextLine = lines[i + 1]
      if (nextLine && /^\s*([-*+]|\d+[.)])\s+/.test(nextLine)) {
        i++
        continue
      }
      break
    }
    const matched = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/)
    if (!matched) break
    items.push({
      indent: matched[1].replace(/\t/g, '  ').length,
      ordered: /^\d/.test(matched[2]),
      content: matched[3],
    })
    i++
  }

  if (!items.length) return { html: '', next: i }

  const root: ListNode = { ordered: items[0].ordered, items: [] }
  // 基准缩进取列表首项：否则同级（如全为 0 缩进）的后续项会被误判为比根更深而嵌套。
  const stack: { indent: number; node: ListNode }[] = [{ indent: items[0].indent, node: root }]

  for (const item of items) {
    while (stack.length > 1 && item.indent < stack[stack.length - 1].indent) stack.pop()
    const top = stack[stack.length - 1]
    // 缩进更深 → 作为上一项的子列表
    if (item.indent > top.indent && top.node.items.length > 0) {
      const child: ListNode = { ordered: item.ordered, items: [] }
      top.node.items[top.node.items.length - 1].children = child
      stack.push({ indent: item.indent, node: child })
    }
    stack[stack.length - 1].node.items.push({ content: item.content, children: null })
  }

  return { html: serializeList(root), next: i }
}

// ---------------------------------------------------------------- 表格

function splitTableRow(line: string): string[] {
  let row = line.trim()
  if (row.startsWith('|')) row = row.slice(1)
  if (row.endsWith('|')) row = row.slice(0, -1)
  return row.split('|').map((cell) => cell.trim())
}

/** 分隔行：只含 `-`、`:`、`|` 与空白，且至少一个 `-` */
function isTableSeparator(line: string): boolean {
  const text = line.trim()
  if (!text || !text.includes('-')) return false
  return /^[|\-:\s]+$/.test(text)
}

function isTableStart(lines: string[], i: number): boolean {
  const head = lines[i]
  const sep = lines[i + 1]
  if (!head || !sep) return false
  return head.includes('|') && isTableSeparator(sep)
}

function parseAligns(separator: string): (string | null)[] {
  return splitTableRow(separator).map((cell) => {
    const left = cell.startsWith(':')
    const right = cell.endsWith(':')
    if (left && right) return 'center'
    if (right) return 'right'
    if (left) return 'left'
    return null
  })
}

function renderTable(header: string[], aligns: (string | null)[], body: string[][]): string {
  const cell = (tag: 'th' | 'td', text: string, index: number): string => {
    const align = aligns[index]
    const style = align ? ` style="text-align:${align}"` : ''
    return `<${tag}${style}>${renderInline(text)}</${tag}>`
  }
  const head = `<thead><tr>${header.map((h, k) => cell('th', h, k)).join('')}</tr></thead>`
  const rows = body
    .map((row) => `<tr>${header.map((_, k) => cell('td', row[k] ?? '', k)).join('')}</tr>`)
    .join('')
  return `<div class="md-table-wrap"><table class="md-table">${head}<tbody>${rows}</tbody></table></div>`
}

// ---------------------------------------------------------------- 块级

const FENCE_RE = /^\s*(`{3,}|~{3,})\s*([\w+#.-]*)\s*$/
const HEADING_RE = /^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$/
const HR_RE = /^\s{0,3}([-*_])(\s*\1){2,}\s*$/
const QUOTE_RE = /^\s{0,3}>\s?/
const LIST_RE = /^\s*([-*+]|\d+[.)])\s+/

function isBlockStart(lines: string[], i: number): boolean {
  const line = lines[i]
  if (!line || !line.trim()) return false
  return (
    FENCE_RE.test(line) ||
    HEADING_RE.test(line) ||
    HR_RE.test(line) ||
    QUOTE_RE.test(line) ||
    LIST_RE.test(line) ||
    isTableStart(lines, i)
  )
}

/** Markdown 原文 → 安全 HTML 字符串 */
export function renderMarkdown(source: string): string {
  if (!source) return ''

  const lines = source.replace(/\r\n?/g, '\n').split('\n')
  const blocks: string[] = []
  const total = lines.length
  let i = 0

  while (i < total) {
    const line = lines[i]

    // 空行
    if (!line.trim()) {
      i++
      continue
    }

    // 围栏代码块
    const fence = line.match(FENCE_RE)
    if (fence) {
      const mark = fence[1][0]
      const lang = fence[2]
      const closeRe = new RegExp(`^\\s*${mark}{3,}\\s*$`)
      const body: string[] = []
      i++
      while (i < total && !closeRe.test(lines[i])) {
        body.push(lines[i])
        i++
      }
      i++ // 跳过闭合围栏
      const langClass = lang ? ` class="language-${escapeHtml(lang)}"` : ''
      blocks.push(`<pre class="md-pre"><code${langClass}>${escapeHtml(body.join('\n'))}</code></pre>`)
      continue
    }

    // 表格
    if (isTableStart(lines, i)) {
      const header = splitTableRow(line)
      const aligns = parseAligns(lines[i + 1])
      i += 2
      const body: string[][] = []
      while (i < total && lines[i].trim() && lines[i].includes('|')) {
        body.push(splitTableRow(lines[i]))
        i++
      }
      blocks.push(renderTable(header, aligns, body))
      continue
    }

    // 标题
    const heading = line.match(HEADING_RE)
    if (heading) {
      const level = heading[1].length
      blocks.push(
        `<h${level} class="md-heading md-h${level}">${renderInline(heading[2])}</h${level}>`,
      )
      i++
      continue
    }

    // 分隔线
    if (HR_RE.test(line)) {
      blocks.push('<hr class="md-hr">')
      i++
      continue
    }

    // 引用（内部递归解析，支持引用里再放列表/标题）
    if (QUOTE_RE.test(line)) {
      const body: string[] = []
      while (i < total && QUOTE_RE.test(lines[i])) {
        body.push(lines[i].replace(QUOTE_RE, ''))
        i++
      }
      blocks.push(`<blockquote class="md-quote">${renderMarkdown(body.join('\n'))}</blockquote>`)
      continue
    }

    // 列表
    if (LIST_RE.test(line)) {
      const { html, next } = renderList(lines, i)
      blocks.push(html)
      i = next
      continue
    }

    // 段落：连续非空、且未开启新块的行
    const paragraph: string[] = []
    while (i < total) {
      const current = lines[i]
      if (!current.trim()) break
      if (paragraph.length && isBlockStart(lines, i)) break
      paragraph.push(current)
      i++
    }
    blocks.push(`<p class="md-p">${paragraph.map(renderInline).join('<br>')}</p>`)
  }

  return blocks.join('\n')
}

export default renderMarkdown
