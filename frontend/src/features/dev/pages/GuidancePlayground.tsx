import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { BookOpen, GitBranch } from 'lucide-react'
import { OnboardingBanner } from '@/features/onboarding/components/OnboardingBanner'
import { OnboardingContext } from '@/features/onboarding/hooks/onboardingContext'
import { StoryOnboarding } from '@/features/story-map/components/StoryOnboarding'
import { OrientationStepView } from '@/features/story-map/components/orientation/OrientationStepView'
import { Button } from '@/shared/components/Button'
import { GameplayWorkspaceTour } from '@/shared/level/components/GameplayWorkspaceTour'
import { CommandGuideLauncher } from '@/features/story-map/components/CommandGuideLauncher'
import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import './guidance-preview.css'

const STEPS = [
  { id: 'map', selector: '#guide-preview-map', icon: GitBranch, title: 'Your next adventure starts here',
    body: 'Choose a glowing level to practice. I’ll help you read the objective and find your first command.', placement: 'right' as const },
  { id: 'terminal', selector: '#guide-preview-terminal', icon: BookOpen, title: 'Try a command and watch what changes',
    body: 'The terminal and commit graph show the state of your repository. Start with git status to see what needs attention.', placement: 'left' as const },
]
const GUIDES = [
  { teaching_key: 'status', title: 'Read repository state', command_form: { usage_form: 'git status' } },
  { teaching_key: 'add', title: 'Stage your changes', command_form: { usage_form: 'git add <path>' } },
] as CommandIntroduction[]

/** Dev-only review of the real guide components, without an account or API. */
export function Component() {
  const [params] = useSearchParams()
  const [mode, setMode] = useState('page')
  const [complete, setComplete] = useState(false)
  const [guideKey, setGuideKey] = useState('status')
  return <main className="guidance-preview">
    <header className="guidance-preview__header">
      <div><h1>Your Git-It guide</h1><p>Onboarding, workspace tours, and Git primer instructions.</p></div>
      <nav aria-label="Preview guidance">
        <Button variant="outline" onClick={() => setMode('welcome')}>Welcome</Button>
        <Button variant="outline" onClick={() => setMode('page')}>Page guide</Button>
        <Button variant="outline" onClick={() => setMode('tour')}>Start tour</Button>
        <Button variant="outline" onClick={() => setMode('primer')}>Git primer</Button>
      </nav>
    </header>
    <OnboardingBanner title="Let’s get you ready for your first adventure."
      actions={<Button onClick={() => setMode('tour')}>Show me around</Button>}
      onSkip={() => setMode('page')}>
      Choose a companion, explore your map, and try your first Git command. I’ll guide you along the way.
    </OnboardingBanner>
    {mode === 'primer' ? <OrientationStepView step={{
      id: 'preview-status', kind: 'git_command', title: 'Read the state of your repository',
      prompt: 'Before making changes, use git status to see your current branch and which files need attention.',
      accept_exact: ['git status'], success_output: 'On branch main\nnothing to commit, working tree clean',
    }} layout="guide_terminal" completed={complete} onStepComplete={() => setComplete(true)}
      hasNextStep={false} onContinueToNext={() => {}} /> : <div className="guidance-preview__workspace">
      <section id="guide-preview-map"><h2>Your adventure map</h2><p>Repository foundations</p>
        <button className="guidance-preview__level" onClick={() => setMode('tour')}>1<span>Stage & commit</span></button>
      </section>
      <section id="guide-preview-terminal"><h2>Practice terminal</h2><pre><code>$ git status{'\n'}On branch main{'\n'}nothing to commit, working tree clean{'\n'}$ <span>▍</span></code></pre></section>
    </div>}
    {mode === 'tour' ? <GameplayWorkspaceTour label="Getting started" steps={STEPS}
      transformable={params.has('reference')}
      aside={params.has('reference') ? <div className="guidance-preview__reference"><h2>Command reference</h2><p><code>git status</code> shows which files are staged, changed, or untracked.</p><p><code>git add</code> stages changes for your next commit.</p></div> : undefined}
      finishLabel="Let’s practice" onClose={() => setMode('page')} /> : null}
    {params.has('mascot') ? <CommandGuideLauncher guides={GUIDES} currentGuideKey={guideKey} guideOpen={mode === 'command'}
      onSelectGuide={(key) => { setGuideKey(key); setMode('command') }} /> : null}
    {mode === 'command' ? <GameplayWorkspaceTour label="Command guide" steps={[{
      id: guideKey, selector: '#guide-preview-terminal', icon: BookOpen,
      title: GUIDES.find((guide) => guide.teaching_key === guideKey)!.title,
      body: guideKey === 'status' ? 'Use git status to see your current branch and check which files are staged, modified, or untracked.' : 'Use git add <path> to put a file’s changes into the staging area for your next commit.',
      placement: 'left',
    }]} showProgress={false} skipIconOnly skipLabel="Hide command guide" finishLabel="Got it" transformable
      collapseTarget="[data-command-guide-launcher]" onClose={() => setMode('page')} /> : null}
    <OnboardingContext.Provider value={{ phase: mode === 'welcome' ? 'welcome' : 'done', setPhase: () => setMode('page') }}>
      <StoryOnboarding ready={false} compact={false} hasCompanion orientationAvailable
        onStartOrientation={() => setMode('primer')} onSkipOrientation={() => setMode('page')} />
    </OnboardingContext.Provider>
  </main>
}
