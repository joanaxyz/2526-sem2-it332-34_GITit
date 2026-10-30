export type ScenarioStep = {
  title: string
  body: string
}

export const SCENARIO_STEPS: ScenarioStep[] = [
  {
    title: 'Read the brief',
    body: 'You get a repository and a job: rescue a lost commit, ship a hotfix, untangle a merge.',
  },
  {
    title: 'Work the terminal',
    body: 'Type real Git. The graph redraws after every command, so you see what it actually did.',
  },
  {
    title: 'Judged by state',
    body: 'No answer key to match. When the repository matches the target, the scenario is cleared.',
  },
]

export type VignetteCommand = {
  command: string
  output: string
}

// One branch-and-merge, played a command at a time. Step N of the vignette has
// run the first N commands; the graph in ScenarioVignette reads the same index.
export const VIGNETTE_COMMANDS: VignetteCommand[] = [
  { command: 'git switch -c spellbook', output: "Switched to a new branch 'spellbook'" },
  { command: 'git commit -am "Add fire ward"', output: '[spellbook 3f9a2c1] Add fire ward' },
  { command: 'git switch main', output: "Switched to branch 'main'" },
  { command: 'git merge --no-ff spellbook', output: "Merge made by the 'ort' strategy." },
]

export type EncounterSpell = {
  family: string
  command: string
}

// Each family has its own spell sheet under /cosmetics/companion/blue/effects.
export const ENCOUNTER_SPELLS: EncounterSpell[] = [
  { family: 'commit', command: 'git commit' },
  { family: 'merge', command: 'git merge' },
  { family: 'rebase', command: 'git rebase' },
  { family: 'revert', command: 'git revert' },
]

export type SpireModule = {
  number: string
  title: string
  commands: string[]
}

// Mirrors CHAPTER_SPECS in backend/curriculum/management/commands/seed_curriculum.py.
export const SPIRE_MODULES: SpireModule[] = [
  { number: '00', title: 'Orientation', commands: ['eight guided lessons'] },
  { number: '01', title: 'Repository Foundations', commands: ['init', 'clone', 'add', 'commit', 'amend'] },
  { number: '02', title: 'Branching & Collaboration', commands: ['switch', 'stash', 'push', 'pull', 'merge'] },
  { number: '03', title: 'Conflict Resolution', commands: ['diff', 'merge', 'mergetool', 'cherry-pick'] },
  { number: '04', title: 'Recovery & History', commands: ['reset', 'revert', 'rebase'] },
]

export type TierSupport = {
  tier: 'Easy' | 'Medium' | 'Hard'
  supports: { label: string; on: boolean }[]
}

// Mirrors the adventure TIER_SCAFFOLDING_LADDER in practice/services/scaffolding.py.
export const TIER_SUPPORT: TierSupport[] = [
  {
    tier: 'Easy',
    supports: [
      { label: 'Live graph', on: true },
      { label: 'Target state', on: true },
      { label: 'Guided feedback', on: true },
    ],
  },
  {
    tier: 'Medium',
    supports: [
      { label: 'Live graph', on: true },
      { label: 'Target state', on: true },
      { label: 'Guided feedback', on: false },
    ],
  },
  {
    tier: 'Hard',
    supports: [
      { label: 'Live graph', on: true },
      { label: 'Target state', on: false },
      { label: 'Guided feedback', on: false },
    ],
  },
]
