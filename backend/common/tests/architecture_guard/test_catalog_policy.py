"""Catalog architecture contract-policy tests."""

import json
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.catalog import (  # noqa: E402
    CATALOG_BACKEND_SERIALIZERS,
    CATALOG_FRONTEND_API,
    CATALOG_FRONTEND_TYPES,
    CATALOG_GENERATED_OPENAPI,
    catalog_contract_source_violations,
    catalog_openapi_contract_violations,
    catalog_secondary_backend_contract_violations,
    catalog_secondary_frontend_contract_violations,
    check_catalog_contract_ownership,
)
from scripts.checks.architecture_guard.repository import (  # noqa: E402
    ROOT,
)

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_catalog_contract_guard_rejects_loose_backend_and_frontend_overrides():
    root = ROOT
    serializers_source = (root / CATALOG_BACKEND_SERIALIZERS).read_text(encoding="utf-8")
    types_source = (root / CATALOG_FRONTEND_TYPES).read_text(encoding="utf-8")
    api_source = (root / CATALOG_FRONTEND_API).read_text(encoding="utf-8")
    violations = catalog_contract_source_violations(
        serializers_source=serializers_source.replace(
            "coins = serializers.IntegerField()", "coins = serializers.CharField()"
        ).replace("    @extend_schema_field(StoryPrerequisiteSerializer(allow_null=True))\n", ""),
        story_types_source=types_source.replace(
            "export type Story = ApiSchemas['Story']",
            "export type Story = { id: number; slug: string }",
        )
        + "\ntype ChestReward = { threshold: number; coins: number }\n"
        + "export type CatalogStoryResult = ApiSchemas['Story'] & { legacy: true }\n",
        story_api_source=api_source.replace(
            "apiOperationRequest('stories_list', '/stories/')",
            "apiOperationRequest<'stories_list', Story[]>('stories_list', '/stories/')",
        ),
    )
    assert any(
        "ChapterChestRewardSerializer field signatures must be exact" in row for row in violations
    )
    assert any(
        "StorySerializer.get_prerequisite_story must use exactly" in row for row in violations
    )
    assert any("Story must derive exactly" in row for row in violations)
    assert any("displaced catalog DTO ChestReward" in row for row in violations)
    assert any("secondary catalog DTOs are not allowed" in row for row in violations)
    assert any("listStories must return" in row for row in violations)
    assert any("stories_list must not pass a custom response generic" in row for row in violations)


