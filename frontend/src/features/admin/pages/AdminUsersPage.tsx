import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity,
  CheckCircle2,
  ChevronDown,
  Search,
  UserX,
  X,
  XCircle,
} from 'lucide-react'
import { useState } from 'react'

import { adminApi, type KpiRate } from '@/features/admin/api/adminApi'
import { adminErrorMessage } from '@/features/admin/utils/errors'
import { formatDate } from '@/features/admin/utils/format'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

// ─── KPI catalogue ───────────────────────────────────────────────────────────
const KPI_META = {
  scr:  { abbr: 'SCR',  name: 'Scenario Completion Rate',  target: 80, up: true,  pct: true  },
  car:  { abbr: 'CAR',  name: 'Command Accuracy Rate',     target: 70, up: true,  pct: true  },
  hlcr: { abbr: 'HLCR', name: 'Hard-Level Completion Rate',target: 70, up: true,  pct: true  },
  arc:  { abbr: 'ARC',  name: 'Avg Retry Count',           target: 2,  up: false, pct: false },
  rta:  { abbr: 'RTA',  name: 'Retry Transfer Accuracy',   target: 65, up: true,  pct: true  },
} as const

type KpiKey = keyof typeof KPI_META

function fmtKpi(r: KpiRate, pct: boolean) {
  return r.value === null ? '—' : pct ? `${r.value}%` : r.value.toFixed(2)
}

function kpiStatus(r: KpiRate, key: KpiKey): 'met' | 'miss' | 'none' {
  if (r.value === null || r.denominator === 0) return 'none'
  const { target, up } = KPI_META[key]
  return (up ? r.value >= target : r.value <= target) ? 'met' : 'miss'
}

