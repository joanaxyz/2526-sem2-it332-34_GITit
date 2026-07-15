"""Detailed conceptual lessons for the two additive advanced stories."""

from curriculum.library import _bullets, _callout, _diagram, _paragraph, _warning, lesson_pages

CHAPTER_LESSON_BLUEPRINTS = {
    "frost-temper-the-commit": {
        "concept": "A commit is a reviewable unit, not a backup checkpoint. Advanced staging and reset modes let you rebuild that unit without discarding valuable work.",
        "model": [
            "Working tree holds all edits.",
            "The index defines the exact next snapshot.",
            "HEAD names the commit being replaced or moved.",
            "Reset mode determines which of those three layers move together.",
        ],
        "workflow": [
            "Inspect with diff, word diff, and whitespace checks.",
            "Stage by hunk or tracked path.",
            "Amend only unpublished local history.",
            "Use soft or mixed reset before hard reset.",
        ],
        "risk": "A hard reset is not a stronger mixed reset; it also replaces working-tree content. Verify the target and preserve anything uncommitted first.",
    },
    "frost-choose-the-integration": {
        "concept": "Integration strategy is a history-design decision. The right choice depends on ancestry, review needs, and whether the branch boundary should remain visible.",
        "model": [
            "Fast-forward moves a ref without creating a commit.",
            "A merge commit records two parents and preserves the branch join.",
            "Squash stages one combined patch but does not preserve ancestry.",
            "Three-dot comparisons use the merge base as the starting point.",
        ],
        "workflow": [
            "Find the merge base.",
            "Measure left/right divergence.",
            "Inspect first-parent history.",
            "Choose ff-only, no-ff, or squash deliberately.",
        ],
        "risk": "Do not choose an integration command from team habit alone. First confirm the graph you are about to create.",
    },
    "frost-survive-the-conflict": {
        "concept": "A conflict is structured index state. Git keeps base, ours, and theirs so you can make a deliberate fourth version rather than guess from markers alone.",
        "model": [
            "Stage 1 is the merge base.",
            "Stage 2 is ours.",
            "Stage 3 is theirs.",
            "The resolved working file becomes the new stage-0 index entry.",
        ],
        "workflow": [
            "Read status and unmerged index entries.",
            "Compare base, ours, and theirs.",
            "Resolve one file at a time.",
            "Stage resolutions, then continue—or abort before committing.",
        ],
        "risk": "Taking ours or theirs is a content decision, not a synonym for keeping the current or incoming branch wholesale.",
    },
    "frost-move-the-patch": {
        "concept": "Stash, cherry-pick, and revert all move change content, but they preserve different amounts of commit identity and history context.",
        "model": [
            "Stash shelves uncommitted local state.",
            "Cherry-pick creates a new commit from another commit's patch.",
            "Revert creates a new inverse commit.",
            "Inspecting a stash as a patch shows exactly what will move before it moves.",
        ],
        "workflow": [
            "Inspect the source patch before moving it.",
            "Choose whether authorship and commit identity matter.",
            "Use no-commit when a patch needs editing or combining.",
            "Abort sequenced operations rather than resetting blindly.",
        ],
        "risk": "Patch movement can duplicate changes already present through another path. Inspect ancestry and current tree content first.",
    },
    "frost-reforge-the-branch": {
        "concept": "Rebase rebuilds commits on a new parent chain. Interactive rebase additionally edits the sequence, messages, and boundaries of unpublished work.",
        "model": [
            "Original commits remain in reflog until expiry.",
            "Replayed commits receive new object IDs.",
            "--onto separates the new base from the commit range being moved.",
            "range-diff compares old and rewritten series by patch meaning.",
        ],
        "workflow": [
            "Define upstream and new base explicitly.",
            "Create fixup commits while working.",
            "Review the interactive todo.",
            "Run tests, inspect range-diff, then publish with a lease.",
        ],
        "risk": "Rebasing shared commits changes the foundation collaborators may already have. Rewrite only with an agreed publication strategy.",
    },
    "frost-govern-the-remote": {
        "concept": "Remotes are ref namespaces plus transfer rules. Upstreams, refspecs, pruning, and pull policy determine which references move and how local history integrates.",
        "model": [
            "Fetching updates remote-tracking refs, not local branches.",
            "An upstream is configuration attached to a local branch.",
            "A refspec maps a source ref to a destination ref.",
            "Force-with-lease rejects publication when the remote moved unexpectedly.",
        ],
        "workflow": [
            "Inspect remote URLs and tracking state.",
            "Fetch and prune before integrating.",
            "Use an explicit pull policy.",
            "Delete or rewrite remote refs only after verifying collaborators' state.",
        ],
        "risk": "Plain force push discards the remote-state safety check. Use a lease and refresh remote-tracking refs first.",
    },
    "frost-deliver-the-release": {
        "concept": "A release is a verifiable reference plus its supporting evidence. Tags name the artifact, describe relates commits to it, and shortlog credits the contributors behind it.",
        "model": [
            "Lightweight tags are refs.",
            "Annotated tags are tag objects that carry a message, tagger, and date.",
            "Describe names any commit relative to the nearest reachable release tag.",
            "Shortlog condenses a commit range into a per-contributor summary.",
        ],
        "workflow": [
            "Verify the release commit.",
            "Create an annotated tag and release note.",
            "Generate the contributor summary for the release range.",
            "Publish the intended tags to the relay stations deliberately.",
        ],
        "risk": "A tag name is not proof of authenticity. Critical releases require signature verification and a trusted key policy.",
    },
    "skyline-revision-language": {
        "concept": "Revision syntax is a query language over the commit graph. Precise expressions let you select one object, an ancestor, or a set difference without manual ID copying.",
        "model": [
            "^ selects parents or excludes commits in sets.",
            "~ follows first parents repeatedly.",
            "A..B means reachable from B but not A.",
            "A...B means commits unique to either side; commands interpret the symmetric set or merge base appropriately.",
        ],
        "workflow": [
            "Resolve names with rev-parse.",
            "Test ancestry before mutation.",
            "Use -- to separate revisions from paths.",
            "Record reflog selectors when recovering moving refs.",
        ],
        "risk": "Ambiguous names can resolve as either a ref or path. Use explicit refs and the -- separator in automation.",
    },
    "skyline-hidden-history": {
        "concept": "Repository forensics combines graph filters, patch searches, path history, line attribution, and content search. Each answers a different question.",
        "model": [
            "--grep searches messages.",
            "-S searches changes in occurrence count.",
            "-G searches added and removed lines by regex.",
            "Blame attributes lines but must be interpreted with surrounding history.",
        ],
        "workflow": [
            "Start with the narrowest question.",
            "Use log filters to find candidate commits.",
            "Inspect patches and path history.",
            "Confirm with blame or grep rather than treating one command as proof.",
        ],
        "risk": "Blame identifies the last modifying commit, not the person responsible for the underlying design or defect.",
    },
    "skyline-first-broken-commit": {
        "concept": "Bisect turns debugging into a bounded graph search. Reliable classification of good and bad revisions matters more than the number of commands run.",
        "model": [
            "A known-good and known-bad boundary define the search interval.",
            "Each classification removes roughly half the candidates.",
            "Skip preserves uncertainty for untestable revisions.",
            "Bisect run automates classification using an authored deterministic test.",
        ],
        "workflow": [
            "Save the current branch and working state.",
            "Mark trustworthy boundaries.",
            "Run or automate the same test at every step.",
            "Save the log, identify the first bad commit, then reset.",
        ],
        "risk": "A flaky test produces a plausible but wrong culprit. Stabilize the reproduction before automating bisect.",
    },
    "skyline-repeated-conflict": {
        "concept": "Rerere treats a conflict resolution as reusable knowledge keyed by conflict shape. Merge-tree and range-diff let you inspect integrations before repeating work.",
        "model": [
            "Rerere stores preimage and postimage pairs.",
            "A later matching conflict can reuse the recorded resolution.",
            "diff3 and zdiff3 expose base context.",
            "merge-tree previews a merge without changing the working tree.",
        ],
        "workflow": [
            "Enable rerere intentionally.",
            "Resolve and review the first conflict carefully.",
            "Inspect rerere status and diff.",
            "Verify reused resolutions with tests and range comparisons.",
        ],
        "risk": "Recorded resolutions are automation, not authority. Always review a reused result when surrounding code changed.",
    },
    "skyline-many-realities": {
        "concept": "Large repositories separate object availability, checkout visibility, and working-directory location. Worktrees, sparse checkout, partial clone, and submodules solve different scaling problems.",
        "model": [
            "Worktrees share the object database and refs but have separate indexes and working files.",
            "Sparse checkout limits paths materialized in one worktree.",
            "Partial clone defers selected objects.",
            "Submodules record another repository and commit as a dependency.",
        ],
        "workflow": [
            "Choose the scaling mechanism by constraint.",
            "Keep branch ownership clear across worktrees.",
            "Treat sparse definitions as workspace configuration.",
            "Update submodule URLs and commits explicitly.",
        ],
        "risk": "A submodule directory is not ordinary tracked content. The parent records a gitlink commit, so both repositories must be coordinated.",
    },
    "skyline-enchant-behavior": {
        "concept": "Git behavior is assembled from configuration scopes, attributes, ignore sources, aliases, hooks, and filters. Effective behavior depends on precedence and repository trust.",
        "model": [
            "System, global, local, and worktree scopes layer values.",
            "includeIf selects config by context.",
            ".gitattributes controls path behavior in Git operations.",
            "Hooks and filters execute code outside the object model.",
        ],
        "workflow": [
            "Inspect origin and scope before changing a value.",
            "Keep team rules in versioned attributes where appropriate.",
            "Use aliases for clarity, not hidden destructive behavior.",
            "Document and review executable hooks or filters.",
        ],
        "risk": "Configuration can execute external programs through hooks, filters, diff drivers, and merge drivers. Do not trust repository configuration blindly.",
    },
    "skyline-guard-the-archive": {
        "concept": "Signing proves that a configured key endorsed an object; trust policy determines whether that key should be accepted. Credentials and safe-directory rules protect different boundaries.",
        "model": [
            "Commit and tag signatures cover specific object content.",
            "Verification reports cryptographic validity and signer identity.",
            "Credential helpers store or retrieve authentication material.",
            "safe.directory protects ownership boundaries, not remote authenticity.",
        ],
        "workflow": [
            "Define trusted signing identities.",
            "Verify objects before release or deployment.",
            "Use the least-exposing credential helper available.",
            "Restrict protocols and explicitly trust exceptional directories.",
        ],
        "risk": "A valid signature from an unknown or compromised key is not sufficient. Verification must be tied to an organizational trust decision.",
    },
    "skyline-restore-maintain": {
        "concept": "Recovery operates on reachability. Reflogs preserve recent ref movement, fsck exposes object connectivity, and count-objects reveals what the object store is actually holding.",
        "model": [
            "Unreachable is not immediately deleted.",
            "Reflogs can make recent commits discoverable after ref movement.",
            "Fsck reports dangling and unreachable objects without changing them.",
            "Count-objects measures loose and packed storage so drift is visible.",
        ],
        "workflow": [
            "Recover before anything is allowed to expire.",
            "Run integrity checks and inspect dangling objects.",
            "Create a recovery ref for important commits.",
            "Restore the known-good state and verify the graph afterwards.",
        ],
        "risk": "Once reflogs expire and unreachable objects are gone, recovery may be impossible. Treat every recovery as evidence-preservation first.",
    },
    "skyline-git-machinery": {
        "concept": "Git stores immutable objects addressed by content and uses mutable refs to name them. Porcelain commands coordinate blobs, trees, commits, the index, and refs through safer workflows.",
        "model": [
            "Blobs store file content.",
            "Trees map names to blobs and subtrees.",
            "Commits point to a tree and parent commits.",
            "Refs and symbolic refs provide movable names; packfiles compress object storage.",
        ],
        "workflow": [
            "Inspect object type before content.",
            "Read tree and index entries.",
            "Follow HEAD's symbolic chain to the ref it names.",
            "Cross-check every visible ref against the objects it resolves to.",
        ],
        "risk": "Plumbing reads bypass porcelain presentation. Interpret raw objects carefully and verify conclusions against the visible graph before acting on them.",
    },
}



