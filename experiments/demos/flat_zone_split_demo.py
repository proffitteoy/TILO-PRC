from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyprc.enums import FlatStruct, FlatType
from pyprc.matrix import BoundaryObject


def _find_split_on_boundary(boundary_values: list[float]) -> dict[str, object]:
    b = BoundaryObject()
    b.resize(len(boundary_values), boundary_values[0] if boundary_values else 0.0)
    for i, v in enumerate(boundary_values):
        b.set_at(i, float(v))

    marks: list[FlatStruct] = []
    b.findLocalMinAndMax(marks)

    best_r = float("inf")
    best_d = -float("inf")
    best_idx = -1
    cur_start = 0
    cur_stop = len(boundary_values) - 1

    for z, mark in enumerate(marks):
        if mark.type == FlatType.LocalMax:
            continue
        if mark.start >= cur_stop:
            continue
        if mark.stop <= cur_start:
            continue
        if mark.start == cur_start:
            continue

        local_min_cut = float(b.at(mark.start))
        am = local_min_cut
        bm = local_min_cut

        for x in range(z - 1, -1, -1):
            if marks[x].start <= cur_start:
                break
            if marks[x].type == FlatType.LocalMin:
                continue
            bval = float(b.at(marks[x].start))
            if bval > am:
                am = bval

        for x in range(z + 1, len(marks)):
            if marks[x].start >= cur_stop:
                break
            if marks[x].type == FlatType.LocalMin:
                continue
            bval = float(b.at(marks[x].start))
            if bval > bm:
                bm = bval

        thick = min(am, bm)
        pinch_ratio = abs(local_min_cut / thick) if thick > 0 else float("inf")
        diff = thick - local_min_cut

        if (pinch_ratio < best_r) or (pinch_ratio == best_r and diff > best_d):
            best_r = pinch_ratio
            best_d = diff
            best_idx = z

    if best_idx < 0:
        return {
            "split_loc": -1,
            "split_flat_start": -1,
            "split_flat_stop": -1,
            "pinch_ratio": None,
            "marks": [
                {"start": m.start, "stop": m.stop, "type": "min" if m.type == FlatType.LocalMin else "max"}
                for m in marks
            ],
        }

    chosen = marks[best_idx]
    return {
        "split_loc": int(chosen.start),
        "split_flat_start": int(chosen.start),
        "split_flat_stop": int(chosen.stop),
        "pinch_ratio": None if not math.isfinite(best_r) else float(best_r),
        "marks": [
            {"start": m.start, "stop": m.stop, "type": "min" if m.type == FlatType.LocalMin else "max"}
            for m in marks
        ],
    }


def _draw(boundary_values: list[float], split_info: dict[str, object], output_file: Path) -> None:
    canvas = Image.new("RGB", (1320, 620), color=(248, 248, 248))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    rect = (40, 50, 1280, 440)
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, outline=(0, 0, 0), width=2)
    draw.text((x0 + 8, y0 + 8), "Flat-zone split simulation (PinchRatio rule)", fill=(0, 0, 0), font=font)

    vals = [float(v) for v in boundary_values]
    if len(vals) >= 2:
        vmin = min(vals)
        vmax = max(vals)
        if abs(vmax - vmin) < 1e-12:
            vmax = vmin + 1.0
        inner_w = (x1 - x0) - 40
        inner_h = (y1 - y0) - 50
        pts: list[tuple[float, float]] = []
        for i, val in enumerate(vals):
            tx = x0 + 20 + (i / (len(vals) - 1)) * inner_w
            ty = y1 - 20 - ((val - vmin) / (vmax - vmin)) * inner_h
            pts.append((tx, ty))
        draw.line(pts, fill=(20, 20, 26), width=5)

        split_start = int(split_info["split_flat_start"])
        split_stop = int(split_info["split_flat_stop"])
        if 0 <= split_start < len(pts):
            sx = pts[split_start][0]
            draw.line((sx, y0 + 22, sx, y1 - 20), fill=(230, 33, 40), width=2)
            draw.text((sx + 4, y0 + 24), f"chosen split={split_start}", fill=(230, 33, 40), font=font)
        if 0 <= split_start <= split_stop < len(pts):
            px0 = pts[split_start][0]
            px1 = pts[split_stop][0]
            py = pts[split_start][1]
            draw.line((px0, py - 8, px1, py - 8), fill=(255, 140, 0), width=3)
            draw.text((px0, py - 24), f"flat zone [{split_start}, {split_stop}]", fill=(255, 140, 0), font=font)

    lines = [
        f"boundary length={len(boundary_values)}",
        f"split_loc={split_info['split_loc']}",
        f"flat_start={split_info['split_flat_start']}, flat_stop={split_info['split_flat_stop']}",
        "rule detail: split in flat zone uses mark.start",
    ]
    if split_info["pinch_ratio"] is not None:
        lines.append(f"pinch_ratio={split_info['pinch_ratio']:.6f}")
    ty = 470
    for line in lines:
        draw.text((52, ty), line, fill=(0, 0, 0), font=font)
        ty += 20

    output_file.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_file)


def main() -> int:
    parser = argparse.ArgumentParser(description="模拟平坦地带（plateau）时 PRC 的切分位置")
    parser.add_argument(
        "--boundary",
        type=str,
        default="2,4,7,10,7,4,2,2,2,2,2,2,2,2,4,7,10,7,4,2",
        help="边界序列，逗号分隔",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/demos/flat_zone_split"),
        help="输出目录",
    )
    args = parser.parse_args()

    boundary = [float(x.strip()) for x in args.boundary.split(",") if x.strip()]
    if len(boundary) < 3:
        raise ValueError("boundary 至少需要 3 个点。")

    split_info = _find_split_on_boundary(boundary)
    out_img = args.output_dir / "flat_zone_split_demo.png"
    out_json = args.output_dir / "flat_zone_split_demo.json"
    _draw(boundary, split_info, out_img)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(
            {
                "boundary": boundary,
                **split_info,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"image: {out_img}")
    print(f"summary: {out_json}")
    print(f"split_loc: {split_info['split_loc']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
