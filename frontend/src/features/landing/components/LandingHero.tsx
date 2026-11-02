import { Link } from 'react-router-dom'

import gitLogoImage from '@/assets/images/git-it-logo-new.png'
import { Button } from '@/shared/components/Button'

export function LandingHeader() {
  return (
    <header className="landing-header" />
  )
}

export function LandingHero() {
  return (
    <section className="landing-hero" aria-labelledby="landing-hero-title">
      <div className="landing-hero__sky" aria-hidden="true" />
      <div className="landing-hero__copy">
        <img className="landing-hero__logo" src={gitLogoImage} alt="GIT it!" width={900} height={305} />
        <h1 id="landing-hero-title" className="landing-hero__title">
          Stop memorising Git. Start reading the repository.
        </h1>
        <p className="landing-hero__lede">
          Clear real Git scenarios in a simulated terminal while a live graph redraws with every command. You pass when
          the repository is right, however you got there.
        </p>
        <div className="landing-hero__actions">
          <Button asChild size="lg">
            <Link to="/register">Begin your quest</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <a href="#how-it-works">See a scenario</a>
          </Button>
        </div>
        <p className="landing-hero__note">Nothing here touches a real repository. Break things freely.</p>
      </div>
    </section>
  )
}
