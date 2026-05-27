# GIT it!

GIT it! is a web-based, scenario-driven Git learning platform. It trains practical Git problem-solving through a simulated terminal, live repository visualization, and state-based evaluation inside a consequence-safe environment.

This repository contains the current implementation split into:
- `frontend/` - React + Vite single-page application
- `backend/` - Django + Django REST Framework API, simulator, evaluator, and persistence

## Why This System Exists

Based on project documents and local study context, the platform addresses recurring beginner failure patterns in Git learning (command memorization, destructive conflict handling, and low repository-state reasoning). The core design focus is:
- scenario practice over command memorization
- repository-state outcomes over exact command-string matching
- fading scaffolding from guided to independent execution
- transfer-oriented retries through structurally changed variants

## Core Learning Model

The student flow is:
1. Access orientation lessons (Unit 1) for foundational concepts and platform walkthrough.
2. Expand a learning unit and open a `Scenario Skill Focus`.
3. Choose a difficulty action (`Start`, `Continue`, `Retry`, or `Review`) and pass through `Skill Focus Preview`.
4. Enter the practice workspace with:
   - terminal-style command input
   - live animated DAG
   - difficulty-specific supports
5. Submit Git commands to the backend simulator.
6. Have the evaluator check whether resulting repository state matches target state.
7. Complete, retry, or review based on outcomes.

### Difficulty and Scaffolding

- `Easy` - Live DAG + expected-state diagram + contextual feedback panel
- `Medium` - Live DAG + expected-state diagram
- `Hard` - Live DAG + narrative only

Difficulty progression is per scenario skill focus: Easy -> Medium -> Hard unlock chain.

## Architecture Overview

### Frontend (`frontend/`)

- React + Vite SPA
- Terminal interaction, scenario workspace, dashboard, unit/skill focus cards
- Live DAG visualization using graph tooling (`reactflow`, `dagre`)
- State and data fetching via modern React tooling (`@tanstack/react-query`, form and schema validation libs)

### Backend (`backend/`)

- Django + DRF API
- Auth/session endpoints and protected learning endpoints
- Repository state simulator and command adapter
- State-based evaluator for completion logic
- Session and step logging for KPI computation

### Data and Supporting Services

- Persistent store: PostgreSQL-compatible backend (Supabase-compatible deployment model in docs)
- Cache/session acceleration: Redis-compatible cache
- JWT-based auth with refresh flow

## Simulator and Evaluator Design (Critical System Behavior)

Per ADR 0001 and requirements:
- production command execution is fully simulated (not shelling out to Git binaries)
- student input is parsed, normalized, mapped to safe intents, then applied to simulated repository state
- unsupported or unsafe patterns are rejected with neutral terminal-style responses
- evaluator checks state equivalence to authored targets instead of fixed command text
- diagnostic/read-only commands are tracked separately from counted action commands

This keeps behavior deterministic, safe, and curriculum-aligned while still supporting multiple valid solution paths.

## No-Answer Policy

The system is designed to never reveal exact solution commands or command sequences in student-facing surfaces. Supports (DAG, expected-state view, easy feedback text) are educational scaffolds, not answer reveal mechanisms.

## Functional Scope by Module

Current release centers on student-facing modules:
- Module 0 - system access prerequisites (registration/login/session)
- Module 1 - orientation and conceptual readiness
- Module 2 - scenario practice and state-based evaluation
- Module 3 - repository visualization and fading scaffolding
- Module 4 - adaptive retry and transfer practice
- Module 5 - progress tracking and self-monitoring

Planned Phase 2 modules:
- Module 6 - administrative management
- Module 7 - AI-assisted learning support

## Metrics and Evaluation Model

The system computes progress from logs (not command quizzes), including:
- `SCR` - Scenario Completion Rate
- `ARC` - Average Retry Count
- `CAR` - Command Accuracy Rate (counted commands vs authored threshold)
- `HLCR` - Hard-Level Completion Rate
- `RTA` - Retry Transfer Accuracy (changed-variant retries)

## Local Development Setup

## Prerequisites

- Python 3.10+ (recommended)
- Node.js 20+ and npm
- PostgreSQL (or compatible DSN)
- Redis (or compatible cache endpoint)

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Test Commands

Frontend:
```bash
cd frontend
npm run test
```

Backend (example):
```bash
cd backend
python manage.py test
```

These documents are the authoritative source for detailed requirements, research framing, and module-level behavior.
