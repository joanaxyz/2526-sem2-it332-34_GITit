"""Core and workflow architecture-guard tests."""

import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[3]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.typescript_analysis import (  # noqa: E402
    canonical_ts_module_reference,
    ts_module_specifiers,
)
from scripts.checks.check_architecture_boundaries import (  # noqa: E402
    admin_authoring_import_violations,
    adminconsole_selector_source_violations,
    adminconsole_view_init_source_violations,
    adminconsole_view_source_violations,
    check_adminconsole_http_read_ownership,
    check_adminconsole_selectors_are_http_free,
    check_content_editor_workflow_ownership,
    check_home_hub_profile_ownership,
    check_home_overview_ownership,
    content_editor_css_violations,
    content_editor_source_violations,
    css_selector_list,
    css_top_level_rule_headers,
    home_hub_hook_owner_violations,
    home_hub_source_violations,
    home_overview_achievement_import_violations,
    home_overview_css_source_violations,
    home_overview_source_violations,
    strongly_connected_components,
)

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_architecture_guard_detects_runtime_cycles_deterministically():
    assert strongly_connected_components(
        {"app.a": {"app.b"}, "app.b": {"app.c"}, "app.c": {"app.a"}, "app.leaf": set()}
    ) == [("app.a", "app.b", "app.c")]


def test_adminconsole_layer_guard_rejects_wrong_owner_dependencies():
    view_violations = adminconsole_view_source_violations(
        source="from example.models import Item\nitems = Item.objects.all()\n",
        path_label="backend/adminconsole/views/example.py",
    )
    selector_violations = adminconsole_selector_source_violations(
        source="from rest_framework.response import Response\n",
        path_label="backend/adminconsole/selectors/example.py",
    )
    assert len(view_violations) == 2
    assert "must delegate persistence reads" in view_violations[0]
    assert "must not access ORM managers" in view_violations[1]
    assert len(selector_violations) == 1
    assert "must not import HTTP layer" in selector_violations[0]
    relative_view_violations = adminconsole_view_source_violations(
        source="from ..models import Item\nfrom .. import models\n",
        path_label="backend/adminconsole/views/relative.py",
    )
    relative_selector_violations = adminconsole_selector_source_violations(
        source="from ..views import AdminOverviewAPIView\nfrom .. import views\n",
        path_label="backend/adminconsole/selectors/relative.py",
    )
    assert len(relative_view_violations) == 2
    assert len(relative_selector_violations) == 2
    django_alias_violations = adminconsole_view_source_violations(
        source="from django import db\nfrom django.contrib import auth\n",
        path_label="backend/adminconsole/views/django_aliases.py",
    )
    assert len(django_alias_violations) == 2
    initializer_violations = adminconsole_view_init_source_violations(
        source='"""Exports."""\nfrom .dashboard import AdminOverviewAPIView\n__all__ = ["AdminOverviewAPIView"]\ndef hidden_query():\n    return None\n',
        path_label="backend/adminconsole/views/__init__.py",
    )
    assert len(initializer_violations) == 1
    assert "initializer may contain exports only" in initializer_violations[0]
    for manager_name in ("objects", "_default_manager", "_base_manager"):
        manager_violations = adminconsole_view_source_violations(
            source=f"rows = model_type.{manager_name}.all()\n",
            path_label="backend/adminconsole/views/manager_alias.py",
        )
        assert len(manager_violations) == 1
        assert "must not access ORM managers" in manager_violations[0]


def test_adminconsole_runtime_layers_obey_http_read_ownership():
    assert check_adminconsole_http_read_ownership() == []
    assert check_adminconsole_selectors_are_http_free() == []


