# CEBU INSTITUTE OF TECHNOLOGY – UNIVERSITY
## COLLEGE OF COMPUTER STUDIES

---

# Software Requirements Specifications
# for
# GIT it!

**Team Code:** 2526-sem2-it332-34

**Team Members:**
- Cañete, Rod Gabrielle M.
- Gako, Joana Carla D.
- Leonardo, Natasha Kate A.
- Riconalla, Frances Anne B.
- Vallo, Bianca Margarette G.

---

## Change History

| Version | Date | Author | Description of Change |
|---------|------|--------|-----------------------|
| 1.0 | May 11, 2026 | Team 2526-sem2-it332-34 | Initial SRS draft. |
| 1.1 | May 13, 2026 | Team 2526-sem2-it332-34 | Revised the current-release functional requirements for access, orientation, scenario practice, repository visualization, adaptive retry behavior, progress tracking, and planned Phase 2 placeholders. |
| 1.2 | May 15, 2026 | Team 2526-sem2-it332-34 | Refined state-based evaluation, simulator boundary rules, contextual feedback behavior, no-answer policy constraints, command logging, KPI definitions, and use case classification. |
| 2.0 | May 18, 2026 | Team 2526-sem2-it332-34 | Aligned the SRS with the five-objective proposal, revised student-facing content terminology from modules to units, updated Review Mode as playable re-attempt behavior, restored software interface requirements, and finalized objective-to-module traceability. |
| 2.1 | May 18, 2026 | Team 2526-sem2-it332-34 | Updated scenario difficulty and metric references to use Easy, Medium, and Hard levels only. |
| 2.2 | May 18, 2026 | Team 2526-sem2-it332-34 | Added targeted scenario-card state synchronization after scenario session state changes so returning students see updated completion and unlock states without reloading every scenario card. |

---

## Table of Contents

1. Introduction
   - 1.1 Purpose
   - 1.2 Scope
   - 1.3 Definitions, Acronyms and Abbreviations
   - 1.4 References
2. Overall Description
   - 2.1 Product Perspective
   - 2.2 User Characteristics
   - 2.4 Constraints
   - 2.5 Assumptions and Dependencies
3. Specific Requirements
   - 3.1 External Interface Requirements
     - 3.1.1 Hardware Interfaces
     - 3.1.2 Software Interfaces
     - 3.1.3 Communications Interfaces
   - 3.2 Functional Requirements
     - Module 0: System Access Prerequisites *(Supporting — no General Objective)*
     - Module 1: Orientation and Conceptual Readiness *(General Objective 1)*
     - Module 2: Scenario Practice and State-Based Evaluation *(General Objective 2)*
     - Module 3: Repository Visualization and Fading Scaffolding *(General Objective 3)*
     - Module 4: Adaptive Retry and Transfer Practice *(General Objective 4)*
     - Module 5: Progress Tracking and Self-Monitoring *(General Objective 5)*
     - Module 6: Administrative Management *(Planned Phase 2 / Next-Semester Scope)*
     - Module 7: AI-Assisted Learning Support *(Planned Phase 2 / Next-Semester Scope)*
   - 3.3 Objective-to-Module Traceability Matrix
   - 3.4 Non-Functional Requirements

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the complete functional and non-functional requirements for **GIT it!**, a web-based, scenario-driven learning platform designed to develop Git version control competency among third-year Bachelor of Science in Information Technology (BSIT) students at Cebu Institute of Technology – University (CIT-U). This document serves as the authoritative reference governing system scope, behavioral requirements, interface specifications, and design constraints throughout the development lifecycle. It is intended for use by the development team, the project adviser, and all project stakeholders as the basis for design decisions, implementation planning, scope validation, and system verification.

The requirements specified herein are informed by a documented competency gap among the target population. A preliminary survey of 35 third-year BSIT students at CIT-U revealed that 89% routinely paste Git errors into AI tools and execute the returned commands without comprehension, 71% resolve merge conflicts by discarding a teammate's work entirely, and 46% delete and re-clone the local repository when confronted with an unresolvable error state. GIT it! is designed to address these failure patterns through consequence-safe, scenario-driven practice with progressively fading instructional scaffolding — enabling students to develop transferable Git competency before these behaviors manifest in graded collaborative projects.

The system is self-paced and student-directed at the scenario-selection level. Students may choose any scenario skill focus without global unit prerequisites, cohort pacing, or quiz scores. Difficulty levels within each scenario follow a completion-based mastery progression: Easy is initially available, Medium unlocks after Easy completion for the same scenario, and Hard unlocks after Medium completion for the same scenario. The scenario engine's state-based evaluation is a practice feedback mechanism — not a quiz assessment — and all performance metrics are derived exclusively from system-generated logs without reliance on pre-test or post-test instruments.

### 1.2 Scope

GIT it! is a self-directed, web-based Git learning platform delivered as a browser-accessible web application. The system is built on a client-server architecture with a strict separation between a browser-based frontend client and a backend application API.

**In Scope**

The platform serves third-year BSIT students at CIT-U enrolled in team-based development courses, including Information Management 2 and Applications Development. The current release uses a static, pre-authored Git starter syllabus seeded before deployment, while syllabus and content configuration is reserved for the planned Phase 2 Administrative Management module. The starter content library comprises Unit 1 Orientation lessons with non-scorable interactive concept walkthroughs, published learning units, lesson pages, scenario skill focuses, difficulty instances, authored command-count policies, and difficulty-owned RTA-eligible retry variants. A Lesson is a single scrollable instructional page within a learning unit; it may contain explanations, examples, callouts, command snippets, diagrams, or DAG illustrations as needed, but it is not constrained to a fixed static template. The exact scenario count, learning-unit names, difficulty-instance coverage, and variant library size are finalized as implementation content before deployment rather than fixed as permanent SRS commitments, allowing the team to adjust content coverage before pilot release if syllabus needs change. Students can access the seeded content but cannot create or modify it in the current release.

The student-facing interface includes the following core components: registration and login screens, Student Dashboard, Dashboard/Units tab, Learning Unit list, expandable unit cards, Unit 1 Orientation interface, reference Lesson pages, Scenario Skill Focus cards, Easy/Medium/Hard Difficulty Action buttons, Skill Focus Preview modal, demo-only Live DAG panel, demo command input, demo explanation panel, Scenario Practice Workspace, terminal-style command input, Live DAG panel, Expected-State Diagram panel, Contextual Feedback panel, playable Review Mode, and student-facing progress/KPI indicators. Scenario selection begins from an expanded learning-unit card, where the student sees Scenario Skill Focus cards directly under the unit instead of opening a long scenario-bearing Lesson page first. Administrative Management, AI-assisted authoring, and administrator-facing content editing interfaces are planned Phase 2 / next-semester modules, not current-release requirements.

The system incorporates a light gamification layer — including a streak counter, first-attempt star indicators, and retry-count trend displays — to support sustained engagement. User authentication is handled via manual student ID, CIT email, and password registration with student ID/email login and JWT-based session management. The system is accessible via modern web browser on desktop, tablet, and mobile form factors. No native mobile application is in scope.

**Out of Scope**

The system does not execute external Git command-line binaries, connect to any external Git hosting service (e.g., GitHub, GitLab, Bitbucket), or interact with live remote repositories. Repository states are handled internally by the backend Repository State Simulator inside isolated server-side sessions. Institutional LMS integration, multi-institution deployment, CI/CD integrations, offline mode, social or collaborative features between students, and native mobile applications are explicitly excluded from the current release. Generalizability of evaluation findings beyond the CIT-U third-year BSIT population is not claimed.

**Planned Phase 2 / Next-Semester Scope**

The current semester deliverable focuses on the student-facing scenario practice platform using static, pre-authored content. Administrative Management and AI-Assisted Learning Support are documented as planned Phase 2 modules for next-semester implementation. They are excluded from the current-release MVP evaluation and KPI computation, but are specified in Section 3.2 to preserve architectural continuity, traceability, and future development direction.

The planned Administrative Management module (Module 6) is intended for the authorized platform administrator. It consolidates non-student capabilities into one area: viewing cohort-level and student-level KPI summaries derived from system logs, managing student accounts and access, creating and maintaining learning content units, maintaining Lesson HTML/CSS content, adding or editing scenario skill focus records, managing difficulty-owned variants, and reviewing administrative audit logs. The current release still logs the data needed to compute the required student and cohort KPIs, while the administrative interface for viewing or maintaining those records is introduced only through Phase 2.

The planned AI-Assisted Learning Support module (Module 7) includes a conceptual Git chatbot, an AI-assisted Lesson HTML/CSS drafting workflow, and an AI-assisted scenario-drafting workflow. AI-generated content requires administrator review, validation, and publication before becoming student-accessible.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term / Acronym | Definition |
|---|---|
| API | Application Programming Interface |
| BSIT | Bachelor of Science in Information Technology |
| CIT-U | Cebu Institute of Technology – University |
| CLI | Command Line Interface |
| DAG | Directed Acyclic Graph — the data structure Git uses internally to represent commit history, where nodes are commits and edges point to parent commits |
| Live Animated DAG | The real-time, animated commit graph rendered on the GIT it! interface; updates after every simulator-processed command at all difficulty levels to reflect the learner's current repository state |
| Lesson | A single scrollable instructional page within a learning unit. Stored and displayed as administrator-approved or pre-authored HTML with scoped CSS. Unit 1 uses standalone orientation lessons; scenario-bearing units may retain reference lesson content, but lessons are no longer the main access path for scenario selection. |
| Scenario Skill Focus List | The unit-level list of public Scenario Skill Focus cards displayed directly inside an expanded learning-unit card. Each card shows the skill focus title, summary, focus command/s, and Easy/Medium/Hard action states. |
| Unit Card Expansion | The Dashboard/Units tab interaction where a student expands a learning unit card. Unit 1 displays orientation lessons; scenario-bearing units display Scenario Skill Focus cards directly, with optional reference lessons shown separately. |
| Skill Focus Preview | A pre-practice modal that presents public command/skill explanation, focus command/s, demo-only DAG/repository visualization, safe demo command input, and demo text explanation before Start, Continue, Review, or Retry enters the actual Scenario Practice Workspace. It must not expose actual scenario narrative, repository state, branch names, file names, target-state rules, exact solution sequence, evaluator rules, or hidden solution notes. |
| Expected-State Diagram | A static diagram showing the target repository state the student must reach to complete the current scenario step; visible on Easy and Medium levels only |
| Contextual Feedback Panel | An Easy-level interface component that displays a brief text summary of the repository-state consequence produced by the student's own command after it is processed by the Repository State Simulator, without judging the command, suggesting the next command, or revealing the correct command sequence |
| Fading Scaffolding | The progressive removal of instructional support across difficulty levels: Easy (full support), Medium (partial), Hard (minimal — live DAG and narrative only) |
| Scenario | A self-contained Git problem-solving exercise presented with a professional narrative context, a starting repository state, and one or more required resolution steps |
| Scenario Skill Focus | The public Git skill, command, concept, or workflow being practiced. Stores the short instructional explanation, skill focus type, primary focus command/s, optional supporting inspection commands, safe demo commands, demo repository/DAG state, demo explanation content, related concepts, and linked Easy/Medium/Hard difficulty instances. It does not store actual scenario-solving data. |
| Scenario Instance | One specific loaded attempt of a scenario difficulty instance, including the selected difficulty-level configuration, selected variant, active repository state, and session logs |
| Difficulty Instance | The configured playable Easy, Medium, or Hard level under a scenario skill focus. Each difficulty instance owns its own narrative/task prompt, initial repository-state definition, target-state rule, command-count policy, scaffolding configuration, expected-state diagram behavior, and variant pool |
| Scenario Variant | A structurally distinct template-based variation owned by one difficulty instance, differing in branch names, commit structures, file-state markers, starting repository state, file/context details, or target-state details while preserving the same Git skill focus |
| Repository State Simulator | The backend component that maintains and updates isolated simulated repository sessions in response to student-typed commands. Shall not execute external Git command-line binaries or shell commands from student input. |
| State-Based Evaluator | The evaluation engine that compares the student's resulting repository state against the expected target state; accepts any valid command or sequence that produces the correct outcome |
| HEAD | A special Git pointer that refers to the currently checked-out commit or branch tip |
| Detached HEAD | A repository state where HEAD points directly to a commit instead of a branch reference |
| JWT | JSON Web Token — a compact, stateless token format used for authentication |
| REST | Representational State Transfer — the architectural style used for backend API design |
| SRS | Software Requirements Specification |
| SUS | System Usability Scale — a standardized ten-item usability questionnaire; target score ≥ 70 |
| TAM | Technology Acceptance Model — used to measure Perceived Usefulness (PU ≥ 4.0), Perceived Ease of Use (PEOU ≥ 3.5), and Behavioral Intention to Use (BI ≥ 4.0) |
| OLCR | Orientation Lesson Completion Rate — proportion of available Unit 1 orientation lesson records marked complete by registered students during the evaluation period |
| SCR | Scenario Completion Rate — proportion of started scenario sessions that reach the correct final repository state |
| ARC | Average Retry Count — number of retry attempts before successful scenario completion |
| CAR | Command Accuracy Rate — proportion of latest completed primary difficulty-level attempts finished at or below the authored minimum counted-command threshold for that level |
| Command-Count Policy | The authored configuration attached to a scenario difficulty instance that defines the minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns for that instance |
| Counted Action Command | A simulator-processed command that changes, or is intended to change, the repository state and is included in CAR and remaining counted-command calculations |
| Non-Counted Diagnostic Command | A simulator-processed read-only inspection command that is logged but excluded from CAR and remaining counted-command calculations according to the authored command-count policy |
| Maximum Counted-Command Limit | The authored upper limit for counted action commands allowed in a scenario session before the session is marked Failed |
| HLCR | Hard-Level Completion Rate — proportion of started Hard-level sessions that reach the correct final repository state |
| RTA | Retry Transfer Accuracy — first-attempt completion rate on structurally changed retry variants served from the same difficulty instance's variant pool after a prior Failed or Abandoned scenario session for the same scenario skill focus and difficulty level; first-ever encounters are excluded |
| SAR | Scenario Abandonment Rate — proportion of started sessions that are abandoned mid-session |
| No-Answer Policy | The system-wide, absolute, non-overridable constraint that the correct command and correct command sequence are never revealed to the student at any point during or after a scenario session. Expected-state diagrams may show the repository goal state only on the difficulty levels where that scaffold is explicitly required. |
| Streak Counter | A gamification element tracking consecutive days of scenario practice, displayed on the student dashboard |
| Non-Target-Matching Submission | A simulator-processed command submission whose resulting repository state does not satisfy the current scenario-step target. An evaluation result for the current step, not a judgment that the command itself is inherently wrong. |
| Failed Scenario Attempt | A scenario session outcome assigned only when a started scenario attempt ends without reaching all required target states because the student explicitly chooses Retry/Restart/Give Up before completion, the configured command/attempt limit is reached, or the session enters a scenario-defined unrecoverable state. A TargetNotYetMatched command result by itself does not make the scenario attempt failed. |
| First-Attempt Star | A badge awarded when a student completes a scenario instance without any non-target-matching, unprocessable, or invalid command submission during the entire session |
| Review Mode | A playable re-attempt mode available after a student completes a scenario difficulty instance. It starts a new Review Mode practice session for the completed scenario difficulty, provides the live terminal, live DAG, and difficulty-appropriate scaffolding, logs the attempt separately for Review Mode SCR, and does not reveal correct commands or command sequences. |

### 1.4 References

| Ref | Document Title | Report No. / Standard No. | Date / Year | Publishing Organization | Source / Availability |
|-----|----------------|--------------------------|-------------|------------------------|-----------------------|
| [1] | IEEE Recommended Practice for Software Requirements Specifications | IEEE Std 830-1998 | 1998 | IEEE Computer Society | IEEE Standards |
| [2] | GIT it! Approved Capstone Proposal | Not applicable | 2026 | Team 2526-sem2-it332-34, CIT-U | Internal project document |
| [3] | Capstone Proposal Evaluation: Observations and Recommendations | IT332, G1–G7, SEM2 2025–2026 | 2026 | CIT-U, College of Computer Studies | Course-provided instruction document |
| [4] | Data Privacy Act of 2012 | Republic Act No. 10173 | 2012 | Republic of the Philippines | Official Gazette / National Privacy Commission |
| [5] | JSON Web Token (JWT) | RFC 7519 | 2015 | IETF | IETF RFC Editor |
| [6] | Transport Layer Security (TLS) Protocol Version 1.2 | RFC 5246 | 2008 | IETF | IETF RFC Editor |
| [7] | React Documentation | Not applicable | Online | Meta Open Source / React Team | React official documentation |
| [8] | Django Documentation | Not applicable | Online | Django Software Foundation | Django official documentation |
| [26] | Django REST Framework Documentation | Not applicable | Online | Encode OSS Ltd. | Django REST Framework official documentation |
| [27] | PostgreSQL Documentation | Not applicable | Online | PostgreSQL Global Development Group | PostgreSQL official documentation |
| [28] | Supabase Documentation | Not applicable | Online | Supabase Inc. | Supabase official documentation |
| [29] | Redis Documentation | Not applicable | Online | Redis Ltd. / Redis Open Source Project | Redis official documentation |
| [30] | pygit2 Documentation | Not applicable | Online | pygit2 Project | pygit2 official documentation |
| [31] | libgit2 Documentation | Not applicable | Online | libgit2 Project | libgit2 official documentation |
| [9] | Cognitive Load During Problem Solving: Effects on Learning | Not applicable | 1988 | Cognitive Science | Sweller, J. |
| [10] | Multimedia Learning, 2nd Edition | Not applicable | 2009 | Cambridge University Press | Mayer, R. E. |
| [11] | SUS: A Quick and Dirty Usability Scale | Not applicable | 1996 | Taylor & Francis | Brooke, J. |
| [12] | Perceived Usefulness, Perceived Ease of Use, and User Acceptance of IT | Not applicable | 1989 | MIS Quarterly | Davis, F. D. |
| [13] | Aligning Software Engineering Education with Industrial Needs: A Meta-Analysis | Not applicable | 2019 | IEEE Access | Garousi et al. |
| [14] | Closing the Gap Between Software Engineering Education and Industrial Needs | Not applicable | 2020 | IEEE Software | Garousi et al. |
| [15] | Analysis of Software Engineering Skills Gap in the Industry | Not applicable | 2022 | ACM Transactions on Computing Education | Akdur, D. |
| [16] | Challenges and Confusions in Learning Version Control with Git | Not applicable | 2014 | Springer | Isomöttönen & Cochez |
| [17] | A Behavioral Approach to Understanding the Git Experience | Not applicable | 2021 | HICSS | Milliken et al. |
| [18] | Simulation-Based Learning in Higher Education: A Meta-Analysis | Not applicable | 2020 | Review of Educational Research | Chernikova et al. |
| [19] | A Review of Generic Program Visualization Systems | Not applicable | 2013 | ACM Transactions on Computing Education | Sorva et al. |
| [20] | Effects of Feedback in a Computer-Based Learning Environment: A Meta-Analysis | Not applicable | 2015 | Review of Educational Research | Van der Kleij et al. |
| [21] | Towards Understanding the Effective Design of Automated Formative Feedback | Not applicable | 2022 | Computer Science Education | Hao et al. |
| [22] | A Systematic Literature Review of Automated Feedback Generation | Not applicable | 2019 | ACM Transactions on Computing Education | Keuning et al. |
| [23] | Online or Traditional Learning at the Near End of the Pandemic | Not applicable | 2023 | Sustainability | Illescas et al. |
| [24] | Teaching Tip: Rethinking How We Teach Git | Not applicable | 2024 | Journal of Information Systems Education | Wagner & Thurner |
| [25] | Cognitive Load Theory | Not applicable | 2011 | Springer | Sweller, Ayres & Kalyuga |