def test_catalog_contract_guard_rejects_secondary_contract_owners():
    backend = catalog_secondary_backend_contract_violations(
        {
            "backend/example/catalog.py": "from curriculum.serializers import StorySerializer as Base\nimport curriculum.serializers\nclass StoryPrerequisiteV2Serializer(serializers.Serializer):\n    pass\nChapterListV2Serializer = StoryPrerequisiteV2Serializer\nclass StoryResponseSerializer(serializers.Serializer):\n    pass\nCatalogChapterSerializer = StoryResponseSerializer\nclass StoryDto(serializers.Serializer):\n    pass\nStoryPayload = StorySerializer\nCatalogPayload = StorySerializer\nCatalog = Base\nclass CatalogV2(Base):\n    pass\nCatalogAttribute = curriculum.serializers.StorySerializer\n",
            "backend/curriculum/catalog_aliases.py": "from .serializers import StorySerializer as Base\nCatalogRelative = Base\nclass CatalogRelativeV2(Base):\n    pass\n",
        }
    )
    frontend = catalog_secondary_frontend_contract_violations(
        {
            f"{_FRONTEND}/src/features/example/types.ts": "export interface Story { id: number }\nexport type LearningChapter = { id: number }\nexport type StoryCatalogDto = Story & { legacy: true }\nexport interface ChapterCatalogResponse extends LearningChapter { legacy: true }\nexport type CatalogStoryResult = ApiSchemas['Story'] & { legacy: true }\nexport type CatalogItem = Story & { legacy: true }\nexport interface CatalogChapter extends LearningChapter { legacy: true }\nexport type NeutralShape = { id: number; slug: string; title: string; summary: string; price: number; sort_order: number; is_published: boolean; completed: boolean; owned: boolean; world_slug: string; difficulty: string; prerequisite_story: unknown; locked: boolean; lock_reason: string; legacy: true }\n",
            f"{_FRONTEND}/src/features/example/importedTypes.ts": "import type { Story as Tale } from '@/features/story-map/types'\nexport type ImportedCatalog = (Tale & { legacy: true })\n",
            f"{_FRONTEND}/src/features/example/relativeTypes.ts": "import type { Story as Tale } from '../story-map/types'\nexport type RelativeCatalog = Tale & { legacy: true }\n",
            f"{_FRONTEND}/src/features/example/api.ts": "export const loadStories = () => apiOperationRequest<'stories_list', Story[]>('stories_list', '/stories/')\nexport const loadChapters = () => fetch('/api/chapters/')\n",
            f"{_FRONTEND}/src/features/example/adapter.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nexport const loadCatalog = () => storyMapApi.listStories()\n",
            f"{_FRONTEND}/src/features/example/derivedAdapter.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nexport async function loadCatalog() {\n  const rows = await storyMapApi.listStories()\n  return rows\n}\n",
            f"{_FRONTEND}/src/features/example/referenceAdapter.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nexport const loadCatalog = storyMapApi.listStories\n",
            f"{_FRONTEND}/src/features/example/objectAdapter.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nexport const alternateCatalogApi = {\n  stories: storyMapApi.listStories,\n  chapters: storyMapApi.listChapters,\n}\n",
            f"{_FRONTEND}/src/features/example/boundPath.ts": "const endpoint = '/api/stories/'\nconst url = endpoint\nexport const loadCatalog = () => fetch(url)\n",
            f"{_FRONTEND}/src/features/example/objectAlias.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nconst catalog = storyMapApi\nexport const loadCatalog = catalog.listStories\n",
            f"{_FRONTEND}/src/features/example/destructuredAlias.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nconst { listStories: loadStories } = storyMapApi\nexport const loadCatalog = loadStories\n",
            f"{_FRONTEND}/src/features/example/exportList.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nconst load = storyMapApi.listStories\nexport { load }\n",
            f"{_FRONTEND}/src/features/example/reexport.ts": "export { storyMapApi as catalogApi } from '@/features/story-map/api/storyMapApi'\n",
            f"{_FRONTEND}/src/features/example/separateWrapper.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nconst load = () => storyMapApi.listStories()\nexport { load }\n",
            f"{_FRONTEND}/src/features/example/defaultAdapter.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nexport default () => storyMapApi.listStories()\n",
            f"{_FRONTEND}/src/features/example/relativeAdapter.ts": "import { storyMapApi as api } from '../story-map/api/storyMapApi'\nexport const load = () => api.listStories()\n",
        }
    )
    assert len(backend) == 12
    assert any("StoryPrerequisiteV2Serializer" in row for row in backend)
    assert any("ChapterListV2Serializer" in row for row in backend)
    assert any("StoryResponseSerializer" in row for row in backend)
    assert any("CatalogChapterSerializer" in row for row in backend)
    assert any("StoryDto" in row for row in backend)
    assert any("StoryPayload" in row for row in backend)
    assert any("CatalogPayload" in row for row in backend)
    assert any("Catalog" in row for row in backend)
    assert any("CatalogV2" in row for row in backend)
    assert any("CatalogAttribute" in row for row in backend)
    assert any("CatalogRelative" in row for row in backend)
    assert any("CatalogRelativeV2" in row for row in backend)
    assert any("frontend catalog contract Story" in row for row in frontend)
    assert any("frontend catalog contract LearningChapter" in row for row in frontend)
    assert any("StoryCatalogDto" in row for row in frontend)
    assert any("ChapterCatalogResponse" in row for row in frontend)
    assert any("CatalogStoryResult" in row for row in frontend)
    assert any("CatalogItem" in row for row in frontend)
    assert any("CatalogChapter" in row for row in frontend)
    assert any("NeutralShape" in row for row in frontend)
    assert any("ImportedCatalog" in row for row in frontend)
    assert any("RelativeCatalog" in row for row in frontend)
    assert any("catalog operation wrapper stories_list" in row for row in frontend)
    assert any("catalog endpoint request path" in row for row in frontend)
    assert any("exported catalog response adapter" in row for row in frontend)
    for path_name in (
        "adapter.ts",
        "derivedAdapter.ts",
        "referenceAdapter.ts",
        "objectAdapter.ts",
        "objectAlias.ts",
        "destructuredAlias.ts",
        "exportList.ts",
        "reexport.ts",
        "separateWrapper.ts",
        "defaultAdapter.ts",
        "relativeAdapter.ts",
    ):
        assert any(
            path_name in row and "exported catalog response adapter" in row for row in frontend
        )
    assert any("boundPath.ts" in row and "catalog endpoint request path" in row for row in frontend)