def test_content_editor_guard_detects_import_forms_and_controller_forwarding():
    source = "\nimport { useQuery as readQuery } from '@tanstack/react-query'\nconst api = import('@/features/authoring/api/authoringApi')\nconst auth = require('@/shared/auth/useAuth')\nconst controller = useContentEditorController()\nexport const Page = () => (\n  <ContentMetadataSection {...controller} controller={controller} form={form} />\n)\n"
    assert ts_module_specifiers(source) == [
        "@tanstack/react-query",
        "@/features/authoring/api/authoringApi",
        "@/shared/auth/useAuth",
    ]
    violations = content_editor_source_violations(
        source=source,
        path_label=f"{_FRONTEND}/src/features/authoring/pages/ContentEditorPage.tsx",
        role="page",
    )
    assert any("must not import @tanstack/react-query" in row for row in violations)
    assert any("must not import @/features/authoring/api/authoringApi" in row for row in violations)
    assert any("destructure useContentEditorController" in row for row in violations)
    assert any("must not be forwarded" in row for row in violations)
    assert any("must not receive form or setForm" in row for row in violations)


def test_content_editor_guard_rejects_component_and_reverse_feature_edges():
    component_violations = content_editor_source_violations(
        source="import { useContentEditorController as useWorkflow } from '@/features/authoring/hooks/useContentEditorController'\nconst Page = import('@/features/authoring/pages/ContentEditorPage')\ntype Props = { form: unknown }\n",
        path_label=f"{_FRONTEND}/src/features/authoring/components/content-editor/ContentMetadataSection.tsx",
        role="component",
    )
    reverse_violations = admin_authoring_import_violations(
        source="import { authoringApi as contentApi } from '@/features/authoring/api/authoringApi'\nconst editor = import('@/features/authoring/pages/ContentEditorPage')\n",
        path_label=f"{_FRONTEND}/src/features/admin/api/example.ts",
    )
    assert len(component_violations) == 3
    assert any("must not import" in row for row in component_violations)
    assert any("only ContentEditorDiagnostics" in row for row in component_violations)
    assert len(reverse_violations) == 2


def test_content_editor_guard_rejects_relative_and_barrel_import_bypasses():
    page_path = f"{_FRONTEND}/src/features/authoring/pages/ContentEditorPage.tsx"
    component_path = f"{_FRONTEND}/src/features/authoring/components/content-editor/Escape.tsx"
    hook_path = f"{_FRONTEND}/src/features/authoring/hooks/useContentEditorController.ts"
    support_path = f"{_FRONTEND}/src/features/authoring/hooks/contentEditorDraftState.ts"
    assert (
        canonical_ts_module_reference(module="../../api", path_label=component_path)
        == f"{_FRONTEND}/src/features/authoring/api"
    )
    assert (
        canonical_ts_module_reference(
            module="@/features/authoring/api/authoringApi.ts", path_label=page_path
        )
        == f"{_FRONTEND}/src/features/authoring/api/authoringApi"
    )
    page_violations = content_editor_source_violations(
        source="import '../api'\nconst api = import(`../api/authoringApi`)\n",
        path_label=page_path,
        role="page",
    )
    component_violations = content_editor_source_violations(
        source="import '../../api'\nconst workflow = import('../../hooks/useContentEditorController')\nconst Page = require(`../../pages/ContentEditorPage`)\n",
        path_label=component_path,
        role="component",
    )
    hook_violations = content_editor_source_violations(
        source="import '../components'\nconst Page = import('../pages/ContentEditorPage')\n",
        path_label=hook_path,
        role="hook",
    )
    support_violations = content_editor_source_violations(
        source="import '../api'\nimport controller from './useContentEditorController'\nconst guard = import(`./useUnsavedChangesGuard`)\nconst Page = import(`../pages/ContentEditorPage`)\n",
        path_label=support_path,
        role="support",
    )
    reverse_violations = admin_authoring_import_violations(
        source="import '../../authoring'\nconst editor = import(`../../authoring/pages/ContentEditorPage`)\n",
        path_label=f"{_FRONTEND}/src/features/admin/api/example.ts",
    )
    assert len(page_violations) == 3
    assert len(component_violations) == 3
    assert len(hook_violations) == 2
    assert len(support_violations) == 4
    assert len(reverse_violations) == 2


def test_content_editor_runtime_obeys_workflow_ownership_and_css_boundary():
    assert check_content_editor_workflow_ownership() == []
    css_violations = content_editor_css_violations(
        source=".author-destination-row { display: flex; }",
        path_label=f"{_FRONTEND}/src/styles/features/authoring/editor-shell.css",
    )
    assert len(css_violations) == 4
    assert any("must own align-items" in row for row in css_violations)
    assert any("input must own flexible sizing" in row for row in css_violations)


