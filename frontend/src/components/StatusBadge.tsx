import type { RunStatus } from '../types'

const labels: Record<string, string> = { PASS: '通过', WARN: '警告', FAIL: '失败', SKIP: '跳过', PENDING: '等待中', RUNNING: '检查中', completed: '已完成' }
export default function StatusBadge({ status }: { status: RunStatus }) { const key = status.toUpperCase(); return <span className={`status status--${key.toLowerCase()}`}>{labels[key] ?? status}</span> }
