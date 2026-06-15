import json

from django.core.files.base import ContentFile
from django.utils.text import slugify
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from assets.descriptors import asset_descriptor, descriptor_map, owned_descriptor_map
from assets.models import (
    ASSET_KINDS,
    KIND_MONSTER,
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    MONSTER_TIERS,
    Asset,
    AssetSprite,
    TowerPieceAsset,
    TowerPieceType,
)
from assets.sanitize import sanitize_svg
from assets.sprite_actions import (
    LOOPING_ACTIONS,
    MONSTER_ACTIONS,
    REQUIRED_MONSTER_ACTIONS,
)
from assets.tags import normalize_tags
from common.performance import timing

# Default per-tier display scale for uploaded monsters (mirrors seed conventions).
_MONSTER_TIER_SCALE = {"mob": 1.0, "elite": 1.1, "boss": 1.6}
_MONSTER_RASTER_EXTENSIONS = (".png", ".webp", ".gif", ".jpg", ".jpeg")


class AssetDescriptorAPIView(APIView):
    def get(self, request):
        kind = request.query_params.get("kind") or ""
        valid_kinds = {value for value, _label in ASSET_KINDS}
        if kind not in valid_kinds:
            return Response(
                {"detail": "Unknown asset kind.", "valid_kinds": sorted(valid_kinds)},
                status=400,
            )
        # `?mine=1` merges the requester's own (private) assets onto the official
        # map so the editor can show uploads without leaking them to other users.
        include_owned = request.query_params.get("mine") in {"1", "true", "yes"}
        with timing("assets.descriptors", kind=kind):
            results = (
                owned_descriptor_map(request.user, kind) if include_owned else descriptor_map(kind)
            )
            return Response({"kind": kind, "results": results})


class AssetUploadAPIView(APIView):
    """Upload an owned tower piece or artifact (SVG sanitized, raster validated)."""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Sign in to upload assets.")

        kind = request.data.get("kind")
        if kind not in {KIND_TOWER_PIECE, KIND_TOWER_ARTIFACT}:
            raise ValidationError({"kind": "Only tower_piece and tower_artifact uploads are supported."})

        label = (request.data.get("label") or "").strip()
        if not label:
            raise ValidationError({"label": "A label is required."})

        tags = _parse_tags(request.data.get("tags"))

        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "A file is required."})

        upload, sanitized = _prepare_tower_upload(upload, field="file")

        piece_type = None
        if kind == KIND_TOWER_PIECE:
            piece_type = request.data.get("piece_type")
            valid_types = {value for value, _label in TowerPieceType.choices}
            if piece_type not in valid_types:
                raise ValidationError({"piece_type": "A valid tower piece type is required."})

        asset = Asset.objects.create(
            kind=kind,
            owner=user,
            visibility="private",
            price=0,
            slug=_unique_slug(user=user, label=label),
            label=label,
            tags=tags,
            is_published=False,
        )
        AssetSprite.objects.create(
            asset=asset,
            action="default",
            image=upload,
            fps=_safe_int(request.data.get("fps_default"), default=12),
            loops=True,
        )
        for action in ("hover", "click"):
            action_upload = request.FILES.get(f"file_{action}") or request.FILES.get(f"sprite_{action}")
            if action_upload is None:
                continue
            prepared, _action_sanitized = _prepare_tower_upload(
                action_upload, field=f"file_{action}"
            )
            AssetSprite.objects.create(
                asset=asset,
                action=action,
                image=prepared,
                fps=_safe_int(request.data.get(f"fps_{action}"), default=12),
                loops=action != "click",
            )

        view_box = (request.data.get("view_box") or "").strip()
        parsed_view_box = _parse_view_box(view_box) if view_box else None

        if kind == KIND_TOWER_PIECE:
            normalized_view_box = _format_view_box(parsed_view_box) if parsed_view_box else ""
            anchors = _parse_json(request.data.get("anchors")) or {}
            TowerPieceAsset.objects.create(
                asset=asset,
                piece_type=piece_type,
                view_box=normalized_view_box,
                anchors=anchors,
                svg_sanitized=sanitized,
            )
        elif parsed_view_box:
            x, y, width, height = parsed_view_box
            asset.config = {
                **asset.config,
                "view_box": _format_view_box(parsed_view_box),
                "bounds": {"x": x, "y": y, "width": width, "height": height},
            }
            asset.save(update_fields=["config", "updated_at"])

        return Response(asset_descriptor(asset), status=201)


