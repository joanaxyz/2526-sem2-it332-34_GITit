"""Cross-stack Git command forms verified outside an authored level.

Most capability keys are discovered from existing adventure levels.  This small
explicit set covers advanced diagnostic forms whose deterministic frontend
execution and backend read-only classification are regression-tested even before
they are assembled into full battle scenarios.
"""

ENGINE_SUPPORTED_REFERENCE_FORMS = frozenset(
    {
        "git-shortlog/summary",
        "git-shortlog/numbered",
        "git-rev-parse/revision",
        "git-rev-parse/toplevel",
        "git-blame/path",
        "git-grep/pattern",
        "git-describe/tags",
        "git-range-diff/series",
        "git-merge-tree/branches",
        "git-verify-commit/commit",
        "git-verify-tag/tag",
        "git-fsck/full",
        "git-count-objects/verbose-human",
        "git-cat-file/pretty",
        "git-cat-file/type",
        "git-ls-tree/tree",
        "git-show-ref/all",
        "git-for-each-ref/all",
        "git-symbolic-ref/head",
    }
)