def test_home_hub_guard_rejects_role_bypasses_and_integration_forwarding():
    hub_path = f"{_FRONTEND}/src/features/home/components/HomeHubView.tsx"
    workspace_path = f"{_FRONTEND}/src/features/home/components/home-hub/HomeProfileWorkspace.tsx"
    profile_path = f"{_FRONTEND}/src/features/home/components/home-hub/HomeProfilePanel.tsx"
    combat_path = f"{_FRONTEND}/src/features/home/components/home-hub/HomeCombatShowcase.tsx"
    status_path = f"{_FRONTEND}/src/features/home/components/home-hub/HomeCompanionStatus.tsx"
    contract_path = f"{_FRONTEND}/src/features/home/components/home-hub/companionPresentation.ts"
    assert (
        canonical_ts_module_reference(
            module="../../../skills/hooks/useLearnedSkills", path_label=workspace_path
        )
        == f"{_FRONTEND}/src/features/skills/hooks/useLearnedSkills"
    )
    hub_violations = home_hub_source_violations(
        source="import { useLearnedSkills } from '../../skills/hooks/useLearnedSkills'\nimport { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'\nconst effects = import('@/shared/battle/effects/effectRegistry')\ntype Props = { skills: unknown }\nconst state = useState(null)\nconst playerLoadout = usePlayerLoadout()\nexport const View = () => <HomeProfileWorkspace playerLoadout={playerLoadout} />\n",
        path_label=hub_path,
        role="hub",
    )
    workspace_violations = home_hub_source_violations(
        source="import { useLearnedSkills } from '../../../skills/hooks/useLearnedSkills'\nimport { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'\nconst rank = require('@/shared/progress/rank')\nconst effects = import(`@/shared/battle/effects/effectRegistry`)\nconst learnedQuery = useLearnedSkills()\nconst { companion } = usePlayerLoadout()\nconst local = useRef(null)\nexport const View = () => (\n  <section className=\"home-ref-grid\">\n    <HomeProfilePanel query={learnedQuery} />\n    <HomeCombatShowcase {...learnedQuery} />\n  </section>\n)\n",
        path_label=workspace_path,
        role="workspace",
    )
    profile_violations = home_hub_source_violations(
        source='const sprites = import(\'../../../../shared/sprites/SpriteAnimator\')\nsetTimeout(() => null, 1)\nexport const View = () => (\n  <aside className="home-profile-panel">\n    <div className="home-profile-view" />\n    <div className="home-rank-view" />\n  </aside>\n)\n',
        path_label=profile_path,
        role="profile",
    )
    combat_violations = home_hub_source_violations(
        source='const learned = import(`../../../skills/hooks/useLearnedSkills`)\nconst rank = require(\'@/shared/progress/rank\')\neffectForSkill(); effectPlacementForSkill(); homeGroundPoint();\nsetTimeout(() => null, 1); clearTimeout(1);\nconst SpriteAnimator = null\nexport const View = () => (\n  <><section className="home-sprite-panel" />\n  <section className="home-spellbook-panel" /></>\n)\n',
        path_label=combat_path,
        role="combat",
    )
    oversized_hub = home_hub_source_violations(
        source="\n".join(["// line"] * 141), path_label=hub_path, role="hub"
    )
    link_only_profile = home_hub_source_violations(
        source='import { Link } from \'react-router-dom\'\nexport const View = () => <aside className="home-profile-panel"><div className="home-profile-view" /><div className="home-rank-view"><Link to="/shop">Shop</Link></div></aside>\n',
        path_label=profile_path,
        role="profile",
    )
    router_hook_profile = home_hub_source_violations(
        source='import { Link, useNavigate } from \'react-router-dom\'\nexport const View = () => <aside className="home-profile-panel"><div className="home-profile-view" /><div className="home-rank-view"><Link to="/shop">Shop</Link></div></aside>\n',
        path_label=profile_path,
        role="profile",
    )
    oversized_combat = home_hub_source_violations(
        source="\n".join(["// line"] * 251), path_label=combat_path, role="combat"
    )
    link_only_status = home_hub_source_violations(
        source='import { Link } from \'react-router-dom\'\nexport function HomeProfileCompanionStatus() { return <div className="home-profile-companion-empty"><Link to="/shop">Shop</Link></div> }\nexport function HomeCombatCompanionStatus() { return <div className="home-sprite-stage--empty" /> }\n',
        path_label=status_path,
        role="status",
    )
    oversized_status = home_hub_source_violations(
        source="\n".join(["// line"] * 121), path_label=status_path, role="status"
    )
    type_only_contract = home_hub_source_violations(
        source="import type { CompanionDef } from '@/shared/cosmetics/types'\n\nexport type CompanionPresentation =\n  | { status: 'loading' | 'error' | 'empty' }\n  | { status: 'ready'; definition: CompanionDef; slug: string }\n\nexport type UnresolvedCompanionPresentation = Exclude<\n  CompanionPresentation,\n  { status: 'ready' }\n>\n",
        path_label=contract_path,
        role="contract",
    )
    runtime_contract = home_hub_source_violations(
        source="import { getCompanion } from '@/shared/cosmetics/companions/registry'\nexport type CompanionPresentation = { status: 'ready' }\nexport type UnresolvedCompanionPresentation = CompanionPresentation\nexport const deriveCompanion = () => getCompanion('blue')\n",
        path_label=contract_path,
        role="contract",
    )
    default_export_contract = home_hub_source_violations(
        source="import type { CompanionDef } from '@/shared/cosmetics/types'\n\nexport type CompanionPresentation =\n  | { status: 'loading' | 'error' | 'empty' }\n  | { status: 'ready'; definition: CompanionDef; slug: string }\n\nexport type UnresolvedCompanionPresentation = Exclude<\n  CompanionPresentation,\n  { status: 'ready' }\n>\nexport default () => ({ status: 'empty' })\n",
        path_label=contract_path,
        role="contract",
    )
    executable_contract = home_hub_source_violations(
        source="import type { CompanionDef } from '@/shared/cosmetics/types'\n\nexport type CompanionPresentation =\n  | { status: 'loading' | 'error' | 'empty' }\n  | { status: 'ready'; definition: CompanionDef; slug: string }\n\nexport type UnresolvedCompanionPresentation = Exclude<\n  CompanionPresentation,\n  { status: 'ready' }\n>\nderiveCompanion()\n",
        path_label=contract_path,
        role="contract",
    )
    hook_owner_violations = home_hub_hook_owner_violations(
        {
            hub_path: "const { companion } = usePlayerLoadout()",
            workspace_path: "const { data } = useLearnedSkills()",
            f"{_FRONTEND}/src/features/home/components/Rogue.tsx": (
                "const duplicate = usePlayerLoadout()"
            ),
        }
    )
    assert any(
        "must not import ../../skills/hooks/useLearnedSkills" in row for row in hub_violations
    )
    assert any("four-prop contract" in row for row in hub_violations)
    assert any("must not own useState" in row for row in hub_violations)
    assert any("must destructure usePlayerLoadout" in row for row in hub_violations)
    assert any("only narrow Profile workspace props" in row for row in hub_violations)
    assert any("must destructure useLearnedSkills" in row for row in workspace_violations)
    assert any(
        "must not import @/shared/player-loadout/usePlayerLoadout" in row
        for row in workspace_violations
    )
    assert any("must pass narrow data props" in row for row in workspace_violations)
    assert any("must not own useRef" in row for row in workspace_violations)
    assert any(
        "must not import ../../../../shared/sprites/SpriteAnimator" in row
        for row in profile_violations
    )
    assert any("must not own setTimeout" in row for row in profile_violations)
    assert any(
        "must not import ../../../skills/hooks/useLearnedSkills" in row for row in combat_violations
    )
    assert any("must not import @/shared/progress/rank" in row for row in combat_violations)
    assert any("has 141 lines; limit is 140" in row for row in oversized_hub)
    assert any("must not import react-router-dom" in row for row in link_only_profile)
    assert any("must not import react-router-dom" in row for row in router_hook_profile)
    assert any("must not own useNavigate" in row for row in router_hook_profile)
    assert any("has 251 lines; limit is 250" in row for row in oversized_combat)
    assert link_only_status == []
    assert any("has 121 lines; limit is 120" in row for row in oversized_status)
    assert type_only_contract == []
    assert any("type-only imports" in row for row in runtime_contract)
    assert any("must remain type-only" in row for row in runtime_contract)
    assert any("canonical type-only union" in row for row in default_export_contract)
    assert any("canonical type-only union" in row for row in executable_contract)
    assert any("usePlayerLoadout" in row and "ownership" in row for row in hook_owner_violations)


