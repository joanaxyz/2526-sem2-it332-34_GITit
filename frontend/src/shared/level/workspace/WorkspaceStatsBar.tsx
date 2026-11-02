import { GitBranch } from 'lucide-react'

import type { RepoGraphTrigger, WorkspaceStat } from '@/shared/level/workspace/types'
import { cn } from '@/shared/utils/cn'

/**
 * Full-width run status strip under the command bar. Callers keep the
 * command budget and star target anchors (`command-budget`, `star-budget`)
 * on their values so the first-run tour can find them.
 */
export function WorkspaceStatsBar({ stats, repoGraph, compactLabels = [] }: { stats: WorkspaceStat[]; repoGraph?: RepoGraphTrigger; compactLabels?: readonly string[] }) {
  return (
    <div className={cn('tier-stats-bar', compactLabels.length > 0 && 'tier-stats-bar--compact')} role="group" aria-label="Level status">
      <dl className="tier-stats">
        {stats.map((stat) => (
          <div className="tier-stat" key={stat.label}>
            <dt className={compactLabels.includes(stat.label) ? 'sr-only' : undefined}>
              <stat.icon aria-hidden="true" className={cn('tier-stat-icon', stat.iconClass)} />
              {stat.label}
            </dt>
            <dd>{stat.value}</dd>
          </div>
        ))}
      </dl>
      {repoGraph ? (
        <button
          ref={repoGraph.buttonRef}
          type="button"
          className="tier-repo-graph-button"
          aria-haspopup="dialog"
          aria-expanded={repoGraph.open}
          aria-controls={repoGraph.controls}
          data-tour-target="live-dag"
          onClick={repoGraph.onOpen}
        >
          <GitBranch aria-hidden="true" />
          Repo graph
          {repoGraph.hasUpdate ? (
            <>
              <span className="tier-repo-graph-dot" aria-hidden="true" />
              <span className="sr-only">, updated</span>
            </>
          ) : null}
        </button>
      ) : null}
    </div>
  )
}
