# CEBU INSTITUTE OF TECHNOLOGY
# UNIVERSITY

## COLLEGE OF COMPUTER STUDIES

---

# Software Design Description
# for
# GIT it!

---

## Change History Signature

| Version | Date | Author | Description of Change |
|---|---|---|---|
| 1.0 | May 18, 2026 | Team 2526-sem2-it332-34 | Initial Software Design Description draft aligned with the revised SRS and Proposal. |

---

## Preface

This Software Design Description (SDD) documents the implementation design for **GIT it!** based on the revised Software Requirements Specification and Proposal. It contains the technology stack, architectural components, module-level design, front-end and back-end components, object-oriented component placeholders, sequence diagram placeholders, and data-design placeholders. Diagrams are intentionally left as placeholders for later insertion.

---

## Table of Contents

1. Introduction
   - 1.1 Purpose
   - 1.2 Scope
   - 1.3 Definitions and Acronyms
   - 1.4 References
2. Architectural Design
3. Detailed Design
   - Module 0: System Access Prerequisites
   - Module 1: Orientation and Conceptual Readiness
   - Module 2: Scenario Practice and State-Based Evaluation
   - Module 3: Repository Visualization and Fading Scaffolding
   - Module 4: Adaptive Retry and Transfer Practice
   - Module 5: Progress Tracking and Self-Monitoring
   - Module 6: Administrative Management
   - Module 7: AI-Assisted Learning Support

---

# 1. Introduction

## 1.1 Purpose

This Software Design Description defines how **GIT it!** will be implemented. It translates the functional and non-functional requirements from the SRS into a concrete system design using selected technologies, front-end and back-end components, object-oriented components, interaction flows, and data structures. The SDD serves as the implementation guide for developers and as the design reference for checking whether the built system matches the approved requirements.

## 1.2 Scope

This SDD covers the current-release student-facing system and the planned Phase 2 design placeholders. The current release includes student account access, Unit 1 orientation, scenario selection, terminal-based Git practice, repository-state simulation, state-based evaluation, live DAG visualization, difficulty-based scaffolding, adaptive retries, playable Review Mode, progress tracking, and student dashboard indicators. Planned Phase 2 design sections cover Administrative Management and AI-Assisted Learning Support at a design-placeholder level.

## 1.3 Definitions and Acronyms

| Term / Acronym | Definition |
|---|---|
| API | Application Programming Interface |
| DRF | Django REST Framework |
| DAG | Directed Acyclic Graph used to represent Git commit history |
| JWT | JSON Web Token |
| SPA | Single Page Application |
| SDD | Software Design Description |
| SRS | Software Requirements Specification |
| Repository State Simulator | Backend component that initializes and manipulates isolated simulated Git repository sessions |
| State-Based Evaluator | Backend component that compares normalized repository-state snapshots against expected target-state rules |
| Command-Count Policy | Scenario difficulty configuration storing the minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns |
| Difficulty Instance | Configured Easy, Medium, or Hard playable level under a scenario skill focus; owns its narrative/task prompt, initial state, target-state rule, command-count policy, scaffolding configuration, expected-state behavior, and variant pool |
| Difficulty Variant | Structurally distinct variant owned by one difficulty instance and used to initialize a session or changed retry |
| Counted Action Command | Simulator-processed command included in CAR and remaining counted-command calculations |
| Non-Counted Diagnostic Command | Simulator-processed read-only inspection command that is logged but excluded from CAR and remaining counted-command calculations |
| No-Answer Policy | Design rule preventing student-facing screens and AI responses from revealing correct commands, command sequences, hidden evaluator rules, or unauthorized target-state comparisons |
| Review Mode | Playable re-attempt mode for a previously completed scenario difficulty instance |
| RTA | Retry Transfer Accuracy |
| SAR | Scenario Abandonment Rate |
| OLCR | Orientation Lesson Completion Rate |

## 1.4 References

