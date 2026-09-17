// 通用格式化与枚举映射（前端展示用）

export function formatDate(d: string | null | undefined): string {
  if (!d) return '未定'
  return String(d).slice(0, 10)
}

export function formatRange(
  s: string | null | undefined,
  e: string | null | undefined,
): string {
  return `${formatDate(s)} ~ ${formatDate(e)}`
}

export function yuan(n: number | null | undefined): string {
  if (n == null) return '—'
  return `¥${Number(n).toLocaleString('zh-CN')}`
}

export function statusLabel(s: string): string {
  const map: Record<string, string> = {
    planning: '规划中',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[s] || s || '规划中'
}

export function statusTagType(s: string): 'info' | 'success' | 'warning' | 'danger' | 'primary' {
  const map: Record<string, 'info' | 'success' | 'warning' | 'danger' | 'primary'> = {
    planning: 'info',
    confirmed: 'success',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[s] || 'info'
}

export const TRAVEL_STYLES: { value: string; label: string }[] = [
  { value: 'relaxed', label: '休闲度假' },
  { value: 'adventurous', label: '探险挑战' },
  { value: 'cultural', label: '文化探索' },
  { value: 'family', label: '亲子游' },
  { value: 'romantic', label: '浪漫情侣' },
  { value: 'business', label: '商务出行' },
  { value: 'foodie', label: '美食之旅' },
  { value: 'photography', label: '摄影采风' },
]

export function styleLabel(s: string): string {
  const found = TRAVEL_STYLES.find((x) => x.value === s)
  return found ? found.label : s || '休闲度假'
}

// 把 el-date-picker 的 Date 对象格式化为 YYYY-MM-DD
export function toDateStr(d: Date | string | null | undefined): string | undefined {
  if (!d) return undefined
  if (typeof d === 'string') return d.slice(0, 10)
  const y = d.getFullYear()
  const m = `${d.getMonth() + 1}`.padStart(2, '0')
  const day = `${d.getDate()}`.padStart(2, '0')
  return `${y}-${m}-${day}`
}
