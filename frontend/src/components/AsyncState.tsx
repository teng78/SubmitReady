import type { ReactNode } from 'react'

export function Loading({ label = '正在加载…' }: { label?: string }) { return <div className="state-card" role="status"><span className="spinner" aria-hidden="true" /><p>{label}</p></div> }
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) { return <div className="state-card state-card--error" role="alert"><strong>暂时无法完成操作</strong><p>{message}</p>{retry && <button className="button button--secondary" onClick={retry}>重试</button>}</div> }
export function EmptyState({ title, children }: { title: string; children?: ReactNode }) { return <div className="state-card"><span className="empty-mark" aria-hidden="true">○</span><strong>{title}</strong>{children}</div> }