| Ref | Document Title | Date / Year | Publishing Organization | Source / Availability |
|---|---|---|---|---|
| [1] | GIT it! Revised Software Requirements Specification | 2026 | Team 2526-sem2-it332-34, CIT-U | Internal project document |
| [2] | GIT it! Revised Capstone Proposal | 2026 | Team 2526-sem2-it332-34, CIT-U | Internal project document |
| [3] | Django Documentation | Online | Django Software Foundation | Official documentation |
| [4] | Django REST Framework Documentation | Online | Encode OSS Ltd. | Official documentation |
| [5] | React Documentation | Online | Meta Open Source / React Team | Official documentation |
| [6] | Vite Documentation | Online | Vite Team | Official documentation |
| [7] | pygit2 Documentation | Online | pygit2 Project | Official documentation |
| [8] | libgit2 Documentation | Online | libgit2 Project | Official documentation |
| [9] | PostgreSQL Documentation | Online | PostgreSQL Global Development Group | Official documentation |
| [10] | Redis Documentation | Online | Redis Ltd. / Redis Open Source Project | Official documentation |
| [11] | JSON Web Token (JWT) | 2015 | IETF | RFC 7519 |
| [12] | Transport Layer Security (TLS) Protocol Version 1.2 | 2008 | IETF | RFC 5246 |

---

# 2. Architectural Design

GIT it! uses a client-server web architecture. The front end is implemented as a React.js single-page application using Vite. The backend is implemented using Django with Django REST Framework for REST API endpoints. PostgreSQL is used as the persistent relational database, and Redis is used for active session cache, scenario metadata cache, and token/session support where applicable. The Repository State Simulator uses pygit2/libgit2 to manipulate isolated server-side Git repository sessions. The State-Based Evaluator is a custom Python service layer that extracts normalized repository-state snapshots and compares them against the target-state rules for the active scenario step.

[PLACEHOLDER — Insert architectural block diagram showing the React/Vite frontend, Django REST API backend, PostgreSQL database, Redis cache, pygit2/libgit2 Repository State Simulator, State-Based Evaluator, authentication/session components, and optional Phase 2 AI service boundary.]

The architecture uses the following implementation technologies:

| Layer | Selected Technology | Design Purpose |
|---|---|---|
| Frontend | React.js with Vite | Student-facing SPA, dashboard, unit pages, scenario workspace, live DAG rendering, terminal UI |
| Backend API | Django + Django REST Framework | Authentication endpoints, scenario endpoints, command execution API, progress/KPI endpoints, admin/AI endpoints in Phase 2 |
| Repository Simulation | pygit2/libgit2 | Internal Git repository manipulation inside isolated server-side sessions |
| State Evaluation | Custom Python evaluator service | Normalized repository-state comparison against authored target-state rules |
| Database | PostgreSQL, hosted through Supabase or equivalent PostgreSQL provider | Persistent storage of users, units, lessons, scenario skill focuses, difficulty-instance configurations, difficulty-owned variants, sessions, step logs, and progress records |
| Cache | Redis or compatible managed Redis service | Active scenario state cache, metadata caching, token/session support, and performance optimization |
| Authentication | JWT access token + secure refresh-token flow | Authenticated API access and session continuity |
| Deployment | Static frontend hosting + WSGI/ASGI backend hosting | Separate deployment for frontend and backend services |

The main component interaction flow is as follows:

1. The student interacts with the React frontend.
2. The frontend sends authenticated JSON requests to the Django REST API.
3. The backend validates authentication, permissions, scenario access rules, and difficulty unlock rules.
4. Scenario commands are passed to an application-controlled command adapter.
5. The command adapter maps supported Git-like commands to pygit2/libgit2 operations inside an isolated repository session.
6. The simulator returns the updated repository state.
7. The command-count policy service classifies the processed command as a counted action command or non-counted diagnostic command.
8. The evaluator converts the resulting repository state into a normalized snapshot and compares it with the expected target state.
9. The backend persists session logs, step logs, progress records, command classifications, counted-command totals, and KPI-relevant fields.
10. The frontend updates the terminal output, live DAG, expected-state panel, feedback panel, Remaining Counted-Command Counter, and dashboard indicators.
11. The No-Answer Policy guard is applied to student-facing feedback, completion messages, Review Mode outputs, and AI responses before they are returned or rendered.

---

# 3. Detailed Design

## Module 0: System Access Prerequisites