def test_home_hub_hook_owner_guard_rejects_aliased_direct_module_bypasses():
    hub_path = f"{_FRONTEND}/src/features/home/components/HomeHubView.tsx"
    workspace_path = f"{_FRONTEND}/src/features/home/components/home-hub/HomeProfileWorkspace.tsx"
    rogue_path = f"{_FRONTEND}/src/features/home/components/Rogue.tsx"
    valid_sources = {
        hub_path: "import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'\nconst { companion } = usePlayerLoadout()\n",
        workspace_path: "import { useLearnedSkills } from '@/features/skills/hooks/useLearnedSkills'\nconst { data } = useLearnedSkills()\n",
    }
    assert home_hub_hook_owner_violations(valid_sources) == []
    assert (
        home_hub_hook_owner_violations(
            {
                **valid_sources,
                rogue_path: "// import { usePlayerLoadout as useLoadout } from '@/shared/player-loadout/usePlayerLoadout'\n// const loadout = useLoadout()\n",
            }
        )
        == []
    )

    bypasses = (
        (
            "named alias",
            "import { usePlayerLoadout as useLoadout } from '@/shared/player-loadout/usePlayerLoadout'\nconst loadout = useLoadout()\n",
            "usePlayerLoadout import ownership",
        ),
        (
            "relative named alias",
            "import { usePlayerLoadout as useLoadout } from '../../../shared/player-loadout/usePlayerLoadout'\nconst loadout = useLoadout()\n",
            "usePlayerLoadout import ownership",
        ),
        (
            "namespace alias",
            "import * as Loadout from '@/shared/player-loadout/usePlayerLoadout'\nconst loadout = Loadout.usePlayerLoadout()\n",
            "usePlayerLoadout call ownership",
        ),
        (
            "re-export",
            "export { usePlayerLoadout as useLoadout } from '@/shared/player-loadout/usePlayerLoadout'\n",
            "usePlayerLoadout import ownership",
        ),
        (
            "dynamic import",
            "const loadout = import('@/shared/player-loadout/usePlayerLoadout')\n",
            "usePlayerLoadout import ownership",
        ),
        (
            "require",
            "const loadout = require('@/shared/player-loadout/usePlayerLoadout')\n",
            "usePlayerLoadout import ownership",
        ),
        (
            "learned-skill named alias",
            "import { useLearnedSkills as useSkills } from '@/features/skills/hooks/useLearnedSkills'\nconst skills = useSkills()\n",
            "useLearnedSkills import ownership",
        ),
    )
    for label, rogue_source, expected in bypasses:
        violations = home_hub_hook_owner_violations({**valid_sources, rogue_path: rogue_source})
        assert any(expected in row and rogue_path in row for row in violations), label
        if label == "namespace alias":
            call_row = next(row for row in violations if expected in row)
            assert f"('{rogue_path}', 1)" in call_row


