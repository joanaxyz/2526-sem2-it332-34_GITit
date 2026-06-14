"""Conservative SVG sanitization for user uploads.

User-uploaded SVG is an XSS vector: inline <script>, event handlers, external
references, and XML entities (XXE/billion-laughs) can all execute or exfiltrate.
This module strips the dangerous surface and rejects anything it cannot make
safe. It is intentionally strict for the first upload release — better to reject
an exotic-but-benign file than to serve a malicious one.
"""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

# Elements that can execute script or pull in external/active content.
_FORBIDDEN_ELEMENTS = ("script", "foreignobject", "iframe", "object", "embed", "audio", "video")
# on* event handler attributes (onload, onclick, onmouseover, ...).
_EVENT_ATTR_RE = re.compile(r"\son[a-z]+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.IGNORECASE)
# javascript:/vbscript: URIs anywhere in an attribute value.
_SCRIPT_URI_RE = re.compile(r"(javascript|vbscript)\s*:", re.IGNORECASE)
# External http(s) references via href / xlink:href (data:image is allowed below).
_EXTERNAL_HREF_RE = re.compile(
    r"\s(?:xlink:)?href\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.IGNORECASE
)

MAX_SVG_BYTES = 512 * 1024


def sanitize_svg(raw: bytes) -> bytes:
    """Return sanitized SVG bytes, or raise ValidationError if it is unsafe."""
    if len(raw) > MAX_SVG_BYTES:
        raise ValidationError({"file": "SVG is too large."})
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError({"file": "SVG must be UTF-8 text."}) from exc

    lowered = text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered or "<?php" in lowered:
        # DOCTYPE/ENTITY enable XXE / entity-expansion attacks; refuse outright.
        raise ValidationError({"file": "SVG document type declarations are not allowed."})
    if "<svg" not in lowered:
        raise ValidationError({"file": "File is not an SVG."})

    for element in _FORBIDDEN_ELEMENTS:
        # Drop both paired (<script>...</script>) and self-closing/empty forms.
        text = re.sub(rf"<{element}\b[^>]*>.*?</{element}>", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(rf"<{element}\b[^>]*/?>", "", text, flags=re.IGNORECASE)

    text = _EVENT_ATTR_RE.sub("", text)

    if _SCRIPT_URI_RE.search(text):
        raise ValidationError({"file": "SVG contains a script URI."})

    def _strip_external_href(match: re.Match[str]) -> str:
        value = match.group(1).strip("\"'")
        lowered_value = value.lower()
        if lowered_value.startswith("#") or lowered_value.startswith("data:image/"):
            return match.group(0)  # internal anchor or inline image is fine
        if lowered_value.startswith("http://") or lowered_value.startswith("https://") or "//" in lowered_value:
            return ""  # drop external references
        return match.group(0)

    text = _EXTERNAL_HREF_RE.sub(_strip_external_href, text)
    return text.encode("utf-8")
