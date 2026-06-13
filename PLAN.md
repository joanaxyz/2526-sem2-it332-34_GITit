# Roadmap: User Authored Content, Private Towers, and Store

## Current Status

Phases 2-4 are foundation work and are already represented in the current
worktree. Do not re-plan them as future work.

Already built:

- `AssetKind.TOWER_PIECE`, `TowerPieceType`, and `TowerPieceAsset`.
- Official tower-piece seed assets for `spire`, `landing`, `door`,
  `adventure_section`, `challenge_section`, and `tome`.
- `storey_content_overview` emits `tower_layout`.
- `StoreyLevelHub.tsx` and `TowerPieces.tsx` consume tower layout and
  descriptor data.
- Blue's controller can read SVG rail anchors, with DOM fallback shims still
  present for migration safety.

Not built yet:

- Phase 5: user authored adventures, challenges, and tomes.
- Phase 6: private user-owned tower designs and the editor page.
- Phase 7: store/gallery listings, entitlements, purchasing, and remixing.

Important constraint: the missing pages cannot be implemented as frontend-only
screens. Each page depends on backend ownership, visibility, validation, and
access-control models.

## First Pass Scope

Build a complete MVP vertical slice for each missing phase:

1. Users can create, validate, test-play, and publish authored content.
2. Users can create one private tower design, bind content to it, place
   artifacts, preview it, and publish it.
3. Users can browse public/store listings, buy paid items with GitCoins, unlock
   the purchased item, and remix unlocked content/designs.

Keep the scope intentionally narrow:

- No arbitrary code execution in authoring.
- No broad public upload launch until SVG/media hardening is complete.
- No replacement of official `CommandAdventure`, `Challenge`, or `Tome` runtime
  tables in the first pass.
- No full WYSIWYG level scripting language. Use declarative JSON schemas that
  adapt into existing simulator/evaluator services.

## Shared Product Rules

- `owner = null` means official seeded content.
- User-owned rows default to `private`.
- Visibility values: `private`, `public`, `store`.
- Status values for editable things: `draft`, `testable`, `published`,
  `archived`.
- Store listing state is separate from publication state. A creator may publish
  free public work without listing it for sale.
- Entitlements grant access; they do not copy the purchased record.
- Remixing creates a private editable copy and stores source attribution.
- Runtime hot paths must not query store/listing/entitlement tables on command
  submit. Check access before run start and serialize enough run payload data up
  front.

## Phase 5 - User Authored Content

Goal: add backend-first authoring for adventures, challenges, and tomes, then
build the authoring UI on top.

### Backend App

Create a new `backend/authoring/` Django app and add it to
`INSTALLED_APPS`.

Core models:

```python
class ContentKind(models.TextChoices):
    ADVENTURE = "adventure", "Adventure"
    CHALLENGE = "challenge", "Challenge"
    TOME = "tome", "Tome"


class ContentDefinition(models.Model):
    kind = models.CharField(max_length=20, choices=ContentKind.choices)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    source_definition = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="private")
    status = models.CharField(max_length=16, default="draft")
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    command_family = models.CharField(max_length=80, blank=True)
    difficulty = models.CharField(max_length=12, blank=True)
    definition = models.JSONField(default=dict)
    validation_errors = models.JSONField(default=list, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Runtime bridge model:

```python
class PublishedContentRuntime(models.Model):
    content_definition = models.OneToOneField(ContentDefinition, related_name="runtime", on_delete=models.CASCADE)
    storey = models.ForeignKey("curriculum.Storey", null=True, blank=True, on_delete=models.SET_NULL)
    command_adventure = models.ForeignKey("adventures.CommandAdventure", null=True, blank=True, on_delete=models.SET_NULL)
    challenge = models.ForeignKey("challenges.Challenge", null=True, blank=True, on_delete=models.SET_NULL)
    tome = models.ForeignKey("curriculum.Tome", null=True, blank=True, on_delete=models.SET_NULL)
    definition_signature = models.CharField(max_length=64)
    compiled_at = models.DateTimeField(auto_now=True)