---

## 2. Overall Description

### 2.1 Product Perspective

GIT it! is a self-contained web-based Git learning platform that provides scenario-driven practice through a client-server architecture. Students access the system through a browser, read Unit 1 orientation lessons at their own pace, view learning-unit lessons, select scenario skill focuses, choose available difficulty levels, enter simulated Git commands, and observe repository-state changes through a live DAG visualization.

The system evaluates student progress by comparing the resulting repository state against expected scenario outcomes rather than by checking fixed command strings. It supports difficulty-based scaffolding, adaptive retry variants, playable Review Mode, progress tracking, and log-derived performance indicators. It stores student accounts, learning content records, scenario progress, completion records, session logs, and step logs needed for dashboard indicators and system-generated metrics.

The system does not connect to live external repositories, does not execute student input as operating-system shell commands, and does not invoke external Git command-line binaries from student input. Student personal data is limited to first name, last name, student ID, and CIT educational email address and is encrypted at rest and in transit in compliance with the Philippine Data Privacy Act of 2012 (RA 10173).

### 2.2 User Characteristics

| User Type | Role and Characteristics |
|-----------|--------------------------|
| Student (Primary) | Third-year BSIT students at CIT-U enrolled in team-based development courses. They have been introduced to Git in prior coursework but lack reliable proficiency under realistic collaborative conditions. Survey data shows that 89% rely on AI tools without understanding results, 71% discard a teammate's code during merge conflicts, and 46% delete and re-clone the repository to escape a conflict. Students interact with all current-release platform features: registration, dashboard, Unit 1 orientation lessons, lessons, terminal command input, live DAG, and scenario completion tracking. |
| Administrator (Planned Phase 2) | The authorized non-student platform operator for Administrative Management features. In the capstone deployment, this role represents the single platform administrator responsible for planned Phase 2 learning analytics review, student access maintenance, Lesson maintenance, scenario and variant management, and audit-log review. This role is out of scope for current-release completion. |
| Guest / Unregistered Visitor | Any user who reaches the landing page or login/registration screens. Limited to public-facing content and account creation. No access to learning content without registration. |

### 2.4 Constraints

| Constraint Category | Description |
|--------------------|-------------|
| Regulatory / Legal | The platform must comply with the Philippine Data Privacy Act of 2012 (RA 10173) for the collection, storage, and processing of student personal data. Data must be encrypted at rest and in transit. |
| Institutional Policy | The platform must comply with CIT-U's institutional data privacy and acceptable-use policies for systems used in academic settings. |
| Hardware | The platform targets standard classroom hardware: minimum 4 GB RAM, modern web browser (Chrome, Firefox, or Edge — latest two major versions), screen resolution ≥ 1280×720 pixels, stable internet connection ≥ 1 Mbps. No specialized hardware is required. |
| No External Git Execution | The system must not execute external Git command-line binaries, invoke shell commands from student input, or connect to external Git repositories. Repository states are handled internally by the Repository State Simulator inside isolated server-side sessions. |
| No Offline Mode | The platform requires an active internet connection. Offline access is not in scope. |
| Concurrent Users | The system must support at least 40 concurrent users without performance degradation during the evaluation period, with architectural headroom to 100 concurrent users. |
| Evaluation Period | The platform is scoped for a single academic semester pilot deployment with approximately 35 enrolled students. |
| No-Answer Policy | The system shall never reveal the correct command or correct command sequence to the student at any point during or after a scenario session, at any difficulty level, on any student-facing interface surface — including the Contextual Feedback Panel, completion screens, Review Mode, and all other student-facing components. Expected-state diagrams may show the repository goal state only on Easy and Medium levels as a difficulty-specific scaffold. This is an absolute, non-overridable design constraint. |
| Self-Paced with Difficulty Progression | The system is self-paced at the scenario-selection level: students may choose any scenario skill focus without global unit prerequisites, cohort pacing, or quiz scores. Difficulty levels within each scenario are completion-gated as part of the fading-scaffolding design: Easy is initially available, Medium unlocks after Easy completion for the same scenario, and Hard unlocks after Medium completion for the same scenario. The scenario engine's state-based evaluation is a practice feedback mechanism, not a quiz assessment. |

### 2.5 Assumptions and Dependencies

- The backend is deployable on any compatible server environment. The frontend is OS-agnostic (browser-based).
- The system depends on a running Persistent Data Store instance. If the database is unavailable, all data persistence operations will fail and the system will not be operational.
- The system depends on a running in-memory cache. If the cache is unavailable, the system degrades gracefully: session metadata falls through to the database, but token revocation via blacklisting will be temporarily unavailable.
- Students must have internet access. The platform is not designed for offline use.
- The frontend requires JavaScript to be enabled in the browser. The platform is accessible via Chrome, Firefox, or Edge (latest two major versions).
- Students are assumed to have a valid CIT educational email address ending in @cit.edu and a unique student ID in NN-NNNN-NNN format for manual registration.
- The approved starter content library — including learning units, Lesson pages, scenario skill focuses, difficulty-level instances, authored command-count policies, and required difficulty-owned variant pools — is authored and seeded into the database prior to deployment. This syllabus/content set is static in the current release. The exact number, names, ordering, and syllabus coverage of learning units, scenario skill focuses, difficulty-level instances, and variants may be finalized before deployment and are not permanent SRS commitments.
- Unit 1 orientation content is authored and deployed as single scrollable, no-terminal instructional lesson pages before the evaluation period begins.
- Scenario selection is reachable from expanded learning-unit cards through unit-level Scenario Skill Focus cards. Scenario-bearing units no longer require students to open and scroll through a detailed Lesson page before choosing practice. Each Start, Continue, Review, or Retry action opens the Skill Focus Preview before the actual Scenario Practice Workspace.
- The Retry Transfer Accuracy (RTA) metric is computed only from RTA-eligible changed-variant retry sessions: sessions served from the same difficulty instance's variant pool after a prior Failed or Abandoned scenario session for the same scenario skill focus and difficulty level, where the new variant is structurally different from the prior attempt. A student's first-ever session for a given scenario skill focus and difficulty level is excluded from this metric.
- Platform usability and technology acceptance will be assessed post-deployment using the System Usability Scale (SUS, target ≥ 70) and a TAM-based survey (PU ≥ 4.0, PEOU ≥ 3.5, BI ≥ 4.0 on a 5-point Likert scale).

**Performance Metrics Definition**

| Metric | Type | What It Measures | Formula | Target | What the Result Means |
|--------|------|-----------------|---------|--------|-----------------------|
| Orientation Lesson Completion Rate (OLCR) | Primary | Whether students engage with the available Unit 1 orientation lessons | Completed Unit 1 orientation lesson records ÷ expected Unit 1 orientation lesson records for registered students × 100 | ≥80% lesson completion across the evaluation period | A higher rate means students are using the foundational Git orientation content, without making Unit 1 a prerequisite for scenario access |
| Scenario Completion Rate (SCR) | Primary | Whether students can eventually reach the correct final repository state for a scenario | Completed sessions ÷ Started sessions × 100 | ≥80% across the active published scenario library; also report per active learning unit when data is available | A higher percentage means students can resolve realistic Git repository problems, even if retries were needed |
| Average Retry Count (ARC) | Primary | How much retrying is needed before successful completion | Total retries ÷ Total completed sessions | ≤2 across the active published scenario library | A lower average means students need fewer retries before completion, indicating more efficient repository-state reasoning after practice |
| Command Accuracy Rate (CAR) | Primary | Whether students demonstrate difficulty-level command mastery by completing a scenario difficulty level within the authored minimum counted-command threshold for that level | Latest completed primary difficulty-level attempts finished at or below the authored minimum counted-command threshold ÷ Latest completed primary difficulty-level attempts × 100 | ≥60% across the active published scenario library | A higher percentage means students are completing scenarios using the expected efficient action-command path for that level. Non-counted diagnostic commands are logged but excluded from CAR. |
| Hard-Level Completion Rate (HLCR) | Primary | Whether students can resolve scenarios with minimal scaffolding support | Completed Hard sessions ÷ Started Hard sessions × 100 | ≥70% across active Hard-level sessions | A higher percentage means students can solve realistic Git problems with only the live DAG and narrative context |
| Retry Transfer Accuracy (RTA) | Primary | Whether students complete a structurally changed retry variant after a prior Failed or Abandoned scenario session | Successful first-attempt completions on RTA-eligible changed-variant retry sessions ÷ All RTA-eligible changed-variant retry sessions × 100 | ≥65% across RTA-eligible changed-variant retry sessions | A higher percentage means students applied the same Git concept to a changed repository topology instead of repeating a memorized command pattern |
| Scenario Abandonment Rate (SAR) | Secondary | Whether students disengage mid-session without completing or resuming | Abandoned sessions ÷ Started sessions × 100 | ≤20% across the active published scenario library; also report per active learning unit when data is available | A lower rate means professional narrative framing and dashboard continuity sustain student engagement |

---

## 3. Specific Requirements

### 3.1 External Interface Requirements

#### 3.1.1 Hardware Interfaces

GIT it! is a browser-based web application and does not interface with specialized hardware. The minimum client requirements are: a modern web browser (Chrome, Firefox, or Edge — latest two major versions), a screen resolution of ≥ 1280×720 pixels, and a stable internet connection of ≥ 1 Mbps. No peripheral devices beyond keyboard and pointing device are required. All key interface components — including the live DAG panel, terminal input, and expected-state diagram — must be visible without horizontal scrolling at the minimum supported resolution.

Recommended server hardware for the backend: ≥ 2 vCPUs, ≥ 4 GB RAM, ≥ 20 GB SSD storage. The server environment shall provide sufficient compute, memory, and storage resources for the expected evaluation-period workload.

#### 3.1.2 Software Interfaces

| Interface | Description |
|-----------|-------------|
| Frontend SPA (React.js / Vite) | Browser-based student interface for registration, login, dashboard, Units view, reference Lesson pages, unit-level Scenario Skill Focus cards, Skill Focus Preview modal, Scenario Practice Workspace, terminal input, live DAG visualization, expected-state diagram, contextual feedback panel, playable Review Mode, and progress indicators. Communicates with the backend exclusively through RESTful HTTPS endpoints using JSON payloads. |
| Backend REST API (Django / Django REST Framework) | Server-side application interface responsible for authentication, scenario delivery, command processing, repository-state simulation coordination, state-based evaluation, session logging, progress tracking, and dashboard metric retrieval. Exposes RESTful JSON endpoints consumed by the frontend SPA. |
| Supabase (PostgreSQL) | Managed relational database for persistent storage of user accounts, unit and lesson records, scenario skill focus definitions, difficulty-instance configurations, difficulty-owned variant pools, session logs, step logs, completion records, Review Mode attempt logs, and progress records. All writes involving completion records use database transactions and unique constraints to prevent duplicate entries. |
| In-Memory Cache (Redis / Upstash Redis) | Used for active scenario session state, repository snapshot/session metadata caching, frequently accessed scenario metadata, and JWT revocation blacklisting. Refresh tokens added on logout use a time-to-live equal to their remaining lifetime. |
| Python Git Library (pygit2 / libgit2) | Internal implementation dependency used by the Repository State Simulator to initialize and manipulate isolated server-side repository sessions. This is not an external Git hosting integration and does not permit execution of student input through an operating-system shell or external Git command-line binary. |
| Repository State Simulator | Internal backend component that maintains isolated simulated repository sessions and processes student-entered Git commands through an application-controlled command adapter before any repository operation is performed. |
| State-Based Evaluator | Internal backend component that compares normalized post-command repository-state snapshots against the expected target state for the current scenario step. Returns evaluation results such as TargetMatched or TargetNotYetMatched without checking the submitted command against a fixed answer string. |

#### 3.1.3 Communications Interfaces

All client-server communication occurs over HTTPS (TLS 1.2 or higher). Plain HTTP connections are automatically redirected to HTTPS. The backend exposes a RESTful JSON API consumed by the frontend web client. JWT access tokens are transmitted in the Authorization header as Bearer tokens. Refresh tokens are stored and transmitted exclusively in httpOnly, Secure, SameSite=Strict cookies, inaccessible to JavaScript. CORS is restricted to the frontend application's origin domain.

---

## 3.2 Functional Requirements

---

## Module 0: System Access Prerequisites

**Corresponds to:** Supporting prerequisite module only. This module does not correspond to any General Objective. It provides secure account creation, authentication, and session management — the access layer that enables all other modules to function.

**Module Overview:** This module covers account registration, login, authenticated page access, session continuity, and logout. These requirements are necessary for secure platform access but are not treated as objective-linked Git competency modules. Authentication is a pre-condition for accessing any learning content; it does not itself represent a measurable Git learning outcome.

---

### 0.1 Register a New Student Account

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AUTH-01 |
| **Use Case Name** | Register a New Student Account |
| **Actor(s)** | Unregistered Visitor |
| **Preconditions** | The visitor has no existing account. The /register page is accessible. |
| **Main Flow** | 1. Visitor navigates to /register.<br>2. System displays the registration form: student ID, first name, last name, CIT educational email address, password, confirm password.<br>3. Visitor fills in the form and submits.<br>4. System validates: student ID presence and NN-NNNN-NNN digit format, email format (RFC 5322), @cit.edu email domain, password complexity (minimum 8 characters, at least one letter and one number), password/confirm-password match.<br>5. System checks that the student ID and email address are not already registered.<br>6. System hashes the password using a secure one-way algorithm (an industry-standard password hashing algorithm). The plaintext password is never persisted.<br>7. System creates a new user record with the Student role and generates an initial progress record with all unit completion statuses set to 'Not Started'.<br>8. System generates an access token (15-minute expiry) and a refresh token (7-day expiry). Refresh token is stored in an httpOnly, Secure, SameSite=Strict cookie.<br>9. System returns the access token and user profile to the frontend.<br>10. Frontend stores the access token in memory and redirects to /dashboard. |
| **Postconditions** | A new Student account exists in the database. An initial progress record exists. The user is authenticated and lands on the Student Dashboard. |
| **Alternative Flows** | AF1 — Email already registered: System returns HTTP 409; frontend displays 'An account with this email already exists. Please log in.'<br>AF2 — Student ID already registered: System returns HTTP 409; frontend displays that the student ID is already associated with an account.<br>AF3 — Client-side validation failure: Frontend displays inline field-level error messages before submission.<br>AF4 — Server-side validation failure: System returns HTTP 422 with field-level error details. |
| **Functional Requirements** | FR-AUTH-01: Validate student ID in NN-NNNN-NNN digit format, first name, last name, @cit.edu email format/domain, password complexity, and password confirmation match before creating an account.<br>FR-AUTH-02: Reject registration if the email or student ID is already associated with an existing account (HTTP 409).<br>FR-AUTH-03: Hash all passwords using a secure one-way password hashing algorithm before storage; plaintext passwords shall never be persisted or logged.<br>FR-AUTH-04: Upon successful registration, create an initial progress record for the new student.<br>FR-AUTH-05: Upon successful registration, authenticate the user and redirect to the Student Dashboard. |

**UC-AUTH-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Register a New Student Account
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Unregistered Visitor** actor as the initiating subject. Place the use case oval "Register a New Student Account" inside the system boundary. Show that a successful registration outcome transitions the actor into the Authenticated Student role. No system actor should initiate this use case.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Register a New Student Account
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the step-by-step main flow and alternative flows, including client-side and server-side validation decision nodes and swim lanes.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Registration Form
Tool: Draw.io, Figma, or equivalent
Contents: Show the registration form with all fields, inline validation states, and the post-registration redirect to /dashboard.
[PLACEHOLDER — Insert diagram here]

---

### 0.2 Log In to Student Account

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AUTH-02 |
| **Use Case Name** | Log In to Student Account |
| **Actor(s)** | Registered Student |
| **Preconditions** | The student has a registered account. The /login page is accessible. |
| **Main Flow** | 1. Student navigates to /login.<br>2. System displays the login form: student ID or CIT educational email address, password.<br>3. Student submits credentials.<br>4. System looks up the account by student ID or @cit.edu email address.<br>5. System verifies the submitted password against the stored hash.<br>6. System generates an access token (15-minute expiry) and a refresh token (7-day expiry).<br>7. System stores the refresh token in an httpOnly, Secure, SameSite=Strict cookie.<br>8. System returns the access token and user profile to the frontend.<br>9. Frontend stores the access token in memory and redirects to /dashboard. |
| **Postconditions** | The student is authenticated. Access and refresh tokens are issued. |
| **Alternative Flows** | AF1 — Invalid credentials: System returns HTTP 401; frontend displays 'Invalid student ID/email or password.' (No indication of which field is wrong, to prevent account enumeration.)<br>AF2 — Account not found: Same HTTP 401 response and message as AF1. |
| **Functional Requirements** | FR-AUTH-06: Authenticate students using either student ID/password or @cit.edu email/password.<br>FR-AUTH-07: Issue short-lived access tokens (15-minute expiry) and long-lived refresh tokens (7-day expiry) on successful login.<br>FR-AUTH-08: Store refresh tokens in httpOnly, Secure, SameSite=Strict cookies.<br>FR-AUTH-09: Not differentiate between 'identifier not found' and 'wrong password' in the error message returned to the client. |

**UC-AUTH-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Log In to Student Account
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Registered Student** actor as the initiating subject. Place "Log In to Student Account" inside the system boundary. Show that a successful login outcome results in the actor becoming an Authenticated Student with access to the dashboard.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Log In to Student Account
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the step-by-step main flow and alternative flows, including decision nodes for credential validation and swim lanes.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Login Form
Tool: Draw.io, Figma, or equivalent
Contents: Show the login form, error states, and the post-login redirect to /dashboard.
[PLACEHOLDER — Insert diagram here]

---

### 0.3 Access Authenticated Platform Pages

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AUTH-03 |
| **Use Case Name** | Access Authenticated Platform Pages |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | The student has successfully logged in and has a valid session. |
| **Main Flow** | 1. Student opens an authenticated platform page such as the Student Dashboard, Dashboard/Units tab, Learning Unit list, Lesson page, scenario list, Scenario Practice Workspace, or Review Mode.<br>2. System verifies that the student's session is valid.<br>3. System displays the requested authenticated page.<br>4. Student continues using the requested platform feature. |
| **Postconditions** | The student accesses the requested authenticated page while the session remains valid. |
| **Alternative Flows** | AF1 — Session expired or invalid: System redirects the student to the login page and displays a session-expired message.<br>AF2 — Student attempts to access an authenticated page without logging in: System prevents access and redirects the student to the login page. |
| **Functional Requirements** | FR-AUTH-10: Verify that a valid authenticated session exists before displaying protected platform pages.<br>FR-AUTH-11: Allow authenticated students to access protected platform pages while their session remains valid.<br>FR-AUTH-12: Prevent unauthenticated or expired sessions from accessing protected platform pages.<br>FR-AUTH-13: Redirect students with invalid or expired sessions to the login page.<br>FR-AUTH-14: Maintain session continuity for valid logged-in students without requiring repeated manual login during normal platform use. |

**UC-AUTH-03 — Required Diagrams**