### 0.1 Register a New Student Account

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Register a New Student Account.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AuthForm | Displays and validates student ID in NN-NNNN-NNN format, first name, last name, @cit.edu email, and password registration fields before API submission. | React component |
| AuthApiClient | Sends authentication requests to the backend API and handles token responses. | TypeScript/JavaScript service |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AuthViewSet/RegisterAPIView | Validates registration payload, enforces unique NN-NNNN-NNN student ID and @cit.edu email requirements, creates student account, hashes password, initializes progress record. | Django REST Framework API view |
| UserService | Handles user creation and initial progress setup. | Django service class |
| TokenService | Issues JWT access token and refresh token. | Python service class |

#### Object-Oriented Components

Primary classes/components: User, StudentProfile, ProgressRecord, TokenService, AuthSerializer. StudentProfile stores the unique NN-NNNN-NNN student ID while User stores first name, last name, and CIT educational email.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Register a New Student Account.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Register a New Student Account.]

#### Data Design
Tables/entities involved: User, StudentProfile, ProgressRecord, RefreshToken/SessionRecord. Registration writes must be transactional so that user, unique student ID profile, and initial progress records are created together.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Register a New Student Account.]

### 0.2 Log In to Student Account

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Log In to Student Account.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AuthForm | Displays and validates a student ID or @cit.edu email identifier with password before API submission. | React component |
| AuthApiClient | Sends authentication requests to the backend API and handles token responses. | TypeScript/JavaScript service |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LoginAPIView | Authenticates student ID/password or @cit.edu email/password and returns session tokens. | Django REST Framework API view |
| TokenService | Creates access and refresh tokens and sets secure cookie metadata. | Python service class |

#### Object-Oriented Components

Primary classes/components: User, StudentProfile, LoginSerializer, TokenService, SessionRecord.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Log In to Student Account.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Log In to Student Account.]

#### Data Design
Tables/entities involved: User, StudentProfile, SessionRecord, RefreshToken. Failed login attempts return a generic invalid-credentials response without disclosing whether the submitted identifier was an unknown student ID/email or the password was wrong.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Log In to Student Account.]

### 0.3 Access Authenticated Platform Pages

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Access Authenticated Platform Pages.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AuthProvider | Maintains authenticated frontend state and exposes session status to protected pages. | React context/provider |
| ProtectedRoute | Prevents unauthenticated access to protected platform routes and redirects invalid sessions to login. | React route guard/component |
| ApiInterceptor | Handles expired access-token responses, requests session renewal when possible, and retries the original request after renewal succeeds. | Frontend API utility |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AuthenticationMiddleware/PermissionClass | Verifies whether the incoming request has a valid authenticated session before protected resources are returned. | Django/DRF middleware or permission class |
| RefreshTokenAPIView | Supports automatic session renewal by validating refresh tokens and issuing new access tokens when allowed. | Django REST Framework API view |
| TokenBlacklistService | Checks token revocation state when available. | Python service class |

#### Object-Oriented Components

Primary classes/components: User, SessionRecord, RefreshToken, TokenService, TokenBlacklistService, ProtectedRoute.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Access Authenticated Platform Pages.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Access Authenticated Platform Pages and automatic session renewal.]

#### Data Design
Tables/entities involved: User, SessionRecord, RefreshToken. Redis may hold revoked token identifiers until expiry.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Access Authenticated Platform Pages.]

### 0.4 Log Out

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Log Out.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LogoutButton | Triggers logout request and clears frontend auth state. | React component |
| AuthProvider | Clears stored access token and redirects to login. | React context/provider |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LogoutAPIView | Revokes refresh token and clears secure cookie. | Django REST Framework API view |
| TokenBlacklistService | Adds refresh token to revocation cache with TTL. | Python service class |

#### Object-Oriented Components

Primary classes/components: TokenService, TokenBlacklistService, SessionRecord.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Log Out.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Log Out.]

#### Data Design
Tables/entities involved: SessionRecord/RefreshToken. Redis may store token blacklist entries with TTL equal to remaining token lifetime.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Log Out.]

## Module 1: Orientation and Conceptual Readiness

