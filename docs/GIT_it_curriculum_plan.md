# GIT it! Starter Curriculum Plan

This plan defines the current-release static starter syllabus seeded by the backend. It stays inside the student-facing MVP: Units, Lesson Overview pages, scenario skill focuses, difficulty instances, retry variants, and command-count policies. It does not introduce administrator authoring, AI assistance, chatbot support, or external Git hosting.

## Unit 1: Orientation

Unit 1 is a no-terminal, concept-only Orientation Completion Gate. Its eight lessons are derived from the SRS and Proposal requirements for foundational Git concepts, command structure and anatomy, DAG literacy, platform conventions, and the documented examples in UC-ORI-02.

1. The Three File Areas: working tree, staging area, repository
2. Tracked vs. Untracked Files
3. What HEAD Is
4. Commits, Parents, and DAG Literacy
5. Branches as Movable Pointers
6. Git Command Anatomy
7. GIT it! Practice Rules and No-Answer Policy
8. Difficulty, Scaffolding, Retry, and Review Mode

## Unit 2: Repository State Foundations

Goal: teach students to inspect repository state before acting and to connect working-tree/staging changes to commits.

- Reading Git Status
- First Commits and Staging Decisions
- Inspecting History Without Changing State

Scenario skill focuses:
- Create a first clean commit
- Stage selected changes

## Unit 3: Branching and Navigation

Goal: build the mental model that branches are pointers, HEAD marks the current position, and moving work safely depends on pointer/state reasoning.

- Branch Pointers and HEAD
- Detached HEAD and Safe Navigation
- Moving Work to the Right Branch

Scenario skill focuses:
- Move a commit made on the wrong branch

## Unit 4: Collaboration and Integration

Goal: prepare students for realistic team repository states: divergence, merges, conflicts, and cleanup without discarding teammate work.

- Divergent Branches
- Merge Conflict State
- Branch Cleanup After Integration

Scenario skill focuses:
- Resolve divergent branches after team edits
- Finish a merge after conflict markers appear
- Clean up a merged feature branch

## Unit 5: Undo and Recovery

Goal: address avoidance behaviors from the proposal: deleting folders, re-cloning, abandoning repositories, or blindly running AI-suggested commands.

- Undo Without Panic
- Recovering After Pointer Movement
- Choosing a Safe Recovery Path

Scenario skill focuses:
- Recover after an accidental local reset

## Current-Release Boundaries

- All practice uses the backend Repository State Simulator.
- No student command is executed by a shell or real Git CLI.
- No GitHub, GitLab, Bitbucket, or external remote is connected.
- Expected-state diagrams appear only on Easy and Medium.
- Contextual feedback appears only on Easy.
- Review Mode is playable and logged separately from primary KPI records.