*Diagram 1 — Use Case Diagram*  
Title: Use Case Diagram — Access Authenticated Platform Pages  
Tool: Draw.io (or equivalent UML-compliant tool)  
Contents: Show the **Authenticated Student** actor initiating access to protected platform pages inside the system boundary. Include representative authenticated destinations such as Student Dashboard, Learning Unit list, Lesson, Scenario Practice Workspace, and Review Mode. No internal token-renewal process should be modeled as a separate use case oval.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*  
Title: Activity Diagram — Access Authenticated Platform Pages  
Tool: Draw.io (or equivalent UML-compliant tool)  
Contents: Show the student opening an authenticated page, the system checking session validity, the requested page being displayed, and the invalid-session redirect path.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*  
Title: Wireframe — Authenticated Page Access and Session-Expired Redirect  
Tool: Draw.io, Figma, or equivalent  
Contents: Show a representative protected page and the login screen state reached when the session is expired or invalid.
[PLACEHOLDER — Insert diagram here]

---

### 0.4 Supporting Functional Requirement Group: Session Continuity and Token Renewal

| Field | Description |
|-------|-------------|
| **Requirement Group ID** | FRG-AUTH-01 |
| **Requirement Group Name** | Session Continuity and Token Renewal |
| **Classification** | Supporting functional requirement group, not a student-initiated use case |
| **External Actor** | None. Token renewal is performed automatically to maintain a logged-in student's valid session. |
| **Triggering Events** | Authenticated page request;<br>authenticated API request;<br>access token expiry;<br>refresh-token validation;<br>invalid or expired session detection;<br>logout/session revocation. |
| **System Responsibilities** | 1. Maintain authenticated access while the student's session remains valid.<br>2. Detect expired access tokens during authenticated platform use.<br>3. Request and issue a new access token only when a valid refresh token is available.<br>4. Validate refresh-token signature, expiry, and revocation status when applicable.<br>5. Redirect the student to the login page when the session is no longer valid. |
| **Postconditions** | Valid sessions continue without repeated manual login. Invalid, expired, missing, or revoked sessions are blocked from authenticated platform pages and redirected to login. |
| **Exception Handling** | EX1 — Refresh token expired, missing, invalid, or revoked: System clears the session and redirects the student to login with a session-expired message.<br>EX2 — Revocation store temporarily unavailable: System degrades gracefully according to reliability requirements while still validating token signature and expiry. |
| **Functional Requirements** | FR-AUTH-15: The system shall maintain authenticated access for a logged-in student while the student's session remains valid.<br>FR-AUTH-16: The system shall automatically request a new access token when the current access token expires and a valid refresh token is still available.<br>FR-AUTH-17: The system shall validate the refresh token before issuing a new access token.<br>FR-AUTH-18: The system shall check refresh-token revocation status before issuing a new access token when the revocation store is available.<br>FR-AUTH-19: The system shall invalidate the session and redirect the student to the login page when the refresh token is expired, missing, invalid, or revoked.<br>FR-AUTH-20: If the revocation store is temporarily unavailable, the system shall degrade gracefully according to the reliability requirements while still validating token signature and expiry. |
| **Diagram Guidance** | Do not create a standalone use case diagram for token renewal. If documentation requires a diagram, represent session continuity as part of the activity or sequence flow for accessing authenticated platform pages. |
---

### 0.5 Log Out

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AUTH-04 |
| **Use Case Name** | Log Out |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | The student is authenticated and holds a valid session. |
| **Main Flow** | 1. Student clicks the 'Log Out' button.<br>2. Frontend sends a POST request to /auth/logout including the refresh token from the httpOnly cookie.<br>3. System adds the refresh token to the revocation blacklist in the in-memory cache, with TTL equal to the token's remaining lifetime.<br>4. System clears the refresh token cookie.<br>5. System returns HTTP 200.<br>6. Frontend clears the in-memory access token and redirects to /login. |
| **Postconditions** | The refresh token is revoked. The access token expires naturally within 15 minutes. The student is unauthenticated. |
| **Alternative Flows** | AF1 — Cache unavailable: Token blacklisting fails silently. Logout still completes. Frontend clears tokens and redirects to /login. The refresh token expires naturally within its remaining lifetime. |
| **Functional Requirements** | FR-AUTH-21: Revoke the refresh token on logout by adding it to the in-memory blacklist.<br>FR-AUTH-22: Clear the refresh token cookie on logout.<br>FR-AUTH-23: Clear all in-memory tokens on the frontend and redirect to /login on logout. |

**UC-AUTH-04 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Log Out
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor initiating "Log Out" within the system boundary. Show that a successful logout transitions the actor to the unauthenticated state.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Log Out
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the student's logout action, token revocation, cookie clearing, frontend token clearing, and redirect to /login, including the cache-unavailable graceful degradation path.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Log Out Action and Post-Logout State
Tool: Draw.io, Figma, or equivalent
Contents: Show the logout button in context and the /login screen reached after successful logout.
[PLACEHOLDER — Insert diagram here]

---

## Module 1: Orientation and Conceptual Readiness

**Corresponds to:** General Objective 1 — Establish the foundational Git mental model students need for scenario-driven practice by providing accessible, richly authored Unit 1 orientation lessons that students can read at their own pace before or during practice.

**Module Overview:** This module covers Unit 1 orientation lesson access, single-page concept reading, and optional orientation completion tracking. Unit 1 contains structured, no-terminal Git orientation content that students may read before or during scenario-driven practice. Each orientation lesson is a consequence-safe, scrollable instructional page — not a scored quiz and not a paginated click-through — that may use authored HTML, scoped CSS, diagrams, callouts, and command snippets to build the student's foundational mental model of Git. Orientation completion is tracked for student progress and evaluation insight, but it does not block scenario selection or scenario session initialization. The Unit 1 orientation content is authored and seeded before deployment and is not administrator-configurable in the current release.

**Specific Objectives addressed:**
- SO 1.1 — 100% of Unit 1 orientation lessons render correctly and are accessible to all registered students throughout the evaluation period (100% lesson accessibility)
- SO 1.2 — Orientation lesson completion is tracked for registered students without blocking scenario access, and first-session logs record whether Unit 1 was complete at the time of the student's first scenario start for later readiness analysis (OLCR ≥ 80%)
- SO 1.3 — Average Retry Count at or below 2 across the active published scenario library is reported as an indirect indicator that orientation preparation reduces random command submission and avoidance behavior (ARC ≤ 2)

---

### 1.1 Access and Navigate Unit 1 Orientation Topics

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ORI-01 |
| **Use Case Name** | Access and Navigate Unit 1 Orientation Topics |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is logged in and navigates to the Unit 1 orientation area. Unit 1 orientation lessons have been seeded and are accessible. |
| **Main Flow** | 1. Student navigates to the Unit 1 orientation area from the Student Dashboard or Units page.<br>2. System displays the list of Unit 1 orientation lessons.<br>3. Student selects a lesson.<br>4. System renders the orientation lesson as a single scrollable, no-terminal instructional page with authored HTML and scoped CSS. The page may include diagrams, callouts, command snippets, concept cards, and DAG illustrations as needed.<br>5. Student reads or scrolls through the content and may mark the lesson as read.<br>6. Student may browse orientation lessons in any order or navigate to scenario-bearing units at any time. |
| **Postconditions** | The student can view all Unit 1 orientation lessons and their current completion status. |
| **Alternative Flows** | AF1 — No Unit 1 lessons are seeded: System displays a message indicating that orientation content is not yet available.<br>AF2 — Student navigates away mid-lesson: No step position is persisted because the lesson is a single scrollable page. Completion remains unchanged unless the student marked the lesson as read. |
| **Functional Requirements** | FR-ORI-01: Display the Unit 1 orientation lesson list to all authenticated students.<br>FR-ORI-02: Each orientation lesson shall be a no-terminal, single-scroll instructional page.<br>FR-ORI-03: Each orientation lesson may include authored HTML, scoped CSS, diagrams, callouts, command snippets, and DAG illustrations. No quiz question, correct-answer requirement, or paginated next-step control shall be used.<br>FR-ORI-04: The orientation lesson list shall display the completion/read status for each lesson. |

**UC-ORI-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Access and Navigate Unit 1 Orientation Topics
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Place "Access and Navigate Unit 1 Orientation Topics" inside the system boundary. May show "Complete Orientation Topic" as an included or extended use case indicating individual lesson completion.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Access and Navigate Unit 1 Orientation Topics
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the student navigating to the orientation area, selecting lessons, reading content, and checking completion status across multiple lessons.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Unit 1 Orientation Topic List Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show the orientation lesson list with completion indicators and links to single-scroll lesson pages.
[PLACEHOLDER — Insert diagram here]

---

### 1.2 Complete a Unit 1 Orientation Topic

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ORI-02 |
| **Use Case Name** | Complete a Unit 1 Orientation Topic |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is logged in and is viewing a Unit 1 orientation lesson. |
| **Main Flow** | 1. Student selects a Unit 1 lesson (for example: 1-A — The Three File Areas: working tree, staging area, repository; 1-B — Tracked vs. Untracked Files; 1-C — What HEAD Is).<br>2. System renders the orientation lesson as a single scrollable, no-terminal instructional page.<br>3. Student reads or scrolls through the content.<br>4. Student selects **Mark lesson read**.<br>5. System marks the lesson as complete in the student's progress record and updates the Unit 1 completion status on the dashboard. No answer correctness check is performed.<br>6. Student may open another orientation lesson or navigate to a practice unit at any time. |
| **Postconditions** | The selected orientation lesson is marked as complete/read in the student's progress record. Scenario access is unchanged because Unit 1 completion is not a prerequisite. |
| **Alternative Flows** | AF1 — Student exits mid-lesson without marking it read: The lesson remains incomplete/read-unmarked and can be reopened later. |
| **Functional Requirements** | FR-ORI-05: Provide eight no-terminal, single-scroll orientation lessons in Unit 1, covering foundational Git concepts, command structure and anatomy, DAG literacy, platform conventions, and other orientation content approved for the starter syllabus.<br>FR-ORI-06: Mark an orientation lesson as complete/read when the student selects the lesson completion action, without evaluating answer correctness and without requiring paginated steps.<br>FR-ORI-07: Persist orientation lesson completion status in the student's progress record.<br>FR-ORI-08: The orientation lesson interface shall not render a terminal input, terminal command area, scenario evaluation mechanism, or next-step walkthrough control. |

**UC-ORI-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Complete a Unit 1 Orientation Topic
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. The use case oval "Complete a Unit 1 Orientation Topic" is inside the system boundary. Show that completion is triggered by the student marking the single-scroll lesson as read — not by a correctness check.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Complete a Unit 1 Orientation Topic
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the student selecting a lesson, reading a single scrollable page, marking it read, system marking completion, and progress record update.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Unit 1 Orientation Lesson Screen (single-scroll and completed state)
Tool: Draw.io, Figma, or equivalent
Contents: Show the single-scroll concept lesson page with authored content, optional diagram/callout areas, a Mark lesson read action, and post-completion state showing the lesson as complete.
[PLACEHOLDER — Insert diagram here]

---

### 1.3 Supporting Functional Requirement Group: Orientation Completion Tracking

| Field | Description |
|-------|-------------|
| **Requirement Group ID** | FRG-ORI-01 |
| **Requirement Group Name** | Orientation Completion Tracking |
| **Classification** | Supporting functional requirement group, not a student-initiated use case |
| **External Actor** | None. Completion tracking is updated automatically when the student marks an orientation lesson as read and observed when scenario sessions start. |
| **Triggering Events** | Student marks a Unit 1 lesson as read;<br>student starts a scenario session;<br>dashboard KPI/progress data is refreshed. |
| **System Responsibilities** | 1. Persist Unit 1 lesson completion/read status when the student marks a lesson as read.<br>2. Allow scenario session initialization regardless of Unit 1 completion status.<br>3. Record whether Unit 1 was complete at scenario start as non-blocking analytics context.<br>4. Expose orientation completion progress for the dashboard and lesson list. |
| **Postconditions** | Orientation completion status is available for student progress display and readiness analysis. No scenario access is blocked by incomplete Unit 1 lessons. |
| **Exception Handling** | EX1 — Progress record unavailable while marking a lesson read: System rejects the completion update, logs the error, and prompts the student to refresh.<br>EX2 — Orientation progress unavailable at scenario start: System still initializes the scenario session and marks orientation-complete-at-start as false or unavailable for analytics. |
| **Functional Requirements** | FR-ORI-09: The system shall persist Unit 1 lesson completion/read status when the student marks a lesson as read.<br>FR-ORI-10: Scenario selection and scenario session initialization shall not be blocked by incomplete Unit 1 orientation lessons.<br>FR-ORI-11: The system shall log whether all Unit 1 orientation lessons were complete at each first-session start as a non-blocking boolean analytics field.<br>FR-ORI-12: Orientation completion tracking shall support OLCR computation without enforcing prerequisite access. |
| **Diagram Guidance** | Do not create a standalone use case diagram for orientation completion tracking. If documentation requires a diagram, represent the non-blocking completion-status capture as part of lesson completion, scenario session initialization, or dashboard computation flows. |
---

## Module 2: Scenario Practice and State-Based Evaluation

**Corresponds to:** General Objective 2 — Improve students' ability to resolve realistic Git repository problems through consequence-safe, terminal-based practice with state-based evaluation and answer-safe Review Mode re-attempts, so that at least 80% of started scenario sessions across the active published scenario library reach the correct final repository state, at least 60% of latest completed primary difficulty-level attempts demonstrate difficulty-level command mastery, and at least 60% of Review Mode sessions result in a successful scenario completion.

**Module Overview:** This module covers the core student scenario loop: expanding a learning unit, choosing a Scenario Skill Focus card, selecting an available Easy/Medium/Hard difficulty action, viewing or skipping the Skill Focus Preview, loading the actual Scenario Practice Workspace, entering Git commands, simulating repository-state changes, evaluating outcomes by final repository state, completing a scenario, retrying failed or abandoned attempts, and re-attempting a completed scenario difficulty through playable Review Mode. Scenario selection begins from the expanded unit container rather than from the bottom of a long Lesson page. The Scenario Skill Focus stores only public instructional preview data, while each Difficulty Instance remains the authoritative configured practice unit for its level and owns the actual narrative/task prompt, initial repository-state definition, target-state rule, command-count policy, scaffolding configuration, expected-state behavior, and variant pool. Success is measured primarily by Scenario Completion Rate, Command Accuracy Rate, Average Retry Count, and Review Mode SCR. The State-Based Evaluator accepts any valid command sequence that produces the correct final repository state and does not rely on brittle command-string matching.

**Specific Objectives addressed:**
- SO 2.1 — ≥80% of started scenario sessions across the active published scenario library reach the correct final repository state (SCR ≥ 80%)
- SO 2.2 — ≥60% of latest completed primary difficulty-level attempts are completed at or below the authored minimum counted-command threshold for that level (CAR ≥ 60%)
- SO 2.3 — ≥60% of Review Mode sessions result in a successful scenario completion (Review Mode SCR ≥ 60%)

**Content Organization Model:**

| Content Element | Purpose | Flexibility Rule |
|---|---|---|
| Learning Unit | Groups related lessons for students | Seeded content record in the current release; administrator-managed only through the planned Phase 2 Administrative Management module |
| Lesson | Provides standalone orientation or optional reference context within a learning unit | Unit 1 lessons remain standalone orientation content; scenario-bearing units do not require lesson-first access before practice |
| Unit Scenario Hub | Displays the Scenario Skill Focus cards belonging to an expanded learning unit | Rendered directly inside the expanded unit container on the Dashboard/Units tab |
| Scenario Skill Focus | Represents the public Git command, concept, or workflow being practiced | Stores title, short explanation, skill focus type, focus command/s, safe demo commands, demo repository/DAG state, demo explanation content, and related concepts; never stores hidden target-state rules or solution notes |
| Skill Focus Preview | Provides a short pre-practice warm-up before any Start, Continue, Retry, or Review action enters the workspace | Contains public explanation and demo-only interaction; does not create sessions, affect command counts, affect CAR/SCR/RTA/retry metrics, or reveal actual scenario state |
| Difficulty Instance | Provides Easy, Medium, and Hard practice levels for a scenario skill focus | Stores actual playable scenario configuration including narrative/task prompt, initial repository state, hidden target-state rule, expected-state behavior, scaffolding configuration, command-count policy, difficulty-owned variant pool, and internal solution notes if used by admins |
| Command-Count Policy | Stores the minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns for a scenario difficulty instance | Authored per scenario difficulty instance; seeded before deployment in the current release and administrator-managed in Phase 2 |
| Difficulty Variant Pool | Stores structurally distinct variants attached to one scenario difficulty instance | Required for RTA-eligible difficulty instances; exact variant count is finalized before deployment |
| Retry Variant | Provides structurally changed attempts for transfer measurement | Selected from the active difficulty instance's variant pool; required only for RTA-eligible difficulty instances |
| Review Mode Session | Provides a playable re-attempt of a previously completed scenario difficulty instance | Logged separately from primary scenario attempts for Review Mode SCR; does not reveal correct commands or command sequences |

---

### 2.1 View Reference Lessons and Unit Skill Focuses

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DASH-02 |
| **Use Case Name** | View Reference Lessons and Unit Skill Focuses |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is authenticated and is viewing either the Dashboard/Units tab or the Learning Unit list. At least one published learning unit exists. |
| **Main Flow** | 1. Student expands a learning unit card.<br>2. If the unit is Unit 1 Orientation, the system displays the unit's orientation lessons with read/completion status.<br>3. If the unit is scenario-bearing, the system displays Scenario Skill Focus cards directly inside the expanded unit container.<br>4. Each Scenario Skill Focus card shows its public title, one-line summary, focus command/s, optional supporting inspection commands, Easy/Medium/Hard progress state, and available difficulty action buttons.<br>5. Optional reference lessons may be displayed separately from the primary scenario access path.<br>6. Student may open a reference lesson, but scenario selection does not require reading or scrolling through that lesson first. |
| **Postconditions** | Student can see unit-level Scenario Skill Focus cards and available difficulty actions without opening a detailed Lesson page first. |
| **Alternative Flows** | AF1 — Unit has no published scenario skill focuses: System displays an empty-state message in the expanded unit container.<br>AF2 — Student opens a reference lesson: System renders the Lesson page as reference content and directs scenario practice back to the unit-level skill focus cards. |
| **Functional Requirements** | FR-DASH-10: Unit 1 shall retain standalone orientation lessons with completion/read tracking.<br>FR-DASH-11: Reference Lesson pages shall render saved or pre-authored lesson HTML and scoped CSS when opened.<br>FR-DASH-12: Scenario-bearing units shall display Scenario Skill Focus cards directly inside the expanded unit container instead of requiring embedded lesson scenario lists.<br>FR-DASH-13: Each Scenario Skill Focus card shall show public skill focus title, summary, focus command/s, supporting inspection commands when present, and Easy/Medium/Hard action states.<br>FR-DASH-14: Lesson pages shall not be the primary access path for scenario-bearing units. |

**UC-DASH-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Reference Lessons and Unit Skill Focuses
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Include use cases "Expand Unit," "View Unit Skill Focuses," and optional "Open Reference Lesson" inside the system boundary. Do not show embedded scenario lists as the main scenario access path.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — View Reference Lessons and Unit Skill Focuses
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show unit expansion, Unit 1 orientation lesson display, scenario-bearing unit skill focus display, optional reference lesson opening, and return to unit-level practice access.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Expanded Unit with Scenario Skill Focus Cards
Tool: Draw.io, Figma, or equivalent
Contents: Show an expanded unit card containing Scenario Skill Focus cards with Easy/Medium/Hard difficulty actions and optional reference lesson links shown separately.
[PLACEHOLDER — Insert diagram here]

---