### 1.1 View and Complete Orientation Lesson

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for View and Complete Orientation Lesson.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| OrientationLessonPage | Renders Unit 1 topic content as a single scrollable page with completion state. | React page component |
| LessonReadAction | Sends the mark-read completion update to the API. | React component/service |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| OrientationLessonAPIView | Returns published Unit 1 topic content and interaction metadata. | Django REST Framework API view |
| OrientationProgressAPIView | Persists topic completion status. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: LearningUnit, Lesson, OrientationLesson, OrientationProgress, ProgressService.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for View and Complete Orientation Lesson.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for View and Complete Orientation Lesson.]

#### Data Design
Tables/entities involved: LearningUnit, Lesson, OrientationLesson, OrientationProgress, StudentProgress. Completion is stored when the student marks a single-scroll orientation lesson as read.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for View and Complete Orientation Lesson.]

### 1.2 Track Orientation Lesson Completion

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Track Orientation Lesson Completion.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| OrientationProgressStatus | Displays Unit 1 lesson read/completion progress without blocking scenario navigation. | React component |
| LessonReadAction | Marks a single-scroll orientation lesson as read. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| OrientationService | Stores and retrieves Unit 1 lesson completion/read status. | Python service class |
| ScenarioSessionAPIView | Starts scenario sessions regardless of Unit 1 completion and records orientation-complete-at-start as non-blocking analytics context. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: OrientationService, StudentProgress, ScenarioSession, LearningUnit.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Track Orientation Lesson Completion.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Track Orientation Lesson Completion.]

#### Data Design
Tables/entities involved: OrientationProgress, StudentProgress, ScenarioSession. Scenario start records whether all Unit 1 lessons were complete as non-blocking analytics context for readiness analysis.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Track Orientation Lesson Completion.]

## Module 2: Scenario Practice and State-Based Evaluation

### 2.1 View Lesson, Browse Attached Scenarios, and Select Difficulty

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for View Lesson, Browse Attached Scenarios, and Select Difficulty.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LessonPage | Renders lesson HTML/CSS and embedded scenario list. | React page component |
| ScenarioCardList | Displays scenario cards and Easy/Medium/Hard access states. | React component |
| DifficultySelector | Allows available difficulty selection and displays lock reasons. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LessonAPIView | Returns published lesson content. | Django REST Framework API view |
| ScenarioListAPIView | Returns scenarios, difficulty status, and completion indicators. | Django REST Framework API view |
| DifficultyAccessService | Determines Easy/Medium/Hard access states. | Python service class |

#### Object-Oriented Components

Primary classes/components: LearningUnit, Lesson, ScenarioSkillFocus, DifficultyInstance, DifficultyAccessService, StudentProgress.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for View Lesson, Browse Attached Scenarios, and Select Difficulty.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for View Lesson, Browse Attached Scenarios, and Select Difficulty.]

#### Data Design
Tables/entities involved: LearningUnit, Lesson, ScenarioSkillFocus, DifficultyInstance, StudentProgress, CompletionRecord.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for View Lesson, Browse Attached Scenarios, and Select Difficulty.]

### 2.2 Load Scenario Instance

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Load Scenario Instance.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ScenarioWorkspace | Main scenario practice page containing narrative, explicit success rules, terminal, live DAG, expected-state panel, and feedback panel. | React page component |
| ScenarioContextPanel | Displays scenario narrative, task, state-based grading rule, commit-message expectation, and non-counted diagnostic commands. | React component |
| ScenarioLoader | Requests session initialization and stores active session state. | Frontend service |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ScenarioSessionAPIView | Creates a new scenario session from the selected difficulty instance, selects a variant from that difficulty's variant pool, and attaches the applicable command-count policy snapshot. | Django REST Framework API view |
| VariantSelectionService | Selects initial or retry variant from the selected difficulty instance's valid variant pool according to rules. | Python service class |
| CommandCountPolicyService | Loads the difficulty instance's authored minimum counted-command threshold, maximum counted-command limit, and non-counted diagnostic command patterns. | Python service class |
| RepositorySessionService | Initializes isolated repository session through pygit2/libgit2. | Python service class |

#### Object-Oriented Components

Primary classes/components: ScenarioSession, DifficultyInstance, DifficultyVariant, RepositorySessionService, VariantSelectionService, CommandCountPolicy, TargetStateRule.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Load Scenario Instance.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Load Scenario Instance.]