CHAPTER_LESSON_BLUEPRINTS.update(
    {
        "guild-archive-handoff": {
            "concept": "A reliable handoff combines the beginner skills into one explainable path: inspect, isolate work, stage intentionally, commit, integrate, verify, and publish.",
            "model": [
                "The working tree contains the unfinished handoff.",
                "A topic branch isolates the repair from stable main.",
                "The merge shape records how the repair entered shared history.",
                "Remote-tracking refs prove whether the Guild received the final tip.",
            ],
            "workflow": [
                "Inspect status and the graph before creating a branch.",
                "Commit only the requested handoff files.",
                "Integrate with the history shape requested by the review.",
                "Verify the DAG, clean state, and published ref.",
            ],
            "risk": "A handoff is not complete merely because a commit exists. The branch, merge, workspace, and remote state must all agree.",
        },
        "frost-hunt-the-regression": {
            "concept": "Regression hunting is an evidence loop: establish one known-good boundary, one known-bad boundary, test the midpoint, and preserve the first-bad result before repairing it.",
            "model": [
                "Good and bad marks bound the search range.",
                "Bisect repeatedly selects a midpoint commit.",
                "Skipped commits remain unresolved evidence, not automatic failures.",
                "The repair should add a visible corrective commit after the culprit is identified.",
            ],
            "workflow": [
                "Confirm the test distinguishes good from bad behavior.",
                "Start bisect and mark trustworthy boundaries.",
                "Run or automate the test until Git identifies the first bad commit.",
                "Reset the bisect session, repair or revert the culprit, and verify the graph.",
            ],
            "risk": "Incorrect boundary marks produce a confident but false culprit. Verify both endpoints before trusting an automated bisect.",
        },
        "frost-publish-the-core": {
            "concept": "Publishing a restored core is a release-governance task: the final commit, tag, signature evidence, remote ref, and clean workspace must describe the same artifact.",
            "model": [
                "The release branch points at the reviewed correction.",
                "An annotated tag gives the release a durable name and message.",
                "Verification checks identity evidence without changing history.",
                "The remote branch and tag are separate refs that must both be published deliberately.",
            ],
            "workflow": [
                "Inspect the release tip and contributor summary.",
                "Create or verify the annotated release tag.",
                "Publish the branch and intended tags without overwriting unseen work.",
                "Read refs and the graph to prove the handoff is complete.",
            ],
            "risk": "A tag name alone does not prove provenance or publication. Verify what it points to and whether the remote received it.",
        },
        "skyline-serve-the-city": {
            "concept": "Repository services expose refs and objects to other systems. Administration therefore begins by deciding which refs are authoritative and which transport behavior is safe.",
            "model": [
                "A bare repository has no working tree and exists to exchange objects and refs.",
                "Advertised refs define what clients can discover.",
                "Server-info and protocol helpers support different transport modes.",
                "Access controls belong around the service; Git commands alone are not an authorization system.",
            ],
            "workflow": [
                "Inventory refs before exposing the repository.",
                "Separate public release refs from internal operational refs.",
                "Update service metadata only when the chosen transport requires it.",
                "Verify from a client-shaped view, then record a visible corrective ref change.",
            ],
            "risk": "Serving every ref can leak internal branches or credentials embedded in history. Audit the namespace before enabling access.",
        },
        "skyline-migrate-the-grid": {
            "concept": "A repository migration is complete only when object identity, commit topology, refs, tags, and authorship provably survive the transfer — and proof comes from inspection, not from a clean exit code.",
            "model": [
                "Every ref in the migrated archive must resolve to the expected object type.",
                "Tree inspection proves that file layout survived the move.",
                "Object inspection proves that commit content and authorship survived.",
                "An integrity check proves that nothing reachable was left behind.",
            ],
            "workflow": [
                "Inventory the refs the migrated archive advertises.",
                "Resolve each critical ref and confirm its object type.",
                "Inspect representative commits and trees against the source record.",
                "Run a full integrity check before the district trusts the new archive.",
            ],
            "risk": "Matching branch names is insufficient. Missing tags, rewritten identities, or unreachable objects can make a migration silently incomplete.",
        },
        "skyline-command-laboratory": {
            "concept": "The laboratory is where every campaign discipline meets: diagnosis, history search, integration, recovery, and verification combine into one incident that must end in a proven ref change.",
            "model": [
                "Porcelain commands perform the final ref change safely.",
                "Rev-parse turns any revision expression into a verifiable object ID.",
                "For-each-ref enumerates the refs that must agree when work is done.",
                "The DAG, workspace, and refs must all tell the same story before handoff.",
            ],
            "workflow": [
                "Diagnose the incident with the campaign's inspection commands.",
                "Choose and execute the repair with porcelain workflows.",
                "Resolve the resulting refs to object IDs and confirm them.",
                "Finish scored work with a verifiable ref transition visible in the DAG.",
            ],
            "risk": "A capstone repair that cannot be proven is not complete. Verify the final refs explicitly instead of trusting the last command's silence.",
        },
    }
)