### 2.2 Browse Unit Skill Focuses and Select Difficulty Action

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DASH-04 |
| **Use Case Name** | Browse Unit Skill Focuses and Select Difficulty Action |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is authenticated and is viewing an expanded scenario-bearing unit. Easy is available by default for every Scenario Skill Focus. Medium and Hard may be locked depending on the student's completion status for the same Scenario Skill Focus. |
| **Main Flow** | 1. Student views Scenario Skill Focus cards in the expanded unit container.<br>2. System displays Easy, Medium, and Hard difficulty actions for each card using the states Not Started, In Progress, Completed, Locked, Failed, or Abandoned.<br>3. Student clicks Start, Continue, Review, or Retry for an unlocked difficulty.<br>4. System opens the Skill Focus Preview modal before starting, resuming, retrying, or reviewing the actual scenario.<br>5. From the modal, Start Practice or Skip proceeds to the actual Scenario Practice Workspace; Close/X dismisses the modal and returns to the unit page without changing scenario state.<br>6. Difficulty progression follows the Scenario Skill Focus mastery gate: Easy is initially available, Medium unlocks only after Easy completion for the same Scenario Skill Focus, and Hard unlocks only after Medium completion for the same Scenario Skill Focus. |
| **Postconditions** | The selected available action opens the Skill Focus Preview first, or, if locked, remains disabled. No actual scenario session starts until the student chooses Start Practice or Skip from the preview. |
| **Alternative Flows** | AF1 — Locked difficulty selected: System disables the button and does not open the preview modal.<br>AF2 — Completed difficulty selected: System labels the action Review and opens the Skill Focus Preview before entering playable Review Mode.<br>AF3 — Failed or Abandoned difficulty selected: System labels the action Retry and opens the Skill Focus Preview before creating a retry attempt. |
| **Functional Requirements** | FR-DASH-15: The Dashboard/Units tab shall allow a student to expand a learning unit card to display scenario skill focuses directly for scenario-bearing units.<br>FR-DASH-16: Unit-level Scenario Skill Focus cards shall use the same scenario records, difficulty access rules, and completion data as the scenario session APIs.<br>FR-DASH-17: Display all three difficulty levels (Easy, Medium, Hard) for every Scenario Skill Focus with current access/status state: Not Started, In Progress, Completed, Locked, Failed, or Abandoned.<br>FR-DASH-18: Gate Medium behind completion of Easy for the same Scenario Skill Focus and gate Hard behind completion of Medium for the same Scenario Skill Focus.<br>FR-DASH-19: Display the action label and icon for each difficulty as Start, Continue, Review, Lock, or Retry according to its state.<br>FR-DASH-20: Scenario selection shall not be globally gated by unit completion, quiz scores, manual approval, or completion of unrelated scenarios.<br>FR-DASH-21: After a primary scenario session starts, completes, fails, is abandoned, or is retried, the frontend shall update only the affected Scenario Skill Focus card and difficulty-state entry in any already-loaded scenario list, including completion status, Review availability, First-Attempt Star status, retry state, active-session state, and next-difficulty unlock state, without forcing every card in the list to reload.<br>FR-DASH-22: Start, Continue, Review, and Retry actions shall open the Skill Focus Preview modal before routing to any actual Scenario Practice Workspace session; Locked shall not open the modal. |

**UC-DASH-04 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Browse Unit Skill Focuses and Select Difficulty Action
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Include use cases "Browse Unit Skill Focuses," "Select Difficulty Action," and "Open Skill Focus Preview" inside the system boundary. No system actor appears as a primary initiator.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Browse Unit Skill Focuses and Select Difficulty Action
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the expanded unit skill focus list, difficulty access check, locked-state disablement, Skill Focus Preview opening, and Start Practice/Skip/Close decisions.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Scenario Skill Focus Card with Difficulty Actions
Tool: Draw.io, Figma, or equivalent
Contents: Show a unit-level Scenario Skill Focus card with title, one-line summary, focus command/s, Easy/Medium/Hard action buttons, progress states, and the Skill Focus Preview modal trigger.
[PLACEHOLDER — Insert diagram here]

---

### 2.2A Skill Focus Preview Modal

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DASH-04A |
| **Use Case Name** | View Skill Focus Preview |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student has clicked Start, Continue, Review, or Retry on an unlocked Easy, Medium, or Hard difficulty action from a Scenario Skill Focus card. |
| **Main Flow** | 1. System opens a modal titled **Skill Focus Preview**.<br>2. Modal header displays the Scenario Skill Focus title, selected difficulty label, and Close/X control.<br>3. Modal displays a short concept explanation, clear focus command labels, optional supporting inspection commands, demo-only Live DAG/repository visualization, lightweight single-line demo command input, demo explanation panel, Previous/Next controls when multiple preview steps exist, Skip, and Start Practice.<br>4. Student may enter only safe demo commands; these update demo-only state and explanation text.<br>5. Student chooses Start Practice or Skip to continue to the actual Scenario Practice Workspace, or Close/X to return to the unit page without starting, continuing, retrying, or reviewing anything. |
| **Postconditions** | Start Practice or Skip routes to the actual session behavior requested by the original difficulty action. Close/X dismisses the modal and does not create or resume any scenario session. |
| **Functional Requirements** | FR-PREVIEW-01: The modal title shall be **Skill Focus Preview** and shall not use Scenario Briefing, Scenario Preview, Lesson Overview, Detailed Lesson, or Full Lesson Modal.<br>FR-PREVIEW-02: The preview shall use only public Scenario Skill Focus data: short explanation, skill focus type, focus command/s, supporting inspection commands, safe demo commands, demo repository/DAG state, demo explanation content, and related concepts.<br>FR-PREVIEW-03: The preview shall not expose actual scenario narrative, actual repository state, actual branch names, actual file names, actual target state, exact solution command sequence, hidden evaluator rules, or hidden solution notes.<br>FR-PREVIEW-04: Demo command input shall use demo-only state and shall not create sessions, affect command limits, CAR, SCR, RTA, retry count, or evaluation logs.<br>FR-PREVIEW-05: Previous and Next controls shall move only between preview steps and shall not affect scenario state or progress metrics.<br>FR-PREVIEW-06: Start Practice and Skip shall route to the actual Scenario Practice Workspace behavior for the original Start, Continue, Review, or Retry action.<br>FR-PREVIEW-07: Review Mode launched after the preview shall remain playable and shall not be read-only. |

---

### 2.3 Load a Scenario Instance

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-SCENE-01 |
| **Use Case Name** | Load a Scenario Instance |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A Scenario Skill Focus and available difficulty action have been selected from an expanded unit, and the student has chosen Start Practice or Skip in the Skill Focus Preview. Unit 1 orientation completion is not required for scenario access. Difficulty access is controlled only by the Scenario Skill Focus Easy → Medium → Hard completion progression. |
| **Main Flow** | 1. System receives the selected Difficulty Instance and action intent after the Skill Focus Preview.<br>2. System validates that the selected difficulty belongs to the selected Scenario Skill Focus and that the difficulty/action is allowed.<br>3. System loads the selected Difficulty Instance as the authoritative scenario configuration, including its narrative/task prompt, authored command-count policy, target-state rule, expected-state behavior, and selected variant from that difficulty's variant pool; if the student's prior attempt requires adaptive retry behavior, the system selects the next structurally valid retry variant from the same Difficulty Instance's pool.<br>4. System initializes or resumes the correct session behavior: new primary session for Start, existing primary session for Continue, retry session for Retry, or playable Review Mode session for Review.<br>5. System initializes the Repository State Simulator with the selected difficulty variant's starting repository state, records the source entry point, stores the applicable command-count policy for the session, and logs session start time, difficulty-instance ID, and variant ID through FRG-LOG-01 when a new session is created.<br>6. System renders the scenario interface with: (a) the Difficulty Instance's narrative context card and task prompt, (b) explicit success rules explaining state-based grading, commit-message expectations when applicable, and non-counted diagnostic commands, (c) the terminal-style command input, auto-focused and keyboard-ready, (d) the live animated DAG showing the selected variant's actual starting repository state, (e) the expected-state diagram on Easy and Medium only, (f) the contextual feedback panel area on Easy only, visible but blank until a command is processed by the simulator, and (g) the Remaining Counted-Command Counter.<br>7. Student is ready to enter Git commands in the actual evaluated Scenario Practice Workspace. |
| **Postconditions** | A scenario session is initialized and logged. The session has an applicable authored command-count policy. The student sees the starting repository state in the live DAG. The terminal input is focused. |
| **Alternative Flows** | AF1 — All variants in the pool have been played: System selects at random from the full valid pool, except when RTA eligibility requires a structurally different retry variant.<br>AF2 — Entry path or unit/scenario relationship mismatch: System rejects the request and returns the student to the correct scenario list.<br>AF3 — Selected difficulty is locked: System does not load the scenario instance and displays the missing completion requirement. |
| **Functional Requirements** | FR-SCENE-01: Load a valid variant from the selected Difficulty Instance's variant pool on each new session start after validating that the selected difficulty action is allowed.<br>FR-SCENE-02: Initialize the Repository State Simulator only for actual Scenario Practice Workspace sessions, never for Skill Focus Preview demo commands.<br>FR-SCENE-03: Display the appropriate interface components based on difficulty level: Easy (live DAG + expected-state diagram + contextual feedback panel); Medium (live DAG + expected-state diagram); Hard (live DAG + narrative context only).<br>FR-SCENE-04: Create and persist a session log record on scenario load through FRG-LOG-01, including selected scenario, difficulty-instance ID, difficulty level, variant ID, timestamp, source entry point, and applicable command-count policy ID or snapshot.<br>FR-SCENE-05: The terminal input shall be the default focused element when a scenario loads so students can begin typing immediately.<br>FR-SCENE-05A: The system shall support loading scenario instances from unit-level Scenario Skill Focus actions after the Skill Focus Preview and from valid Review Mode launchers.<br>FR-SCENE-05B: Each loaded Scenario Difficulty Instance shall include an authored command-count policy containing a minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns.<br>FR-SCENE-05C: Each Scenario Difficulty Instance shall be independently configured with its own student-facing narrative/task prompt, initial repository-state definition, target-state rule, expected-state diagram behavior, and difficulty-specific variant pool. |

**UC-SCENE-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Load a Scenario Instance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Show "Load a Scenario Instance" inside the system boundary. Show unit-level difficulty action selection and Skill Focus Preview as preceding entry-point use cases that include or precede "Load a Scenario Instance." Do not model logging as a student use case.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Load a Scenario Instance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show both entry paths merging into the same unlock validation, variant selection, session initialization, and scenario workspace rendering flow.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Scenario Practice Workspace (Easy, Medium, and Hard states)
Tool: Draw.io, Figma, or equivalent
Contents: Show the transition from a selected scenario card/difficulty selector into the scenario practice workspace at Easy, Medium, and Hard support levels.
[PLACEHOLDER — Insert diagram here]

---

### 2.4 Enter and Submit a Git Command

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-TERM-01 |
| **Use Case Name** | Enter and Submit a Git Command |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A scenario session is active. The terminal input is focused. |
| **Main Flow** | 1. Student types a Git command into the terminal input (e.g., 'git checkout -b feature/login').<br>2. Student presses Enter to submit.<br>3. Frontend displays the entered command in the terminal output area with a prompt prefix.<br>4. Frontend sends the command to the backend (UC-SCENE-02 is triggered).<br>5. Backend returns the terminal output, updated repository state, command classification, and remaining counted-command value.<br>6. Terminal output area appends the command result below the entered command.<br>7. Live DAG re-renders to reflect the updated repository state when the command changes the repository state.<br>8. The Remaining Counted-Command Counter updates only when the submitted command is classified as a counted action command. |
| **Postconditions** | The command and its output are visible in the terminal area. The repository state, command classification, step log, and Remaining Counted-Command Counter reflect the command result. |
| **Alternative Flows** | AF1 — Empty input submitted: System ignores the submission; no API call is made.<br>AF2 — Command history navigation (Up/Down arrow keys): Terminal cycles through previously entered commands in the current session.<br>AF3 — Command submitted while processing: System does not permit terminal input while a command is being processed, to prevent concurrent submissions. |
| **Functional Requirements** | FR-TERM-01: Accept free-text Git command input in the terminal input field.<br>FR-TERM-02: Display all commands entered and their results in chronological order in the terminal output area, with a prompt prefix.<br>FR-TERM-03: Support command history navigation via Up/Down arrow keys within the current session.<br>FR-TERM-04: Not permit terminal input while a command is being processed.<br>FR-TERM-05: The terminal interface shall be keyboard-accessible and operable without a mouse.<br>FR-TERM-06: Treat the terminal as a simulated Git command interface only; submitted text shall be parsed by the Repository State Simulator command adapter and shall never be executed by a real shell, operating-system process, or external Git command-line binary.<br>FR-TERM-07: For malformed commands or commands outside the simulator's implemented Git operation set, display a neutral terminal-style message, leave the repository state unchanged, and return the result to UC-SCENE-02 for logging as an unprocessable command attempt.<br>FR-TERM-08: The simulator's implemented Git operation set shall cover every Git operation required by the approved starter scenario library and active variant pools.<br>FR-TERM-09: The scenario workspace shall display a Remaining Counted-Command Counter based on the current session's authored command-count policy. |

**UC-TERM-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Enter and Submit a Git Command
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject typing and submitting a command. The use case "Enter and Submit a Git Command" is inside the system boundary. Show that this use case includes or triggers "Execute Git Command and Evaluate Result" (UC-SCENE-02). No system actor appears as a primary initiator.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Enter and Submit a Git Command
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the student typing a command, submitting via Enter, frontend display, backend processing trigger, result display, and live DAG update. Show alternative flows for empty input, history navigation, and concurrent-submission prevention.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Terminal Input and Command Output Area
Tool: Draw.io, Figma, or equivalent
Contents: Show the terminal input field, prompt prefix, command history area, and live DAG adjacent to the terminal.
[PLACEHOLDER — Insert diagram here]

---

### 2.5 Execute Git Command and Evaluate Repository State

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-SCENE-02 |
| **Use Case Name** | Execute Git Command and Evaluate Repository State |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A scenario session is active. The student has submitted a Git command via UC-TERM-01. |
| **Main Flow** | 1. Frontend sends the command string to the backend API.<br>2. Backend passes the command to the Repository State Simulator command adapter for the active session.<br>3. The command adapter determines whether the submitted text maps to an implemented simulator operation.<br>4. If the command is processable and valid for the current simulated state, the Repository State Simulator applies the operation or read-only inspection, then produces the post-command repository state and terminal output.<br>5. The system classifies the simulator-processed command against the session's authored command-count policy as either a counted action command or a non-counted diagnostic command.<br>6. For simulator-processed commands, the system generates a state-change description from the pre-command and post-command repository states.<br>7. Backend passes the post-command state to the State-Based Evaluator along with the expected target state for the current scenario step.<br>8. State-Based Evaluator compares the two states and returns either TargetMatched or TargetNotYetMatched.<br>9. Frontend re-renders the live DAG with the post-command state, displays terminal output, and updates the Remaining Counted-Command Counter only when the command is classified as a counted action command.<br>10. On Easy level only, the Contextual Feedback Panel displays the state-change description as text-based repository consequence feedback; on Medium and Hard, no feedback panel message appears.<br>11a. If TargetMatched: the step is marked complete; the system logs command text, timestamp, attempt number, result, command classification, and counted-command totals; the step counter advances; if all steps are complete, the scenario is marked completed and UC-SCENE-03 is triggered.<br>11b. If TargetNotYetMatched: the step remains open; the system logs command text, timestamp, attempt number, result, command classification, and counted-command totals; the student continues from the resulting repository state unless scenario rules require restart. |
| **Postconditions** | The repository state, command classification, counted-command total, and step log reflect the command result. On a TargetMatched step, the scenario advances. A TargetNotYetMatched result keeps the current step open; it does not by itself mark the whole scenario attempt as Failed. |
| **Alternative Flows** | AF1 — Malformed command or command outside the simulator's implemented Git operation set: Repository State Simulator returns a neutral terminal-style message, leaves the repository state unchanged, and logs the submission as an unprocessable command attempt.<br>AF2 — Simulator-processed command changes the repository but does not satisfy the current target state: Simulator updates the state, evaluator records TargetNotYetMatched, and the student continues from the resulting state.<br>AF3 — Simulator-processed diagnostic command produces no repository-state change: Terminal output explains the no-change result; on Easy level, the Contextual Feedback Panel may summarize that no repository state changed. The command is logged but does not reduce the Remaining Counted-Command Counter when it matches an authored non-counted diagnostic command pattern.<br>AF4 — Maximum counted-command limit reached before completion: System marks the scenario session as Failed, records the failure reason as COUNTED_COMMAND_LIMIT_REACHED, and offers retry behavior according to Module 4. |
| **Functional Requirements** | FR-SCENE-06: Pass every entered command to the Repository State Simulator command adapter and update the internal repository state only when the command maps to an implemented simulator operation.<br>FR-SCENE-07: The State-Based Evaluator shall compare the resulting repository state against the expected target state — not the specific command entered.<br>FR-SCENE-08: Any simulator-processable command or sequence that produces the correct target state shall be accepted, even if it differs from the authored reference sequence.<br>FR-SCENE-09: The live DAG shall update after every simulator-processed command at all difficulty levels.<br>FR-SCENE-10: Log every command submission with timestamp, attempt number, result category (TargetMatched, TargetNotYetMatched, Unprocessable, or Invalid), command classification, counted-command increment value, and current counted-command total.<br>FR-SCENE-11: On Easy level, the Contextual Feedback Panel shall display a state-change description after each simulator-processed command. Unprocessable or invalid commands shall receive terminal-style output only.<br>FR-SCENE-12: Student-facing interface elements shall never reveal the correct command or correct command sequence, in conformance with the No-Answer Policy.<br>FR-SCENE-12A: State equivalence shall be evaluated using the simulated repository state relevant to the current step, including commit graph relationships, branch pointer locations, HEAD position, staging/working-tree status, conflict status, and required file-state markers when applicable.<br>FR-SCENE-12B: The system shall classify simulator-processed commands using the applicable authored command-count policy before updating CAR-related counts or the Remaining Counted-Command Counter.<br>FR-SCENE-12C: The system shall mark a scenario session as Failed when the maximum counted-command limit is reached before all required target states are achieved. |

**UC-SCENE-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Execute Git Command and Evaluate Repository State
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. "Execute Git Command and Evaluate Repository State" is inside the system boundary. This use case is included by or triggered from "Enter and Submit a Git Command" (UC-TERM-01). Logging is not a separate student use case.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Execute Git Command and Evaluate Repository State
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show command receipt, simulator adapter decision, processable vs. unprocessable paths, state-based evaluation, TargetMatched/TargetNotYetMatched outcomes, DAG update, and Easy-level feedback panel update.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Scenario Workspace After Command Evaluation (Easy, Medium, Hard)
Tool: Draw.io, Figma, or equivalent
Contents: Show the terminal output after a command, the updated live DAG, the contextual feedback panel (Easy only), and the expected-state diagram (Easy/Medium only).
[PLACEHOLDER — Insert diagram here]

---