#### Data Design
Tables/entities involved: ScenarioSession, DifficultyInstance, DifficultyVariant, CommandCountPolicy, TargetStateRule, SessionLog. Active repository data may be cached in Redis and persisted by session identifiers. The scenario session stores the selected difficulty-instance ID, selected variant ID, target-state rule reference/hash, and command-count policy ID or snapshot used for that attempt.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Load Scenario Instance.]

### 2.3 Submit Command and Evaluate Repository State

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Submit Command and Evaluate Repository State.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| TerminalPanel | Accepts Git-like command input and displays terminal output/history. | React component |
| LiveDagPanel | Updates current repository visualization after processed commands. | React component |
| FeedbackPanel | Displays Easy-level repository consequence feedback. | React component |
| RemainingCountedCommandCounter | Displays the remaining counted action commands available in the current session. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| CommandExecutionAPIView | Receives command submissions and returns output, state snapshot, and evaluation result. | Django REST Framework API view |
| CommandAdapter | Maps supported command syntax to safe simulator operations. | Python service class |
| RepositoryStateSimulator | Applies supported operations through pygit2/libgit2. | Python service class |
| StateBasedEvaluator | Compares normalized state snapshot against target-state rules. | Python service class |
| CommandCountPolicyService | Classifies simulator-processed commands as counted action commands or non-counted diagnostic commands and updates counted-command totals. | Python service class |

#### Object-Oriented Components

Primary classes/components: CommandAdapter, RepositoryStateSimulator, RepositorySnapshot, StateBasedEvaluator, TargetStateRule, CommandCountPolicy, StepLog.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Submit Command and Evaluate Repository State.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Submit Command and Evaluate Repository State.]

#### Data Design
Tables/entities involved: ScenarioSession, StepLog, CommandCountPolicy, TargetStateRule, RepositoryStateSnapshot/StateHash. Every command submission writes a step log with result category, command classification, counted-command increment value, and current counted-command total.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Submit Command and Evaluate Repository State.]

### 2.4 Complete Scenario and Unlock Next Difficulty

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Complete Scenario and Unlock Next Difficulty.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| CompletionScreen | Displays scenario completion details, counted-command summary, and applicable CAR indicator without revealing answers. | React component |
| NextDifficultyPrompt | Shows newly unlocked difficulty level when applicable. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| CompletionService | Persists completion record, counted-command totals, CAR eligibility, star eligibility, streak, and unlock status. | Python service class |
| CompletionAPIView | Returns completion summary to frontend. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: CompletionRecord, ScenarioSession, StudentProgress, StreakRecord, FirstAttemptStar.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Complete Scenario and Unlock Next Difficulty.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Complete Scenario and Unlock Next Difficulty.]

#### Data Design
Tables/entities involved: CompletionRecord, StudentProgress, ScenarioSession, StreakRecord, FirstAttemptStar. Completion updates must be transactional.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Complete Scenario and Unlock Next Difficulty.]

### 2.5 Re-attempt Completed Scenario in Review Mode

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Re-attempt Completed Scenario in Review Mode.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ReviewModeLauncher | Starts Review Mode from completed scenario card or completion screen. | React component |
| ScenarioWorkspace | Renders terminal, live DAG, and difficulty-appropriate supports with Review Mode label. | React page component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ReviewModeAPIView | Validates prior completion and initializes a review_mode session. | Django REST Framework API view |
| ReviewModeService | Tags session separately and preserves original completion record. | Python service class |

#### Object-Oriented Components

Primary classes/components: ReviewModeService, ScenarioSession, CompletionRecord, StepLog, StateBasedEvaluator.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Re-attempt Completed Scenario in Review Mode.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Re-attempt Completed Scenario in Review Mode.]

#### Data Design
Tables/entities involved: ScenarioSession with review_mode flag, StepLog, CompletionRecord. Review Mode sessions are included only in Review Mode SCR and do not overwrite primary completion/progression records.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Re-attempt Completed Scenario in Review Mode.]

## Module 3: Repository Visualization and Fading Scaffolding

