# AI learning tutor implementation plan

**Intent:** Independent Home Git help and guide-bound workspace help without scenario solutions.
**Truth owner:** Backend tutoring owns recognition, teaching eligibility, rendering and provider failover. Seed banks own scenario text; the command catalog and reviewed concepts own teaching content.
**Contract boundary:** Authenticated `/api/tutoring/chat/`; generated OpenAPI/TypeScript; no provider prose or solution data crosses the response boundary.
**Cutover:** Exact guide examples are removed, prospective changes generalized, tokens digest their private binding, and old browser guide history is invalidated.
**Displaced path:** `example_command` feedback and raw objective-bearing signed tokens.
**Acceptance evidence:** Authenticated two-tab Home/workspace walkthrough, response/token audits, adversarial scenario coverage, failover checks, desktop/mobile screenshots.
**Kill criteria:** No exact-example fallback, unrestricted provider reply, or alternate client-side answer policy remains.
**Forbidden moves:** Change grading/rewards, send seed solutions to providers, expose keys, overwrite unrelated working changes.
**Plan review gate:** PRE review completed in planning; POST/correctness/maintainability review required.

## Approved behavior

- General chatbot is available across Dashboard, Modules (including module maps), and Shop independently of guides. Workspace chatbot has its own separate window outside the guide container, available only while a first-encounter or reopened guide is active. Closing the guide unmounts chat and cancels pending requests.
- General and workspace AI use floating mascot portraits without visible labels. The open interface has the mascot beside its speech-style card (inside the header on mobile) and assistant message bubbles. The user's screenshot refinement supersedes the earlier avatar-free workspace request and intermediate chat-bubble launcher. The latest request removes the mascot from both the command-guide card and launcher; its separate command icon preserves history and dragging. No book icon is used. Help controls stay available when decorative mascot is hidden.
- Chat opens by default, can be dragged and resized with pointer or keyboard, and remains within the viewport. While open its floating launcher is hidden; closing chat restores the single mascot launcher and reopening retains its window position and size.
- Recognize all 399 scenarios in both seed banks through public-field text and semantic retrieval. Recognition is independent of active runs/tabs.
- Retrieve reviewed teaching blocks separately. Models select eligible block IDs; server renders approved explanations and placeholders only.
- Do not recommend a solution, next form/flag, confirm guesses, fill scenario operands, or assemble command sequences. Task-only prompts receive neutral learning guidance/topic selection.
- Ordered configurable Gemini models use GOOGLE_AI_STUDIO_API_KEY; once rate limited, fail over to Groq using GROQ_API_KEY. Bound attempts/deadline and honor cooldowns. Static teaching remains usable when providers fail.
- Session-only, account-isolated bounded chat history. No chat persistence or database migration.

## Ordered task board

1. **Main / backend safety:** Implement reviewed teaching catalog, strict eligibility/renderer, all-bank recognizer and versioned cached embeddings, authenticated API, provider adapters/cooldowns. Verify with adversarial/ownership/failover tests.
2. **Main / guide cutover:** Remove exact examples, sanitize legacy/pending/prospective payloads, digest token bindings and retire old cache. Verify existing command accounting and introduction completion.
3. **Main / client:** Add shared bubble chat UI, floating icon entry, separate guide-scoped workspace window, cancellation/account isolation, accessible responsive styling. Regenerate contracts; test and build.
4. **Main / evidence:** Build semantic index if credentials permit, run API/browser scenarios, capture screenshots and focused evidence. Run repo guards and required independent reviews; fix material findings.

Tasks are sequential; all implementation stays with main. Reviewers are read-only.