### 2.6 Complete Scenario and Handle Retry or Advancement

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-SCENE-03 |
| **Use Case Name** | Complete Scenario and Handle Retry or Advancement |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | All steps in the current scenario instance have been completed successfully. |
| **Main Flow** | 1. The final step receives a TargetMatched result (UC-SCENE-02).<br>2. System marks the scenario instance (scenario × difficulty level) as 'Complete' in the student's progress record.<br>3. System records session end time, total steps, total counted action commands, total non-counted diagnostic commands, total retries, total time, applicable command-count policy ID or snapshot, and variant ID.<br>4. System determines CAR eligibility by comparing the completed session's counted action-command total against the authored minimum counted-command threshold for that difficulty instance.<br>5. If the student completed the scenario with no non-target-matching, unprocessable, or invalid command submissions during the entire session, the system awards a First-Attempt Star for this instance.<br>6. System updates the streak counter if this is the student's first scenario completion on the current calendar day.<br>7. System displays a completion screen showing scenario name, difficulty level, retries used, counted-command total, CAR indicator when applicable, and star status. The completion screen shall not reveal the correct command, sequence, or target state.<br>8. If the completed difficulty unlocks the next level, the system displays the newly available level. Student may choose to: (a) attempt a newly unlocked or already available difficulty level of the same scenario, (b) replay the same completed difficulty level as a new session, or (c) navigate back to the dashboard.<br>9. On retry after a failed scenario attempt or abandonment: the system serves a different variant from the pool when a structurally different variant is available (Adaptive Retry Logic). |
| **Postconditions** | Completion record is updated. Stars and streaks are awarded if applicable. The Review button for this scenario instance becomes visible on the dashboard. Any already-loaded scenario list reflects the affected card's updated completion and unlock state when the student returns from the practice workspace. |
| **Alternative Flows** | AF1 — Student exits mid-scenario (browser close, navigation away): Session is marked as abandoned after a configurable inactivity timeout. Partial step progress within the current attempt is not persisted. |
| **Functional Requirements** | FR-SCENE-13: Persist scenario completion records immediately upon the final step receiving a TargetMatched result, within a database transaction.<br>FR-SCENE-14: Award a First-Attempt Star only when no non-target-matching, unprocessable, or invalid command submissions occurred during the entire scenario session.<br>FR-SCENE-15: Unlock Medium for the same scenario after Easy completion and unlock Hard for the same scenario after Medium completion.<br>FR-SCENE-16: Update the streak counter on the student's first completed scenario session for the current calendar day.<br>FR-SCENE-17: On retry after a failed scenario attempt or abandonment, serve a different variant from the selected difficulty instance's variant pool when available; no RTA-eligible retry shall use the identical difficulty variant from the immediately preceding Failed or Abandoned session.<br>FR-SCENE-18: Log total retries, session duration, difficulty-instance ID, variant ID, command-count policy ID or snapshot, counted action-command total, non-counted diagnostic command total, completion status, abandonment status, and first-attempt-star eligibility for every session.<br>FR-SCENE-19: The completion screen shall not display, hint at, or reveal the correct command or correct command sequence, in conformance with the No-Answer Policy.<br>FR-SCENE-20: CAR shall be computed from counted action commands only; non-counted diagnostic commands shall be excluded from CAR computation. |

**UC-SCENE-03 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Complete Scenario and Handle Retry or Advancement
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. "Complete Scenario and Handle Retry or Advancement" is inside the system boundary. Show that the student may choose to retry, advance to the next difficulty, or return to dashboard — all as student-initiated actions after completion.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Complete Scenario and Handle Retry or Advancement
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show final TargetMatched result, completion record write, first-attempt star check, streak update, difficulty unlock, completion screen display, and the three post-completion student choices. Include mid-session abandonment alternative flow.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Scenario Completion Screen with Post-Completion Options
Tool: Draw.io, Figma, or equivalent
Contents: Show the completion screen with scenario name, difficulty, retries used, star status, newly unlocked difficulty indicator, and navigation options (retry, next difficulty, back to dashboard).
[PLACEHOLDER — Insert diagram here]

---

### 2.7 Re-attempt a Completed Scenario in Review Mode

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-REVIEW-01 |
| **Use Case Name** | Re-attempt a Completed Scenario in Review Mode |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | The student has at least one completed session for the selected scenario difficulty instance. The Review button is visible from the dashboard/unit scenario card or from the completion screen. |
| **Main Flow** | 1. Student clicks the Review button for a completed scenario difficulty instance.<br>2. System opens the Skill Focus Preview modal for the selected Scenario Skill Focus and difficulty.<br>3. Student chooses Start Practice or Skip from the preview.<br>4. System verifies that the student has a completed session for the selected scenario difficulty.<br>5. System initializes a new playable Review Mode session for that scenario difficulty and records the session as review_mode = true.<br>6. System loads the scenario narrative, starting repository state, and selected variant according to the platform's replay/re-attempt rules.<br>7. System renders the Scenario Practice Workspace with the live terminal, live DAG, and the same difficulty-appropriate scaffolding used in regular practice: Easy shows live DAG, expected-state diagram, and contextual feedback; Medium shows live DAG and expected-state diagram; Hard shows live DAG and narrative context only.<br>8. Student enters Git commands through the terminal.<br>9. System processes commands through the Repository State Simulator and State-Based Evaluator using the same state-based evaluation rules in UC-SCENE-02.<br>10. If the target state is reached, system marks the Review Mode session as completed and includes it in Review Mode SCR.<br>11. Student exits to the dashboard or chooses another available scenario action. |
| **Postconditions** | A Review Mode session record exists and is tagged separately from primary scenario attempts. Review Mode SCR can be computed from Review Mode sessions. The student's original completion record remains intact. |
| **Alternative Flows** | AF1 — No completed session exists: The Review button is not displayed. If the endpoint is accessed directly, the system returns HTTP 404.<br>AF2 — Student exits mid-session: The Review Mode session is marked Abandoned after the configured inactivity timeout.<br>AF3 — Selected scenario content is unavailable: System prevents Review Mode start and displays an unavailable-content message. |
| **Functional Requirements** | FR-REVIEW-01: Display a Review button only for scenario difficulty instances with at least one completed session by the student.<br>FR-REVIEW-02: Starting Review Mode shall initialize a new playable scenario session tagged as review_mode = true.<br>FR-REVIEW-03: Review Mode shall provide live terminal input and shall accept new command submissions.<br>FR-REVIEW-04: Review Mode shall use the same Repository State Simulator, State-Based Evaluator, and authored command-count policy rules as regular scenario practice.<br>FR-REVIEW-05: Review Mode shall render difficulty-appropriate scaffolding consistently with regular practice: Easy with live DAG, expected-state diagram, and contextual feedback; Medium with live DAG and expected-state diagram; Hard with live DAG and narrative context only.<br>FR-REVIEW-06: Review Mode session outcomes shall be logged separately so Review Mode SCR can be computed without overwriting the student's original completion record.<br>FR-REVIEW-07: Review Mode shall not reveal the correct command or correct command sequence at any point, in conformance with the No-Answer Policy.<br>FR-REVIEW-08: Failed or abandoned sessions shall not unlock Review Mode; they shall instead follow retry behavior under Module 4 when the student chooses to try again. |

**UC-REVIEW-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Re-attempt a Completed Scenario in Review Mode
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Place "Re-attempt a Completed Scenario in Review Mode" inside the system boundary. Show that this use case requires a prior completed scenario difficulty instance and includes the same command submission and state-based evaluation behavior used in scenario practice.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Re-attempt a Completed Scenario in Review Mode
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the student clicking Review, the system verifying prior completion, initializing a Review Mode session, rendering the workspace with difficulty-appropriate scaffolding, processing commands, evaluating repository state, recording completion or abandonment, and returning to the dashboard.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Review Mode Scenario Practice Workspace
Tool: Draw.io, Figma, or equivalent
Contents: Show the Scenario Practice Workspace in Review Mode with a Review Mode label, scenario narrative, live DAG, terminal input, and difficulty-appropriate support panels.
[PLACEHOLDER — Insert diagram here]

---


### 2.8 Supporting Functional Requirement Group: Command-Count Policy and Diagnostic Command Classification

| Field | Description |
|-------|-------------|
| **Requirement Group ID** | FRG-CMD-01 |
| **Requirement Group Name** | Command-Count Policy and Diagnostic Command Classification |
| **Classification** | Supporting functional requirement group, not a standalone student-initiated use case |
| **External Actor** | None. The policy is applied automatically during scenario loading, command evaluation, completion handling, Review Mode, and KPI computation. |
| **Triggering Events** | Scenario difficulty instance is loaded;<br>student submits a command;<br>command is processed by the simulator;<br>remaining counted-command value is updated;<br>scenario completion or failure is evaluated;<br>CAR is computed. |
| **System Responsibilities** | 1. Load the authored command-count policy for the selected scenario difficulty instance.<br>2. Store the session's applicable minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns.<br>3. Classify simulator-processed commands as counted action commands or non-counted diagnostic commands.<br>4. Exclude matched non-counted diagnostic commands from CAR and remaining counted-command calculations.<br>5. Log all commands regardless of whether they are counted.<br>6. Prevent state-changing commands from being treated as non-counted diagnostic commands.<br>7. Apply a separate submission-safety limit for repeated malformed, invalid, unprocessable, or diagnostic inputs when needed. |
| **Postconditions** | Command-count behavior is traceable to the authored scenario difficulty configuration. CAR and remaining counted-command values are computed from counted action commands only. |
| **Exception Handling** | EX1 — Missing command-count policy: System prevents scenario publication or session start for the affected difficulty instance and displays a content-configuration error.<br>EX2 — Diagnostic pattern matches a state-changing command: System rejects the pattern during content validation and requires correction before publication.<br>EX3 — Repeated non-counted or invalid submissions exceed the submission-safety limit: System stops accepting additional submissions for the session and records the configured safety outcome without treating diagnostic commands as counted action commands. |
| **Functional Requirements** | FR-CMD-01: Each scenario difficulty instance shall have an authored command-count policy containing a minimum counted-command threshold, maximum counted-command limit, and zero or more non-counted diagnostic command patterns.<br>FR-CMD-02: The minimum counted-command threshold shall be used for CAR computation and shall be authorable per scenario difficulty instance.<br>FR-CMD-03: The maximum counted-command limit shall define the maximum number of counted action commands allowed before the session is marked Failed and shall be authorable per scenario difficulty instance.<br>FR-CMD-04: Non-counted diagnostic command patterns shall be authorable per scenario difficulty instance and shall apply only to read-only inspection commands.<br>FR-CMD-05: The system shall classify each simulator-processed command as either a counted action command or a non-counted diagnostic command before updating counted-command totals.<br>FR-CMD-06: The system shall not decrement the Remaining Counted-Command Counter for simulator-processed commands that match the session's authored non-counted diagnostic command patterns.<br>FR-CMD-07: The system shall still persist non-counted diagnostic commands in the session and step logs, including command text, timestamp, command classification, evaluation result, and resulting repository-state reference when applicable.<br>FR-CMD-08: The system shall prevent state-changing commands from being saved or treated as non-counted diagnostic commands.<br>FR-CMD-09: The system shall apply submission-safety controls separately from the maximum counted-command limit so repeated diagnostic, malformed, invalid, or unprocessable inputs cannot be used to abuse or stall a session. |
| **Diagram Guidance** | Do not create a standalone use case diagram for command-count policy enforcement. If documentation requires a diagram, show the policy load and command classification steps inside the scenario loading, command evaluation, completion, Review Mode, and KPI computation activity or sequence diagrams. |

---

## Module 3: Repository Visualization and Fading Scaffolding

**Corresponds to:** General Objective 3 — Improve students' independent repository-state reasoning through live DAG visualization and progressively reduced instructional scaffolding, so that Hard-Level Completion Rate reaches at least 70% across active Hard-level sessions.

**Module Overview:** This module defines the visual and instructional supports available during scenario practice. The live animated DAG remains visible at all difficulty levels and provides a visual representation of the learner's current repository state, updating after every simulator-processed command. The expected-state diagram appears only on Easy and Medium levels. The contextual feedback panel appears only on Easy level and describes the consequence of the student's own processed command without revealing the correct command, command sequence, or target repository state. These are student-visible learning supports, documented as student-observable use cases.

**Specific Objectives addressed:**
- SO 3.1 — The live animated DAG accurately reflects repository state after every processed command at all difficulty levels, with rendering accuracy verified against the approved repository-state rendering test set (0% DAG-state mismatch)
- SO 3.2 — 100% of scenario sessions render the correct instructional supports and access state for their difficulty level: Easy shows live DAG, expected-state diagram, and contextual feedback; Medium shows live DAG and expected-state diagram only; Hard shows live DAG and narrative context only (100% correct scaffolding rendering across the approved test set)
- SO 3.3 — Hard-Level Completion Rate reaches ≥70% across active Hard-level sessions (HLCR ≥ 70%)

---

### 3.1 View Live Animated DAG During Scenario Practice

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DAG-01 |
| **Use Case Name** | View Live Animated DAG During Scenario Practice |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A scenario session is active at any difficulty level. |
| **Main Flow** | 1. Student loads a scenario instance.<br>2. System renders the starting repository state in the Live Animated DAG panel.<br>3. Student enters a Git command that maps to the simulator's implemented operation set.<br>4. System processes the command through the Repository State Simulator and returns the updated repository state.<br>5. System updates the DAG to visually reflect the updated repository state, including commit history, parent-child commit relationships, branch pointer positions, and HEAD position (attached or detached) when applicable.<br>6. Student observes how the command changed the repository state.<br>7. This process repeats after each simulator-processed command. |
| **Postconditions** | The student can observe the current internal repository state after each simulator-processed command. |
| **Alternative Flows** | AF1 — Repository state unchanged by command: DAG remains in its current state and no state-transition animation is shown.<br>AF2 — Unprocessable or malformed command: The terminal displays a neutral terminal-style message and the DAG remains unchanged. |
| **Functional Requirements** | FR-DAG-01: The live DAG shall be present and visible at all difficulty levels (Easy, Medium, and Hard).<br>FR-DAG-02: The live DAG shall update after every simulator-processed command to reflect the current internal repository state.<br>FR-DAG-03: The DAG shall render the repository commit history and relationships in a way that makes commit reachability, branch pointer locations, and HEAD position (attached or detached) observable to the student during scenario practice.<br>FR-DAG-04: State transitions shall be animated, with animation timing governed by NFR-PERF-02.<br>FR-DAG-05: The DAG panel shall remain visible during a scenario session without requiring horizontal scrolling on a 1280×720 display. |

**UC-DAG-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Live Animated DAG During Scenario Practice
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject observing the Live Animated DAG. The use case "View Live Animated DAG During Scenario Practice" is inside the system boundary. Show that this use case is active throughout "Enter and Submit a Git Command" (UC-TERM-01) as a continuous observation — not a one-time action.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Live DAG Update During Scenario Practice
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show command submission, repository-state simulation, state return, DAG update, and student observation of the updated state. Show unchanged-state and unprocessable-command alternative flows.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Live Animated DAG Panel in Scenario Workspace (Easy, Medium, Hard)
Tool: Draw.io, Figma, or equivalent
Contents: Show the DAG panel placement inside the scenario workspace at Easy, Medium, and Hard levels, confirming the DAG is visible at all three levels.
[PLACEHOLDER — Insert diagram here]

---

### 3.2 View Expected-State Diagram on Easy and Medium

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DAG-02 |
| **Use Case Name** | View Expected-State Diagram on Easy and Medium |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A scenario session is active at Easy or Medium difficulty level. |
| **Main Flow** | 1. Student loads an Easy or Medium scenario instance.<br>2. System retrieves the expected-state diagram for the current scenario variant and current step.<br>3. System displays the expected-state diagram adjacent to the live DAG.<br>4. Student compares the current live DAG with the expected-state diagram while deciding what command to enter.<br>5. If the scenario has multiple steps, the expected-state diagram updates only after the current step is completed and the next step begins.<br>6. At Hard level, the expected-state diagram is absent; the student must infer the goal from the narrative context and live DAG alone. |
| **Postconditions** | On Easy and Medium, the student has a visual target-state reference for the current step. On Hard, no expected-state diagram is provided. |
| **Alternative Flows** | AF1 — Expected-state diagram cannot be loaded: System displays an error state and prevents session start because an Easy or Medium scenario must not run with missing required scaffolding. |
| **Functional Requirements** | FR-DAG-06: Display the expected-state diagram on Easy and Medium difficulty levels only.<br>FR-DAG-07: The expected-state diagram shall be static and shall not update in response to student commands.<br>FR-DAG-08: The expected-state diagram shall update between scenario steps only after the current step is completed.<br>FR-DAG-09: The expected-state diagram shall be absent at Hard difficulty level.<br>FR-DAG-10: Expected-state diagrams shall be generated or validated from the same structured target-state model used by the State-Based Evaluator to prevent mismatch between visual guidance and evaluation behavior. |

**UC-DAG-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Expected-State Diagram on Easy and Medium
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. The use case "View Expected-State Diagram on Easy and Medium" is inside the system boundary. Show the difficulty-level constraint as a note or condition attached to this use case. The student is the sole actor.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Expected-State Diagram Visibility by Difficulty
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the difficulty check: Easy/Medium displays expected-state diagram; Hard hides it. Show the step-completion trigger for diagram update in multi-step scenarios.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Expected-State Diagram Visibility Across Difficulty Levels
Tool: Draw.io, Figma, or equivalent
Contents: Show Easy and Medium layouts with the expected-state diagram visible and the Hard layout without it.
[PLACEHOLDER — Insert diagram here]

---

### 3.3 Receive Text-Based Repository Consequence Feedback

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-FEED-01 |
| **Use Case Name** | Receive Text-Based Repository Consequence Feedback |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | A scenario session is active at Easy difficulty level. The student has entered a command that the Repository State Simulator can process. |
| **Main Flow** | 1. Student enters a Git command during an Easy-level scenario, and the command maps to the simulator's implemented operation set.<br>2. Repository State Simulator processes the command and produces the post-command repository state.<br>3. System generates a concise state-change description from the difference between the pre-command and post-command repository states.<br>4. System displays the description in the Contextual Feedback Panel as a text companion to the live DAG.<br>5. Student reads what changed in the repository state as a result of their own command: HEAD movement, branch-pointer movement, staging-area changes, working-tree cleanliness, conflict-state changes, or no state change.<br>6. The State-Based Evaluator separately determines whether the current step target is matched; the feedback panel itself does not label the command as correct or incorrect.<br>7. The panel does not suggest the next command, reveal the correct command sequence, or compare the student's current state against hidden evaluator rules.<br>8. On the next simulator-processed command submission, the panel updates to the newest state-change description. |
| **Postconditions** | The student receives text-based consequence feedback about their own command's repository-state effect without receiving the correct answer in any form. |
| **Alternative Flows** | AF1 — Simulator-processed command produces no repository-state change: The panel displays a no-state-change message instead of a corrective hint.<br>AF2 — Unprocessable or malformed command: The terminal displays a neutral terminal-style message; the Contextual Feedback Panel is not used.<br>AF3 — Medium or Hard level: The Contextual Feedback Panel component is not rendered. |
| **Functional Requirements** | FR-FEED-01: The Contextual Feedback Panel shall be present and active on Easy difficulty level only.<br>FR-FEED-02: The panel shall display a concise text state-change description after every simulator-processed command on Easy level.<br>FR-FEED-03: The state-change description shall be generated from the pre-command and post-command repository states and may describe HEAD movement, branch-pointer movement, commit-graph changes, staging-area changes, working-tree status, conflict-state changes, or no state change.<br>FR-FEED-04: The panel shall not label the student's command as correct or incorrect, shall not suggest the next command, and shall not compare the student's state against the evaluator target.<br>FR-FEED-05: All student-facing interface surfaces, including the Contextual Feedback Panel, shall never reveal the correct command or correct command sequence, in conformance with the No-Answer Policy. The Contextual Feedback Panel shall not expose hidden evaluator rules or target-state comparisons.<br>FR-FEED-06: On each new simulator-processed command submission, the panel shall update to the newest state-change description.<br>FR-FEED-07: Unprocessable or malformed commands shall be handled through neutral terminal-style output, not through repository consequence feedback.<br>FR-FEED-08: On Medium and Hard difficulty levels, the Contextual Feedback Panel component shall not be rendered. |