### 3.1 Render Live Animated DAG

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Render Live Animated DAG.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LiveDagPanel | Displays commit nodes, parent edges, branch labels, HEAD position, and state markers. | React visualization component |
| DagStateMapper | Converts backend repository snapshot JSON into graph nodes/edges. | Frontend utility |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| RepositorySnapshotService | Extracts normalized graph state after each simulator-processed command. | Python service class |
| CommandExecutionAPIView | Returns updated graph snapshot to frontend. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: RepositorySnapshot, DagNode, DagEdge, BranchPointer, HeadPointer.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Render Live Animated DAG.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Render Live Animated DAG.]

#### Data Design
Tables/entities involved: StepLog may store repository state hash/snapshot metadata. Runtime graph state is returned as structured JSON.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Render Live Animated DAG.]

### 3.2 Render Expected-State Diagram on Easy and Medium

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Render Expected-State Diagram on Easy and Medium.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ExpectedStatePanel | Displays static target-state diagram for Easy and Medium sessions. | React component |
| ScaffoldingResolver | Shows or hides support panels based on difficulty. | Frontend utility |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ExpectedStateAPIView | Returns target-state diagram metadata for current step. | Django REST Framework API view |
| ScaffoldingService | Determines support availability per difficulty. | Python service class |

#### Object-Oriented Components

Primary classes/components: TargetStateRule, ExpectedStateDiagram, DifficultyInstance, ScaffoldingService.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Render Expected-State Diagram on Easy and Medium.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Render Expected-State Diagram on Easy and Medium.]

#### Data Design
Tables/entities involved: TargetStateRule, ExpectedStateDiagram, DifficultyInstance. Expected-state diagrams must match evaluator target-state rules.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Render Expected-State Diagram on Easy and Medium.]

### 3.3 Display Contextual Feedback on Easy

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Display Contextual Feedback on Easy.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| FeedbackPanel | Displays answer-safe state-change summary after processed commands. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| FeedbackGenerationService | Compares pre-state and post-state snapshots and creates repository consequence feedback. | Python service class |
| CommandExecutionAPIView | Returns feedback text only for Easy-level sessions. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: FeedbackGenerationService, RepositorySnapshot, StepLog, DifficultyInstance.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Display Contextual Feedback on Easy.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Display Contextual Feedback on Easy.]

#### Data Design
Tables/entities involved: StepLog may store feedback category or generated consequence summary. Feedback must not reveal correct commands, command sequences, or target state.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Display Contextual Feedback on Easy.]

## Module 4: Adaptive Retry and Transfer Practice

### 4.1 Serve Structurally Changed Retry Variant

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Serve Structurally Changed Retry Variant.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| RetryButton | Allows student to retry after failed or abandoned attempt. | React component |
| ScenarioWorkspace | Loads the selected retry variant as a new session. | React page component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| RetryScenarioAPIView | Creates retry session and requests changed variant selection. | Django REST Framework API view |
| VariantSelectionService | Selects a structurally different variant from the same difficulty instance's variant pool when available. | Python service class |

#### Object-Oriented Components

Primary classes/components: DifficultyVariant, ScenarioSession, DifficultyInstance, VariantSelectionService, PriorSessionReference.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Serve Structurally Changed Retry Variant.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Serve Structurally Changed Retry Variant.]

#### Data Design
Tables/entities involved: DifficultyVariant, VariantStructureSignature, DifficultyInstance, ScenarioSession, PriorSessionReference. Retry sessions must store prior-session, difficulty-instance, and variant IDs. RTA-eligible retries compare the new variant against the prior Failed or Abandoned session within the same scenario skill focus and difficulty level.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Serve Structurally Changed Retry Variant.]

### 4.2 Compute Retry Transfer Accuracy Eligibility

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Compute Retry Transfer Accuracy Eligibility.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| DashboardMetricBadge | Displays RTA-related progress when available. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| MetricsService | Identifies RTA-eligible sessions and computes RTA. | Python service class |
| ProgressAPIView | Returns log-derived metric values. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: MetricsService, ScenarioSession, DifficultyInstance, DifficultyVariant, StepLog, ProgressSummary.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Compute Retry Transfer Accuracy Eligibility.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Compute Retry Transfer Accuracy Eligibility.]

