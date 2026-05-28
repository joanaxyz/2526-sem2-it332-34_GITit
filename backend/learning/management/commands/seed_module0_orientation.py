from django.core.management.base import BaseCommand

from learning.models import LearningUnit, Lesson

EMPTY_REPO = {
    "repository_initialized": False,
    "commits": [],
    "branches": {"main": None},
    "head": {"type": "none", "name": None},
    "working_tree": {},
    "staging": {},
    "conflicts": [],
}

STATUS_DEMO_STATE = {
    "repository_initialized": True,
    "commits": [
        {
            "id": "c0",
            "message": "Initial commit",
            "parents": [],
            "tree": {"app.txt": "tracked", "notes.txt": "tracked"},
            "order": 0,
        }
    ],
    "branches": {"main": "c0"},
    "head": {"type": "branch", "name": "main"},
    "working_tree": {"app.txt": "modified"},
    "staging": {"notes.txt": "staged"},
    "conflicts": [],
}

DAG_DEMO_STATE = {
    "repository_initialized": True,
    "commits": [
        {
            "id": "c0",
            "message": "Initial commit",
            "parents": [],
            "tree": {"README.md": "tracked"},
            "files": {"README.md": "tracked"},
            "order": 0,
        },
        {
            "id": "c1",
            "message": "Shared base",
            "parents": ["c0"],
            "tree": {"README.md": "tracked"},
            "files": {"README.md": "tracked"},
            "order": 1,
        },
        {
            "id": "c2",
            "message": "Main line",
            "parents": ["c1"],
            "tree": {"README.md": "tracked", "app.txt": "tracked"},
            "files": {"README.md": "tracked", "app.txt": "tracked"},
            "order": 2,
        },
        {
            "id": "c3",
            "message": "Feature branch",
            "parents": ["c1"],
            "tree": {"README.md": "tracked", "feature.txt": "tracked"},
            "files": {"README.md": "tracked", "feature.txt": "tracked"},
            "order": 3,
        },
    ],
    "branches": {"main": "c2", "feature": "c3"},
    "head": {"type": "branch", "name": "main"},
    "working_tree": {},
    "staging": {},
    "conflicts": [],
}

CANONICAL_SLUGS = [
    "what-is-git-and-why-it-matters",
    "installing-git-and-environment",
    "command-line-basics",
    "git-diagram-four-areas",
    "commits-and-history",
    "reading-a-dag",
    "git-command-anatomy",
    "how-git-it-works",
]

STATUS_SAMPLE_OUTPUT = """On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   notes.txt
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
	modified:   app.txt"""

