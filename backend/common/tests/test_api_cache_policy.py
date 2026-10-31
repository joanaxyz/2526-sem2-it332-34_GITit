import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from common.views import LivenessAPIView


@pytest.mark.parametrize(
    "path", ["/api/health/live/", "/api/auth/me/", "/api/missing/", "/api/auth/oauth/github/start/"]
)
def test_api_success_errors_and_redirects_are_not_http_cached(path):
    response = APIClient().get(path)
    assert response["Cache-Control"] == "private, no-store"
    assert response["CDN-Cache-Control"] == "no-store"
    assert response["Vercel-CDN-Cache-Control"] == "no-store"


@override_settings(DEBUG=False)
def test_api_500_is_not_cached():
    with patch.object(LivenessAPIView, "get", side_effect=RuntimeError("private")):
        response = APIClient(raise_request_exception=False).get("/api/health/live/")
    assert response.status_code == 500
    assert response["Cache-Control"] == "private, no-store"


def test_vercel_api_cache_and_asset_routing_contract():
    config = json.loads((Path(__file__).resolve().parents[3] / "frontend/vercel.json").read_text())
    headers = {
        entry["source"]: {item["key"]: item["value"] for item in entry["headers"]}
        for entry in config["headers"]
    }
    assert headers["/api/:path(.*)"]["x-vercel-enable-rewrite-caching"] == "0"
    assert headers["/api/:path(.*)"]["Cache-Control"] == "private, no-store"
    assert headers["/assets/:path(.*)"]["Cache-Control"].endswith("immutable")
    # Check the declared negative-lookahead regex, including missing static files.
    source = config["rewrites"][1]["source"]
    spa_pattern = source.removeprefix("/:path(")[:-1]
    for directory in ("api", "assets", "cosmetics", "audio", "mascot", "email", "cursors"):
        assert not re.fullmatch(spa_pattern, f"{directory}/missing.png")
    assert re.fullmatch(spa_pattern, "story-map/chapter/1")
