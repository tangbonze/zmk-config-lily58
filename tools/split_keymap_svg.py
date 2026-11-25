#!/usr/bin/env python3
"""Split keymap-drawer/lily58.svg into one standalone SVG per layer.

The upstream keymap-drawer action only emits the combined lily58.svg (all layers
stacked vertically). The README embeds the per-layer files produced here so each
layer can sit next to its own description.

Usage:  python3 tools/split_keymap_svg.py [keymap-drawer/lily58.svg]
"""

from __future__ import annotations

import math
import re
import sys
import xml.dom.minidom
from pathlib import Path

LAYER_OPEN = re.compile(r'<g transform="translate\((\d+), (\d+)\)" class="layer-([^"]+)">$')
G_OPEN = re.compile(r"<g(?=[ >])")
G_CLOSE = re.compile(r"</g>")
ROTATED = re.compile(r"translate\(-?[\d.]+, (-?[\d.]+)\) rotate\(")
KEY_SIDE = 52
TOP_PAD = 22


def find_matching_close(lines: list[str], start: int) -> int:
    """Return the index of the `</g>` that closes the group opened at `start`."""
    depth = 1
    idx = start + 1
    while idx < len(lines) and depth > 0:
        depth += len(G_OPEN.findall(lines[idx])) - len(G_CLOSE.findall(lines[idx]))
        idx += 1
    return idx - 1


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    svg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "keymap-drawer" / "lily58.svg"
    if not svg_path.is_file():
        print(f"error: {svg_path} not found", file=sys.stderr)
        return 1

    lines = svg_path.read_text(encoding="utf-8").split("\n")

    defs_end = next((i for i, line in enumerate(lines) if "</defs>" in line), None)
    style_start = next(i for i, line in enumerate(lines) if "<style>" in line)
    style_end = next(i for i, line in enumerate(lines) if "</style>" in line)
    glyphs = lines[1 : defs_end + 1] if defs_end is not None else []
    style = lines[style_start : style_end + 1]

    layers = []
    for idx, line in enumerate(lines):
        match = LAYER_OPEN.match(line)
        if match:
            x_offset = int(match.group(1))
            y_offset = int(match.group(2))
            layers.append((idx, x_offset, y_offset, match.group(3)))
    if not layers:
        print("error: no layer groups found", file=sys.stderr)
        return 1

    width = int(re.search(r'width="(\d+)"', lines[0]).group(1))
    total_h = int(re.search(r'height="(\d+)"', lines[0]).group(1))
    out_dir = svg_path.parent / "layers"
    out_dir.mkdir(parents=True, exist_ok=True)

    half_diagonal = KEY_SIDE / 2 * math.sqrt(2)
    failures = 0

    for idx, (start, x_offset, y_offset, name) in enumerate(layers):
        end = find_matching_close(lines, start)
        seg = list(lines[start : end + 1])
        seg[0] = re.sub(
            r"translate\(\d+, \d+\)",
            f"translate({x_offset}, 0)",
            seg[0],
            count=1,
        )
        body = "\n".join(seg)

        ys = [float(m.group(1)) for m in re.finditer(r"translate\(-?[\d.]+, (-?[\d.]+)\)", body)]
        rotated = [float(m.group(1)) + half_diagonal for m in ROTATED.finditer(body)]
        bottom = max(ys + rotated + [0.0])

        if idx + 1 < len(layers):
            height = layers[idx + 1][2] - y_offset
        else:
            height = total_h - y_offset

        doc = [
            f'<svg width="{width}" height="{height}" viewBox="0 -{TOP_PAD} {width} {height + TOP_PAD}" '
            'class="keymap" xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink">',
            *glyphs,
            *style,
            *seg,
            "</svg>",
        ]
        dest = out_dir / f"{name}.svg"
        dest.write_text("\n".join(doc), encoding="utf-8")

        try:
            xml.dom.minidom.parse(str(dest))
        except Exception as exc:
            print(f"  {name}.svg  INVALID XML: {exc}", file=sys.stderr)
            failures += 1
            continue
        print(f"  {name}.svg  {height}px (content bottom {bottom:.0f})")

    if failures:
        print(f"error: {failures} layer file(s) failed XML validation", file=sys.stderr)
        return 1
    print(f"wrote {len(layers)} layer file(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