#### Data Design
Tables/entities involved: ScenarioSession, DifficultyInstance, DifficultyVariant, StepLog, ProgressSummary. RTA eligibility requires a prior Failed or Abandoned session for the same scenario skill focus and difficulty level, plus a structurally changed retry variant from the same difficulty instance's variant pool.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Compute Retry Transfer Accuracy Eligibility.]

## Module 5: Progress Tracking and Self-Monitoring

### 5.1 View Student Dashboard and Progress Indicators

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for View Student Dashboard and Progress Indicators.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| DashboardPage | Displays student progress summary and available learning units. | React page component |
| ProgressMetricCards | Displays log-derived progress/KPI indicators. | React component |
| UnitCardList | Displays expandable learning unit cards with lesson lists. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ProgressSummaryAPIView | Returns log-derived dashboard values. | Django REST Framework API view |
| MetricsService | Computes dashboard metric values from session and step logs. | Python service class |

#### Object-Oriented Components

Primary classes/components: ProgressSummary, MetricsService, StudentProgress, ScenarioSession, StepLog.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for View Student Dashboard and Progress Indicators.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for View Student Dashboard and Progress Indicators.]

#### Data Design
Tables/entities involved: StudentProgress, ScenarioSession, StepLog, CompletionRecord, StreakRecord, FirstAttemptStar, ProgressSummary/cache.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for View Student Dashboard and Progress Indicators.]

### 5.2 Record Session and Step Logs

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Record Session and Step Logs.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ApiClient | Receives command/session responses produced after logged operations. | Frontend service |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| LoggingService | Writes session logs and step logs atomically. | Python service class |
| CommandExecutionAPIView | Triggers step logging after every command result. | Django REST Framework API view |
| ScenarioSessionAPIView | Triggers session start/end logging. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: LoggingService, ScenarioSession, StepLog, EvaluationResult, RepositoryStateHash.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Record Session and Step Logs.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Record Session and Step Logs.]

#### Data Design
Tables/entities involved: ScenarioSession, StepLog, EvaluationResult, RepositoryStateHash. Logging is not shown as a standalone use case diagram because it is an internal supporting behavior.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Record Session and Step Logs.]

### 5.3 Access Review Mode from Dashboard or Completion Screen

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Access Review Mode from Dashboard or Completion Screen.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ReviewButton | Appears only for completed scenario difficulty instances. | React component |
| DashboardPage | Routes valid Review action to Review Mode workspace. | React page component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| ReviewAccessService | Validates ownership and prior completion before allowing Review Mode. | Python service class |
| ReviewModeAPIView | Starts playable Review Mode session after validation. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: ReviewAccessService, CompletionRecord, ScenarioSession, StudentProgress.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Access Review Mode from Dashboard or Completion Screen.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Access Review Mode from Dashboard or Completion Screen.]

#### Data Design
Tables/entities involved: CompletionRecord, ScenarioSession, StudentProgress. Review access checks must prevent direct access to uncompleted scenario difficulties.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Access Review Mode from Dashboard or Completion Screen.]

## Module 6: Administrative Management

### 6.1 Manage Learning Content and Scenario Records

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Manage Learning Content and Scenario Records.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AdminContentPage | Allows administrator to create/edit/archive learning units, lessons, scenario skill focuses, difficulty-instance configurations, difficulty-owned variants, and target-state data. | React admin page component |
| HtmlCssCodeEditor | Edits Lesson HTML and scoped CSS. | Frontend code editor component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AdminContentAPIView | Creates, updates, archives, and publishes content records. | Django REST Framework API view |
| ContentValidationService | Validates lesson HTML/CSS, scenario fields, variants, and target-state rules. | Python service class |

#### Object-Oriented Components

Primary classes/components: LearningUnit, Lesson, ScenarioSkillFocus, DifficultyInstance, DifficultyVariant, CommandCountPolicy, TargetStateRule, AdminAuditLog.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Manage Learning Content and Scenario Records.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Manage Learning Content and Scenario Records.]

#### Data Design
Tables/entities involved: LearningUnit, Lesson, ScenarioSkillFocus, DifficultyInstance, DifficultyVariant, CommandCountPolicy, TargetStateRule, AdminAuditLog. This module is planned Phase 2 scope. DifficultyVariant records belong to exactly one DifficultyInstance so Easy, Medium, and Hard can maintain different repository-state templates and retry pools under the same scenario skill focus.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Manage Learning Content and Scenario Records.]