```

Why this bridge exists: current run services are tied to official runtime
tables. The first pass should compile published user content into hidden runtime
rows so `AdventureRunService`, `ChallengeRunService`, simulator, battle, and
evaluator code can be reused instead of rewritten.

### Runtime Bridge Details

For adventures:

- Create a hidden `Storey` per published adventure definition.
- Use a reserved synthetic storey number range and set `is_published=False`.
- Set `chest_rewards=[]` for hidden runtime storeys.
- Create a `CommandAdventure` on that hidden storey.
- Create private `CommandSkill` and `CommandForm` rows from the authored command
  metadata.
- Create `AdventureLevel` and `AdventureVariant` rows from the authored
  definition.
- Add a nullable `source_content_definition` field to `CommandAdventure` so
  launch/access can distinguish official rows from user-authored rows.

For challenges:

- Create a hidden `Storey` per challenge definition.
- Use a reserved synthetic storey number range and set `is_published=False`.
- Set `chest_rewards=[]` for hidden runtime storeys.
- Create a `Challenge`, `ChallengeLevel`, and `ChallengeVariant` rows from the
  definition.
- Add nullable `source_content_definition` to `Challenge`.
- Update challenge run start access checks so content-backed challenge levels
  require ownership, public visibility, or entitlement.

For tomes:

- Compile to a hidden-storey `Tome` only when needed by legacy payloads.
- Private tower payloads may also serialize tome pages directly from
  `ContentDefinition.definition`.
- Add nullable `source_content_definition` to `Tome` if compiled rows are used.

Progress and reward isolation:

- Content-backed runs must not award official storey chests unless a later
  product decision explicitly enables creator-content rewards.
- `StoreyChestService` should return early for hidden/user-authored runtime
  storeys, even if a bad seed accidentally leaves chest rewards present.
- Dashboard/stat selectors should either exclude content-backed completions or
  report them in separate "community content" fields.
- Test-play runs should never create durable official progression, streak, or
  wallet effects.

### Validation Services

Add these modules:

- `backend/authoring/schemas.py`
- `backend/authoring/validators.py`
- `backend/authoring/compiler.py`
- `backend/authoring/services.py`
- `backend/authoring/selectors.py`
- `backend/authoring/views.py`
- `backend/authoring/urls.py`

Validation must reject:

- Unknown or unsupported Git commands.
- Unknown monster/asset slugs.
- Invalid repository states.
- Evaluation specs that do not compile.
- Authored solutions that do not satisfy evaluation specs.
- Scenario context that leaks solution commands.
- Tome pages that do not match the existing book page/block schema.
- Battle specs that cannot produce a valid encounter or boss.

Reuse existing services where possible:

- `practice.builders.StaticLevelVariantBuilder`
- `simulator.services.RepositoryStateSimulator`
- `simulator.workspace_files.WorkspaceFileStateService`
- `evaluation.compiler.compile_evaluation_spec`
- `evaluation.engine.EvaluationEngine`
- `practice.context.ScenarioContextNormalizer`

### API Endpoints

Add under `/api/authoring/`:

- `GET /content-definitions/`
- `POST /content-definitions/`
- `GET /content-definitions/<id>/`
- `PATCH /content-definitions/<id>/`
- `POST /content-definitions/<id>/validate/`
- `POST /content-definitions/<id>/publish/`
- `POST /content-definitions/<id>/remix/`
- `POST /content-definitions/<id>/test-run/`

Rules:

- Only owners can edit drafts.
- Private definitions are visible only to owner and staff.
- Public definitions are readable by everyone.
- Store definitions are readable in marketplace contexts, but launch/remix
  requires ownership or entitlement unless price is 0.
- `test-run` must work for drafts owned by the requester and must not expose the
  draft to anyone else.

### Frontend

Add:

- `frontend/src/features/authoring/api/authoringApi.ts`
- `frontend/src/features/authoring/types.ts`
- `frontend/src/features/authoring/pages/AuthoringLibraryPage.tsx`
- `frontend/src/features/authoring/pages/ContentEditorPage.tsx`
- `frontend/src/features/authoring/components/*`

Routes:

- `/authoring`
- `/authoring/new/:kind`
- `/authoring/:definitionId`

MVP editor controls:

- Kind selector: adventure, challenge, tome.
- Title, summary, tags, command family, difficulty.
- Repository setup editor backed by structured JSON, not free-form code.
- Solution commands.
- Evaluation/checklist rule builder using existing supported rule vocabulary.
- Hints and scaffold policy.
- Monster picker by `Asset.slug`.
- Tome page/block editor using the existing book schema.
- Validate, test-play, publish buttons with server errors shown inline.

### Phase 5 Verification

Backend tests:

- `backend/authoring/tests/test_content_definition_models.py`
- `backend/authoring/tests/test_content_validation.py`
- `backend/authoring/tests/test_content_compile.py`
- `backend/authoring/tests/test_content_api.py`

User-visible acceptance:

- A user can create and validate one adventure definition.
- A user can test-play the adventure through the existing adventure UI.
- A user can create and validate one challenge definition.
- A user can test-play the challenge through the existing challenge UI.
- A user can create and publish one tome definition.
- Private definitions are not visible to another user.

## Phase 6 - Private Tower and Editor

Goal: users own tower designs that bind tower pieces to authored content and
place artifacts.

### Backend App

Create a new `backend/towers/` app and add it to `INSTALLED_APPS`.

Models:

```python
class TowerDesign(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    source_design = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="private")
    status = models.CharField(max_length=16, default="draft")
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TowerPieceInstance(models.Model):
    tower_design = models.ForeignKey(TowerDesign, related_name="pieces", on_delete=models.CASCADE)
    piece_asset = models.ForeignKey("assets.Asset", on_delete=models.PROTECT)
    piece_type = models.CharField(max_length=32)
    sort_order = models.PositiveIntegerField(default=0)
    parent_instance = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    transform = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True)


class TowerContentBinding(models.Model):
    piece_instance = models.OneToOneField(TowerPieceInstance, related_name="content_binding", on_delete=models.CASCADE)
    content_definition = models.ForeignKey("authoring.ContentDefinition", on_delete=models.PROTECT)


class ArtifactPlacement(models.Model):
    tower_design = models.ForeignKey(TowerDesign, related_name="artifact_placements", on_delete=models.CASCADE)
    target_piece_instance = models.ForeignKey(TowerPieceInstance, related_name="artifact_placements", on_delete=models.CASCADE)
    artifact_asset = models.ForeignKey("assets.Asset", on_delete=models.PROTECT)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    scale = models.FloatField(default=1)
    rotation = models.FloatField(default=0)
    anchor = models.CharField(max_length=80, blank=True)
    z_index = models.IntegerField(default=0)
```

Validation:

- `piece_asset.kind` must be `tower_piece`.
- `piece_type` must match `piece_asset.tower_piece.piece_type`.
- Content bindings must match compatible piece types:
  - adventure content only on `adventure_section`
  - challenge content only on `challenge_section`
  - tome content only on `tome`
- Artifact assets must use `tower_artifact`.
- Artifact placements must stay inside piece safe bounds when bounds exist.
- Publishing requires every interactive content piece to have a valid published
  or testable content definition.

### API Endpoints

Add under `/api/tower-designs/`:

- `GET /mine/`
- `POST /`
- `GET /<id>/`
- `PATCH /<id>/`
- `POST /<id>/set-active/`
- `POST /<id>/publish/`
- `POST /<id>/remix/`
- `GET /<id>/layout/`
- `POST /<id>/pieces/`
- `PATCH /<id>/pieces/<piece_id>/`
- `DELETE /<id>/pieces/<piece_id>/`
- `POST /<id>/bindings/`
- `DELETE /<id>/bindings/<binding_id>/`
- `POST /<id>/artifacts/`
- `PATCH /<id>/artifacts/<placement_id>/`
- `DELETE /<id>/artifacts/<placement_id>/`

Add private play route payload:

- `GET /api/my-tower/overview/`

This should return the active design for the current user in a shape close to
the current `StoreyContentOverview`, but design-based:

```ts
type TowerDesignOverview = {
  design: { id: number; slug: string; title: string; status: string }
  tower_layout: TowerLayoutDescriptor
  content: {
    adventures: Record<string, CommandAdventureSummary>
    challenges: Record<string, ChallengeSummary>
    tomes: Record<string, TomeSummary>
  }
  artifacts: ArtifactPlacementDescriptor[]
}
```

### Frontend

Add:

- `frontend/src/features/towers/api/towersApi.ts`
- `frontend/src/features/towers/types.ts`
- `frontend/src/features/towers/pages/MyTowerPage.tsx`
- `frontend/src/features/towers/pages/TowerEditorPage.tsx`
- `frontend/src/features/towers/components/TowerDesignRenderer.tsx`
- `frontend/src/features/towers/components/TowerEditorCanvas.tsx`
- `frontend/src/features/towers/components/PiecePalette.tsx`
- `frontend/src/features/towers/components/ContentBindingPanel.tsx`
- `frontend/src/features/towers/components/ArtifactPalette.tsx`

Routes:

- `/my-tower`
- `/tower/editor`
- `/tower/editor/:designId`

Keep `/tower` as the official shared tower until the private tower is stable.
Add navigation to the private tower/editor after the backend routes exist.

Editor MVP behavior:

- Create a design from official tower pieces.
- Add, remove, and reorder pieces.
- Bind authored adventure/challenge/tome content.
- Place official or entitled artifacts on piece safe bounds.
- Preview with the same renderer used by play mode.
- Publish after validation.

Renderer rules:

- Reuse `TowerPieces.tsx` and descriptor loading.
- Keep Blue movement anchor data in the rendered DOM/SVG attributes.
- Do not fork tower physics for editor preview.
- Keep compatibility shims until private tower play mode passes movement tests.

### Phase 6 Verification

Backend tests:

- `backend/towers/tests/test_tower_design_models.py`
- `backend/towers/tests/test_tower_design_api.py`
- `backend/towers/tests/test_tower_layout_payload.py`
- `backend/towers/tests/test_tower_access.py`

Frontend tests:

- Render editor with seeded official pieces.
- Bind one content definition per content type.
- Reorder pieces without losing bindings.
- Preview uses the same descriptors as play mode.

User-visible acceptance:

- A user can create a private tower design.
- A user can bind one authored adventure, one challenge, and one tome.
- A user can place one artifact.
- Another user cannot read or edit the private design.
- The active private tower renders on `/my-tower`.

## Phase 7 - Store, Gallery, Sharing, and Remixing

Goal: turn assets, content definitions, and tower designs into a controlled
public ecosystem.

### Backend App

Create a new `backend/marketplace/` app and add it to `INSTALLED_APPS`.

Models:

```python
class StoreListing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    item_kind = models.CharField(max_length=24)  # asset | content_definition | tower_design
    asset = models.ForeignKey("assets.Asset", null=True, blank=True, on_delete=models.CASCADE)
    content_definition = models.ForeignKey("authoring.ContentDefinition", null=True, blank=True, on_delete=models.CASCADE)
    tower_design = models.ForeignKey("towers.TowerDesign", null=True, blank=True, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, default="draft")  # draft | active | paused | archived
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Entitlement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item_kind = models.CharField(max_length=24)
    asset = models.ForeignKey("assets.Asset", null=True, blank=True, on_delete=models.CASCADE)
    content_definition = models.ForeignKey("authoring.ContentDefinition", null=True, blank=True, on_delete=models.CASCADE)
    tower_design = models.ForeignKey("towers.TowerDesign", null=True, blank=True, on_delete=models.CASCADE)
    source_listing = models.ForeignKey(StoreListing, null=True, blank=True, on_delete=models.SET_NULL)
    granted_at = models.DateTimeField(auto_now_add=True)
```

Constraints:

- A listing references exactly one item.
- An entitlement references exactly one item.
- A user can have only one entitlement per item.
- Owners have implicit access and do not need entitlement rows.
- Official free items may be treated as implicitly entitled.

### Wallet Purchase Flow

Extend `progress.wallet.WalletService` with a debit method:

- Lock the buyer wallet row with `select_for_update`.
- Reject insufficient balance.
- Create a negative `CoinTransaction`.
- Use an idempotent `award_key`, such as `purchase:<listing_id>:<user_id>`.
- Create the entitlement in the same transaction.
- Return the updated wallet summary and entitlement payload.

Do not mutate balances outside `WalletService`.

### API Endpoints

Add under `/api/store/`:

- `GET /listings/`
- `GET /listings/<id>/`
- `POST /listings/`
- `PATCH /listings/<id>/`
- `POST /listings/<id>/purchase/`

Add under `/api/gallery/`:

- `GET /assets/`
- `GET /content/`
- `GET /tower-designs/`
- `POST /assets/<id>/remix/`
- `POST /content/<id>/remix/`
- `POST /tower-designs/<id>/remix/`

Filters:

- asset kind
- tower piece type
- content kind
- difficulty
- command family
- creator
- price
- ownership
- entitled/unlocked
- public/store visibility

### Access Service

Add `backend/marketplace/access.py`:

- `can_view(user, item)`
- `can_edit(user, item)`
- `can_launch(user, content_definition)`
- `can_use_asset(user, asset)`
- `can_use_tower_design(user, tower_design)`
- `can_remix(user, item)`

Use this service from:

- authoring selectors and launch endpoints
- tower design selectors and editor pickers
- store/gallery endpoints
- asset picker endpoints
- content-backed run start checks

### Frontend

Add:

- `frontend/src/features/store/api/storeApi.ts`
- `frontend/src/features/store/pages/StorePage.tsx`
- `frontend/src/features/store/components/ListingGrid.tsx`
- `frontend/src/features/store/components/PurchaseDialog.tsx`
- `frontend/src/features/gallery/api/galleryApi.ts`
- `frontend/src/features/gallery/pages/GalleryPage.tsx`
- `frontend/src/features/gallery/components/GalleryFilters.tsx`

Routes:

- `/store`
- `/gallery`

MVP behavior:

- Browse active listings.
- Filter by item type and owned/unlocked state.
- Buy with GitCoins.
- See the wallet balance update after purchase.
- Purchased assets/content/designs appear in editor pickers.
- Remix unlocked public/store items into private editable copies.

### Phase 7 Verification

Backend tests:

- `backend/marketplace/tests/test_store_listing_models.py`
- `backend/marketplace/tests/test_entitlements.py`
- `backend/marketplace/tests/test_purchase_flow.py`
- `backend/marketplace/tests/test_gallery_visibility.py`
- `backend/progress/tests/test_wallet.py` updated for debits.

Frontend tests:

- Listing grid renders owned and locked states.
- Purchase success invalidates wallet and picker queries.
- Purchase failure shows insufficient balance.
- Remix creates a private copy and navigates to the editor.

User-visible acceptance:

- Buying grants an entitlement and debits the wallet exactly once.
- Purchased items unlock in the relevant tower/content/asset picker.
- Private items are invisible to other users.
- Public free items can be remixed.
- Store queries do not expose draft, archived, unpublished, or unentitled
  private records.

## Implementation Order

1. Clean up the current Phases 2-4 branch only enough to keep tests green.
2. Add `authoring` models, migrations, admin, and validation services.
3. Add content compile/runtime bridge and access checks for content-backed run
   starts.
4. Add authoring API endpoints and tests.
5. Add authoring frontend routes and test-play handoff.
6. Add `towers` models, migrations, selectors, and layout payload.
7. Add tower design API endpoints and tests.
8. Add `/my-tower` and `/tower/editor` frontend pages.
9. Add `marketplace` models, access service, and wallet debit support.
10. Add store/gallery APIs and tests.
11. Add store/gallery frontend pages and editor picker integration.
12. Run backend and frontend verification end to end.

## Files Expected To Change

Backend:

- `backend/config/settings.py`
- `backend/config/urls.py`
- `backend/adventures/models.py`
- `backend/adventures/services.py`
- `backend/adventures/views.py`
- `backend/challenges/models.py`
- `backend/challenges/services.py`
- `backend/challenges/views.py`
- `backend/curriculum/models.py`
- `backend/curriculum/selectors.py`
- `backend/progress/models.py`
- `backend/progress/chests.py`
- `backend/progress/services.py`
- `backend/progress/wallet.py`
- `backend/assets/descriptors.py`
- new `backend/authoring/*`
- new `backend/towers/*`
- new `backend/marketplace/*`

Frontend:

- `frontend/src/app/router.tsx`
- `frontend/src/app/layouts/HomeLayout.tsx`
- `frontend/src/shared/api/queryKeys.ts`
- `frontend/src/shared/assets/types.ts`
- `frontend/src/features/storeys/components/TowerPieces.tsx`
- new `frontend/src/features/authoring/*`
- new `frontend/src/features/towers/*`
- new `frontend/src/features/store/*`
- new `frontend/src/features/gallery/*`

## Verification Commands

Backend:

```powershell
cd backend
python manage.py makemigrations --check --dry-run
python -m pytest assets curriculum adventures challenges authoring towers marketplace progress
```

Frontend:

```powershell
cd frontend
npm test -- --run
npm run build
```

Manual browser checks:

- Create, validate, test-play, and publish an adventure definition.
- Create, validate, test-play, and publish a challenge definition.
- Create and publish a tome definition.
- Create a private tower design and bind all three content types.
- Open `/my-tower` and verify the private design renders.
- Buy a store listing and confirm wallet balance plus picker unlocks.
- Remix a public item and confirm the copy is private and editable.

## Open Decisions

- Whether to keep the hidden-storey runtime bridge long term or replace it with
  first-class content-backed run models after the MVP proves the authoring
  schema.
- Whether public SVG uploads are served as sanitized SVG or rasterized at
  upload time.
- Whether the first marketplace release allows paid user listings or starts
  with free public sharing plus remixing.
- Whether private `/my-tower` eventually replaces `/tower` as the default tower
  route after onboarding.
- Whether moderation/reporting must block public listing activation in the first
  shipped version or can be admin-review-only for an internal alpha.