def test_home_hub_runtime_obeys_profile_workspace_ownership():
    assert check_home_hub_profile_ownership() == []


def test_home_overview_guard_rejects_role_bypasses_and_wide_boundaries():
    composition_path = f"{_FRONTEND}/src/features/home/components/HomeStatsView.tsx"
    model_path = f"{_FRONTEND}/src/features/home/components/home-stats/homeStatsModel.ts"
    dashboard_path = f"{_FRONTEND}/src/features/home/components/home-stats/HomeStatsDashboard.tsx"
    gallery_path = f"{_FRONTEND}/src/features/home/components/home-stats/HomeAchievementGallery.tsx"
    composition_violations = home_overview_source_violations(
        source="import { useMemo, useState } from 'react'\nimport './home-stats/homeStatsModel'\nconst dashboard = import('./home-stats/HomeStatsDashboard')\nconst gallery = require(`./home-stats/HomeAchievementGallery`)\nconst api = import('../api/homeApi')\nconst model = useMemo(() => buildHomeStatsModel(home, stats), [home, stats])\nexport const View = () => <section className=\"home-overview-grid\">\n  <HomeStatsDashboard {...model.dashboard} />\n  <HomeAchievementGallery achievements={model.achievements} />\n</section>\n",
        path_label=composition_path,
        role="composition",
    )
    model_violations = home_overview_source_violations(
        source="import type { HomeSummary } from '../../../types'\nimport { deriveAchievements } from '../../../utils/achievements'\nimport type { StatsSummary } from '../../../../stats/types'\nconst router = import('react-router-dom')\nconst root = require('../HomeStatsView')\nuseState(); document.querySelector('.home-overview-grid')\nexport type HomeStatsModel = unknown\nexport type HomeStatsDashboardModel = unknown\n",
        path_label=model_path,
        role="model",
    )
    dashboard_violations = home_overview_source_violations(
        source="import type { HomeStatsDashboardModel } from './homeStatsModel'\nconst summaries = import('../../types')\nconst root = require(`../HomeStatsView`)\nuseState(); const marker = 'home-overview-achievement-card'\nexport function HomeStatsDashboard({ home, stats }) { return null }\n",
        path_label=dashboard_path,
        role="dashboard",
    )
    gallery_violations = home_overview_source_violations(
        source="import type { Achievement } from '../../../utils/achievements'\nconst router = import(`react-router-dom`)\nconst root = require('../HomeStatsView')\nderiveAchievements(home, stats)\nconst marker = 'home-overview-story-body'\nexport function HomeAchievementGallery({ home, stats }) { return null }\n",
        path_label=gallery_path,
        role="gallery",
    )
    oversized = home_overview_source_violations(
        source="\n".join(["// line"] * 81), path_label=composition_path, role="composition"
    )
    assert any("must not import ../api/homeApi" in row for row in composition_violations)
    assert any("must not own useState" in row for row in composition_violations)
    assert any("must not spread objects" in row for row in composition_violations)
    assert any(
        "HomeStatsDashboard must receive only dashboard" in row for row in composition_violations
    )
    assert any("must not import react-router-dom" in row for row in model_violations)
    assert any("must not import ../HomeStatsView" in row for row in model_violations)
    assert any("must not own home-overview-" in row for row in model_violations)
    assert any("must not import ../../types" in row for row in dashboard_violations)
    assert any("must not receive raw home or stats" in row for row in dashboard_violations)
    assert any("must not own home-overview-achievement-card" in row for row in dashboard_violations)
    assert any("must not import react-router-dom" in row for row in gallery_violations)
    assert any("must not own deriveAchievements" in row for row in gallery_violations)
    assert any("must not own home-overview-story" in row for row in gallery_violations)
    assert any("has 81 lines; limit is 80" in row for row in oversized)


