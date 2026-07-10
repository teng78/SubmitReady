import type { ApiErrorBody, Report, RuleSummary, RunSummary } from './types'

export class ApiError extends Error { constructor(message: string, public status: number, public details?: unknown) { super(message) } }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init)
  if (!response.ok) {
    let body: ApiErrorBody = {}
    try { body = await response.json() as ApiErrorBody } catch { /* non-JSON failure */ }
    const detail = Array.isArray(body.detail) ? body.detail.map((item) => item.msg).filter(Boolean).join('；') : body.detail
    throw new ApiError(body.error?.message || detail || `请求失败（HTTP ${response.status}）`, response.status, body.error?.details)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

function listFrom<T>(value: T[] | { items?: T[]; runs?: T[]; rules?: T[] }): T[] {
  if (Array.isArray(value)) return value
  return value.items ?? value.runs ?? value.rules ?? []
}

export const api = {
  async rules() { return listFrom(await request<RuleSummary[] | { items?: RuleSummary[]; rules?: RuleSummary[] }>('/rules')) },
  importRule(file: File) { const data = new FormData(); data.append('file', file); return request<RuleSummary>('/rules', { method: 'POST', body: data }) },
  createRun(file: File, ruleId: string) { const data = new FormData(); data.append('project', file); data.append('rule_id', ruleId); return request<RunSummary>('/runs', { method: 'POST', body: data }) },
  run(id: string) { return request<RunSummary>(`/runs/${encodeURIComponent(id)}`) },
  report(id: string) { return request<Report>(`/runs/${encodeURIComponent(id)}/report`) },
  async history() { return listFrom(await request<RunSummary[] | { items?: RunSummary[]; runs?: RunSummary[] }>('/runs')) },
  deleteRun(id: string) { return request<void>(`/runs/${encodeURIComponent(id)}`, { method: 'DELETE' }) },
  explain(id: string) { return request<{ explanation?: string; text?: string; provider?: string }>(`/runs/${encodeURIComponent(id)}/explanation`, { method: 'POST' }) },
}
