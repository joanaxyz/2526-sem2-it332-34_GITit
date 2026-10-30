import { Link } from 'react-router-dom'

import gitCoinImage from '@/assets/images/GIT_coin.png'
import { EncounterStage } from '@/features/landing/components/EncounterStage'
import { ScenarioVignette } from '@/features/landing/components/ScenarioVignette'
import { SCENARIO_STEPS, SPIRE_MODULES, TIER_SUPPORT } from '@/features/landing/utils/landingContent'
import { Button } from '@/shared/components/Button'
import { storyPath } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'

export function HowItWorks() {
  return (
    <section id="how-it-works" className="landing-section landing-how" aria-labelledby="landing-how-title">
      <div className="landing-how__intro">
        <p className="landing-eyebrow">How a scenario plays</p>
        <h2 id="landing-how-title" className="landing-section__title">
          Every command leaves a mark you can see.
        </h2>
      </div>
      <ScenarioVignette />
      <ol className="landing-steps">
        {SCENARIO_STEPS.map((step, index) => (
          <li key={step.title} className="landing-steps__item">
            <span className="landing-steps__number">{String(index + 1).padStart(2, '0')}</span>
            <div>
              <h3 className="landing-steps__title">{step.title}</h3>
              <p className="landing-steps__body">{step.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

export function SpireClimb() {
  return (
    <section className="landing-section landing-climb" aria-labelledby="landing-climb-title">
      <div className="landing-climb__intro">
        <p className="landing-eyebrow">The Arcane Spire</p>
        <h2 id="landing-climb-title" className="landing-section__title">
          Twenty-one levels, one storey at a time.
        </h2>
        <p className="landing-section__lede">
          Eight orientation lessons, then four modules. Every level runs Easy, Medium and Hard, and every module ends at
          a Challenge Gate of fresh problems with no guide.
        </p>

        <div className="landing-tiers" role="table" aria-label="Support at each difficulty">
          <p className="landing-tiers__caption">Support fades as you climb</p>
          {TIER_SUPPORT.map((row) => (
            <div key={row.tier} className="landing-tiers__row" role="row">
              <span className="landing-tiers__tier" role="rowheader">
                {row.tier}
              </span>
              {row.supports.map((support) => (
                <span
                  key={support.label}
                  role="cell"
                  className={cn('landing-tiers__support', !support.on && 'is-off')}
                >
                  <span aria-hidden="true">{support.on ? '●' : '○'}</span>
                  {support.label}
                  {support.on ? null : <span className="sr-only"> (off)</span>}
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>

      <ol className="landing-spire" aria-label="Modules, from the base of the Spire to the summit">
        {SPIRE_MODULES.map((module) => (
          <li key={module.number} className="landing-spire__storey">
            <span className="landing-spire__node" aria-hidden="true" />
            <span className="landing-spire__number">{module.number}</span>
            <div>
              <h3 className="landing-spire__title">{module.title}</h3>
              <p className="landing-spire__commands">{module.commands.join(' · ')}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

export function EncounterBand() {
  return (
    <section className="landing-encounter" aria-labelledby="landing-encounter-title">
      <div className="landing-encounter__hall" aria-hidden="true" />
      <div className="landing-encounter__copy">
        <p className="landing-eyebrow">Encounters</p>
        <h2 id="landing-encounter-title" className="landing-section__title">
          Every scenario is a fight you win with Git.
        </h2>
        <p className="landing-section__lede">
          Choose a companion, clear encounters, and spend the GitCoin you earn in the shop. Rewards are paid for cleared
          tiers, not for showing up.
        </p>
        <p className="landing-encounter__coin">
          <img src={gitCoinImage} alt="" width={28} height={28} loading="lazy" />
          GitCoin
        </p>
      </div>
      <EncounterStage />
    </section>
  )
}

export function ClosingCall() {
  return (
    <section className="landing-section landing-closing" aria-labelledby="landing-closing-title">
      <h2 id="landing-closing-title" className="landing-closing__title">
        The Spire is open.
      </h2>
      <p className="landing-section__lede">Create an account, pick a companion, and clear your first scenario tonight.</p>
      <div className="landing-hero__actions">
        <Button asChild size="lg">
          <Link to="/register">Begin your quest</Link>
        </Button>
        <Button asChild variant="ghost" size="lg">
          <Link to={storyPath()}>I already have an account</Link>
        </Button>
      </div>
    </section>
  )
}
