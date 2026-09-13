import { ActivityTrendChart } from '@/shared/components/charts/ActivityTrendChart'
import {
  ACTIVITY_WINDOWS,
  type ActivityWindow,
} from '@/features/stats/utils/activityWindow'

import type { HomeProgressModel } from './homeStatsModel'

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

/** Week / Month / Year. The span is a request parameter, so picking one refetches. */
function ActivitySpanPicker({
  activityWindow,
  onSelectActivityWindow,
}: {
  activityWindow: ActivityWindow
  onSelectActivityWindow: (next: ActivityWindow) => void
}) {
  return (
    <div className="home-overview-span" role="group" aria-label="Activity span">
      {ACTIVITY_WINDOWS.map((option) => (
        <button
          aria-pressed={option.id === activityWindow}
          className={option.id === activityWindow ? 'is-active' : ''}
          key={option.id}
          onClick={() => onSelectActivityWindow(option.id)}
          type="button"
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}

/**
 * The trailing window, plotted. It replaced a 7-column heatmap that labelled its
 * columns M-S while the cells were simply the last 14 days in order, so every
 * square sat under the wrong weekday unless the window happened to end on a
 * Sunday. A dated axis cannot drift like that.
 */
function ActivityBand({ activity }: { activity: HomeProgressModel['activity'] }) {
  const { points, peakIndex } = activity
  const peak = peakIndex >= 0 ? points[peakIndex] : undefined

  if (points.length === 0) {
    return (
      <p className="home-overview-activity-empty">
        Nothing plotted yet. Run your first command and this window starts filling in.
      </p>
    )
  }

  return (
    <>
      <ActivityTrendChart
        label={`${activity.heading}: ${formatNumber(activity.commandsRun)} commands run and ${formatNumber(activity.levelsCompleted)} levels finished${peak ? `, busiest in ${peak.caption} with ${formatNumber(peak.commandsRun)} commands` : ''}.`}
        peakIndex={peakIndex}
        peakLabel={activity.peakLabel}
        points={points}
      />
      <p className="home-overview-activity-summary">
        <strong>{formatNumber(activity.commandsRun)}</strong> commands and{' '}
        <strong>{formatNumber(activity.levelsCompleted)}</strong> levels finished on{' '}
        <strong>{formatNumber(activity.activeBuckets)}</strong> of {points.length} {activity.bucket}
      </p>
    </>
  )
}

export function HomeProgressPanel({
  activityWindow,
  onSelectActivityWindow,
  progress,
}: {
  activityWindow: ActivityWindow
  onSelectActivityWindow: (next: ActivityWindow) => void
  progress: HomeProgressModel
}) {
  const { story } = progress
  // The tower is the screen's single finish-rate statement: the share of runs
  // started that were also finished. Named for what it measures, so it can never
  // be read as "how much of the story is left".
  const finished = story.finishRate.value ?? 0
  const attempted = story.finishRate.denominator > 0
  // The picker moves the instant it is clicked; the plot keeps the span it is
  // actually drawing until the new one lands, and dims to say so.
  const pending = activityWindow !== progress.activity.resolvedWindow

  return (
    <section className="home-overview-stats-panel" aria-label="Where you stand" data-onboarding="overview-progress">
      <div className="home-overview-stat-subgrid">
        <section className="home-overview-stat-block">
          <div className="home-overview-band-head">
            <header className="ref-panel-head">
              {progress.activity.heading} <em>commands run, then levels finished</em>
            </header>
            <ActivitySpanPicker
              activityWindow={activityWindow}
              onSelectActivityWindow={onSelectActivityWindow}
            />
          </div>
          <div className="home-overview-activity" data-pending={pending ? 'true' : undefined}>
            <ActivityBand activity={progress.activity} />
          </div>
        </section>

        <section
          className={`home-overview-stat-block home-overview-story-block${finished >= 100 && attempted ? ' is-complete' : ''}`}
        >
          <header className="ref-panel-head">
            Runs finished <em>every story and challenge</em>
          </header>
          <div className="home-overview-story-body">
            <div className="home-overview-story-sigil" aria-hidden="true">
              <div className="home-overview-story-frame">
                <div className="home-overview-story-shell" />
                <div className="home-overview-story-fill" style={{ height: `${finished}%` }}>
                  <div className="home-overview-story-fill-inner" />
                </div>
              </div>
              <span className="home-overview-story-ground" />
            </div>
            <div className="home-overview-story-readout">
              <p
                className="home-overview-story-rate"
                data-empty={attempted ? undefined : 'true'}
                aria-label={attempted ? `Runs finished ${finished}%` : 'Runs finished: no runs yet'}
              >
                <strong>{attempted ? `${finished}%` : '--'}</strong>
                <small>
                  {attempted
                    ? `${formatNumber(story.finishRate.numerator)} of ${formatNumber(story.finishRate.denominator)} runs you started`
                    : 'No runs yet'}
                </small>
              </p>
              <dl>
                <div>
                  <dt>Levels finished</dt>
                  <dd className={story.levelsCompleted === 0 ? 'is-zero' : undefined}>
                    {formatNumber(story.levelsCompleted)}
                  </dd>
                </div>
                <div>
                  <dt>Flawless finishes</dt>
                  <dd className={story.perfectClears === 0 ? 'is-zero' : undefined}>
                    {formatNumber(story.perfectClears)}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </section>
      </div>
    </section>
  )
}
