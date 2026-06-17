"""Diagnostic: compare the LIVE official tower layout (what /tower renders) with
each stored official_fork (what the editor renders), and dump the piece-art data
the renderer/companion depend on (window-section state_variants, landing
walk_rail anchors). Run from a FRESH process (empty cache, reads Postgres/SQLite
directly):

    cd backend && python manage.py shell -c "exec(open('scripts/diff_official_fork.py',encoding='utf-8').read())"
"""

from collections import Counter

from assets.models import KIND_TOWER_PIECE, Asset, TowerPieceAsset
from challenges.models import Challenge
from command_adventures.models import CommandAdventure
from curriculum.models import Tome
from curriculum.selectors import published_chapters, relic_layout_payload
from archive.models import ORIGIN_OFFICIAL_FORK, ArchiveDesign


def live_layout():
    pieces, arts = [], []
    crown_seen = False
    for chapter in published_chapters():
        adventures = list(CommandAdventure.objects.filter(chapter=chapter, is_published=True).order_by("sort_order", "id"))
        tomes = list(Tome.objects.filter(chapter=chapter, is_published=True).order_by("sort_order", "id"))
        challenges = list(Challenge.objects.filter(chapter=chapter, is_published=True).order_by("sort_order", "id"))
        layout = relic_layout_payload(chapter=chapter, chapter_id=chapter.id,
                                      adventures=adventures, tomes=tomes, challenges=challenges)
        for p in layout["pieces"]:
            if p["pieceType"] == "crown":
                if crown_seen:
                    continue
                crown_seen = True
            pieces.append((chapter.id, p["pieceType"], p["assetSlug"]))
        for a in layout["artifacts"]:
            arts.append((chapter.id, a["role"], a["assetSlug"]))
    return pieces, arts


print("=" * 72)
print("DB engine:", ArchiveDesign.objects.db, "| using settings DATABASES['default']")
from django.db import connection
print("DB name:", connection.settings_dict.get("NAME"))

print("\n" + "=" * 72)
print("PUBLISHED CHAPTERS (live curriculum)")
print("=" * 72)
chapters = list(published_chapters())
for s in chapters:
    print(f"  chapter id={s.id:<5} slug={s.slug!r} title={s.title!r}")

live_pieces, live_arts = live_layout()
print(f"\nLIVE official layout (what /tower draws): {len(live_pieces)} pieces, {len(live_arts)} artifacts")
for row in live_pieces:
    print(f"    PIECE chapter={row[0]:<5} {row[1]:<8} {row[2]}")
for row in live_arts:
    print(f"    ART   chapter={row[0]:<5} {row[1]:<10} {row[2]}")

print("\n" + "=" * 72)
print("STORED OFFICIAL FORKS (what the editor draws)")
print("=" * 72)
forks = ArchiveDesign.objects.filter(origin=ORIGIN_OFFICIAL_FORK).select_related("owner").order_by("id")
if not forks:
    print("  (no official_fork designs exist yet)")
live_pc = Counter((t, slug) for _sid, t, slug in live_pieces)
live_ac = Counter((role, slug) for _sid, role, slug in live_arts)
live_chapters = sorted(s.id for s in chapters)
for design in forks:
    print("-" * 72)
    owner = getattr(design.owner, "username", design.owner_id)
    print(f"  fork id={design.id} owner={owner!r} status={design.status} "
          f"created={design.created_at:%Y-%m-%d %H:%M} updated={design.updated_at:%Y-%m-%d %H:%M}")
    fpieces = list(design.pieces.select_related("piece_asset").order_by("sort_order", "id"))
    fparts = list(design.artifact_placements.select_related("artifact_asset").order_by("z_index", "id"))
    print(f"  {len(fpieces)} pieces, {len(fparts)} artifacts")
    for p in fpieces:
        print(f"    PIECE chapter_index={p.chapter_index:<5} {p.piece_type:<8} {p.piece_asset.slug}")
    for a in fparts:
        print(f"    ART   target_piece={a.target_piece_instance_id:<6} {a.role:<10} {a.artifact_asset.slug}")
    fork_pc = Counter((p.piece_type, p.piece_asset.slug) for p in fpieces)
    fork_ac = Counter((a.role, a.artifact_asset.slug) for a in fparts)
    print("  DIFF vs live (multiset, chapter id ignored):")
    print(f"    pieces  live-not-fork: {dict(live_pc - fork_pc) or 'NONE'}")
    print(f"    pieces  fork-not-live: {dict(fork_pc - live_pc) or 'NONE'}")
    print(f"    arts    live-not-fork: {dict(live_ac - fork_ac) or 'NONE'}")
    print(f"    arts    fork-not-live: {dict(fork_ac - live_ac) or 'NONE'}")
    fork_chapters = sorted({p.chapter_index for p in fpieces})
    dead = [sx for sx in fork_chapters if sx not in live_chapters]
    print(f"    fork chapter_index: {fork_chapters} | live chapter ids: {live_chapters}")
    print(f"    STALE chapter_index (no matching live chapter): {dead or 'NONE'}")

print("\n" + "=" * 72)
print("PIECE-ART DATA (from TowerPieceAsset rows - drives windows + Blue's footing)")
print("=" * 72)
for slug in ["official-window-section", "official-landing", "official-challenge-landing", "official-tome-landing"]:
    asset = Asset.objects.filter(slug=slug, kind=KIND_TOWER_PIECE).first()
    if not asset:
        print(f"  {slug}: ASSET MISSING")
        continue
    tp = getattr(asset, "tower_piece", None)
    if not tp:
        print(f"  {slug}: no TowerPieceAsset row")
        continue
    anchors = tp.anchors or {}
    print(f"  {slug}: view_box={tp.view_box!r}")
    print(f"      anchors={anchors}")
    print(f"      state_variants keys={list((tp.state_variants or {}).keys()) or 'NONE'}")
    sprite = next((s for s in asset.sprites.all() if s.action == "default"), None)
    svg_name = getattr(getattr(sprite, "image", None), "name", None)
    print(f"      default sprite={svg_name!r}")
