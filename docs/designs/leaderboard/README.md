# Leaderboard redesign

The existing `/leaderboard` page now shows equipped-companion avatars, an open champion podium, generated gold/silver/bronze portrait frames with rank numbers, category artwork, and highlighted personal standings.

- [ImageGen concept](leaderboard-mockup.png)
- [Implemented desktop view](leaderboard-desktop.png)
- [Implemented mobile view](leaderboard-mobile.png)

The implementation screenshots use isolated demonstration data. The real page reads the existing leaderboard endpoint, including its new nullable `companion_slug` field. Missing, unknown, and unavailable companion images fall back to initials.

Runtime assets are in `frontend/public/leaderboard/` as transparent WebP images (about 203KB combined). Original generated PNGs are retained in [source-frames](source-frames/) and [source-icons](source-icons/). The gold frame includes a crown and number 1; silver and bronze contain numbers 2 and 3. Frames are selected by the actual rank, including ties.

All images were generated with the built-in ImageGen tool. Exact prompts are recorded in [mockup-prompt.md](mockup-prompt.md), [image-prompts.md](image-prompts.md), [frame-prompts.md](frame-prompts.md), and [final-frame-prompts.md](final-frame-prompts.md).

Validation: 10 leaderboard frontend tests, 15 backend XP/leaderboard tests, targeted ESLint, production build, generated API contract consistency and usage checks, typography, and diff whitespace. Browser checks covered desktop, 390px phone, and 320px narrow layouts, with long names/scores, category switching, ties, and empty states.