def test_catalog_contract_guard_allows_ordinary_generated_catalog_consumers():
    backend_violations = catalog_secondary_backend_contract_violations(
        {
            "backend/example/services.py": "class StoryCompletionService:\n    pass\nclass ChapterRewardPolicy:\n    pass\n"
        }
    )
    frontend_violations = catalog_secondary_frontend_contract_violations(
        {
            f"{_FRONTEND}/src/features/example/useCatalog.ts": "import { storyMapApi } from '@/features/story-map/api/storyMapApi'\nimport type { Story } from '@/features/story-map/types'\nimport type { ApiSchemas } from '@/shared/api/generated/apiTypes'\ntype StoryCardProps = { story: ApiSchemas['Story']; onSelect: () => void }\ntype ChapterRow = Pick<ApiSchemas['ChapterList'], 'id' | 'title'>\ntype StoryCatalogFilters = { owned?: boolean; difficulty?: string }\ninterface StoryCardState { story: ApiSchemas['Story'] }\nexport function useCatalog() {\n  return useQuery({ queryKey: ['stories'], queryFn: storyMapApi.listStories })\n}\nexport function useSuspenseCatalog() {\n  return useSuspenseQuery({ queryKey: ['stories'], queryFn: () => storyMapApi.listStories() })\n}\nexport function useNamespacedSuspenseCatalog() {\n  return rq.useSuspenseQuery({ queryKey: ['stories'], queryFn: () => storyMapApi.listStories() })\n}\nexport const catalogOptions = () => queryOptions({\n  queryKey: ['stories'], queryFn: () => storyMapApi.listStories(),\n})\nexport function renderStory(story: Story) { render(story.title) }\n"
        }
    )
    assert backend_violations == []
    assert frontend_violations == []


def test_catalog_openapi_guard_rejects_optional_open_and_wrong_operation_shapes():
    schema = json.loads((ROOT / CATALOG_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]
    schemas["Story"]["required"].remove("summary")
    schemas["Story"]["properties"]["prerequisite_story"] = {
        "type": "object",
        "additionalProperties": {},
        "nullable": True,
    }
    schemas["ChapterList"]["properties"]["level_completion"] = {
        "type": "object",
        "additionalProperties": {},
    }
    schemas["ChapterChestReward"]["properties"]["coins"] = {"type": "string"}
    schema["paths"]["/api/chapters/"]["get"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ] = {"type": "object"}
    violations = catalog_openapi_contract_violations(schema)
    assert any("Story properties/required" in row for row in violations)
    assert any("Story property schemas must be exact" in row for row in violations)
    assert any("ChapterList property schemas must be exact" in row for row in violations)
    assert any("ChapterChestReward property schemas must be exact" in row for row in violations)
    assert any("/api/chapters/ must return an array of ChapterList" in row for row in violations)


def test_catalog_contract_runtime_obeys_one_way_generated_ownership():
    assert check_catalog_contract_ownership() == []