def test_home_overview_guard_allows_equivalent_model_syntax_and_blocks_value_aliases():
    root = Path(__file__).resolve().parents[3]
    model_path = f"{_FRONTEND}/src/features/home/components/home-stats/homeStatsModel.ts"
    model_source = (root / model_path).read_text(encoding="utf-8")
    equivalent_source = model_source.replace(
        "point.commands_run + point.levels_completed * 4",
        "point.levels_completed * 4 + point.commands_run",
    ).replace(
        "stats.headline.levels_completed || home.counts.completed",
        "stats.headline.levels_completed !== 0\n          ? stats.headline.levels_completed\n          : home.counts.completed",
    )
    assert (
        home_overview_source_violations(
            source=equivalent_source, path_label=model_path, role="model"
        )
        == []
    )
    external_path = f"{_FRONTEND}/src/features/stats/utils/achievementBypass.ts"
    alias_violations = home_overview_achievement_import_violations(
        source="import { deriveAchievements as buildAchievements } from '@/features/home/utils/achievements'\nbuildAchievements(home, stats)\n",
        path_label=external_path,
    )
    reexport_violations = home_overview_achievement_import_violations(
        source="export { deriveAchievements as buildAchievements } from '@/features/home/utils/achievements'\n",
        path_label=external_path,
    )
    dynamic_violations = home_overview_achievement_import_violations(
        source="const ledger = import('@/features/home/utils/achievements')\n",
        path_label=external_path,
    )
    type_only_violations = home_overview_achievement_import_violations(
        source="import type { Achievement } from '@/features/home/utils/achievements'\nimport { type AchievementImage } from '@/features/home/utils/achievements'\n",
        path_label=external_path,
    )
    assert len(alias_violations) == 1
    assert "runtime-import the achievement ledger" in alias_violations[0]
    assert len(reexport_violations) == 1
    assert len(dynamic_violations) == 1
    assert type_only_violations == []


