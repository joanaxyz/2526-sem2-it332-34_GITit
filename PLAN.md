# Roadmap: User-Generated Tower, Assets, and Levels

## Current Baseline

The asset foundation is done and should not be re-planned here.

Implemented foundation:

- `backend/assets/` exists with `Asset` and `AssetSprite`.
- Monster sprites are seeded and served through backend descriptors.
- Sprite frame counts are derived by the system from uploaded sheets.
- Battle payloads can carry monster descriptors instead of relying on compiled
  frontend monster registries.
- Storeys already load a single overview payload from
  `backend/curriculum/selectors.py::storey_content_overview`.

Important current constraints:

- `Asset.kind` currently has `monster`, `character`, `tower_artifact`, and
  `projectile`. It has no structural tower-piece kind yet.
- The tower is still rendered as DOM/CSS in
  `frontend/src/features/storeys/components/StoreyLevelHub.tsx` and
  `frontend/src/styles/globals.css`.
- Blue's movement scans DOM classes like `.tower-section-separator` and
  `.tower-tome-separator` in
  `frontend/src/features/storeys/character/useCharacterController.ts`.
- Runtime content is split across existing models:
  `CommandAdventure` / `AdventureLevel` / `AdventureVariant`,
  `Challenge` / `ChallengeLevel` / `ChallengeVariant`, and `Tome`.

This plan starts from that baseline.

## Product Vocabulary

Use these names in code, payloads, docs, and UI going forward.

| Old or vague term | New term | Meaning |
| --- | --- | --- |
| roof | spire | The tower's top cap. Use `spire` in code. UI copy can later choose Spire, Crown, or Tower Crown. |
| separator | landing | The walkable ledge/platform Blue can stand on. |
| adventure section | adventure_section | Structural section that can launch a Command Adventure. |
| challenge section | challenge_section | Structural section that can launch a GIT Challenged level. |
| doors | door | Entry/navigation piece, including locked and unlocked states. |
| tomes | tome | Readable lesson piece. The content is authored separately; the piece is the visual node. |
| artifacts | tower_artifact | User-placeable props layered onto tower pieces. Artifacts do not define tower geometry. |

Tower pieces define structure, geometry, anchors, stacking, and interaction
zones. Artifacts are placed onto pieces. Authored content binds to pieces.

## Asset Taxonomy

The `Asset.kind` enum should answer "which renderer family owns this asset?",
not enumerate every individual tower part. Tower-specific subtypes should be a
second field or detail model.

Recommended shape:

```python
class AssetKind(models.TextChoices):
    MONSTER = "monster", "Monster"
    CHARACTER = "character", "Character"
    PROJECTILE = "projectile", "Projectile"
    TOWER_PIECE = "tower_piece", "Tower piece"
    TOWER_ARTIFACT = "tower_artifact", "Tower artifact"


class TowerPieceType(models.TextChoices):
    SPIRE = "spire", "Spire"
    LANDING = "landing", "Landing"
    DOOR = "door", "Door"
    ADVENTURE_SECTION = "adventure_section", "Adventure section"
    CHALLENGE_SECTION = "challenge_section", "Challenge section"
    TOME = "tome", "Tome"
```

Implementation preference:

- Add a dedicated `TowerPieceAsset` detail model instead of putting every
  tower-only field directly on `Asset`.
- Keep `Asset` as the common ownership, visibility, pricing, slug, label,
  publication, and file/sprite container.
- Let `TowerPieceAsset` carry `piece_type`, geometry metadata, anchor metadata,
  state variants, and SVG sanitization status.
- Keep `tower_artifact` separate. Artifacts are overlays/props; they do not own
  the tower's walk rails, bounds, or click zones.
- Do not add `tower_landing`, `tower_door`, `tower_tome`, etc. to `Asset.kind`.
  That would make the enum brittle and force schema churn for every future tower
  part.

Suggested models:

```python
class TowerPieceAsset(models.Model):
    asset = models.OneToOneField(Asset, related_name="tower_piece", on_delete=models.CASCADE)
    piece_type = models.CharField(max_length=32, choices=TowerPieceType.choices)
    view_box = models.CharField(max_length=80, blank=True)
    anchors = models.JSONField(default=dict, blank=True)
    bounds = models.JSONField(default=dict, blank=True)
    interaction_zones = models.JSONField(default=dict, blank=True)
    state_variants = models.JSONField(default=dict, blank=True)
```

Example anchors:

```json
{
  "walk_rail": { "x1": 12, "y1": 84, "x2": 188, "y2": 84 },
  "door_center": { "x": 100, "y": 68 },
  "artifact_safe_bounds": { "x": 20, "y": 14, "width": 160, "height": 70 }
}
```

## Content Taxonomy

Visual assets and authored content must stay separate.

- A `tower_piece` is the clickable/visible place on the tower.
- A `tower_artifact` is a prop placed on a tower piece.
- A tome/adventure/challenge definition is authored learning content.
- A tower design binds authored content to tower piece instances.

Do not model user-authored levels as image assets.

Recommended content shape:

```python
class ContentKind(models.TextChoices):
    ADVENTURE = "adventure", "Command adventure"
    CHALLENGE = "challenge", "Challenge"
    TOME = "tome", "Tome"


class ContentDefinition(models.Model):
    kind = models.CharField(max_length=20, choices=ContentKind.choices)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    source_definition = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES)
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16)  # draft | testable | published | archived
    definition = models.JSONField(default=dict)
```

Use `definition` as a validated schema, not arbitrary loose JSON. The schema can
later be split into first-class tables once the product shape is proven.

For v1, published user content can adapt into the existing runtime systems
instead of replacing them immediately:

- adventure definitions produce adventure level/variant runtime payloads;
- challenge definitions produce challenge level/variant runtime payloads;
- tome definitions use the existing book page/block schema.

## Cross-Cutting Rules

- Ownership: `owner=null` means official seeded content.
- Visibility: `private`, `public`, and `store` should apply consistently to
  assets, content definitions, and tower designs.
- Remixing: clones keep creator attribution and source references.
- Entitlements: purchases debit `progress.Wallet` through `CoinTransaction` and
  grant access to the purchased asset/content/design.
- Upload safety: sanitize SVGs, reject scriptable markup, validate type/size,
  enforce quotas, and serve media from a strict media origin/CSP.
- Runtime safety: level authoring must remain declarative. No arbitrary code
  execution in repository setup, evaluator rules, hints, or battle scripts.
- Hot paths: descriptor maps should remain cached. Submitting commands should
  not query asset or authoring tables on each command.

## Phase 2 - Asset Enum Cleanup and Character Assets

Goal: make the asset foundation ready for tower pieces, then move Blue onto the
same descriptor path as monsters.

Backend:

1. Convert asset kind constants in `backend/assets/models.py` to a
   `models.TextChoices` shape or equivalent constants with the same values.
2. Add `tower_piece` to `Asset.kind`.
3. Add `TowerPieceAsset` and `TowerPieceType`.
4. Validate that only `Asset(kind=tower_piece)` can have a `TowerPieceAsset`.
5. Keep existing `tower_artifact` assets valid.
6. Extend `backend/assets/descriptors.py` so descriptors include enough
   kind-specific detail for characters and tower pieces.

Frontend:

1. Add shared descriptor types for `monster`, `character`, `tower_piece`, and
   `tower_artifact`.
2. Migrate `frontend/src/shared/sprites/characters.ts` so Blue can be loaded
   from `Asset(kind=character)`.
3. Keep a local fallback for development and failed descriptor fetches.
4. Add active character selection later in this phase only if the descriptor
   migration is stable.

Verification:

- Existing monster tests stay green.
- New tests reject invalid asset/tower-piece combinations.
- Blue renders from a backend descriptor in normal play.
- Fallback character rendering still works in dev/offline contexts.

## Phase 3 - Tower Piece Data Before Renderer Rewrite

Goal: describe the current tower as data while it still renders through the
existing DOM/CSS implementation.

Backend:

1. Seed official `tower_piece` assets for:
   `spire`, `landing`, `door`, `adventure_section`, `challenge_section`, and
   `tome`.
2. Add official descriptors for the current built-in tower look. These may
   initially point to simple SVGs or placeholders while CSS still paints the
   existing visuals.
3. Extend `storey_content_overview` so each storey includes a `tower_layout`
   section describing the ordered pieces and their content bindings.

Frontend:

1. Add `TowerPieceDescriptor` and `TowerLayoutDescriptor` types.
2. Keep `StoreyLevelHub.tsx` rendering the current DOM/CSS pieces, but route
   labels, ordering, and piece identity through `tower_layout`.
3. Introduce landing terminology in code next to existing separator classes:
   `landing` in data/types, compatibility CSS classes in rendering.
4. Do not rewrite Blue movement yet. Keep current DOM scanning until SVG rails
   exist.

Suggested payload shape:

```ts
type TowerPieceDescriptor = {
  instanceId: string
  assetSlug: string
  pieceType: 'spire' | 'landing' | 'door' | 'adventure_section' | 'challenge_section' | 'tome'
  contentBinding?: {
    kind: 'adventure' | 'challenge' | 'tome'
    id: number | string
  }
}

type TowerLayoutDescriptor = {
  storeyId: number
  pieces: TowerPieceDescriptor[]
}
```

Verification:

- Existing tower UI looks and behaves the same.
- Overview payload includes tower piece identity.
- Selection still works for adventures, challenge levels, and tomes.
- The word `landing` exists in new data/types while old `separator` classes
  remain only as compatibility rendering details.

## Phase 4 - SVG Tower Rendering and Landing Rename

Goal: switch from hardcoded DOM/CSS tower pieces to asset-driven SVG pieces.

1. Refactor `StoreyLevelHub.tsx` into renderer components:
   `TowerPiece`, `LandingPiece`, `AdventureSectionPiece`,
   `ChallengeSectionPiece`, `DoorPiece`, `TomePiece`, and `SpirePiece`.
2. Render official SVG tower pieces from descriptors.
3. Move walkable rail data from computed CSS pseudo-elements into piece anchors.
4. Update `useCharacterController.ts` to scan landing rail anchors instead of
   `.tower-section-separator` and `.tower-tome-separator`.