def _concept_lesson(module: str, data: dict) -> dict:
    title = "Mental Model"
    return {
        "module": module,
        "slug": "mental-model",
        "title": title,
        "summary": data["concept"],
        "pages": lesson_pages(
            [
                {
                    "id": "model",
                    "title": "The model",
                    "type": "concept",
                    "content": [
                        _paragraph(data["concept"]),
                        _bullets("Key truths", data["model"]),
                    ],
                },
                {
                    "id": "relationships",
                    "title": "How the parts relate",
                    "type": "overview",
                    "content": [
                        _diagram(
                            kind="flow",
                            title="Observe, decide, execute, verify",
                            caption="Advanced Git work is safest when inspection and verification surround every mutation.",
                            nodes=[
                                {"id": "observe", "label": "Observe", "accent": "muted"},
                                {"id": "decide", "label": "Choose semantics", "accent": "cyan"},
                                {"id": "execute", "label": "Execute", "accent": "cyan"},
                                {
                                    "id": "verify",
                                    "label": "Verify graph and files",
                                    "accent": "muted",
                                },
                            ],
                            edges=[
                                {"from": "observe", "to": "decide", "label": "evidence"},
                                {"from": "decide", "to": "execute", "label": "intent"},
                                {"from": "execute", "to": "verify", "label": "result"},
                            ],
                        ),
                        _callout(
                            "Professional habit",
                            "Explain the expected ref, index, working-tree, and object changes before running the mutating command.",
                        ),
                    ],
                },
            ]
        ),
    }


