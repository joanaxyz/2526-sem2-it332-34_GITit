import { Link } from 'react-router-dom'

import gitLogoImage from '@/assets/images/git-it-logo-arcane.webp'
import { Button } from '@/shared/components/Button'
import { storyPath } from '@/shared/navigation/routes'

export function LandingHeader() {
  return (
    <header className="landing-header">
      <nav className="landing-header__nav" aria-label="Account">
        {/* Protected restores a saved session at the story map, or sends the player to /login. */}
        <Button asChild variant="outline" size="sm" className="landing-header__sign-in">
          <Link to={storyPath()}>Sign in</Link>
        </Button>
        <Button asChild size="sm">
          <Link to="/register">Create account</Link>
        </Button>
      </nav>
    </header>
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