5. Rename active tower CSS/classes from separator to landing once the renderer
   no longer depends on the old names.
6. Keep the same player behavior: scroll, lazy storey loading, selected door
   overview, action dock, challenge locking, and tome reader.
7. Add read-only artifact rendering on top of tower pieces.

Verification:

- Desktop and mobile screenshots match the current composition closely.
- Blue can spawn, walk, fly, land, and teleport using SVG rail anchors.
- Challenge/adventure/tome selection and navigation match current behavior.
- Active tower code no longer uses `separator` except explicit migration shims.

## Phase 5 - User Authored Levels and Tomes

Goal: let users author learning content before the tower editor becomes fully
writeable.

Authoring capabilities:

- Create a draft adventure, challenge, or tome.
- Edit title, summary, tags, command family, difficulty, and story context.
- Author repository setup declaratively:
  files, branches, commits, staged files, working tree changes, ignored files,
  remotes, and HEAD position.
- Author allowed commands and command budgets.
- Build evaluator rules using the existing evaluation/checklist vocabulary.
- Add hints and scaffold policy.
- Choose battle monsters by `Asset.slug`, with optional HP/scale overrides.
- Author tome pages with the existing book page/block schema.
- Test-play the draft before publishing.
- Publish only after server-side validation succeeds.

Validation requirements:

- Unknown commands are rejected.
- Unknown asset slugs are rejected.
- Unsafe or impossible repository states are rejected.
- Evaluator specs must compile before publish.
- Battle specs must produce a valid encounter or boss.
- Tome pages must match the book block schema.

Runtime strategy:

- Start with an authoring schema that adapts into current adventure/challenge
  run services.
- Avoid a large rewrite of `AdventureRunService` and `ChallengeRunService`
  until user-authored definitions are proven.
- Keep official seeded content working through existing models.

Key files likely touched:

- `backend/adventures/models.py`
- `backend/challenges/models.py`
- `backend/curriculum/models.py`
- `backend/evaluation/*`
- `backend/practice/builders.py`
- `backend/practice/context.py`
- `frontend/src/shared/level/*`
- new authoring pages/components under `frontend/src/features/authoring/`

Verification:

- A user can create, test-play, publish, and replay one adventure definition.
- A user can create, test-play, publish, and replay one challenge definition.
- A user can create and publish one tome definition.
- Published definitions can be read by the tower layout payload.

## Phase 6 - Tower Editor and Content Binding

Goal: users compose their own tower from pieces, artifacts, and authored
content.

Models:

```python
class TowerDesign(models.Model):
    owner
    source_design
    visibility
    slug, title, summary
    status  # draft | published | archived


class TowerPieceInstance(models.Model):
    tower_design
    piece_asset
    piece_type
    sort_order
    parent_instance
    transform
    config


class TowerContentBinding(models.Model):
    piece_instance
    content_definition


class ArtifactPlacement(models.Model):
    tower_design
    target_piece_instance
    artifact_asset
    x, y, scale, rotation
    anchor
    z_index
```

Editor behavior:

- Pick or upload tower pieces.
- Add/remove/reorder storey sections.
- Bind adventure definitions to adventure sections.
- Bind challenge definitions to challenge sections.
- Bind tome definitions to tome pieces.
- Drag artifacts onto safe bounds on tower pieces.
- Snap artifacts to anchors when available.
- Preview as a player before publish.

Verification:

- A user can create a tower design from official pieces.
- A user can bind one authored adventure, challenge, and tome.
- A user can place at least one artifact onto an adventure/challenge section.
- Preview mode uses the same tower renderer as play mode.

## Phase 7 - Store, Gallery, Sharing, and Remixing

Goal: turn assets, tower designs, and authored content into a public ecosystem.

1. Add entitlement models for purchased assets/content/designs.
2. Add wallet purchase flow through `progress.Wallet` and `CoinTransaction`.
3. Build gallery filters by asset kind, tower piece type, content kind,
   difficulty, command family, creator, price, and ownership.
4. Add remix flows for assets, content definitions, and tower designs.
5. Preserve creator attribution across remixes.
6. Add moderation, reports, upload quotas, and rate limits before broad public
   upload.
7. Add store listing status separate from publication status so creators can
   publish free work before selling work.

Verification:

- Buying grants an entitlement and unlocks the item in the relevant picker.
- Remixing creates a private editable copy with source attribution.
- Private items are invisible to other users.
- Store/gallery queries do not expose unpublished or unentitled records.

## Open Decisions

- UI label for the top piece: code should use `spire`; product copy can later
  choose Spire, Crown, or Tower Crown.
- Whether `TowerPieceAsset` should parse SVG anchors automatically or require a
  sidecar JSON manifest on upload.
- Whether user-authored content should eventually replace official
  `AdventureLevel`, `ChallengeLevel`, and `Tome` rows, or remain an authoring
  layer that compiles/adapts into them.
- Whether public SVG uploads are sanitized and served as SVG or rasterized on
  upload.
- Whether the first marketplace release supports paid listings or only free
  public sharing plus remixing.
