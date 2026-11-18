import re
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest
from rest_framework.test import APIClient

from adminconsole.services.evidence_xlsx import workbook
from adminconsole.services.kpi_evidence import METRICS, OBJECTIVES, build_evidence
from progress.services import MetricsService
from progress.tests.test_kpi_scope import _player, _run, utc
from progress.tests.test_kpi_scope import tier as tier

from .helpers import make_user


def test_strings_are_never_formulas():
    with ZipFile(
        BytesIO(workbook([("Evidence", [["Header"], ['=HYPERLINK("bad")'], [None], [0]])]))
    ) as archive:
        for name in archive.namelist():
            ET.fromstring(archive.read(name))
        sheet = archive.read("xl/worksheets/sheet1.xml").decode()
        assert "<f>" not in sheet
        assert "=HYPERLINK" in sheet


def test_objective_mapping_matches_ui():
    source = (
        Path(__file__).resolve().parents[3]
        / "frontend/src/features/performance/utils/learningObjectives.ts"
    ).read_text(encoding="utf-8")
    matches = re.findall(
        r"id: '(SO \d+\.\d+)',\s+title: '([^']+)',\s+metrics: \[([^\]]+)\]", source
    )
    assert len(matches) == len(OBJECTIVES) == 29
    for (code, title, metrics), objective in zip(matches, OBJECTIVES, strict=True):
        assert (code, title) == (objective["id"], objective["title"])
        assert [
            (k, int(t or 70), k != "arc")
            for k, t in re.findall(r"(car|hlcr|arc|rta)\((\d*)\)", metrics)
        ] == [(c["key"], c["target"], c["up"]) for c in objective["metrics"]]


@pytest.mark.django_db
def test_export_matches_live_metrics_and_filter(django_user_model, tier):  # noqa: F811 -- imported pytest fixture
    user, player = _player(django_user_model, "included")
    _, staff = _player(django_user_model, "staff", staff=True)
    _run(player, tier, "a", "failed", started_at=utc(2026, 1, 1))
    _run(staff, tier, "b", "failed", started_at=utc(2026, 1, 1))
    expected = MetricsService().admin_player_performance_summary(player=player)["kpis"]
    content, _ = build_evidence("included")
    with ZipFile(BytesIO(content)) as archive:
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = root.findall(".//{*}row")
        assert len(rows) == 2
        cells = list(rows[1])
        for i, (key, _, _) in enumerate(METRICS):
            value = cells[1 + i * 3].find("{*}v")
            assert (float(value.text) if value is not None else None) == expected[key]["value"]
        module_root = ET.fromstring(archive.read("xl/worksheets/sheet2.xml"))
        assert len(module_root.findall(".//{*}row")) == 2


@pytest.mark.django_db
def test_permissions_and_private_empty_evidence(django_user_model):
    client = APIClient()
    url = "/api/admin/users/kpi-evidence/"
    assert client.get(url).status_code in (401, 403)
    learner = make_user(django_user_model, "private-learner")
    client.force_authenticate(learner)
    assert client.get(url).status_code == 403
    staff = make_user(django_user_model, "private-staff", is_staff=True)
    client.force_authenticate(staff)
    response = client.get(url)
    assert response.status_code == 200
    assert "no-store" in response["Cache-Control"]
    with ZipFile(BytesIO(response.content)) as archive:
        xml = "".join(archive.read(name).decode() for name in archive.namelist())
        assert "private-learner" not in xml and "private-staff" not in xml
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        assert len(sheet.findall(".//{*}row")) == 2
    empty, _ = build_evidence("no-matching-account")
    with ZipFile(BytesIO(empty)) as archive:
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        assert len(sheet.findall(".//{*}row")) == 1