### 6.2 View Administrative Analytics and Student Access

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for View Administrative Analytics and Student Access.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AdminAnalyticsPage | Displays cohort-level and student-level KPI summaries. | React admin page component |
| StudentAccessTable | Lists students and account/access status. | React component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AdminAnalyticsAPIView | Returns cohort and student KPI summaries. | Django REST Framework API view |
| StudentManagementAPIView | Manages student account access status. | Django REST Framework API view |

#### Object-Oriented Components

Primary classes/components: AdminAnalyticsService, User, StudentProfile, ScenarioSession, StepLog, AdminAuditLog.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for View Administrative Analytics and Student Access.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for View Administrative Analytics and Student Access.]

#### Data Design
Tables/entities involved: User, StudentProfile, ScenarioSession, StepLog, ProgressSummary, AdminAuditLog. This module is planned Phase 2 scope.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for View Administrative Analytics and Student Access.]

## Module 7: AI-Assisted Learning Support

### 7.1 Generate AI-Assisted Lesson Draft

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Generate AI-Assisted Lesson Draft.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AiLessonDraftPanel | Displays AI chat/revision prompts for lesson drafting. | React admin component |
| HtmlCssCodeEditor | Receives proposed HTML/CSS draft after administrator approval. | Frontend code editor component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AiLessonDraftAPIView | Sends administrator prompt/context to configured AI service and receives draft output. | Django REST Framework API view |
| AiDraftSanitizationService | Sanitizes and validates AI-generated HTML/CSS before insertion. | Python service class |

#### Object-Oriented Components

Primary classes/components: AiDraftRequest, AiDraftResponse, Lesson, LessonDraft, AdminAuditLog.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Generate AI-Assisted Lesson Draft.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Generate AI-Assisted Lesson Draft.]

#### Data Design
Tables/entities involved: Lesson, LessonDraft, AiDraftRequest, AiDraftResponse, AdminAuditLog. AI output remains draft content until administrator validates and publishes it. This module is planned Phase 2 scope.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Generate AI-Assisted Lesson Draft.]

### 7.2 Generate AI-Assisted Scenario Draft and Provide Concept Chat

#### User Interface Design
[PLACEHOLDER — Insert user interface design/wireframe for Generate AI-Assisted Scenario Draft and Provide Concept Chat.]

#### Front-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AiScenarioDraftPanel | Requests scenario title, narrative, target state, variants, and scaffolding suggestions. | React admin component |
| ConceptChatPanel | Allows student to ask conceptual Git questions within answer-safe boundaries. | React student component |

#### Back-end component(s)
| Component Name | Description and purpose | Component type or format |
|---|---|---|
| AiScenarioDraftAPIView | Generates structured scenario draft data for administrator review. | Django REST Framework API view |
| ConceptChatAPIView | Returns answer-safe conceptual explanations within published content boundaries. | Django REST Framework API view |
| NoAnswerPolicyGuard | Filters AI responses to prevent solution/target-state exposure. | Python service class |

#### Object-Oriented Components

Primary classes/components: AiScenarioDraft, ScenarioSkillFocus, DifficultyInstance, DifficultyVariant, CommandCountPolicy, TargetStateRule, ConceptChatSession, NoAnswerPolicyGuard.

##### Class Diagram
[PLACEHOLDER — Insert class diagram for Generate AI-Assisted Scenario Draft and Provide Concept Chat.]

##### Sequence Diagram
[PLACEHOLDER — Insert sequence diagram for Generate AI-Assisted Scenario Draft and Provide Concept Chat.]

#### Data Design
Tables/entities involved: AiScenarioDraft, ScenarioSkillFocus, DifficultyInstance, DifficultyVariant, CommandCountPolicy, TargetStateRule, ConceptChatSession, AdminAuditLog. AI-generated scenario content is not student-accessible until administrator validation and publication. This module is planned Phase 2 scope.

##### ERD or schema
[PLACEHOLDER — Insert ERD/schema excerpt for Generate AI-Assisted Scenario Draft and Provide Concept Chat.]