def test_home_overview_import_guard_handles_trivia_and_statement_boundaries():
    external_path = f"{_FRONTEND}/src/features/stats/utils/achievementBypass.ts"
    violations = home_overview_achievement_import_violations
    side_effect_then_type = violations(
        source="import '@/features/home/utils/achievements'\nimport type { Example } from '@/example/types'\n",
        path_label=external_path,
    )
    commented_from = violations(
        source="import { deriveAchievements as build } from /* ownership note */ '@/features/home/utils/achievements'\n",
        path_label=external_path,
    )
    commented_runtime_calls = violations(
        source="const lazy = import(/* ownership note */ '@/features/home/utils/achievements')\nconst legacy = require(/* ownership note */ '@/features/home/utils/achievements')\n",
        path_label=external_path,
    )
    formatted_type_only = violations(
        source="import {\n  type /* ownership note */ Achievement,\n} from /* module note */ '@/features/home/utils/achievements'\nimport{type AchievementImage}from'@/features/home/utils/achievements'\nimport { type AchievementBadge }/* before from */from '@/features/home/utils/achievements'\n",
        path_label=external_path,
    )
    assert len(side_effect_then_type) == 1
    assert len(commented_from) == 1
    assert len(commented_runtime_calls) == 2
    assert formatted_type_only == []


def test_home_overview_css_guard_rejects_legacy_and_misowned_rules():
    css_violations = home_overview_css_source_violations
    stats_entry = css_violations(
        source="@import './stats-layout.css';\n@import './stats-responsive.css';\n@import './stats-achievements.css';\n@import './stats-actions.css';\n",
        path_label=f"{_FRONTEND}/src/styles/features/home/stats.css",
        role="stats-entry",
    )
    achievements = css_violations(
        source=".home-overview-achievement-grid { display: grid; }\n",
        path_label=f"{_FRONTEND}/src/styles/features/home/stats-achievements.css",
        role="achievements",
    )
    responsive = css_violations(
        source=".home-overview-achievement-card { display: grid; }\n.home-award-card { display: block; }\n@media (max-width: 540px) { .example { display: none; } }\n",
        path_label=f"{_FRONTEND}/src/styles/features/home/stats-responsive.css",
        role="responsive",
    )
    grouped_outside_owner = css_violations(
        source=":is(.compact, .dense), .home-overview-achievement-card { display: grid; }\n",
        path_label=f"{_FRONTEND}/src/styles/features/home/stats-layout.css",
        role="scan",
    )
    assert any("imports must be exactly" in row for row in stats_entry)
    assert any("must own the base achievement-card rule" in row for row in achievements)
    assert any("breakpoint rules only" in row for row in responsive)
    assert any("legacy Home selector" in row for row in responsive)
    assert any("belongs in stats-achievements.css" in row for row in grouped_outside_owner)
    assert css_top_level_rule_headers("@media (max-width: 1px) { .nested { color: red; } }") == [
        "@media (max-width: 1px)"
    ]
    assert css_selector_list(":is(.compact, .dense), .home-overview-achievement-card") == [
        ":is(.compact, .dense)",
        ".home-overview-achievement-card",
    ]


def test_home_overview_runtime_obeys_component_and_css_ownership():
    assert check_home_overview_ownership() == []