**UC-FEED-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Receive Text-Based Repository Consequence Feedback
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the receiving subject. The use case "Receive Text-Based Repository Consequence Feedback" is inside the system boundary. Show the Easy-level constraint as a condition on this use case. The feedback panel is a system-rendered response to the student's command submission — show this as a consequence of "Enter and Submit a Git Command" (UC-TERM-01).
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Text-Based Repository Consequence Feedback
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the Easy-level condition, simulator command processing, pre-state/post-state diff generation, No-Answer Policy check, and panel update on the next simulator-processable command submission. Show alternative flows for no-state-change and unprocessable commands.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Contextual Feedback Panel on Easy Level
Tool: Draw.io, Figma, or equivalent
Contents: Show the Easy-level scenario workspace after a simulator-processed command with the text-based consequence feedback panel visible and answer-safe.
[PLACEHOLDER — Insert diagram here]

---

## Module 4: Adaptive Retry and Transfer Practice

**Corresponds to:** General Objective 4 — Improve students' ability to apply Git concepts to structurally changed repository scenarios rather than memorize command sequences, so that Retry Transfer Accuracy reaches at least 65% across RTA-eligible changed-variant retry sessions.

**Module Overview:** This module prevents command-sequence memorization by managing difficulty-owned variant pools and retry behavior. When a student retries after a failed scenario attempt or abandonment, the system serves a structurally different variant from the selected difficulty instance's pool when one is available and records the difficulty-instance ID, variant ID, attempt relationship, and eligibility needed to compute Retry Transfer Accuracy. A failed scenario attempt is a session-level outcome, not a command-level correctness label. The student's retry action is a use case; the RTA computation itself is an internal supporting functional requirement group, not a use case.

**Specific Objectives addressed:**
- SO 4.1 — RTA reaches ≥65% across RTA-eligible changed-variant retry sessions
- SO 4.2 — No failed scenario attempt or abandoned attempt followed by retry repeats the identical scenario variant when a structurally different valid variant exists (0% identical-variant retries when a changed variant exists)
- SO 4.3 — RTA-eligible scenario skill focuses maintain structurally distinct variants and log variant ID for every attempt (100% RTA computation integrity across eligible sessions)

---

### 4.1 Retry Scenario with a Structurally Different Variant

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-VAR-01 |
| **Use Case Name** | Retry Scenario with a Structurally Different Variant |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student has a prior scenario session for the same scenario skill focus and difficulty level that ended with status Failed or Abandoned, then starts another attempt. A variant pool exists for that difficulty instance. |
| **Main Flow** | 1. Student chooses to retry a scenario difficulty instance after a prior session ended as Failed or Abandoned.<br>2. System checks the most recent variant ID used by the student for that difficulty instance and whether the prior session outcome was Failed or Abandoned.<br>3. System selects a structurally different variant from the selected difficulty instance's available variant pool when one exists.<br>4. Variant differences may include branch names, commit topology, file state, conflict setup, file/context details, or starting repository state.<br>5. System initializes the scenario using the selected difficulty-owned variant and records the difficulty-instance ID, variant ID, and prior-session relationship through FRG-LOG-01.<br>6. Student receives a retry attempt that practices the same Git concept and difficulty level in a changed repository structure. |
| **Postconditions** | Student receives a structurally changed scenario attempt. The variant ID and prior-session relationship are available for transfer analysis. |
| **Alternative Flows** | AF1 — No structurally different valid variant is available: System may allow practice replay, but the attempt is marked ineligible for RTA and the content issue is logged for review.<br>AF2 — Student voluntarily replays after successful completion: System may select any valid variant, but the replay is not counted as RTA unless it satisfies the RTA eligibility rules in FRG-VAR-02. |
| **Functional Requirements** | FR-VAR-01: Maintain structurally distinct variants for RTA-eligible scenario skill focuses.<br>FR-VAR-02: On retry after a failed scenario attempt or abandonment, never serve the identical variant used in the immediately preceding failed or abandoned session when another valid structurally different variant exists.<br>FR-VAR-03: Store variant ID and prior-session relationship on every session record.<br>FR-VAR-04: Mark attempts ineligible for RTA if a structurally different variant was not served.<br>FR-VAR-04A: A voluntary replay after successful completion shall not be counted as RTA unless it satisfies the RTA eligibility rules in FRG-VAR-02. |

**UC-VAR-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Retry Scenario with a Structurally Different Variant
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. The use case "Retry Scenario with a Structurally Different Variant" is inside the system boundary. Show that this use case follows from a prior "Failed or Abandoned" scenario session state. Do not model RTA computation as a student use case.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Retry Scenario with a Structurally Different Variant
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the retry request, previous attempt lookup, variant comparison, changed-variant selection, RTA eligibility marking, and scenario session initialization. Show the no-available-variant alternative flow.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Retry Flow and Variant Selection State
Tool: Draw.io, Figma, or equivalent
Contents: Show the retry action from the completion/failure/return screen and the transition into a new scenario attempt with a structurally different variant.
[PLACEHOLDER — Insert diagram here]

---

### 4.2 Supporting Functional Requirement Group: Retry Transfer Accuracy Computation

| Field | Description |
|-------|-------------|
| **Requirement Group ID** | FRG-VAR-02 |
| **Requirement Group Name** | Retry Transfer Accuracy Computation from Changed-Variant Retry Sessions |
| **Classification** | Supporting functional requirement group, not a student-initiated use case |
| **External Actor** | None. The computation is triggered by scenario session records. |
| **Triggering Events** | Scenario retry after a Failed or Abandoned prior session;<br>scenario completion;<br>scenario abandonment;<br>dashboard KPI refresh. |
| **System Responsibilities** | 1. Identify whether the current retry session is RTA-eligible.<br>2. Exclude first-ever encounters for a scenario skill focus and difficulty level.<br>3. Include only sessions that follow a prior Failed or Abandoned session for the same scenario skill focus and difficulty level.<br>4. Include only sessions where a structurally changed variant from the same difficulty instance's variant pool was served.<br>5. Record successful RTA only when the changed-variant retry session is completed without non-target-matching, unprocessable, or invalid submissions.<br>6. Aggregate RTA across the active published scenario library and, when applicable, by active learning unit, scenario skill focus, and difficulty level. |
| **Postconditions** | RTA is computable from valid RTA-eligible changed-variant retry sessions only. Dashboard indicators can display log-derived RTA values. |
| **Exception Handling** | EX1 — Missing variant ID: Session is excluded from RTA computation and flagged for data review.<br>EX2 — Changed variant is abandoned: Session remains RTA-eligible but is counted as unsuccessful for RTA.<br>EX3 — Student completes the changed variant after one or more non-target-matching submissions: Session is counted as completed practice but not as a successful RTA session. |
| **Functional Requirements** | FR-VAR-05: The system shall exclude first-ever encounters from RTA computation.<br>FR-VAR-06: The system shall include only structurally changed retry sessions that follow a prior session with status Failed or Abandoned in RTA computation.<br>FR-VAR-07: The system shall count an RTA success only when the changed-variant retry session is completed without any non-target-matching, unprocessable, or invalid command submission during that changed exposure.<br>FR-VAR-08: The system shall aggregate RTA across the active published scenario library and, when applicable, by active learning unit and scenario skill focus.<br>FR-VAR-09: The system shall exclude attempts from RTA when variant identity, prior-session relationship, or changed-variant status cannot be determined from logs. |
| **Diagram Guidance** | Do not create a standalone use case diagram for RTA computation. If documentation requires a diagram, represent RTA computation as part of an activity, sequence, or data-flow diagram connected to scenario retry, session logging, and dashboard KPI display. |
---

## Module 5: Progress Tracking and Self-Monitoring

**Corresponds to:** General Objective 5 — Improve students' ability to monitor their own Git practice progress through visible, log-derived progress indicators on the student dashboard, so that all displayed KPI values accurately reflect system-generated session logs and Scenario Abandonment Rate remains at or below 20% across the active published scenario library.

**Module Overview:** This module covers supporting session/step logging, student dashboard indicators, unit-card lesson expansion, Review button visibility, and dashboard routing to Review Mode. All dashboard and progress data are derived from system-generated logs. The module supports progress self-monitoring and engagement continuity through visible completion status, KPI indicators, retry trends, streaks, and scenario access states. Logging is a system responsibility required for progress tracking and KPI computation; it is not modeled as a use case because the student does not initiate "logging" as an independent goal.

**Specific Objectives addressed:**
- SO 5.1 — Student dashboard values are computed from system-generated session and step logs and match source logs across the approved dashboard acceptance test set (100% log-display match accuracy)
- SO 5.2 — Scenario Abandonment Rate remains ≤20% across the active published scenario library (SAR ≤ 20%)
- SO 5.3 — Abandonment patterns are reported per active learning unit where session volume permits, enabling evidence-based refinement of scenario content and difficulty configurations (SAR ≤ 20% per active unit where data is available)

---

### 5.1 Supporting Functional Requirement Group: Scenario Session and Step Logging

| Field | Description |
|-------|-------------|
| **Requirement Group ID** | FRG-LOG-01 |
| **Requirement Group Name** | Scenario Session and Step Logging |
| **Classification** | Supporting functional requirement group, not a student-initiated use case |
| **External Actor** | None. Logging is automatically triggered by student-facing use cases such as Load Scenario Instance, Enter and Submit a Git Command, Complete Scenario, Retry Scenario, Review Mode session initialization, and dashboard access checks. |
| **Triggering Events** | Scenario load;<br>command submission;<br>command evaluation;<br>scenario completion;<br>scenario failure;<br>scenario abandonment;<br>scenario retry;<br>Review Mode session start;<br>dashboard KPI refresh. |
| **System Responsibilities** | 1. Create a session record on scenario start.<br>2. Write a step log entry after each command execution.<br>3. Update the session record on completion, failure, abandonment, or retry.<br>4. Store variant IDs and prior-session references where applicable.<br>5. Tag Review Mode sessions separately from primary scenario attempts.<br>6. Preserve all data needed for OLCR, SCR, ARC, CAR, HLCR, RTA, SAR, Review Mode SCR, dashboard progress, first-attempt stars, and streaks.<br>7. Preserve command-count policy snapshots, command classifications, counted action-command totals, and non-counted diagnostic command totals required for CAR and remaining counted-command calculations. |
| **Postconditions** | Student activity required for progress display and KPI computation is recorded in a queryable format. |
| **Exception Handling** | EX1 — Database write failure: System retries the write up to 3 times. If all retries fail, the failure is logged server-side and the student's session continues when possible.<br>EX2 — Missing required log field: System marks the affected KPI computation as unavailable rather than displaying a misleading zero value. |
| **Functional Requirements** | FR-LOG-01: The system shall create a session record on scenario load capturing student ID, learning unit ID, scenario ID, difficulty-instance ID, difficulty level, variant ID, source entry point, session mode, prior-session reference when applicable, and start timestamp.<br>FR-LOG-02: The system shall write a step log entry after every command submission, including TargetMatched, TargetNotYetMatched, Unprocessable, and Invalid results. TargetNotYetMatched is a step-level result and shall not by itself set the whole scenario session to Failed.<br>FR-LOG-03: Step log entries shall record the command entered, evaluation result category, command classification, counted-command increment value, attempt number for the current step, resulting state hash when applicable, expected target state hash when applicable, and timestamp.<br>FR-LOG-04: The system shall persist total attempts, total counted action commands, total non-counted diagnostic commands, total retries, completion status, failure status, abandonment status, difficulty-instance ID, variant ID, command-count policy ID or snapshot, and first-attempt-star eligibility on session completion, failure, or abandonment.<br>FR-LOG-05: The system shall flag a session as RTA-eligible only when: (a) the session is not the student's first-ever session for that scenario skill focus and difficulty level, (b) the student has a prior session with status Failed or Abandoned for the same scenario skill focus and difficulty level, and (c) the served variant is structurally different from the relevant prior Failed or Abandoned session within the same difficulty instance.<br>FR-LOG-06: The RTA success flag shall be set to true only when the RTA-eligible changed-variant retry session is completed without any non-target-matching, unprocessable, or invalid command submission.<br>FR-LOG-07: The system shall log orientation-complete-at-start for each first-session start as a non-blocking boolean field confirming whether all Unit 1 orientation lessons were complete at the time of scenario initialization.<br>FR-LOG-08: All log writes shall be atomic to prevent partial records.<br>FR-LOG-09: Abandoned session data shall be retained and clearly marked as Abandoned.<br>FR-LOG-10: Review Mode sessions shall be tagged separately from primary scenario attempts so Review Mode SCR can be computed independently from primary SCR, CAR, RTA, and progression records. |
| **Diagram Guidance** | Do not create a standalone use case diagram for logging. If documentation requires a diagram, show logging as part of activity or sequence diagrams for scenario loading, command evaluation, completion, retry, Review Mode, and dashboard computation. |
---

### 5.2 View Student Dashboard and Expand Unit Scenarios

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DASH-01 |
| **Use Case Name** | View Student Dashboard and Expand Unit Scenarios |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is logged in and navigates to /dashboard or the Dashboard/Units tab. |
| **Main Flow** | 1. Student navigates to the Student Dashboard.<br>2. System retrieves the student's unit completion records, scenario completion records, streak data, first-attempt star flags, retry-count trends, Hard-level completion indicators, RTA progress, and session log aggregates from the database.<br>3. System renders dashboard summary indicators and one card for each published learning unit.<br>4. Each unit card displays unit title, short description, progress bar, scenario count or orientation status, and an expand/collapse control.<br>5. Student expands a unit card.<br>6. For Unit 1, system displays orientation lesson rows.<br>7. For scenario-bearing units, system displays Scenario Skill Focus cards directly inside the expanded unit container, each with Easy/Medium/Hard action states.<br>8. Student may open an optional reference lesson, but Start/Continue/Review/Retry actions come from Scenario Skill Focus cards and open the Skill Focus Preview first.<br>9. System displays the active streak counter, first-attempt star indicators, retry-count trends, KPI summary indicators, and improvement indicators derived exclusively from logs. |
| **Postconditions** | Student sees current learning status, progress bars, KPI summary indicators, improvement indicators, expanded unit Scenario Skill Focus cards, difficulty access states, and review access for completed scenario difficulties. |
| **Alternative Flows** | AF1 — Newly registered student with no progress data: All scenario instances show as Not Started, streak counter is 0, KPI indicators display No data available, progress bars display 0%, and no Review buttons are visible.<br>AF2 — Student collapses unit card: System hides the lesson list while preserving dashboard summary data.<br>AF3 — Unit has no published lessons: System displays an empty-state message under the expanded unit card. |
| **Functional Requirements** | FR-DASH-01: Display a unit card for each published learning unit.<br>FR-DASH-02: Display per-scenario completion status at each difficulty level (Easy/Medium/Hard) on unit-level Scenario Skill Focus cards.<br>FR-DASH-03: Display the active streak counter updated after each completed scenario session.<br>FR-DASH-04: Display first-attempt star indicators for qualifying scenario completions with no non-target-matching, unprocessable, or invalid command submissions during the entire session.<br>FR-DASH-05: Display retry-count trends per scenario derived from completed and abandoned session logs; when insufficient historical data exists, display No trend available.<br>FR-DASH-06: Each unit card shall include a progress bar displaying the percentage of scenario instances completed out of the total instances in that unit across all three difficulty levels.<br>FR-DASH-07: Display KPI summary indicators for the active published scenario library and, when data is available, for each active learning unit using OLCR, SCR, ARC, CAR, HLCR, RTA, and SAR values derived exclusively from session logs; when a KPI denominator is zero, display No data available rather than 0%. During acceptance testing, displayed KPI values shall match the corresponding source logs for the approved test cases.<br>FR-DASH-08: Display a Review button on each completed scenario difficulty instance and open the Skill Focus Preview before entering playable Review Mode.<br>FR-DASH-09: For any active learning unit or scenario skill focus with incomplete scenarios, high retry counts, low Hard-level completion, or unmet transfer targets, render a visual improvement indicator adjacent to the KPI summary indicator.<br>FR-DASH-09A: The Dashboard/Units tab shall support expanding a unit card to display unit-level Scenario Skill Focus cards for scenario-bearing units.<br>FR-DASH-09B: The expanded unit card may display optional reference lesson links separately from the primary scenario access path. |

**UC-DASH-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Student Dashboard and Expand Unit Scenarios
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor as the initiating subject. Include use cases "View Student Dashboard," "Expand Unit Card," and "Select Scenario Difficulty" inside the system boundary. Show that the student may optionally trigger "Access Review Mode from Dashboard or Completion Screen" (UC-DASH-05) from the dashboard. No system actor appears as a primary initiator.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Dashboard Units Tab and Unit Card Expansion
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show dashboard load, unit cards rendering, unit expansion, Unit 1 orientation lesson display, scenario-bearing unit Scenario Skill Focus card display, difficulty action selection, Skill Focus Preview opening, locked-state handling, and transition to scenario instance loading.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Dashboard/Units Tab with Expanded Unit Card
Tool: Draw.io, Figma, or equivalent
Contents: Show unit cards, one expanded scenario-bearing unit card with Scenario Skill Focus cards underneath, difficulty action buttons, completion indicators, retry indicators, Review buttons, and a Skill Focus Preview modal before workspace routing.
[PLACEHOLDER — Insert diagram here]

---

### 5.3 Access Review Mode from Dashboard or Completion Screen

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-DASH-05 |
| **Use Case Name** | Access Review Mode from Dashboard or Completion Screen |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | The student is viewing the dashboard/unit Scenario Skill Focus card or a scenario completion screen. At least one completed session exists for the selected scenario difficulty instance. |
| **Main Flow** | 1. Student views a scenario difficulty instance that has already been completed.<br>2. System displays a Review button for that completed scenario difficulty instance.<br>3. Student clicks the Review button.<br>4. System opens the Skill Focus Preview modal for the selected Scenario Skill Focus and difficulty.<br>5. Student chooses Start Practice or Skip in the modal.<br>6. System validates that the selected scenario difficulty has at least one completed session for the student.<br>7. System routes the student to UC-REVIEW-01 under Module 2 to start a playable Review Mode session. |
| **Postconditions** | The student is routed to playable Review Mode for the selected completed scenario difficulty instance after the Skill Focus Preview. |
| **Alternative Flows** | AF1 — No completed session exists: System does not display the Review button.<br>AF2 — Direct route access without completion: System rejects the request and returns the student to the dashboard or scenario list. |
| **Functional Requirements** | FR-DASH-23: Display a Review button only for scenario difficulty instances completed by the student.<br>FR-DASH-24: Allow Review Mode access from the dashboard/unit Scenario Skill Focus card and from the completion screen.<br>FR-DASH-25: Validate completion ownership before routing the student to Review Mode.<br>FR-DASH-26: Route valid Review actions through the Skill Focus Preview before starting the playable Review Mode session behavior specified in UC-REVIEW-01 under Module 2.<br>FR-DASH-27: Preserve dashboard progress records when the student starts Review Mode; Review Mode attempts shall be logged separately through FRG-LOG-01. |

**UC-DASH-05 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Access Review Mode from Dashboard or Completion Screen
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor initiating Review Mode access from either the dashboard/unit scenario card or completion screen. Show that valid access leads to "Re-attempt a Completed Scenario in Review Mode" under Module 2.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Access Review Mode from Dashboard or Completion Screen
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show dashboard or completion screen display, completed-session check, Review button visibility, click action, access validation, and routing to Review Mode.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Review Button on Completed Scenario Difficulty
Tool: Draw.io, Figma, or equivalent
Contents: Show the Review button on a completed scenario difficulty card and on the completion screen, leading to the Review Mode Scenario Practice Workspace.
[PLACEHOLDER — Insert diagram here]

