"""Small SVG geometry cropper for deterministic seed assets.

This intentionally avoids a runtime renderer dependency. The official tower
piece SVGs are authored from basic SVG primitives, so a conservative geometry
bounds pass is enough to normalize their root viewBox at seed time.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass


_COMMAND_OR_NUMBER = re.compile(
    r"[AaCcHhLlMmQqSsTtVvZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
)
_TRANSFORM_RE = re.compile(r"([a-zA-Z]+)\(([^)]*)\)")
_NON_RENDERING_TAGS = {"defs", "clipPath", "mask", "pattern", "linearGradient", "radialGradient", "filter"}


@dataclass
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @classmethod
    def empty(cls) -> "Bounds":
        return cls(math.inf, math.inf, -math.inf, -math.inf)

    @property
    def is_empty(self) -> bool:
        return self.min_x == math.inf

    def include_point(self, x: float, y: float) -> None:
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

    def include_bounds(self, other: "Bounds") -> None:
        if other.is_empty:
            return
        self.include_point(other.min_x, other.min_y)
        self.include_point(other.max_x, other.max_y)

    def expand(self, amount: float) -> "Bounds":
        if self.is_empty:
            return self
        return Bounds(
            self.min_x - amount,
            self.min_y - amount,
            self.max_x + amount,
            self.max_y + amount,
        )


Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1, 0, 0, 1, 0, 0)


def crop_svg_markup(raw: bytes, *, padding: float = 2.0) -> tuple[bytes, str | None]:
    """Return SVG bytes with a root viewBox cropped to visible geometry.

    The returned viewBox is in the SVG's original coordinate system. On parse or
    geometry failure the input is returned unchanged with ``None``.
    """

    try:
        text = raw.decode("utf-8-sig")
        root = ET.fromstring(text)
    except Exception:
        return raw, None

    bounds = _element_bounds(root, IDENTITY, inherited_stroke_width=1.0, inside_defs=False)
    if bounds.is_empty:
        return raw, None

    bounds = bounds.expand(padding)
    view_box = _format_view_box(bounds)
    if re.search(r"\sviewBox=(['\"])(.*?)\1", text):
        cropped = re.sub(r"\sviewBox=(['\"])(.*?)\1", f' viewBox="{view_box}"', text, count=1)
    else:
        cropped = re.sub(r"<svg\b", f'<svg viewBox="{view_box}"', text, count=1)
    return cropped.encode("utf-8"), view_box


def _element_bounds(
    element: ET.Element,
    matrix: Matrix,
    *,
    inherited_stroke_width: float,
    inside_defs: bool,
) -> Bounds:
    tag = _local_name(element.tag)
    if _hidden(element):
        return Bounds.empty()

    next_inside_defs = inside_defs or tag in _NON_RENDERING_TAGS
    next_matrix = _multiply(matrix, _parse_transform(element.attrib.get("transform", "")))
    stroke_width = _number(element.attrib.get("stroke-width"), inherited_stroke_width)

    bounds = Bounds.empty()
    if not next_inside_defs:
        own = _shape_bounds(tag, element.attrib)
        if not own.is_empty and _paints(element.attrib, tag):
            own = _transform_bounds(own.expand(stroke_width / 2), next_matrix)
            bounds.include_bounds(own)

    for child in list(element):
        bounds.include_bounds(
            _element_bounds(
                child,
                next_matrix,
                inherited_stroke_width=stroke_width,
                inside_defs=next_inside_defs,
            )
        )
    return bounds


def _shape_bounds(tag: str, attrs: dict[str, str]) -> Bounds:
    bounds = Bounds.empty()
    if tag == "rect":
        x = _number(attrs.get("x"), 0)
        y = _number(attrs.get("y"), 0)
        width = _number(attrs.get("width"), 0)
        height = _number(attrs.get("height"), 0)
        if width > 0 and height > 0:
            bounds.include_point(x, y)
            bounds.include_point(x + width, y + height)
    elif tag == "line":
        bounds.include_point(_number(attrs.get("x1"), 0), _number(attrs.get("y1"), 0))
        bounds.include_point(_number(attrs.get("x2"), 0), _number(attrs.get("y2"), 0))
    elif tag == "circle":
        cx = _number(attrs.get("cx"), 0)
        cy = _number(attrs.get("cy"), 0)
        r = _number(attrs.get("r"), 0)
        bounds.include_point(cx - r, cy - r)
        bounds.include_point(cx + r, cy + r)
    elif tag == "ellipse":
        cx = _number(attrs.get("cx"), 0)
        cy = _number(attrs.get("cy"), 0)
        rx = _number(attrs.get("rx"), 0)
        ry = _number(attrs.get("ry"), 0)
        bounds.include_point(cx - rx, cy - ry)
        bounds.include_point(cx + rx, cy + ry)
    elif tag in {"polygon", "polyline"}:
        for x, y in _points(attrs.get("points", "")):
            bounds.include_point(x, y)
    elif tag == "path":
        bounds.include_bounds(_path_bounds(attrs.get("d", "")))
    return bounds


def _path_bounds(d: str) -> Bounds:
    tokens = _COMMAND_OR_NUMBER.findall(d)
    bounds = Bounds.empty()
    index = 0
    command = ""
    current = (0.0, 0.0)
    start = (0.0, 0.0)

    def has_number() -> bool:
        return index < len(tokens) and not _is_command(tokens[index])

    def read_float() -> float:
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    def read_point(relative: bool) -> tuple[float, float]:
        x = read_float()
        y = read_float()
        if relative:
            return current[0] + x, current[1] + y
        return x, y

    while index < len(tokens):
        if _is_command(tokens[index]):
            command = tokens[index]
            index += 1
        if not command:
            break
        cmd = command.upper()
        relative = command.islower()

        if cmd == "M":
            if not has_number():
                continue
            current = read_point(relative)
            start = current
            bounds.include_point(*current)
            command = "l" if relative else "L"
            while has_number():
                current = read_point(relative)
                bounds.include_point(*current)
        elif cmd == "L":
            while has_number():
                current = read_point(relative)
                bounds.include_point(*current)
        elif cmd == "H":
            while has_number():
                x = read_float()
                current = (current[0] + x if relative else x, current[1])
                bounds.include_point(*current)
        elif cmd == "V":
            while has_number():
                y = read_float()
                current = (current[0], current[1] + y if relative else y)
                bounds.include_point(*current)
        elif cmd == "C":
            while has_number() and index + 5 < len(tokens):
                for _ in range(3):
                    point = read_point(relative)
                    bounds.include_point(*point)
                current = point
        elif cmd == "S" or cmd == "Q":
            count = 2
            while has_number() and index + (count * 2 - 1) < len(tokens):
                for _ in range(count):
                    point = read_point(relative)
                    bounds.include_point(*point)
                current = point
        elif cmd == "T":
            while has_number():
                current = read_point(relative)
                bounds.include_point(*current)
        elif cmd == "A":
            while has_number() and index + 6 < len(tokens):
                rx = abs(read_float())
                ry = abs(read_float())
                _rotation = read_float()
                _large_arc = read_float()
                _sweep = read_float()
                end = read_point(relative)
                # Conservative: arc extrema can sit between endpoints. Expanding
                # around both endpoints prevents accidental clipping.
                for px, py in (current, end):
                    bounds.include_point(px - rx, py - ry)
                    bounds.include_point(px + rx, py + ry)
                current = end
        elif cmd == "Z":
            current = start
            bounds.include_point(*current)
        else:
            break
    return bounds


def _transform_bounds(bounds: Bounds, matrix: Matrix) -> Bounds:
    if bounds.is_empty:
        return bounds
    transformed = Bounds.empty()
    for x, y in (
        (bounds.min_x, bounds.min_y),
        (bounds.min_x, bounds.max_y),
        (bounds.max_x, bounds.min_y),
        (bounds.max_x, bounds.max_y),
    ):
        transformed.include_point(*_apply(matrix, x, y))
    return transformed


def _parse_transform(value: str) -> Matrix:
    matrix = IDENTITY
    for name, raw_args in _TRANSFORM_RE.findall(value or ""):
        args = [float(part) for part in re.split(r"[\s,]+", raw_args.strip()) if part]
        op = IDENTITY
        if name == "matrix" and len(args) >= 6:
            op = tuple(args[:6])  # type: ignore[assignment]
        elif name == "translate" and args:
            op = (1, 0, 0, 1, args[0], args[1] if len(args) > 1 else 0)
        elif name == "scale" and args:
            sx = args[0]
            sy = args[1] if len(args) > 1 else sx
            op = (sx, 0, 0, sy, 0, 0)
        elif name == "rotate" and args:
            angle = math.radians(args[0])
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rotate = (cos_a, sin_a, -sin_a, cos_a, 0, 0)
            if len(args) >= 3:
                cx, cy = args[1], args[2]
                op = _multiply(_multiply((1, 0, 0, 1, cx, cy), rotate), (1, 0, 0, 1, -cx, -cy))
            else:
                op = rotate
        matrix = _multiply(matrix, op)
    return matrix


def _multiply(a: Matrix, b: Matrix) -> Matrix:
    return (
        a[0] * b[0] + a[2] * b[1],
        a[1] * b[0] + a[3] * b[1],
        a[0] * b[2] + a[2] * b[3],
        a[1] * b[2] + a[3] * b[3],
        a[0] * b[4] + a[2] * b[5] + a[4],
        a[1] * b[4] + a[3] * b[5] + a[5],
    )


def _apply(matrix: Matrix, x: float, y: float) -> tuple[float, float]:
    return (
        matrix[0] * x + matrix[2] * y + matrix[4],
        matrix[1] * x + matrix[3] * y + matrix[5],
    )


def _points(value: str) -> list[tuple[float, float]]:
    numbers = [float(part) for part in re.split(r"[\s,]+", value.strip()) if part]
    return list(zip(numbers[::2], numbers[1::2], strict=False))


def _paints(attrs: dict[str, str], tag: str) -> bool:
    if tag in {"g", "svg"}:
        return False
    fill = attrs.get("fill")
    stroke = attrs.get("stroke")
    return fill != "none" or (stroke not in {None, "none"})


def _hidden(element: ET.Element) -> bool:
    style = element.attrib.get("style", "")
    return (
        element.attrib.get("display") == "none"
        or element.attrib.get("visibility") == "hidden"
        or element.attrib.get("opacity") == "0"
        or "display:none" in style.replace(" ", "")
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _is_command(value: str) -> bool:
    return len(value) == 1 and value.isalpha()


def _number(value: str | None, default: float) -> float:
    if value is None or value == "":
        return default
    try:
        return float(str(value).replace("px", ""))
    except ValueError:
        return default


def _format_view_box(bounds: Bounds) -> str:
    values = [bounds.min_x, bounds.min_y, bounds.max_x - bounds.min_x, bounds.max_y - bounds.min_y]
    return " ".join(_format_number(value) for value in values)


def _format_number(value: float) -> str:
    rounded = round(value, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")
