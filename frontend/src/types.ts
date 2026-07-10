export type RunStatus = 'PASS' | 'WARN' | 'FAIL' | 'SKIP' | 'PENDING' | 'RUNNING' | string
export interface RuleSummary { id: string; name: string; language: string; schema_version?: number; version?: number; revision?: string; builtin?: boolean }
export interface RunSummary { id: string; project_name: string; rule_name?: string; rule?: { name: string }; status: RunStatus; stage: string; started_at: string; duration_ms?: number }
export interface CheckItem { id: string; label: string; category: string; status: RunStatus; message: string; suggestion?: string; details?: string }
export interface CommandResult { command?: string[]; exit_code?: number | null; return_code?: number | null; duration_ms?: number; timed_out?: boolean; stdout?: string; stderr?: string }
export interface Report extends RunSummary { finished_at?: string; rule: { id: string; name: string; version?: number; schema_version?: number }; checks: CheckItem[]; build?: CommandResult | null; test?: CommandResult | null; security_warnings?: string[]; environment?: Record<string, unknown>; explanation?: string }
export interface ApiErrorBody { error?: { code?: string; message?: string; details?: unknown; request_id?: string }; detail?: string | Array<{ msg?: string }> }