LESSON_SPECS = [
    {
        "sort_order": 1,
        "slug": "what-is-git-and-why-it-matters",
        "title": "What Is Git and Why Does It Matter?",
        "subtitle": "Version control fundamentals and the team workflow Git protects.",
        "layout": "storyboard",
        "content_html": """
            <p>Git is a <strong>distributed version control system</strong>. It tracks the full history of your project so teams can compare versions, recover work, and collaborate safely.</p>
            <p>Think of Git as a timeline plus collaboration protocol. It stores <em>what changed</em>, <em>why it changed</em>, and <em>how changes connect</em>.</p>
        """,
        "interaction_steps": [
            {
                "id": "vc-discipline",
                "kind": "continue",
                "title": "Version control discipline",
                "prompt": "Read this scenario, then continue: two teammates both edit a file called report_final.docx and keep making renamed copies.",
                "body": "Manual copy naming breaks quickly in teams: no reliable ownership, unclear latest file, and no safe rollback point. Git replaces that with a shared, auditable history.",
            },
            {
                "id": "centralized-vs-distributed",
                "kind": "compare_toggle",
                "title": "Centralized vs distributed",
                "prompt": "Compare each model and note where authoritative history lives and what happens if the server goes down.",
                "options": [
                    {"id": "centralized", "label": "Centralized (SVN)", "detail": "One central server owns history. Clients depend on it for full context and many operations."},
                    {"id": "distributed", "label": "Distributed (Git)", "detail": "Every clone has complete history. Remotes coordinate sharing, but work can continue locally."},
                ],
            },
            {
                "id": "three-problems",
                "kind": "continue",
                "title": "Three problems Git solves",
                "prompt": "Review these three problems directly and map each one to the Git capability that solves it.",
                "body": "History: identify exactly who changed a line and why. Collaboration: multiple branches can progress without overwriting each other. Recovery: previous known-good states can be restored quickly during incidents.",
            },
            {
                "id": "industry-standard",
                "kind": "continue",
                "title": "Industry standard",
                "prompt": "Git is the default VCS in software teams, open-source projects, and CI/CD pipelines.",
                "body": "Modern workflows (feature branching, code review, release tagging, bisecting regressions, and automated deployments) all assume Git fluency. Build the mental model first, then command syntax becomes predictable rather than memorized.",
            },
        ],
    },
    {
        "sort_order": 2,
        "slug": "installing-git-and-environment",
        "title": "Installing Git and Setting Up Your Environment",
        "subtitle": "Install Git and configure authorship for commits.",
        "layout": "guide_terminal",
        "content_html": "<p>Install Git for your OS, verify the install, and configure your identity. These values appear in commit metadata and power collaboration tools like blame, review, and release auditing.</p>",
        "interaction_steps": [
            {
                "id": "install-notes",
                "kind": "continue",
                "title": "Install Git",
                "prompt": "Windows: Git Bash from git-scm.com. macOS: Homebrew or Xcode CLI. Linux: apt install git.",
                "body": "Use a real terminal on your machine for install; this lesson practices configuration commands.",
            },
            {
                "id": "verify-version",
                "kind": "git_command",
                "title": "Verify installation",
                "prompt": "Type the command that prints the installed Git version (exact flag spelling matters).",
                "accept_prefixes": ["git --version"],
                "hint": "Use git --version (not --v).",
                "require_processed": False,
                "success_output": "git version 2.44.0",
                "initial_state": EMPTY_REPO,
            },
            {
                "id": "set-name",
                "kind": "git_command",
                "title": "Set your name",
                "prompt": 'Set global user.name, e.g. git config --global user.name "Your Name"',
                "accept_prefixes": ["git config --global user.name"],
                "hint": "Use git config --global user.name followed by your name in quotes.",
                "require_processed": False,
                "success_output": "Set global user.name",
                "initial_state": EMPTY_REPO,
            },
            {
                "id": "set-email",
                "kind": "git_command",
                "title": "Set your email",
                "prompt": "Set global user.email with your commit email.",
                "accept_prefixes": ["git config --global user.email"],
                "hint": "Use git config --global user.email and a valid email in quotes.",
                "require_processed": False,
                "success_output": "Set global user.email",
                "initial_state": EMPTY_REPO,
            },
            {
                "id": "list-config",
                "kind": "git_command",
                "title": "List configuration",
                "prompt": "List active Git configuration values, then look for user.name and user.email.",
                "accept_prefixes": ["git config --list", "git config -l"],
                "hint": "Try git config --list, then scan the output for identity keys.",
                "require_processed": False,
                "success_output": "user.name=Your Name\nuser.email=you@example.com",
                "initial_state": EMPTY_REPO,
            },
        ],
    },
    {
        "sort_order": 3,
        "slug": "command-line-basics",
        "title": "Command Line Basics for Git Users",
        "subtitle": "Navigate the filesystem before running Git in the right folder.",
        "layout": "explorer_shell",
        "content_html": "<p>Many Git mistakes start as filesystem mistakes. Before running Git commands, always confirm where you are, what files exist, and what just changed in your working directory.</p>",
        "interaction_steps": [
            {
                "id": "pwd",
                "kind": "shell_command",
                "title": "Where am I?",
                "prompt": "Type pwd to print the working directory.",
                "accept_prefixes": ["pwd"],
                "hint": "pwd takes no arguments.",
            },
            {
                "id": "ls-la",
                "kind": "shell_command",
                "title": "List including hidden",
                "prompt": "Type ls -la to see hidden files like .git later.",
                "accept_prefixes": ["ls -la", "ls -a -l"],
                "hint": "Use ls with -la flags.",
            },
            {
                "id": "mkdir-practice",
                "kind": "shell_command",
                "title": "Create a folder",
                "prompt": "Type mkdir practice to create a project folder.",
                "accept_prefixes": ["mkdir practice"],
                "hint": "mkdir creates a directory.",
            },
            {
                "id": "cd-practice",
                "kind": "shell_command",
                "title": "Enter the folder",
                "prompt": "Type cd practice to move into that folder, then confirm your new location in the next commands.",
                "accept_prefixes": ["cd practice"],
                "hint": "cd changes your working directory.",
            },
            {
                "id": "touch-readme",
                "kind": "shell_command",
                "title": "Create a file",
                "prompt": "Type touch readme.md to create an empty file.",
                "accept_prefixes": ["touch readme.md"],
                "hint": "touch creates an empty file.",
            },
            {
                "id": "echo-readme",
                "kind": "shell_command",
                "title": "Write to the file",
                "prompt": 'Type echo "hello" > readme.md to write text into the file.',
                "accept_prefixes": ['echo "hello" > readme.md', "echo hello > readme.md"],
                "hint": "echo with > writes text to a file.",
            },
            {
                "id": "cat-readme",
                "kind": "shell_command",
                "title": "Read the file",
                "prompt": "Type cat readme.md to print the file contents.",
                "accept_prefixes": ["cat readme.md"],
                "hint": "cat prints file contents to the terminal.",
            },
        ],
    },
    {
        "sort_order": 4,
        "slug": "git-diagram-four-areas",
        "title": "The Git Diagram: How Git Thinks About Your Files",
        "subtitle": "Working tree, staging, local repo, and remote — plus git status.",
        "layout": "pipeline_status",
        "critical": True,
        "content_html": "<p>The four-area model is the core Git mental model: <strong>Working Tree</strong> (your edits), <strong>Staging Area</strong> (selected snapshot), <strong>Local Repository</strong> (committed history), and <strong>Remote</strong> (shared collaboration point). <code>git status</code> tells you where each change currently lives.</p>",
        "interaction_steps": [
            {
                "id": "pipeline-drag",
                "kind": "pipeline",
                "title": "Move through four areas",
                "prompt": "Move a file through the lifecycle: edit in working tree, select in staging, save in local repo, and share to remote.",
                "stages": ["working_tree", "staging", "local_repo", "remote"],
            },
            {
                "id": "staging-why",
                "kind": "continue",
                "title": "Why staging exists",
                "prompt": "Staging exists so one commit can contain only related changes, even when your working tree has multiple tasks in progress.",
                "body": "Use staging to curate commit scope. This is what keeps commit history readable and makes code review faster.",
            },
            {
                "id": "status-annotate",
                "kind": "status_annotate",
                "title": "Read git status",
                "prompt": "Study the sample output and map each section to one area of the model.",
                "sample_output": STATUS_SAMPLE_OUTPUT,
            },
            {
                "id": "run-status",
                "kind": "git_command",
                "title": "Run git status",
                "prompt": "Run git status on the demo repository and compare it with the annotated sample.",
                "accept_prefixes": ["git status"],
                "hint": "git status is diagnostic — use it freely in practice.",
                "initial_state": STATUS_DEMO_STATE,
            },
        ],
    },
    {
        "sort_order": 5,
        "slug": "commits-and-history",
        "title": "Understanding Commits and Commit History",
        "subtitle": "Commit structure, metadata meaning, and why commit objects are immutable.",
        "layout": "anatomy",
        "content_html": "<p>A commit is a structured record, not just a message. It stores a content snapshot plus metadata: hash, author, timestamp, message, and parent commit links. Together these fields make history traceable and verifiable.</p>",
        "interaction_steps": [
            {
                "id": "anatomy-explore",
                "kind": "anatomy",
                "title": "Commit anatomy",
                "prompt": "Inspect each commit field and learn what question it answers during debugging and collaboration.",
                "parts": ["hash", "author", "timestamp", "message", "tree", "parent"],
            },
            {
                "id": "immutability",
                "kind": "immutability_demo",
                "title": "Immutability",
                "prompt": "Use the demo to see why amend creates a new commit object instead of mutating the old one.",
            },
            {
                "id": "messages",
                "kind": "continue",
                "title": "Commit messages",
                "prompt": "Use clear commit message structure: imperative subject line + optional body for rationale.",
                "body": "Recommended format: first line <= 72 chars in imperative mood (for example: Add login validation for empty passwords). Add a body when needed: why this change exists, key constraints, and notable side effects.",
            },
        ],
    },
    {
        "sort_order": 6,
        "slug": "reading-a-dag",
        "title": "Reading a DAG: Branches, HEAD, and Commit Graphs",
        "subtitle": "Read branch labels, HEAD, merges, and git log output.",
        "layout": "dag_log",
        "critical": True,
        "content_html": "<p>Git history is a DAG (Directed Acyclic Graph): each commit points to parent commit(s). Branch labels are movable pointers to commits, and HEAD points to your current checkout context.</p>",
        "interaction_steps": [
            {
                "id": "dag-labels",
                "kind": "dag_explore",
                "title": "Label the graph",
                "prompt": "Inspect the graph and identify which commit each branch label points to, then identify what HEAD currently follows.",
                "initial_state": DAG_DEMO_STATE,
            },
            {
                "id": "detached-head",
                "kind": "continue",
                "title": "Detached HEAD",
                "prompt": "When HEAD points to a commit hash instead of a branch, new work can become unreachable.",
                "body": "Create a branch before switching away from detached HEAD if you want to keep commits.",
            },
            {
                "id": "log-graph",
                "kind": "git_command",
                "title": "Graph log",
                "prompt": "Run git log --oneline --graph --all to print a compact branch-aware commit graph.",
                "accept_prefixes": ["git log --oneline --graph --all", "git log --graph --oneline --all"],
                "hint": "Use git log with --oneline --graph --all (order of flags can vary).",
                "initial_state": DAG_DEMO_STATE,
            },
            {
                "id": "log-decorate",
                "kind": "continue",
                "title": "Branch labels on the graph",
                "prompt": "Branch labels are pointers, not copies of commits. When a branch advances, only the label moves.",
                "body": "In terminal output, --decorate shows these labels beside commits. In this platform, the visual DAG shows the same idea directly.",
            },
        ],
    },
    {
        "sort_order": 7,
        "slug": "git-command-anatomy",
        "title": "Git Command Anatomy",
        "subtitle": "Subcommands, flags, arguments, and reading help output.",
        "layout": "command_builder",
        "critical": True,
        "content_html": "<p>Parse commands as <code>git &lt;subcommand&gt; [flags] [arguments]</code>. Understanding this anatomy helps you debug syntax quickly and adapt commands without memorizing full strings.</p>",
        "interaction_steps": [
            {
                "id": "decompose-commit",
                "kind": "command_builder",
                "title": "Decompose commit",
                "prompt": 'Build: git commit -m "message"',
                "target": 'git commit -m "message"',
            },
            {
                "id": "decompose-log",
                "kind": "command_builder",
                "title": "Decompose log",
                "prompt": "Build: git log --oneline --graph --all",
                "target": "git log --oneline --graph --all",
            },
            {
                "id": "read-help",
                "kind": "git_command",
                "title": "Quick help",
                "prompt": "Type git commit -h to read the short help synopsis and identify required vs optional parts.",
                "accept_prefixes": ["git commit -h"],
                "hint": "Use -h for a short summary of a subcommand.",
                "require_processed": False,
                "success_output": "usage: git commit [-m <msg>] [--amend]\n\n-m <msg>    use the given commit message\n--amend     replace the latest commit with a new commit object",
                "initial_state": EMPTY_REPO,
            },
            {
                "id": "parse-error",
                "kind": "error_parse",
                "title": "Read an error",
                "prompt": "Which part failed? fatal: not a git repository → you are outside a repo (need git init).",
                "error_text": "fatal: not a git repository (or any of the parent directories): .git",
                "answer": "repository",
            },
        ],
    },
    {
        "sort_order": 8,
        "slug": "how-git-it-works",
        "title": "How GIT it! Works: The Platform Walkthrough",
        "subtitle": "Scenario workspace, scaffolding tiers, and progress tools.",
        "layout": "platform_tour",
        "content_html": "<p>Before scenario practice, understand the workspace flow end-to-end: read objective, inspect repository state, run commands, compare actual vs target state, and iterate from feedback.</p>",
        "interaction_steps": [
            {
                "id": "workspace-map",
                "kind": "platform_panel",
                "title": "Practice workspace",
                "prompt": "Walk through a sample practice session by inspecting each workspace region in order of use.",
                "body": "Sample flow: (1) Read the objective in the narrative panel, (2) inspect current repository state in the DAG, (3) run a command in the terminal, (4) compare against expected state, (5) use feedback to decide the next command.",
                "hotspots": ["narrative", "files", "dag", "expected", "terminal", "feedback"],
            },
            {
                "id": "difficulty-tiers",
                "kind": "platform_panel",
                "title": "Difficulty tiers",
                "prompt": "Compare support levels: Easy (guided), Medium (reduced hints), Hard (minimal scaffolding).",
                "body": "Easy exposes all instructional panels. Medium removes direct feedback so you infer more from state. Hard keeps only essential state indicators so you rely on command reasoning.",
                "hotspots": ["easy", "medium", "hard"],
            },
            {
                "id": "counted-commands",
                "kind": "platform_panel",
                "title": "Counted vs diagnostic",
                "prompt": "Diagnostic commands (git status, git log, git diff) do not consume the action budget.",
                "body": "Use diagnostics frequently to inspect state. Counted commands are history-changing actions such as add, commit, merge, checkout conflict-side, and restore operations.",
                "hotspots": ["diagnostic", "counted"],
            },
            {
                "id": "retry-policy",
                "kind": "platform_panel",
                "title": "Retries and no-answer policy",
                "prompt": "Failed sessions retry with changed variants. The platform avoids answer leaks so you build transferable command fluency.",
                "body": "Treat retries as fresh scenarios. Focus on principles instead of memorizing sequences, and rely on status/log/diff evidence to recover.",
                "hotspots": ["retry", "no_answer"],
            },
            {
                "id": "dashboard",
                "kind": "continue",
                "title": "Progress dashboard",
                "prompt": "Track completion, accuracy, and review mode from the dashboard after orientation.",
                "body": "You are ready to open Module 1 scenarios when you feel prepared — orientation is recommended first.",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed Module 0 orientation unit and eight interactive lessons from md_files/Module0.md"

    def handle(self, *args, **options):
        unit, _ = LearningUnit.objects.update_or_create(
            slug="orientation",
            defaults={
                "number": 0,
                "title": "Orientation",
                "description": (
                    "Build your Git mental model and platform familiarity before scenario practice. "
                    "Eight guided lessons — recommended before Modules 1–4."
                ),
                "is_orientation": True,
                "is_published": True,
                "sort_order": 0,
            },
        )
        for spec in LESSON_SPECS:
            Lesson.objects.update_or_create(
                unit=unit,
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "subtitle": spec["subtitle"],
                    "content_html": spec["content_html"].strip(),
                    "scoped_css": "",
                    "interaction_steps": spec["interaction_steps"],
                    "is_published": True,
                    "sort_order": spec["sort_order"],
                },
            )
        unpublished = Lesson.objects.filter(unit=unit).exclude(slug__in=CANONICAL_SLUGS).update(is_published=False)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded orientation unit with {len(LESSON_SPECS)} lessons ({unpublished} legacy lessons unpublished)."
            )
        )
