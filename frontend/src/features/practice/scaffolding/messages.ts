const MESSAGES: Record<'T1' | 'T2' | 'T3', Record<'easy' | 'medium' | 'hard', string>> = {
  T1: {
    easy: "💡 You've used a portion of your available commands without reaching the target state. Before your next command, compare the live DAG against the Expected-State Diagram — check where your current branch pointer is relative to where it needs to be. Diagnostic commands are free to use.",
    medium:
      "💡 You're moving beyond the expected command path. Pause and inspect the live DAG carefully against the Expected-State Diagram before continuing. Diagnostic commands won't cost you.",
    hard: '💡 Your current repository state may no longer align with the scenario objective. Re-read the scenario narrative and inspect the live DAG carefully before your next command.',
  },
  T2: {
    easy: "⚠️ You've used a significant portion of your command budget and the target repository state has not yet been reached. Use the live DAG and Expected-State Diagram to reassess where your repository state currently stands. Diagnostic commands remain available without penalty.\n\nThe concepts covered in this module's Lesson Overview are relevant to what this scenario requires.",
    medium:
      "⚠️ Your current command path significantly exceeds the expected transition. Inspect the live DAG carefully and use diagnostic commands to reassess your repository state before continuing.\n\nThe concepts covered in this module's Lesson Overview apply to this scenario.",
    hard: '⚠️ Your current repository state may have diverged from the scenario objective. Inspect the live DAG and reassess your repository-state transitions carefully before continuing.',
  },
  T3: {
    easy: "🔴 You are far beyond the expected command path and the target state is still unresolved. If the command limit is reached without completing the scenario, the session will end as Failed and a new variant will load on retry.\n\nBefore your next command, compare the live DAG against the Expected-State Diagram carefully. Diagnostic commands remain free to use.\n\nThe concepts covered in this module's Lesson Overview are relevant to what this scenario requires.",
    medium:
      "🔴 Your command path strongly suggests unresolved repository-state divergence. Use diagnostic commands — they are free — to inspect your current state before your next action command.\n\nThe concepts covered in this module's Lesson Overview apply to this scenario.",
    hard: '🔴 Your repository state remains unresolved despite substantial command usage. Use git log or git reflog to assess your current state carefully before your next action command.',
  },
}

export function getScaffoldMessage(
  trigger: 'T1' | 'T2' | 'T3',
  difficulty: 'easy' | 'medium' | 'hard',
): string {
  return MESSAGES[trigger][difficulty]
}