class MonsterUploadAPIView(APIView):
    """Create an owned monster asset from per-action sprite sheets + config.

    Multipart fields:
      - ``label`` (required), ``tier`` (mob|elite|boss), ``tags`` (JSON/CSV)
      - ``attack`` / ``metrics`` (JSON objects), optional ``scale``
      - per-action files keyed ``sprite_<action>`` with matching ``fps_<action>``
        and optional ``frame_width_<action>`` / ``frame_height_<action>``.

    Frames are counted by ``AssetSprite.save``; the uploader only supplies the
    sheet + fps. Created private + unpublished; goes public when shared/sold.
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Sign in to upload monsters.")

        label = (request.data.get("label") or "").strip()
        if not label:
            raise ValidationError({"label": "A label is required."})

        tier = (request.data.get("tier") or "mob").strip()
        valid_tiers = {value for value, _label in MONSTER_TIERS}
        if tier not in valid_tiers:
            raise ValidationError({"tier": f"Tier must be one of {sorted(valid_tiers)}."})

        attack = _parse_json(request.data.get("attack")) or {}
        metrics = _parse_json(request.data.get("metrics")) or {}
        if not isinstance(attack, dict) or not isinstance(metrics, dict):
            raise ValidationError({"attack": "attack and metrics must be JSON objects."})
        tags = _parse_tags(request.data.get("tags"))

        # Collect provided sprite files keyed by action.
        provided = {
            action: request.FILES.get(f"sprite_{action}")
            for action in MONSTER_ACTIONS
            if request.FILES.get(f"sprite_{action}") is not None
        }
        missing = REQUIRED_MONSTER_ACTIONS - provided.keys()
        if missing:
            raise ValidationError(
                {"sprites": f"Missing required sprite(s): {', '.join(sorted(missing))}."}
            )
        for action, upload in provided.items():
            name = (upload.name or "").lower()
            if not name.endswith(_MONSTER_RASTER_EXTENSIONS):
                raise ValidationError({f"sprite_{action}": "Monster sprites must be raster images (PNG/WebP/...)."})

        try:
            scale = float(request.data.get("scale") or _MONSTER_TIER_SCALE.get(tier, 1.0))
        except (TypeError, ValueError):
            scale = _MONSTER_TIER_SCALE.get(tier, 1.0)

        asset = Asset.objects.create(
            kind=KIND_MONSTER,
            owner=user,
            visibility="private",
            price=0,
            slug=_unique_slug(user=user, label=label),
            label=label,
            tags=tags,
            default_scale=scale,
            config={"tier": tier, "attack": attack, "metrics": metrics},
            is_published=False,
        )

        for action, upload in provided.items():
            sprite = AssetSprite(
                asset=asset,
                action=action,
                fps=_safe_int(request.data.get(f"fps_{action}"), default=10),
                frame_width=_safe_int(request.data.get(f"frame_width_{action}"), default=0),
                frame_height=_safe_int(request.data.get(f"frame_height_{action}"), default=0),
                loops=action in LOOPING_ACTIONS,
            )
            sprite.image.save(f"{asset.slug}__{action}.png", upload, save=False)
            sprite.save()  # recompute_frames counts cells from the stored image

        return Response(asset_descriptor(asset), status=201)


def _parse_tags(raw) -> list[str]:
    """Tolerant: accept a JSON array, a CSV string, or an already-parsed list."""
    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped.startswith("["):
            try:
                raw = json.loads(stripped)
            except (TypeError, ValueError):
                raw = stripped
    return normalize_tags(raw)


def _safe_int(value, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _prepare_tower_upload(upload, *, field: str):
    name = (upload.name or "").lower()
    if name.endswith(".svg"):
        return ContentFile(sanitize_svg(upload.read()), name=upload.name), True
    if not name.endswith((".png", ".webp", ".gif", ".jpg", ".jpeg")):
        raise ValidationError({field: "Upload an SVG or raster sprite image."})
    return upload, False


def _unique_slug(*, user, label: str) -> str:
    base = slugify(label) or "asset"
    base = f"{base}-{user.id}"
    slug = base
    index = 2
    while Asset.objects.filter(slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug


def _parse_json(value):
    if not value:
        return None
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        raise ValidationError({"anchors": "anchors must be valid JSON."})


def _parse_view_box(value: str) -> tuple[float, float, float, float]:
    parts = value.replace(",", " ").split()
    if len(parts) != 4:
        raise ValidationError({"view_box": "View box must contain x, y, width, and height."})
    try:
        x, y, width, height = (float(part) for part in parts)
    except ValueError as exc:
        raise ValidationError({"view_box": "View box values must be numbers."}) from exc
    if width <= 0 or height <= 0:
        raise ValidationError({"view_box": "View box width and height must be positive."})
    return x, y, width, height


def _format_view_box(view_box: tuple[float, float, float, float]) -> str:
    return " ".join(f"{value:g}" for value in view_box)