def _workflow_lesson(module: str, data: dict) -> dict:
    return {
        "module": module,
        "slug": "workflow-and-safety",
        "title": "Workflow and Safety",
        "summary": "A repeatable operating procedure and the failure mode to guard against.",
        "pages": lesson_pages(
            [
                {
                    "id": "workflow",
                    "title": "Operating procedure",
                    "type": "practice-notes",
                    "content": [
                        _bullets("Use this sequence", data["workflow"]),
                        _callout(
                            "Verification gate",
                            "Do not count the task complete until status, graph, refs, and relevant file content agree with the intended outcome.",
                        ),
                    ],
                },
                {
                    "id": "safety",
                    "title": "Safety boundary",
                    "type": "warning",
                    "content": [
                        _warning(data["risk"]),
                        _paragraph(
                            "When the risk is uncertain, create a temporary branch or tag, fetch current remote state, and inspect the reflog before proceeding."
                        ),
                    ],
                },
            ]
        ),
    }


def _decision_lab_lesson(module: str, data: dict) -> dict:
    return {
        "module": module,
        "slug": "decision-lab",
        "title": "Decision Lab",
        "summary": (
            "Rehearse the evidence, command semantics, and verification steps needed to "
            "solve this chapter's workflows without relying on memorized command sequences."
        ),
        "pages": lesson_pages(
            [
                {
                    "id": "rehearsal",
                    "title": "Reason before typing",
                    "type": "scenario",
                    "content": [
                        _paragraph(
                            "Treat each task as a state-transition problem. Describe the current graph, "
                            "refs, index, and working tree; name the state that must change; then choose "
                            "the narrowest command whose documented semantics produce that change."
                        ),
                        _bullets(
                            "Questions to answer",
                            [
                                "What evidence in status, history, refs, or object data proves the starting state?",
                                "Which repository layer should change, and which layers must remain untouched?",
                                "Is the operation local and unpublished, shared and published, or purely diagnostic?",
                                "What recovery reference, dry run, or abort path is available before execution?",
                            ],
                        ),
                        _callout(
                            "Explain the transition",
                            data["concept"],
                        ),
                    ],
                },
                {
                    "id": "proof",
                    "title": "Prove the result",
                    "type": "practice-notes",
                    "content": [
                        _bullets(
                            "Verification evidence",
                            [
                                *data["model"],
                                "The final status, graph, refs, and relevant file content match the stated goal.",
                            ],
                        ),
                        _bullets("Repeatable field procedure", data["workflow"]),
                        _warning(data["risk"]),
                    ],
                },
            ]
        ),
    }


ADVANCED_LESSONS = [
    lesson
    for module, data in CHAPTER_LESSON_BLUEPRINTS.items()
    for lesson in (
        _concept_lesson(module, data),
        _workflow_lesson(module, data),
        _decision_lab_lesson(module, data),
    )
]