---

## Module 6: Administrative Management *(Planned Phase 2 / Next-Semester Scope)*

**Corresponds to:** Planned Phase 2 / next-semester scope only. This module is outside the current-release MVP scope and does not correspond to any General Objective.

**Module Overview:** This planned Phase 2 module consolidates all non-student administrative capabilities into one restricted Administrative Management area. In this system, the administrator is the single authorized non-student platform operator for the capstone deployment. Learning analytics, student access maintenance, lesson maintenance, scenario and variant management, and audit-log review belong under this one module. Administrative Management shall not be counted as part of current-release MVP completion, evaluation, or KPI computation. The approved starter content library is pre-authored and seeded before deployment; content modification through an administrator interface is introduced only through this planned Phase 2 module.

---

### 6.1 Administrator Login

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-01 |
| **Use Case Name** | Administrator Login |
| **Actor(s)** | Administrator |
| **Preconditions** | An administrator account has been provisioned prior to deployment. The /admin/login page is accessible. Administrative Management has been enabled. |
| **Main Flow** | 1. Administrator navigates to /admin/login.<br>2. System displays the administrator login form: email address and password.<br>3. Administrator submits credentials.<br>4. System verifies that the account carries the Administrator role.<br>5. System verifies the password against the stored hash.<br>6. System generates an administrator-scoped access token and refresh token.<br>7. System stores the refresh token in an httpOnly, Secure, SameSite=Strict cookie.<br>8. System returns the access token and administrator profile to the frontend.<br>9. Frontend redirects to /admin/dashboard. |
| **Postconditions** | The administrator is authenticated and lands on the Administrative Management dashboard. |
| **Alternative Flows** | AF1 — Invalid credentials: HTTP 401; "Invalid email or password."<br>AF2 — Account exists but is not assigned the Administrator role: HTTP 403.<br>AF3 — Self-registration attempt: The /admin/register endpoint does not exist; administrator accounts are provisioned outside student self-registration. |
| **Functional Requirements** | FR-ADMIN-01: Provide a restricted administrator login endpoint (/admin/login) distinct from the student login endpoint.<br>FR-ADMIN-02: Authenticate only accounts carrying the Administrator role; reject Student-role accounts with HTTP 403.<br>FR-ADMIN-03: Administrator accounts shall be provisioned outside the student self-registration flow.<br>FR-ADMIN-04: Issue administrator-scoped JWT tokens on successful administrator login.<br>FR-ADMIN-05: Administrative endpoints shall reject Student-scoped tokens with HTTP 403. |

**UC-ADMIN-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Administrator Login
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor as the initiating subject. The use case "Administrator Login" is inside the system boundary.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Administrator Login
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the step-by-step main flow and alternative flows, including decision nodes and swim lanes.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrator Login Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show the administrator login form and post-login redirect to /admin/dashboard.
[PLACEHOLDER — Insert diagram here]

---

### 6.2 View Learning Analytics Dashboard

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-02 |
| **Use Case Name** | View Learning Analytics Dashboard |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated and has navigated to /admin/dashboard. Administrative Management has been enabled. |
| **Main Flow** | 1. Administrator navigates to /admin/dashboard.<br>2. System queries session and step log records and computes cohort-level KPIs: (a) Average SCR across the active published scenario library and difficulty levels. (b) Average ARC trend over time. (c) Aggregate RTA — proportion of RTA-flagged sessions that were successful changed-variant attempts. (d) Hard-Level Completion Rate by active learning unit and scenario skill focus when data is available. (e) Most-retried scenarios ranked by average retry count. (f) Drop-off points showing which step number students most commonly abandon within each scenario.<br>3. System renders the learning analytics dashboard.<br>4. Administrator may click on a student entry to view individual student progress details. |
| **Postconditions** | Administrator has a current read-only analytics view derived from system-generated learning logs. |
| **Alternative Flows** | AF1 — No session logs exist: System displays "No learning data available yet."<br>AF2 — KPI query fails: System displays an error message and does not modify any record. |
| **Functional Requirements** | FR-ADMIN-06: Display cohort-level KPIs: SCR, ARC trend, RTA, HLCR by active learning unit and scenario skill focus when data is available, most-retried scenarios, and drop-off points.<br>FR-ADMIN-07: Display per-student KPI details when the administrator selects a student record.<br>FR-ADMIN-08: All learning analytics shall be derived exclusively from system-generated session and step logs; no manual KPI entry shall be possible.<br>FR-ADMIN-09: The analytics dashboard shall not modify student learning records.<br>FR-ADMIN-10: The RTA metric displayed in Administrative Management shall apply the same exclusion, eligibility, and success rules used by the student progress module. |

**UC-ADMIN-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Learning Analytics Dashboard
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor viewing the dashboard.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — View Learning Analytics Dashboard
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the step-by-step main flow and alternative flows.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrative Learning Analytics Dashboard
Tool: Draw.io, Figma, or equivalent
Contents: Show KPI summary cards, cohort SCR, ARC trend, RTA, HLCR, most-retried scenarios, drop-off point data, and individual student drill-down.
[PLACEHOLDER — Insert diagram here]

---

### 6.3 Manage Student Accounts and Access

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-03 |
| **Use Case Name** | Manage Student Accounts and Access |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated. Administrative Management has been enabled. Student accounts exist or are pending review. |
| **Main Flow** | 1. Administrator opens the student account management screen.<br>2. System displays a searchable list of student accounts.<br>3. Administrator selects a student account.<br>4. System displays account status and basic profile details.<br>5. Administrator activates, deactivates, or restores the selected student account.<br>6. System validates the action.<br>7. System saves the change and records the administrative action in the audit log. |
| **Postconditions** | The selected student account access status is updated, and the administrative action is logged. |
| **Alternative Flows** | AF1 — Student account cannot be found: System displays a not-found message and does not modify records.<br>AF2 — Invalid action: System rejects the action and displays a validation message.<br>AF3 — Administrator attempts to modify own administrator role through this screen: System rejects the action. |
| **Functional Requirements** | FR-ADMIN-11: Allow the administrator to view student account status and basic profile details.<br>FR-ADMIN-12: Allow the administrator to activate, deactivate, or restore student accounts.<br>FR-ADMIN-13: Prevent student-account actions from modifying administrator credentials or administrator role status.<br>FR-ADMIN-14: Record every student account access change in the administrative audit log with actor, action type, affected record, timestamp, and result. |

**UC-ADMIN-03 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Manage Student Accounts and Access
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor managing student accounts.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Manage Student Accounts and Access
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show account search, selection, status action, validation, save, and audit log recording.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrative Student Account Management Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show the student list, search, account status display, action controls, and confirmation state.
[PLACEHOLDER — Insert diagram here]

---

### 6.4 Manage Learning Units and Lesson Content

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-04 |
| **Use Case Name** | Manage Learning Units and Lesson Content |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated. Administrative Management has been enabled. The starter content library has been seeded before deployment. |
| **Main Flow** | 1. Administrator opens the Learning Unit Management screen.<br>2. System displays the existing learning content units in the active content library.<br>3. Administrator chooses to add a new learning unit or edit an existing learning unit.<br>4. System displays editable unit fields, including unit title, unit description, ordering, publication status, and content-source label.<br>5. Administrator opens the Lesson content area for the selected learning unit.<br>6. System displays an AI-assisted Lesson authoring interface containing: (a) an AI Lesson Assistant chat panel, (b) a Code Editor with an internal HTML/CSS toggle, and (c) a Preview panel.<br>7. Administrator may manually edit the Lesson HTML and scoped CSS through the Code Editor, or may request AI assistance through UC-AI-02 to generate or revise the HTML/CSS content.<br>8. If AI assistance is used, the system displays the AI explanation in the chat panel and presents proposed HTML/CSS changes for administrator review; AI output is not saved or published automatically.<br>9. Administrator previews the rendered Lesson as it will appear to students.<br>10. Administrator saves the Lesson as draft or publishes it.<br>11. System sanitizes the HTML, scopes CSS to the Lesson container, validates that the content does not expose scenario answers, saves the approved change, and records the administrative action in the audit log. |
| **Postconditions** | A learning unit and its Lesson HTML/CSS content are created, updated, archived, restored, saved as draft, or published, and the administrative action is logged. |
| **Alternative Flows** | AF1 — Administrator attempts to delete a learning unit with existing scenario/session records: System prevents deletion and offers archive or draft/unpublish actions instead.<br>AF2 — Content violates the No-Answer Policy: System rejects publication and displays a validation message.<br>AF3 — Administrator cancels editing: System discards unsaved changes after confirmation.<br>AF4 — Administrator creates a new learning unit: System labels the learning unit as a content extension and excludes it from original KPI targets unless the evaluation framework is formally revised.<br>AF5 — Administrator imports AI-generated Lesson content: System presents proposed HTML and scoped CSS changes in the editor/preview workflow and still requires administrator review and publication.<br>AF6 — HTML or CSS contains unsafe content: System blocks scripts, unsafe attributes, unsafe external embeds, or CSS rules that can affect application areas outside the Lesson container. |
| **Functional Requirements** | FR-ADMIN-15: Allow the administrator to create, edit, archive, restore, save as draft, and publish learning content units.<br>FR-ADMIN-16: Allow the administrator to maintain Lesson content for each learning unit as HTML and scoped CSS.<br>FR-ADMIN-17: Label learning units by content source or status.<br>FR-ADMIN-18: Validate that published unit and Lesson content does not expose correct scenario commands or command sequences.<br>FR-ADMIN-19: Record every learning-unit and Lesson content change in the administrative audit log.<br>FR-ADMIN-20: Provide a Lesson Code Editor with an internal HTML/CSS toggle and a rendered Preview panel.<br>FR-ADMIN-21: Sanitize Lesson HTML before saving or rendering and block scripts, unsafe attributes, and unsafe embeds.<br>FR-ADMIN-22: Scope Lesson CSS to the Lesson container so that administrator-authored CSS cannot affect unrelated application pages or layout components.<br>FR-ADMIN-23: Allow AI-generated Lesson HTML/CSS drafts from UC-AI-02 to be reviewed, edited, previewed, accepted, discarded, saved, or published by the administrator, but prevent direct AI publication without administrator approval. |

**UC-ADMIN-04 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Manage Learning Units and Lesson Content
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor; include unit creation/editing, Lesson HTML/CSS editing, previewing, saving/publishing, and an <<extend>> relationship from Generate Lesson HTML/CSS Draft Using AI Assistance (UC-AI-02) when AI assistance is enabled.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Manage Learning Units and Lesson Content
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the administrator selecting or creating a learning unit, opening the Lesson HTML/CSS editor, optionally requesting AI assistance, reviewing proposed HTML/CSS changes, previewing rendered output, validating No-Answer Policy and HTML/CSS safety rules, saving/publishing, and logging the action.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrative Learning Unit and Lesson Management Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show learning unit list, create/edit unit controls, AI Lesson Assistant chat panel, Code Editor with HTML/CSS toggle, Preview panel, proposed-change controls, draft/publish controls, validation messages, and audit-log confirmation state.
[PLACEHOLDER — Insert diagram here]

---

### 6.5 Add or Edit Scenario Content

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-05 |
| **Use Case Name** | Add or Edit Scenario Content |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated. Administrative Management has been enabled. At least one learning content unit exists in the system. |
| **Main Flow** | 1. Administrator opens the Scenario Management screen.<br>2. System displays existing learning units and their scenario lists.<br>3. Administrator selects a learning unit and chooses to add a new scenario or edit an existing scenario skill focus.<br>4. System displays the Scenario Builder form with editable fields for the shared scenario skill focus plus separate Easy, Medium, and Hard difficulty-instance tabs. Each difficulty tab contains its own narrative context, student task prompt, simulator operation scope, initial repository state setup, target repository state rules, difficulty-level scaffolding settings, command-count policy values, contextual feedback drafts when applicable, expected-state diagram behavior, and difficulty-specific variant pool.<br>5. Administrator defines or edits each difficulty instance's initial repository state using a structured state builder or setup-command sequence.<br>6. Administrator defines or edits each difficulty instance's target repository state using a structured target-state builder or an administrator-only reference solution sequence; the system stores the resulting target state for evaluation rather than command-string matching.<br>7. System renders the Live DAG preview from each difficulty variant's initial repository state and renders the Expected-State Diagram preview from that difficulty instance's target repository state when the difficulty's scaffolding allows it.<br>8. Administrator defines or edits Easy, Medium, and Hard difficulty instances, assigns the correct scaffolding visibility for each level, configures each difficulty instance's minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns, and confirms that each difficulty has a valid variant pool.<br>9. Administrator defines structurally distinct difficulty variants inside the relevant difficulty instance, or imports an AI-generated structured scenario draft from UC-AI-03 into the Scenario Builder form for review.<br>10. Administrator saves the scenario as draft or submits it for publication.<br>11. System validates that required fields are complete, the scenario is assigned to a valid learning unit, all required difficulty instances are present, every published difficulty instance has at least one valid variant and every RTA-eligible difficulty instance has structurally distinct variants, difficulty-to-variant relationships are valid, state definitions are internally consistent, target states are reachable using the simulator's implemented Git operation set, and No-Answer Policy constraints are satisfied.<br>12. System saves or publishes the scenario only if validation passes.<br>13. System records the administrative action in the audit log. |
| **Postconditions** | The scenario is saved as draft, updated, archived, restored, or published under the selected learning unit, and the administrative action is logged. |
| **Alternative Flows** | AF1 — Required scenario fields are incomplete: System rejects saving or publication and identifies the missing fields.<br>AF2 — A difficulty variant pool is incomplete or not structurally distinct for an RTA-eligible difficulty: System rejects publication until the administrator supplies valid variants under the affected difficulty instance.<br>AF3 — Content exposes a correct command or command sequence on a student-facing surface: System rejects publication.<br>AF4 — No suitable learning unit exists: Administrator creates or edits a learning unit through UC-ADMIN-04, then returns to scenario authoring.<br>AF5 — Administrator imports AI-generated draft content: System loads structured AI draft values into the Scenario Builder form and still requires administrator review and publication.<br>AF6 — Initial or target repository state for any difficulty instance cannot be simulated, compared, or rendered as a DAG: System rejects publication and identifies the invalid difficulty instance and state definition. |
| **Functional Requirements** | FR-ADMIN-24: Allow the administrator to create, edit, archive, restore, and publish scenario skill focus records under selected learning units.<br>FR-ADMIN-25: Require each published scenario skill focus to belong to exactly one learning unit and, when the current schema keeps lesson linkage, to one related reference/scenario-bearing lesson without making that lesson the primary student access path.<br>FR-ADMIN-25A: Allow the administrator to author public Scenario Skill Focus preview data, including title, short explanation, skill focus type, primary focus command/s, supporting inspection command/s, safe demo commands, demo repository/DAG state, demo explanation content, and related Git concepts.<br>FR-ADMIN-25B: Prevent Scenario Skill Focus records from storing or exposing actual scenario narratives, actual repository states, actual branch/file names, target-state rules, exact solution command sequences, hidden evaluator rules, or hidden solution notes.<br>FR-ADMIN-26: Require every published scenario skill focus to have Easy, Medium, and Hard difficulty instances, each with a valid command-count policy and at least one valid difficulty-owned variant.<br>FR-ADMIN-26A: Allow the administrator to author the minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns for each scenario difficulty instance.<br>FR-ADMIN-26B: Allow the administrator to author separate narrative context, student task prompt, initial repository state, target-state rule, expected-state behavior, scaffolding configuration, simulator operation scope, variant pool, and internal/admin solution notes for each Easy, Medium, and Hard difficulty instance.<br>FR-ADMIN-27: Require RTA-eligible published difficulty instances to maintain structurally distinct difficulty-owned variants sufficient to prevent immediate identical retry repetition and support transfer measurement.<br>FR-ADMIN-28: Validate that each difficulty instance's state definitions are internally consistent, reachable through the simulator's implemented Git operation set, and usable by the State-Based Evaluator before publication.<br>FR-ADMIN-29: Validate that student-facing scenario content does not expose correct commands or correct command sequences.<br>FR-ADMIN-30: Allow AI-generated scenario drafts from UC-AI-03 to populate editable Scenario Builder fields, but prevent direct AI publication without administrator review.<br>FR-ADMIN-31: Generate Live DAG and Expected-State Diagram previews from the same structured repository-state definitions used for simulation and evaluation for the selected difficulty instance and variant.<br>FR-ADMIN-32: Record every scenario-management action in the administrative audit log. |

**UC-ADMIN-05 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Add or Edit Scenario Content
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor; include scenario creation/editing; show an <<extend>> relationship from Generate Scenario Draft Using AI Assistance (UC-AI-03) when AI assistance is enabled.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Add or Edit Scenario Content
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the administrator selecting a learning unit, entering scenario details, defining initial and target repository states, previewing generated DAG diagrams, optionally importing a structured AI draft, defining difficulty instances, command-count policies, and variants, validating, saving/publishing, and logging.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrative Scenario Management Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show learning unit selector, scenario list, Scenario Builder form, AI assistant side panel, initial/target repository state builders, Live DAG preview, Expected-State Diagram preview, difficulty-level tabs, command-count policy fields, variant editor, and draft/publish controls.
[PLACEHOLDER — Insert diagram here]

---

### 6.6 View Administrative Audit Logs

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-ADMIN-06 |
| **Use Case Name** | View Administrative Audit Logs |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated. Administrative Management has been enabled. At least one administrative action has been logged. |
| **Main Flow** | 1. Administrator opens the audit log screen.<br>2. System displays administrative actions with timestamp, actor, action type, affected record, and result.<br>3. Administrator filters logs by date range, action type, affected record, or result.<br>4. System displays the filtered results. |
| **Postconditions** | Administrator has reviewed administrative actions without modifying learning records. |
| **Alternative Flows** | AF1 — No audit logs match the filter: System displays an empty-state message.<br>AF2 — Unauthorized access attempt: System rejects the request with HTTP 403. |
| **Functional Requirements** | FR-ADMIN-33: Provide a read-only audit log screen for Administrator users.<br>FR-ADMIN-34: Display timestamp, actor, action type, affected record, and result for each administrative action.<br>FR-ADMIN-35: Support filtering audit logs by date range, action type, affected record, and result.<br>FR-ADMIN-36: Prevent audit log modification through the user interface. |

**UC-ADMIN-06 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — View Administrative Audit Logs
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor viewing the read-only audit log.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — View Administrative Audit Logs
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the administrator navigating to audit logs, applying filters, and viewing results.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Administrative Audit Log Screen
Tool: Draw.io, Figma, or equivalent
Contents: Show the log list with timestamp, actor, action type, affected record, result, and filter controls.
[PLACEHOLDER — Insert diagram here]

---

## Module 7: AI-Assisted Learning Support *(Planned Phase 2 / Next-Semester Scope)*

**Corresponds to:** Planned Phase 2 / next-semester scope only. This module is outside the current-release MVP scope and does not correspond to any General Objective.

**Module Overview:** This planned Phase 2 module covers AI-supported conceptual assistance, AI-assisted Lesson HTML/CSS drafting, and AI-assisted scenario drafting. It shall not be implemented, evaluated, or included in KPI computation as part of the current-release MVP. Any Phase 2 AI feature must preserve the No-Answer Policy. The AI chatbot supports student conceptual questions on Lesson screens. The administrative AI drafting features are connected to Administrative Management: AI may generate Lesson HTML/CSS drafts, structured scenario drafts, and variant drafts, but it shall not publish content directly. Publication of all AI-generated content must occur through UC-ADMIN-04 or UC-ADMIN-05 after administrator review and validation.