// ─── main page ───────────────────────────────────────────────────────────────
export function AdminUsersPage() {
  const qc = useQueryClient()
  const [query,    setQuery]    = useState('')
  const [search,   setSearch]   = useState('')
  const [selected, setSelected] = useState<number | null>(null)

  const users = useQuery({
    queryKey: queryKeys.adminUsers(search),
    queryFn:  () => adminApi.users(search),
  })

  function selectUser(id: number) {
    setSelected(prev => prev === id ? null : id)
  }

  return (
    <div className="lu-page">

      {/* ── page header ── */}
      <div className="lu-header">
        <div>
          <h1 className="lu-title">Learners</h1>
          <p className="lu-sub">Search accounts · inspect individual KPI performance</p>
        </div>
        {users.data && (
          <span className="lu-count">
            {users.data.results.length} {search ? 'results' : 'total'}
          </span>
        )}
      </div>

      {/* ── search ── */}
      <form
        className="lu-search"
        onSubmit={e => { e.preventDefault(); setSearch(query.trim()) }}
      >
        <div className="lu-search-wrap">
          <Search className="lu-search-icon" aria-hidden="true" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search by username or email…"
            className="lu-search-input"
          />
          {query && (
            <button
              type="button"
              className="lu-search-clear"
              onClick={() => { setQuery(''); setSearch(''); setSelected(null) }}
              aria-label="Clear search"
            >
              <X aria-hidden="true" />
            </button>
          )}
        </div>
        <Button type="submit" variant="outline" size="sm">Search</Button>
      </form>

      {/* ── body: table + drawer ── */}
      <div className={`lu-body ${selected != null ? 'has-drawer' : ''}`}>

        {/* table panel */}
        <div className="lu-table-panel">
          {users.isPending ? (
            <LoadingState label="Loading learners" variant="panel" />
          ) : users.isError ? (
            <ErrorState title="Could not load learners" description="Try again shortly." />
          ) : users.data.results.length === 0 ? (
            <div className="lu-empty">
              <UserX aria-hidden="true" />
              <p>No learners found{search ? ` for "${search}"` : ''}.</p>
            </div>
          ) : (
            <table className="lu-table">
              <thead>
                <tr>
                  <th>Learner</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {users.data.results.map(u => (
                  <tr
                    key={u.id}
                    className={`lu-row ${selected === u.id ? 'is-selected' : ''}`}
                    onClick={() => selectUser(u.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') selectUser(u.id) }}
                    aria-pressed={selected === u.id}
                  >
                    <td>
                      <div className="lu-row-user">
                        <span className="lu-avatar">{u.username[0].toUpperCase()}</span>
                        <div>
                          <p className="lu-row-name">{u.username}</p>
                          <p className="lu-row-email">{u.email}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="lu-row-tags">
                        {u.is_staff  && <span className="lu-tag lu-tag--staff">staff</span>}
                        {!u.is_active && <span className="lu-tag lu-tag--off">disabled</span>}
                        {u.is_active && !u.is_staff && <span className="lu-tag lu-tag--ok">active</span>}
                      </div>
                    </td>
                    <td className="lu-row-date">{formatDate(u.date_joined)}</td>
                    <td className="lu-row-action">
                      <span className="lu-row-cta">{selected === u.id ? 'Close' : 'View KPIs'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* drawer */}
        {selected != null && (
          <aside className="lu-drawer" aria-label="Learner detail">
            <button
              className="lu-drawer-close"
              onClick={() => setSelected(null)}
              aria-label="Close"
            >
              <X aria-hidden="true" />
            </button>
            <LearnerDetail
              userId={selected}
              onChanged={() => qc.invalidateQueries({ queryKey: queryKeys.adminUsers(search) })}
            />
          </aside>
        )}
      </div>
    </div>
  )
}

// ─── learner detail drawer ───────────────────────────────────────────────────
function LearnerDetail({ userId, onChanged }: { userId: number; onChanged: () => void }) {
  const qc = useQueryClient()
  const [coinAmt,  setCoinAmt]  = useState('')
  const [coinNote, setCoinNote] = useState('')
  const [reqId,    setReqId]    = useState<string | null>(null)
  const [actOpen,  setActOpen]  = useState(false)

  const detail = useQuery({
    queryKey: queryKeys.adminUser(userId),
    queryFn:  () => adminApi.user(userId),
  })
  const kpis = useQuery({
    queryKey: queryKeys.adminUserKpis(userId),
    queryFn:  () => adminApi.userKpis(userId),
  })
  const action = useMutation({
    mutationFn: (p: Parameters<typeof adminApi.userAction>[1]) => adminApi.userAction(userId, p),
    onSuccess: (updated, vars) => {
      qc.setQueryData(queryKeys.adminUser(userId), updated)
      if (vars.action === 'grant_coins') { setCoinAmt(''); setCoinNote(''); setReqId(null) }
      onChanged()
    },
  })

  if (detail.isPending) return <LoadingState label="Loading" variant="panel" />
  if (detail.isError || !detail.data)
    return <ErrorState title="Could not load learner" description="Try again." />

  const user = detail.data

  return (
    <div className="ld-wrap">

      {/* identity */}
      <div className="ld-identity">
        <span className="ld-avatar">{user.username[0].toUpperCase()}</span>
        <div>
          <div className="ld-name-row">
            <h2 className="ld-name">{user.username}</h2>
            {user.is_staff   && <span className="lu-tag lu-tag--staff">staff</span>}
            {!user.is_active && <span className="lu-tag lu-tag--off">disabled</span>}
          </div>
          <p className="ld-email">{user.email}</p>
          <p className="ld-meta">Joined {formatDate(user.date_joined)}</p>
        </div>
      </div>

      {/* KPI section */}
      <div className="ld-section">
        <p className="ld-section-label">
          <Activity aria-hidden="true" />
          Learning KPIs
        </p>

        {kpis.isPending && <p className="ld-loading">Loading…</p>}
        {(kpis.isError || (kpis.data && !kpis.data.has_data)) && (
          <p className="ld-no-data">No activity recorded yet.</p>
        )}
        {kpis.data?.has_data && kpis.data.kpis && (
          <KpiPanel kpis={kpis.data.kpis} modules={kpis.data.modules} />
        )}
      </div>

      {/* account actions */}
      <div className="ld-section ld-section--actions">
        <button
          className="ld-actions-toggle"
          onClick={() => setActOpen(v => !v)}
          aria-expanded={actOpen}
        >
          <span className="ld-section-label" style={{ margin: 0 }}>Account actions</span>
          <ChevronDown className={actOpen ? 'ld-chevron-open' : ''} aria-hidden="true" />
        </button>

        {actOpen && (
          <div className="ld-actions-body">
            <div className="ld-field-group">
              <label className="ld-field-label">Adjust coins</label>
              <div className="ld-coin-row">
                <input
                  className="ld-input"
                  value={coinAmt}
                  onChange={e => { setCoinAmt(e.target.value); setReqId(null) }}
                  placeholder="e.g. 500 or −100"
                  inputMode="numeric"
                />
                <input
                  className="ld-input"
                  value={coinNote}
                  onChange={e => { setCoinNote(e.target.value); setReqId(null) }}
                  placeholder="Reason"
                />
                <Button
                  size="sm"
                  variant="outline"
                  disabled={action.isPending || !coinAmt.trim() || !coinNote.trim()}
                  onClick={() => {
                    const amount = Number(coinAmt)
                    if (!Number.isFinite(amount) || amount === 0) return
                    const id = reqId ?? crypto.randomUUID()
                    setReqId(id)
                    action.mutate({ action: 'grant_coins', amount, reason: coinNote.trim(), request_id: id })
                  }}
                >Apply</Button>
              </div>
            </div>

            <div className="ld-btn-row">
              <Button
                size="sm" variant="outline" className="flex-1"
                disabled={action.isPending}
                onClick={() => {
                  if (user.is_staff && !window.confirm(`Revoke admin for "${user.username}"?`)) return
                  action.mutate({ action: 'set_staff', value: !user.is_staff })
                }}
              >
                {user.is_staff ? 'Revoke staff' : 'Make staff'}
              </Button>
              <Button
                size="sm"
                variant={user.is_active ? 'destructive' : 'outline'}
                className="flex-1"
                disabled={action.isPending}
                onClick={() => {
                  if (user.is_active && !window.confirm(`Disable "${user.username}"?`)) return
                  action.mutate({ action: 'set_active', value: !user.is_active })
                }}
              >
                {user.is_active ? 'Disable' : 'Enable'}
              </Button>
            </div>

            {action.isError && (
              <p className="ld-action-err">
                {adminErrorMessage(action.error, 'Action failed.')}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ─── KPI panel inside drawer ─────────────────────────────────────────────────
function KpiPanel({
  kpis,
  modules,
}: {
  kpis: NonNullable<import('@/features/admin/api/adminApi').UserKpisResponse['kpis']>
  modules: import('@/features/admin/api/adminApi').UserKpisResponse['modules']
}) {
  const overallKeys: KpiKey[] = ['scr', 'car', 'hlcr', 'arc', 'rta']
  const moduleKeys: KpiKey[]  = ['scr', 'hlcr', 'arc', 'rta']

  const metCount = overallKeys.filter(k => kpiStatus(kpis[k], k) === 'met').length

  return (
    <div className="kp-wrap">
      {/* met / total */}
      <div className="kp-summary">
        <span className="kp-summary-label">Targets met</span>
        <span className={`kp-summary-val ${metCount === overallKeys.length ? 'kp-val--all' : ''}`}>
          {metCount}/{overallKeys.length}
        </span>
      </div>

      {/* overall grid */}
      <div className="kp-grid">
        {overallKeys.map(key => {
          const m = KPI_META[key]
          const r = kpis[key]
          const s = kpiStatus(r, key)
          return (
            <div key={key} className={`kp-cell kp-cell--${s}`} title={m.name}>
              <span className="kp-cell-abbr">{m.abbr}</span>
              <strong className={`kp-cell-val kp-val--${s}`}>{fmtKpi(r, m.pct)}</strong>
              <span className="kp-cell-target">{m.up ? '≥' : '≤'}{m.target}{m.pct ? '%' : ''}</span>
              <span className={`kp-cell-icon kp-icon--${s}`} aria-hidden="true">
                {s === 'met'  ? <CheckCircle2 /> : s === 'miss' ? <XCircle /> : null}
              </span>
            </div>
          )
        })}
      </div>

      {/* per-module table */}
      {modules.length > 0 && (
        <div className="kp-mod-wrap">
          <p className="kp-mod-label">By module</p>
          <table className="kp-mod-table">
            <thead>
              <tr>
                <th>Mod</th>
                {moduleKeys.map(k => <th key={k}>{KPI_META[k].abbr}</th>)}
              </tr>
            </thead>
            <tbody>
              {modules.map(mod => (
                <tr key={mod.number}>
                  <td className="kp-mod-num">M{mod.number}</td>
                  {moduleKeys.map(key => {
                    const m = KPI_META[key]
                    const r: KpiRate | undefined = key === 'scr' ? mod.scr : key === 'hlcr' ? mod.hlcr : key === 'arc' ? mod.arc : key === 'rta' ? mod.rta : undefined
                    if (!r) return <td key={key} className="kp-mod-cell kp-mod-cell--none">—</td>
                    const s = kpiStatus(r, key)
                    return (
                      <td key={key} className={`kp-mod-cell kp-mod-cell--${s}`}>
                        {fmtKpi(r, m.pct)}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
