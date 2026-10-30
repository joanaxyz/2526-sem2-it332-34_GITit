"""Reviewed, scenario-independent material. Providers may select IDs, never write replies.

Only committed command-reference metadata and the concept glossary enter this
catalog. Runtime LibraryEntry/guide payloads are deliberately not trusted sources.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from functools import cache

from curriculum.seed_data.command_catalog import COMMAND_CATALOG
from tutoring.services.anatomy import anatomy
from tutoring.services.concepts import CONCEPTS

_OVERVIEWS = {
    "checkout": "Checkout can switch branches or restore selected file content, depending on its options. Branch operations and file operations affect different parts of the repository. Read the particular form before using it.",
    "diff": "Diff compares two versions of content and displays their differences. Its options determine which versions are compared and how the differences are presented; reading a diff does not change the repository.",
}
_DEEPER = {
    "repository": "A repository has both the files you edit and Git's recorded history. Creating repository metadata does not itself save your files as a commit. Think separately about preparing a place for history and recording a snapshot.",
    "working-tree": "Editing a file changes the working tree. The staging area can still hold an earlier version of that same file. This is why a file can have both staged and unstaged changes at the same time.",
    "staging-area": "The staging area lets you decide what belongs together in one snapshot. Later edits to a file do not automatically replace its staged version. A commit records the staged content, which can differ from the files you are currently editing.",
    "commit": "A commit records a tree of file content, a message, and links to earlier commits. Editing your working files afterward does not change that saved snapshot. Recording history and uploading history to another repository are separate ideas.",
    "branch": "A branch is a movable pointer, not a separate copy of every file. Creating a branch and switching to it are distinct actions. Which pointer moves when you commit depends on where HEAD is attached.",
    "head": "When HEAD is attached to a branch, a new commit advances that branch. A detached HEAD points directly at a commit instead. Looking at a commit and moving a branch pointer are different operations.",
    "remote": "A remote is a named connection to another repository. Local branches, remote-tracking branches, and the branches on the server are distinct pointers. A locally remembered remote state can become out of date when someone else pushes.",
    "conflict": "A conflict asks you to decide what the combined content should be. It is not solved simply by choosing a command name. Inspect the affected content and understand both changes before deciding what to keep.",
}

PLACEHOLDERS = (
    "Words in angle brackets are placeholders, not text to copy. Replace each with "
    "a value you determine from your task. A branch name and a folder path are "
    "different inputs; Git does not infer one from the other."
)
NEUTRAL = (
    "I can help you understand the ideas without choosing the solution. Separate "
    "what a task wants to change from the values it supplies. Git concepts and "
    "placeholder meanings can help you reason about those differences. "
    "Choose a topic below, or ask what a specific command or option means."
)
_SLOT = re.compile(r"<[^<>]+>")
_FLAG = re.compile(r"^--?[a-zA-Z][a-zA-Z-]*")
_SUBCOMMANDS = frozenset(
    {"stash", "remote", "worktree", "submodule", "bisect", "sparse-checkout", "reflog", "rerere"}
)
_CONFIG_KEYS = frozenset(
    {
        "user.name",
        "user.email",
        "core.editor",
        "core.autocrlf",
        "rerere.enabled",
        "merge.conflictStyle",
        "safe.directory",
        "alias.<name>",
    }
)
_TECHNIQUE_OPERANDS = frozenset(
    {
        "HEAD~<n>",
        "HEAD^<n>",
        "<from>..<to>",
        "'<pattern>'",
        "<remote>/<branch>",
        "@{upstream}",
        "git@<host>:<path>.git",
    }
)


@cache
def _grammar():
    """Only reviewed grammar may survive projection, never arbitrary form literals."""
    families, slots, flags, subcommands = set(), set(), {}, {}
    for command in COMMAND_CATALOG:
        family = command["base_command"].removeprefix("git ")
        families.add(family)
        for form in command["usages"]:
            usage = form["usage_form"]
            slots.update(_SLOT.findall(usage))
            tokens = usage.split()
            for token in tokens[2:]:
                match = _FLAG.match(token)
                if match:
                    flags.setdefault(family, set()).add(match[0])
            if family in _SUBCOMMANDS and len(tokens) > 2 and tokens[2].isalpha():
                subcommands.setdefault(family, set()).add(tokens[2])
    return families, slots, flags, subcommands


def _safe_operand(token, slots):
    if token in _TECHNIQUE_OPERANDS:
        return token
    found = _SLOT.findall(token)
    # Preserve canonical slots and ref/range punctuation, with no literal prefix
    # or suffix. A name embedded in <...> is not automatically trusted.
    if (
        found
        and all(slot in slots for slot in found)
        and re.fullmatch(r"[/.:^~@{}-]*", _SLOT.sub("", token))
    ):
        return token
    return "<value>"


def safe_usage(usage: str) -> str:
    """Keep syntax, replacing every non-syntax operand with a generic slot."""
    parts = re.findall(r'\[[^\]]+\]|"[^"]*"|\S+', str(usage))
    if len(parts) < 2 or parts[0] != "git":
        return "git <command> <value>"
    families, slots, flags, subcommands = _grammar()
    family = parts[1]
    if family not in families:
        return "git <command> <value>"
    result = parts[:2]
    config_key_seen = False
    after_separator = False
    for index, token in enumerate(parts[2:], start=2):
        optional = token.startswith("[") and token.endswith("]")
        bare = token[1:-1] if optional else token
        if after_separator:
            clean = _safe_operand(bare, slots)
        elif bare == "--":
            clean = bare
            after_separator = True
        elif index == 2 and bare in subcommands.get(family, ()):
            clean = bare
        elif family == "config" and not bare.startswith("-") and not config_key_seen:
            config_key_seen = True
            clean = bare if bare in _CONFIG_KEYS else _safe_operand(bare, slots)
        elif bare.startswith("-"):
            match = _FLAG.match(bare)
            flag = match[0] if match else ""
            if flag not in flags.get(family, ()):
                clean = "<value>"
            else:
                suffix = bare[len(flag) :]
                clean = flag
                if suffix:
                    clean += ("=" if suffix.startswith("=") else "") + _safe_operand(
                        suffix.removeprefix("="), slots
                    )
        else:
            clean = _safe_operand(bare, slots)
        result.append(f"[{clean}]" if optional else clean)
    return " ".join(result)


@dataclass(frozen=True)
class TeachingBlock:
    id: str
    title: str
    text: str
    family: str = ""
    usage: str = ""

    def source(self):
        return {"id": self.id, "title": self.title}


@cache
def catalog() -> dict[str, TeachingBlock]:
    blocks = {
        f"concept:{key}": TeachingBlock(f"concept:{key}", title, text)
        for key, (title, text) in CONCEPTS.items()
    }
    blocks["concept:placeholders"] = TeachingBlock(
        "concept:placeholders", "Reading placeholders", PLACEHOLDERS
    )
    blocks["concept:reasoning"] = TeachingBlock("concept:reasoning", "Reading a task", NEUTRAL)
    for key, text in _DEEPER.items():
        block_id = f"detail:{key}"
        blocks[block_id] = TeachingBlock(block_id, f"{CONCEPTS[key][0]} explained further", text)
    for command in COMMAND_CATALOG:
        family = command["base_command"].removeprefix("git ")
        block_id = f"command:{family}"
        blocks.setdefault(
            block_id,
            TeachingBlock(
                block_id,
                command["base_command"],
                _OVERVIEWS.get(family, command["summary"]),
                family=family,
            ),
        )
        for form in command["usages"]:
            usage = safe_usage(form["usage_form"])
            key = f"syntax:{hashlib.sha256(usage.encode()).hexdigest()[:16]}"
            explanation = "\n".join(f"{part['token']}: {part['text']}" for part in anatomy(usage))
            blocks[key] = TeachingBlock(
                key,
                usage,
                f"Syntax: {usage}\n\n{explanation}",
                family=family,
                usage=usage,
            )
    return blocks


def guide_key(key: str) -> str:
    """Literal-bearing internal identities must not leak through metadata/tokens."""
    if key.startswith("form:") and key[5:] != safe_usage(key[5:]):
        return f"guide:{hashlib.sha256(key.encode()).hexdigest()}"
    return key


def option_blocks(family, requested):
    known = {
        flag
        for block in catalog().values()
        if block.family == family and block.usage
        for flag in re.findall(r"(?<!\w)--?[a-zA-Z][a-zA-Z-]*", block.usage)
    }
    result = []
    for flag in sorted(known & requested):
        meaning = anatomy(f"git {family} {flag}")[-1]["text"]
        key = f"option:{family}:{flag}"
        result.append(TeachingBlock(key, f"git {family} {flag}", f"{flag}: {meaning}.", family))
    return result


def form_blocks(usage: str) -> list[TeachingBlock]:
    """An open, validated guide may also explain a generated technique form."""
    usage = safe_usage(usage)
    family = usage.split()[1]
    overview = catalog().get(f"command:{family}")
    if overview is None:
        return []
    key = f"syntax:{hashlib.sha256(usage.encode()).hexdigest()[:16]}"
    block = catalog().get(key)
    if block is None:
        details = "\n".join(f"{part['token']}: {part['text']}" for part in anatomy(usage))
        block = TeachingBlock(key, usage, f"Syntax: {usage}\n\n{details}", family, usage)
    return [overview, block, catalog()["concept:placeholders"]]


TOPICS = ("repository", "working-tree", "staging-area", "commit", "branch", "head", "placeholders")


def topic_choices():
    return [catalog()[f"concept:{key}"].source() for key in TOPICS]