---

### 7.1 Query AI Chatbot for Conceptual Git Assistance

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AI-01 |
| **Use Case Name** | Query AI Chatbot for Conceptual Git Assistance |
| **Actor(s)** | Authenticated Student |
| **Preconditions** | Student is on a Lesson screen (UC-DASH-02). The AI chatbot feature has been enabled. |
| **Main Flow** | 1. Student types a conceptual Git question into the chatbot input on the Lesson screen.<br>2. System sends the question and the current unit's concept context to the AI backend.<br>3. AI backend returns a response addressing the student's conceptual question.<br>4. Chatbot displays the response in the chat panel on the Lesson screen.<br>5. The chatbot operates strictly within conceptual Git education scope; it shall not provide scenario answers, reveal correct commands for any scenario, or violate the No-Answer Policy. |
| **Postconditions** | Student has received a conceptual clarification. No scenario session data is modified. |
| **Alternative Flows** | AF1 — Student asks a scenario-specific question that would reveal a correct command: Chatbot declines to answer in conformance with the No-Answer Policy and redirects the student to the relevant concept explanation. |
| **Functional Requirements** | FR-AI-01: Provide an AI chatbot interface on Lesson screens for conceptual Git questions.<br>FR-AI-02: The AI chatbot shall not provide scenario-specific answers, command hints, or any information that would violate the No-Answer Policy.<br>FR-AI-03: The chatbot shall be scoped to the conceptual Git topic of the current unit. |

**UC-AI-01 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Query AI Chatbot for Conceptual Git Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Authenticated Student** actor initiating the query; the chatbot use case is inside the system boundary; show <<include>> from the Lesson context.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Query AI Chatbot for Conceptual Git Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show student question, AI processing, No-Answer Policy check, chatbot response, and the scenario-answer-refusal alternative flow.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — Lesson with AI Chatbot Panel
Tool: Draw.io, Figma, or equivalent
Contents: Show the Lesson page with the AI chatbot panel, question input, and response area.
[PLACEHOLDER — Insert diagram here]

---

### 7.2 Generate Lesson HTML/CSS Draft Using AI Assistance

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AI-02 |
| **Use Case Name** | Generate Lesson HTML/CSS Draft Using AI Assistance |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated and is in the Lesson authoring workflow under UC-ADMIN-04. The AI Lesson drafting feature has been enabled. |
| **Main Flow** | 1. Administrator opens the AI Lesson Assistant chat panel from the Lesson editor.<br>2. System displays the AI Lesson Assistant alongside the Code Editor and Preview panel.<br>3. Administrator enters a drafting or revision request, such as a target learning unit, conceptual topic, desired content structure, or proposed HTML/CSS changes.<br>4. System sends the request and relevant content context to the AI backend.<br>5. AI backend returns two coordinated outputs: (a) a conversational response in the chat panel explaining the proposed changes and accepting revision requests, and (b) proposed HTML and scoped CSS updates that may be inserted into the Lesson Code Editor after administrator approval.<br>6. System presents the proposed HTML/CSS changes alongside the current Code Editor content for comparison.<br>7. Administrator reviews the proposed changes, may apply, partially apply, edit, or discard them, and may request further revisions from the AI.<br>8. If changes are applied, system inserts them into the Code Editor; the administrator then previews, validates (No-Answer Policy, HTML/CSS safety), and saves or publishes through UC-ADMIN-04. |
| **Postconditions** | A proposed Lesson HTML/CSS draft has been generated and is available in the Code Editor for administrator review. No Lesson content has been published directly by AI. |
| **Alternative Flows** | AF1 — AI output contains scenario-specific answers or violates the No-Answer Policy: System flags the violation; administrator must remove the violating content before saving or publishing.<br>AF2 — AI output contains unsafe HTML or CSS: System blocks the unsafe content and displays a warning.<br>AF3 — Administrator rejects the draft: Administrator may regenerate with adjusted parameters or continue editing manually. |
| **Functional Requirements** | FR-AI-04: Provide an AI-assisted Lesson drafting interface accessible to Administrator users only when the AI feature is enabled.<br>FR-AI-05: Provide an AI assistant chat panel that explains proposed changes and accepts revision requests.<br>FR-AI-06: Generate proposed Lesson content as editable HTML and scoped CSS, not as separate structured lesson-summary fields.<br>FR-AI-07: Allow the AI to propose coordinated HTML and CSS changes in a single generation or revision action.<br>FR-AI-08: Display proposed AI-generated HTML/CSS changes for administrator review before they become the current Lesson draft.<br>FR-AI-09: AI-generated Lesson HTML/CSS drafts shall conform to the No-Answer Policy.<br>FR-AI-10: AI-generated Lesson drafts shall require administrator review, HTML/CSS safety validation, No-Answer Policy validation, and publication through UC-ADMIN-04 before becoming student-accessible.<br>FR-AI-11: The AI feature shall not create, publish, or activate a learning unit or Lesson without administrator approval. |

**UC-AI-02 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Generate Lesson HTML/CSS Draft Using AI Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor; show UC-AI-02 as an optional <<extend>> of UC-ADMIN-04 Manage Learning Units and Lesson Content.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Generate Lesson HTML/CSS Draft Using AI Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the administrator entering a request, AI returning chat explanation and proposed HTML/CSS, administrator previewing, accepting/editing/discarding, and return to UC-ADMIN-04 for publication.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — AI Lesson Assistant and Lesson HTML/CSS Editor Integration
Tool: Draw.io, Figma, or equivalent
Contents: Show the AI assistant chat panel, Code Editor with HTML/CSS toggle, proposed-change preview, rendered Lesson preview, and validation warnings.
[PLACEHOLDER — Insert diagram here]

---

### 7.3 Generate Scenario Draft Using AI Assistance

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-AI-03 |
| **Use Case Name** | Generate Scenario Draft Using AI Assistance |
| **Actor(s)** | Administrator (Authenticated) |
| **Preconditions** | Administrator is authenticated. The AI scenario-drafting feature has been enabled. The administrator is in the scenario-authoring workflow under UC-ADMIN-05. |
| **Main Flow** | 1. Administrator opens the AI Scenario Assistant from the Scenario Builder screen.<br>2. System displays an AI chat panel beside or within the Scenario Builder form.<br>3. Administrator enters a scenario-generation request specifying target learning unit, Git concept, scenario skill focus, intended difficulty progression, narrative theme, starting repository-state idea, desired conflict/recovery condition, and optional simulator-scope constraints.<br>4. System sends the request and relevant authoring context to the AI backend.<br>5. AI backend returns two coordinated outputs: (a) a conversational response in the chat panel explaining the draft and asking for clarification when needed, and (b) structured draft data mapped to Scenario Builder fields, including scenario title, unit placement, skill focus, narrative, student task prompt, initial repository state setup, target repository state rules or reference solution sequence, difficulty scaffolding notes, feedback drafts, and draft variant definitions.<br>6. System displays the chat explanation and offers an Apply Draft to Form action.<br>7. Administrator applies the draft, partially applies selected fields, asks the AI to revise specific fields, regenerates variants, or rejects the draft.<br>8. If applied, system populates the editable Scenario Builder form fields; the structured form values, not the chat transcript, become the scenario draft record.<br>9. System performs an automated pre-check for required fields, unit assignment, variant completeness, simulator-operation compatibility, and obvious No-Answer Policy violations.<br>10. Administrator continues editing and validation through UC-ADMIN-05. |
| **Postconditions** | A structured scenario draft may be imported into Administrative Management for administrator review. No scenario, unit, variant, target state, or diagram is published directly by AI. |
| **Alternative Flows** | AF1 — Administrator rejects the generated draft: Administrator may regenerate with adjusted parameters or discard.<br>AF2 — AI output fails automated pre-check: System marks the draft as invalid and prevents publication until regenerated or manually corrected.<br>AF3 — AI suggests a new learning unit: System treats the suggestion as draft metadata only; administrator must create or confirm the unit through UC-ADMIN-04.<br>AF4 — AI-generated target state cannot be simulated or rendered as a DAG: System flags the target state for administrator correction and prevents publication. |
| **Functional Requirements** | FR-AI-12: Provide an AI-assisted scenario-drafting interface accessible to Administrator users only when the AI feature is enabled.<br>FR-AI-13: Provide an AI assistant chat panel that displays explanations, revision prompts, and follow-up messages without becoming the authoritative scenario record.<br>FR-AI-14: Generate structured draft output that can populate editable Scenario Builder fields.<br>FR-AI-15: AI-generated scenario drafts shall conform to the No-Answer Policy.<br>FR-AI-16: AI-generated scenario drafts shall require administrator review, validation, and publication through UC-ADMIN-05 before becoming student-accessible.<br>FR-AI-17: The AI scenario-drafting tool shall generate structurally distinct variant suggestions when used for new scenario drafting.<br>FR-AI-18: The AI feature shall not create, publish, or activate a learning unit, scenario, variant, target state, or diagram without administrator approval. |

**UC-AI-03 — Required Diagrams**

*Diagram 1 — Use Case Diagram*
Title: Use Case Diagram — Generate Scenario Draft Using AI Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the **Administrator** actor; show UC-AI-03 as an optional <<extend>> of UC-ADMIN-05 Add or Edit Scenario Content.
[PLACEHOLDER — Insert diagram here]

*Diagram 2 — Activity Diagram*
Title: Activity Diagram — Generate Scenario Draft Using AI Assistance
Tool: Draw.io (or equivalent UML-compliant tool)
Contents: Show the administrator entering generation parameters, AI returning chat explanation and structured draft data, administrator applying draft fields to the Scenario Builder form, automated pre-check, and return to UC-ADMIN-05 for publication.
[PLACEHOLDER — Insert diagram here]

*Diagram 3 — Wireframe*
Title: Wireframe — AI Scenario Assistant and Scenario Builder Integration
Tool: Draw.io, Figma, or equivalent
Contents: Show the AI chat panel, generation parameter form, draft preview, validation warnings, regenerate/discard/import controls, and indication that publication occurs only in Administrative Management.
[PLACEHOLDER — Insert diagram here]

---

### 3.3 Objective-to-Module Traceability Matrix

This matrix confirms that the five current-release student-facing functional modules correspond directly, one-to-one, to the five General Objectives from the approved capstone proposal. Module 0 is a supporting prerequisite module. Modules 6 and 7 are planned Phase 2 supporting modules. No supporting module creates an additional research objective.

| Proposal General Objective | SRS Module | Relationship | Functional Coverage | KPI / Verification Basis |
|---|---|---|---|---|
| General Objective 1: Establish the foundational Git mental model students need for scenario-driven practice through accessible Unit 1 orientation lessons | **Module 1: Orientation and Conceptual Readiness** | One-to-one objective-module | Unit 1 orientation lesson list, single-scroll lesson pages, authored HTML/scoped CSS, completion/read marking, non-blocking orientation completion tracking | OLCR ≥ 80%; 100% lesson accessibility; ARC ≤ 2 as indirect readiness indicator |
| General Objective 2: Improve students' ability to resolve realistic Git repository problems through terminal-based scenario execution and state-based repository evaluation | **Module 2: Scenario Practice and State-Based Evaluation** | One-to-one objective-module | Expanded unit Scenario Skill Focus cards, Skill Focus Preview, difficulty action selection, scenario instance loading, command input, authored command-count policy, repository simulation, state-based evaluation, completion handling, playable Review Mode | SCR ≥ 80%; ARC ≤ 2; CAR ≥ 60%; Review Mode SCR ≥ 60%; evaluator validation test set |
| General Objective 3: Improve repository-state reasoning through live DAG visualization and progressively reduced scaffolding | **Module 3: Repository Visualization and Fading Scaffolding** | One-to-one objective-module | Live DAG at all levels; expected-state diagram on Easy/Medium; contextual feedback on Easy only; Hard level with live DAG and narrative context only | DAG accuracy test set (0% mismatch); 100% correct scaffolding rendering; HLCR ≥ 70% |
| General Objective 4: Improve transfer to structurally changed retry variants after failed scenario attempts or abandoned sessions | **Module 4: Adaptive Retry and Transfer Practice** | One-to-one objective-module | Structurally different retry variant selection; variant identity logging; RTA eligibility rules; exclusion of first-ever encounters | RTA ≥ 65%; 0% identical-variant retries when a different variant exists; 100% RTA computation integrity |
| General Objective 5: Improve progress self-monitoring through visible, log-derived dashboard indicators | **Module 5: Progress Tracking and Self-Monitoring** | One-to-one objective-module | Session/step logging (FRG-LOG-01), log-derived dashboard indicators, unit-card progress display, expanded unit Scenario Skill Focus cards, Review button visibility, Skill Focus Preview routing, Review Mode routing | 100% log-display match accuracy; SAR ≤ 20%; dashboard acceptance test set |
| Supporting prerequisite scope only — no General Objective | **Module 0: System Access Prerequisites** | Prerequisite/enabling module | Student registration, login, authenticated page access, session continuity, logout | Authentication/session tests; enables access to all other modules |
| Planned Phase 2 / next-semester scope only | **Module 6: Administrative Management** | Planned support module; excluded from current-release MVP KPI computation | Administrator access, analytics viewing, student access management, learning unit and scenario management, audit-log review | Phase 2 acceptance tests only |
| Planned Phase 2 / next-semester scope only | **Module 7: AI-Assisted Learning Support** | Planned support module; excluded from current-release MVP KPI computation | Conceptual Git chatbot, Lesson HTML/CSS drafting, scenario draft generation | Phase 2 acceptance tests only |

---

### 3.4 Non-Functional Requirements

#### Performance

| Req ID | Description | Target |
|--------|-------------|--------|
| NFR-PERF-01 | API response time — command evaluation (state update + step check) | ≤ 300 ms at 95th percentile |
| NFR-PERF-02 | Live DAG re-render time after command execution (frontend animation) | ≤ 200 ms for approved performance test scenarios |
| NFR-PERF-03 | Initial page load time — Student Dashboard on a 10 Mbps connection | ≤ 2 seconds |
| NFR-PERF-04 | Concurrent users without performance degradation | ≥ 40 simultaneous users; headroom to 100 |
| NFR-PERF-05 | Database query response time for indexed queries | ≤ 100 ms at 95th percentile |
| NFR-PERF-06 | Scenario load time (variant selection + Repository State Simulator initialization) | ≤ 500 ms |
| NFR-PERF-07 | Planned Phase 2 only — Administrative Management learning-analytics query response time (full cohort aggregation) | ≤ 3 seconds at 95th percentile when Module 6 is implemented; not required for current-release acceptance |

#### Security

| Req ID | Description |
|--------|-------------|
| NFR-SEC-01 | All passwords shall be stored as secure one-way hashes (an industry-standard password hashing algorithm). Plaintext passwords shall never be persisted, logged, or returned to clients. |
| NFR-SEC-02 | All client-server communication shall be transmitted over HTTPS (TLS 1.2 or higher). Plain HTTP connections shall be automatically redirected to HTTPS. |
| NFR-SEC-03 | JWT access tokens shall expire after 15 minutes. Refresh tokens shall expire after 7 days. |
| NFR-SEC-04 | Refresh tokens shall be stored exclusively in httpOnly, Secure, SameSite=Strict cookies — inaccessible to JavaScript running in the browser. |
| NFR-SEC-05 | Refresh tokens shall be added to a server-side revocation blacklist on logout, with TTL equal to the token's remaining lifetime. |
| NFR-SEC-06 | CORS shall be restricted to the frontend application's origin domain. All other origins shall be blocked. |
| NFR-SEC-07 | All user inputs shall be validated and sanitized on both the frontend (client-side) and the backend (server-side). |
| NFR-SEC-08 | SQL injection shall be prevented through exclusive use of parameterized queries or a trusted ORM. Raw string interpolation into SQL is prohibited. |
| NFR-SEC-09 | Rate limiting on authentication endpoints: maximum 10 requests per IP per minute. |
| NFR-SEC-10 | The system shall comply with the Philippine Data Privacy Act of 2012 (RA 10173). Student personal data (first name, last name, student ID, CIT educational email) shall be encrypted at rest and in transit. |
| NFR-SEC-11 | Repository State Simulator inputs (student-typed Git commands) shall be executed in a sandboxed, non-executable context. No external Git command-line binaries shall be invoked. No shell execution from user input shall occur. Internal simulator operations may be used only inside isolated server-side simulator sessions. |
| NFR-SEC-12 | Phase 2 administrative API endpoints shall require administrator-scoped access. Student-scoped tokens shall be rejected with HTTP 403 on all administrative endpoints. |
| NFR-SEC-13 | Phase 2 AI scenario-drafting endpoints shall require administrator-scoped access, while student-facing AI chatbot endpoints shall enforce the No-Answer Policy and reject scenario-answer requests. |

#### Reliability

| Req ID | Description | Target |
|--------|-------------|--------|
| NFR-REL-01 | System uptime during the evaluation period | ≥ 99% |
| NFR-REL-02 | Graceful degradation on cache unavailability | System falls through to database for session state; token revocation temporarily unavailable; no crash |
| NFR-REL-03 | Session state recovery on browser crash or accidental navigation | Student can resume from the last completed step within the current session |
| NFR-REL-04 | Database backup frequency | Automatic daily backups |
| NFR-REL-05 | Structured error responses | All API errors shall return structured JSON with HTTP status code and message; no stack traces in production responses |
| NFR-REL-06 | Data integrity — completion records | All database writes for completion records shall execute within transactions; unique constraints shall prevent duplicate completion entries |
| NFR-REL-07 | Data integrity — step logs | Step log entries shall be written atomically to prevent partial records from persisting |
| NFR-REL-08 | Usability validation target — SUS score administered after student's first completed scenario session | ≥ 70 (research validation target; not a runtime reliability requirement) |
| NFR-REL-09 | Technology acceptance validation target — Perceived Usefulness (PU) | ≥ 4.0 on a 5-point Likert scale (research validation target; not a runtime reliability requirement) |
| NFR-REL-10 | Technology acceptance validation target — Perceived Ease of Use (PEOU) | ≥ 3.5 on a 5-point Likert scale (research validation target; not a runtime reliability requirement) |
| NFR-REL-11 | Technology acceptance validation target — Behavioral Intention to Use (BI) | ≥ 4.0 on a 5-point Likert scale (research validation target; not a runtime reliability requirement) |
| NFR-REL-12 | Keyboard accessibility — all primary actions shall be operable without a mouse | Required |
| NFR-REL-13 | Minimum supported screen resolution | 1280×720 pixels; all key interface components visible without horizontal scrolling |
| NFR-REL-14 | System log structure | Structured and queryable to support automated computation of OLCR, SCR, ARC, CAR, HLCR, RTA, and SAR from lesson completion, session, and step logs; RTA logs shall identify eligible changed-variant retry sessions separately from first-ever encounters and non-eligible replays; Administrative Management analytics views may reuse the same learning logs if Module 6 is later implemented; administrative audit logs shall remain separate from student scenario/session logs |
| NFR-REL-15 | Scenario content maintainability | Scenario skill focus definitions, difficulty-instance configurations, difficulty-owned variant pools, repository-state definitions, expected-state diagram data, target-state rules, command-count policies, and support-level visibility settings shall be stored as seeded content records for the current release so scenario text, diagrams, and evaluator targets are not hardcoded into frontend pages; expected-state diagrams shall be generated from the same structured target-state data used by the evaluator. Administrator-driven revision without redeployment is a planned Phase 2 Administrative Management capability. |
| NFR-REL-16 | Database connection pooling | Required to prevent connection exhaustion under load |


