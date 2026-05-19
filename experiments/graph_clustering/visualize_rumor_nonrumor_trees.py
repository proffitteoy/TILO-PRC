"""谣言/非谣言传播树可视化对比（SVG 输出，无第三方绘图库依赖）。"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CODE_DIR = Path(r"F:\谣言传播\code")
DEFAULT_PSQL_PATH = Path(r"D:\PostgreSQL\bin\psql.exe")
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "graph_clustering" / "rumor_vs_non_rumor_viz"
LABEL_COLORS = {
    "rumor": "#d94848",
    "non_rumor": "#3b82f6",
}


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: str
    database: str
    user: str
    password: str
    psql_path: Path


@dataclass(frozen=True)
class CandidateRoot:
    root_id: str
    label_value: str
    total_nodes: int
    root_created_at: str


@dataclass(frozen=True)
class TreeNode:
    root_id: str
    node_id: str
    parent_id: str | None
    is_root: bool
    created_at: datetime


@dataclass(frozen=True)
class TreeMetric:
    root_id: str
    label_value: str
    node_count: int
    edge_count: int
    max_depth: int
    duration_hours: float
    branching_factor: float
    mean_parent_lag_hours: float
    median_parent_lag_hours: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="可视化对比谣言与非谣言传播树形态和结构指标。")
    parser.add_argument("--source-code-dir", default=str(DEFAULT_SOURCE_CODE_DIR))
    parser.add_argument("--database", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", default="")
    parser.add_argument("--user", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--psql-path", default="")
    parser.add_argument("--label-name", default="risk", help="标签命名空间，默认 risk。")
    parser.add_argument("--label-tier", choices=["all", "strong", "weak"], default="strong")
    parser.add_argument("--label-values", default="rumor,non_rumor")
    parser.add_argument("--sample-per-label", type=int, default=4, help="每类绘制多少棵样例树。")
    parser.add_argument("--metric-limit-per-label", type=int, default=60, help="每类最多统计多少棵树做分布图。")
    parser.add_argument("--min-total-nodes", type=int, default=50, help="仅纳入节点数不低于该值的传播树。")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def resolve_db_config(args: argparse.Namespace) -> DbConfig:
    source_dir = Path(args.source_code_dir)
    file_values: dict[str, str] = {}
    for name in (".env.local", ".env", ".env.example"):
        file_values.update(parse_env_file(source_dir / name))

    def pick(cli_value: str, env_name: str, fallback: str = "") -> str:
        if cli_value:
            return cli_value
        if os.environ.get(env_name):
            return str(os.environ[env_name])
        if file_values.get(env_name):
            return str(file_values[env_name])
        return fallback

    config = DbConfig(
        host=pick(args.host, "PGHOST", "localhost"),
        port=pick(args.port, "PGPORT", "5432"),
        database=pick(args.database, "PGDATABASE", "aigc_propagation"),
        user=pick(args.user, "PGUSER", "postgres"),
        password=pick(args.password, "PGPASSWORD", ""),
        psql_path=Path(pick(args.psql_path, "PSQL_PATH", str(DEFAULT_PSQL_PATH))),
    )
    if not config.password:
        raise RuntimeError("未解析到 PGPASSWORD，请通过 --password 或 .env 提供。")
    if not config.psql_path.exists():
        raise RuntimeError(f"psql 不存在：{config.psql_path}")
    return config


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_psql_sql(config: DbConfig, sql: str) -> str:
    env = os.environ.copy()
    env["PGPASSWORD"] = config.password
    env.setdefault("PGCLIENTENCODING", "UTF8")
    args = [
        str(config.psql_path),
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        config.host,
        "-p",
        config.port,
        "-U",
        config.user,
        "-d",
        config.database,
    ]
    completed = subprocess.run(
        args,
        input=sql,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
        env=env,
    )
    return completed.stdout


def query_dicts(config: DbConfig, sql: str) -> list[dict[str, str]]:
    statement = sql.strip().rstrip(";")
    copy_sql = (
        "COPY (\n"
        f"{statement}\n"
        ") TO STDOUT WITH (FORMAT CSV, HEADER TRUE, DELIMITER E'\\t');\n"
    )
    text = run_psql_sql(config, copy_sql)
    if not text.strip():
        return []
    reader = csv.DictReader(StringIO(text), delimiter="\t")
    rows: list[dict[str, str]] = []
    for row in reader:
        cleaned: dict[str, str] = {}
        for key, value in row.items():
            k = str(key).strip() if key is not None else ""
            v = value.strip() if isinstance(value, str) else ""
            cleaned[k] = v
        rows.append(cleaned)
    return rows


def parse_label_values(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    if not deduped:
        raise RuntimeError("--label-values 不能为空。")
    return deduped


def parse_timestamp(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def fetch_labeled_roots(
    config: DbConfig,
    *,
    label_name: str,
    label_tier: str,
    label_values: list[str],
) -> list[CandidateRoot]:
    tier_filter = "" if label_tier == "all" else f"AND el.label_tier = {sql_literal(label_tier)}"
    quoted_values = ", ".join(sql_literal(value) for value in label_values)
    sql = f"""
        WITH ranked AS (
            SELECT
                el.root_weibo_id,
                el.label_value,
                COALESCE(root.created_at::text, '') AS root_created_at,
                ROW_NUMBER() OVER (
                    PARTITION BY el.root_weibo_id
                    ORDER BY
                        CASE el.label_tier WHEN 'strong' THEN 0 ELSE 1 END,
                        COALESCE(el.confidence, -1) DESC,
                        el.updated_at DESC
                ) AS rn
            FROM wbprop.event_labels el
            JOIN wbprop.propagation_nodes root
              ON root.id = el.root_weibo_id
             AND root.is_root = TRUE
            WHERE el.is_active = TRUE
              AND el.label_name = {sql_literal(label_name)}
              AND el.label_value IN ({quoted_values})
              {tier_filter}
        ),
        canon AS (
            SELECT root_weibo_id, label_value, root_created_at
            FROM ranked
            WHERE rn = 1
        ),
        sizes AS (
            SELECT root_id, COUNT(*) AS total_nodes
            FROM wbprop.propagation_nodes
            GROUP BY root_id
        )
        SELECT
            canon.root_weibo_id,
            canon.label_value,
            canon.root_created_at,
            sizes.total_nodes::text AS total_nodes
        FROM canon
        JOIN sizes
          ON sizes.root_id = canon.root_weibo_id
        ORDER BY canon.label_value, sizes.total_nodes DESC, canon.root_created_at, canon.root_weibo_id
    """
    rows = query_dicts(config, sql)
    result: list[CandidateRoot] = []
    for row in rows:
        result.append(
            CandidateRoot(
                root_id=row["root_weibo_id"],
                label_value=row["label_value"],
                total_nodes=int(row["total_nodes"]),
                root_created_at=row.get("root_created_at", ""),
            )
        )
    return result


def batch(items: list[str], size: int) -> list[list[str]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def fetch_nodes_for_roots(config: DbConfig, root_ids: list[str]) -> dict[str, list[TreeNode]]:
    grouped: dict[str, list[TreeNode]] = defaultdict(list)
    for chunk in batch(root_ids, 50):
        quoted = ", ".join(sql_literal(root_id) for root_id in chunk)
        sql = f"""
            SELECT
                root_id,
                id AS node_id,
                COALESCE(parent_id, '') AS parent_id,
                CASE WHEN is_root THEN 'true' ELSE 'false' END AS is_root,
                created_at::text AS created_at_text
            FROM wbprop.propagation_nodes
            WHERE root_id IN ({quoted})
            ORDER BY root_id, created_at, id
        """
        rows = query_dicts(config, sql)
        for row in rows:
            grouped[row["root_id"]].append(
                TreeNode(
                    root_id=row["root_id"],
                    node_id=row["node_id"],
                    parent_id=row.get("parent_id") or None,
                    is_root=(row.get("is_root", "").lower() == "true"),
                    created_at=parse_timestamp(row["created_at_text"]),
                )
            )
    return grouped


def build_depths(node_map: dict[str, TreeNode]) -> dict[str, int]:
    cache: dict[str, int] = {}

    def resolve(node_id: str, trail: set[str]) -> int:
        if node_id in cache:
            return cache[node_id]
        node = node_map[node_id]
        if node.is_root:
            cache[node_id] = 0
            return 0
        parent_id = node.parent_id
        if not parent_id or parent_id not in node_map or parent_id in trail:
            cache[node_id] = 0
            return 0
        depth = resolve(parent_id, trail | {node_id}) + 1
        cache[node_id] = depth
        return depth

    for node_id in node_map:
        resolve(node_id, set())
    return cache


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = idx - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def compute_tree_metric(root_id: str, label_value: str, nodes: list[TreeNode]) -> TreeMetric:
    if not nodes:
        raise RuntimeError(f"root_id={root_id} 节点为空。")
    node_map = {node.node_id: node for node in nodes}
    root_nodes = [node for node in nodes if node.is_root]
    root_time = root_nodes[0].created_at if root_nodes else min(node.created_at for node in nodes)
    depths = build_depths(node_map)

    edge_count = 0
    parent_lags: list[float] = []
    child_count = Counter()
    for node in nodes:
        if node.is_root:
            continue
        if not node.parent_id or node.parent_id not in node_map:
            continue
        edge_count += 1
        child_count[node.parent_id] += 1
        parent_time = node_map[node.parent_id].created_at
        lag_h = max(0.0, (node.created_at - parent_time).total_seconds() / 3600.0)
        parent_lags.append(lag_h)

    max_time = max(node.created_at for node in nodes)
    duration_hours = max(0.0, (max_time - root_time).total_seconds() / 3600.0)
    max_depth = max(depths.values(), default=0)

    internal_nodes = [node_id for node_id, cnt in child_count.items() if cnt > 0]
    descendant_count = max(len(nodes) - 1, 0)
    branching_factor = float(descendant_count / len(internal_nodes)) if internal_nodes else 0.0

    return TreeMetric(
        root_id=root_id,
        label_value=label_value,
        node_count=len(nodes),
        edge_count=edge_count,
        max_depth=max_depth,
        duration_hours=duration_hours,
        branching_factor=branching_factor,
        mean_parent_lag_hours=(statistics.mean(parent_lags) if parent_lags else 0.0),
        median_parent_lag_hours=(statistics.median(parent_lags) if parent_lags else 0.0),
    )


def safe_token(value: str) -> str:
    text = value.strip()
    if not text:
        return "unknown"
    return "".join(ch if (ch.isalnum() or ch in {"-", "_"}) else "_" for ch in text)


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def tree_layout(nodes: list[TreeNode], width: int, height: int) -> tuple[dict[str, tuple[float, float]], dict[str, int], float]:
    node_map = {node.node_id: node for node in nodes}
    depths = build_depths(node_map)
    root_nodes = [node for node in nodes if node.is_root]
    root_time = root_nodes[0].created_at if root_nodes else min(node.created_at for node in nodes)
    rel_sec = {
        node.node_id: max(0.0, (node.created_at - root_time).total_seconds())
        for node in nodes
    }
    max_rel = max(rel_sec.values(), default=0.0)
    max_depth = max(depths.values(), default=0)

    by_depth: dict[int, list[TreeNode]] = defaultdict(list)
    for node in nodes:
        by_depth[depths.get(node.node_id, 0)].append(node)
    for level in by_depth:
        by_depth[level].sort(key=lambda n: (n.created_at, n.node_id))

    left, right, top, bottom = 40.0, 10.0, 26.0, 16.0
    plot_w = max(10.0, float(width) - left - right)
    plot_h = max(10.0, float(height) - top - bottom)

    coords: dict[str, tuple[float, float]] = {}
    for depth_level, level_nodes in by_depth.items():
        total_at_depth = len(level_nodes)
        for idx, node in enumerate(level_nodes):
            rt = rel_sec[node.node_id]
            if max_rel <= 0:
                x_ratio = 0.0
            else:
                x_ratio = math.log1p(rt) / math.log1p(max_rel)
            x = left + x_ratio * plot_w

            if max_depth <= 0:
                y_base = 0.5
            else:
                y_base = depth_level / max_depth
            if total_at_depth <= 1:
                y_jitter = 0.0
            else:
                y_jitter = (idx / (total_at_depth - 1) - 0.5) * (1.0 / max(2.0, max_depth + 1.0))
            y = top + min(1.0, max(0.0, y_base + y_jitter)) * plot_h
            coords[node.node_id] = (x, y)
    return coords, depths, max_rel


def render_sample_trees_svg(
    *,
    sample_roots_by_label: dict[str, list[str]],
    nodes_by_root: dict[str, list[TreeNode]],
    metrics_by_root: dict[str, TreeMetric],
    output_path: Path,
) -> None:
    labels = list(sample_roots_by_label.keys())
    cols = max((len(sample_roots_by_label[label]) for label in labels), default=1)
    panel_w, panel_h = 340, 220
    left_margin, top_margin = 20, 46
    width = left_margin * 2 + cols * panel_w
    height = top_margin + len(labels) * panel_h + 20

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;}</style>',
        '<text x="20" y="24" font-size="16" font-weight="bold" fill="#111827">谣言 vs 非谣言：样例传播树形态</text>',
    ]

    for row, label in enumerate(labels):
        y_row = top_margin + row * panel_h
        color = LABEL_COLORS.get(label, "#6b7280")
        parts.append(
            f'<text x="20" y="{y_row + 18}" font-size="13" font-weight="bold" fill="{color}">{svg_escape(label)}</text>'
        )
        for col, root_id in enumerate(sample_roots_by_label[label]):
            x_panel = left_margin + col * panel_w
            y_panel = y_row + 22
            inner_w = panel_w - 14
            inner_h = panel_h - 30
            parts.append(
                f'<rect x="{x_panel}" y="{y_panel}" width="{inner_w}" height="{inner_h}" fill="#fafafa" stroke="#e5e7eb" stroke-width="1"/>'
            )

            nodes = nodes_by_root.get(root_id, [])
            if not nodes:
                continue
            coords, depths, max_rel = tree_layout(nodes, inner_w, inner_h)
            node_map = {node.node_id: node for node in nodes}
            metric = metrics_by_root[root_id]
            for node in nodes:
                if node.is_root or not node.parent_id or node.parent_id not in coords:
                    continue
                x1, y1 = coords[node.parent_id]
                x2, y2 = coords[node.node_id]
                parts.append(
                    f'<line x1="{x_panel + x1:.2f}" y1="{y_panel + y1:.2f}" '
                    f'x2="{x_panel + x2:.2f}" y2="{y_panel + y2:.2f}" '
                    f'stroke="{color}" stroke-opacity="0.35" stroke-width="0.7"/>'
                )

            for node in nodes:
                cx, cy = coords[node.node_id]
                radius = 2.4 if node.is_root else 1.4
                fill = "#111827" if node.is_root else color
                parts.append(
                    f'<circle cx="{x_panel + cx:.2f}" cy="{y_panel + cy:.2f}" r="{radius}" fill="{fill}" fill-opacity="0.9"/>'
                )

            title = (
                f"{root_id} | n={metric.node_count}, depth={metric.max_depth}, "
                f"dur={metric.duration_hours:.1f}h"
            )
            parts.append(
                f'<text x="{x_panel + 8}" y="{y_panel + 14}" font-size="10" fill="#374151">{svg_escape(title)}</text>'
            )
            parts.append(
                f'<text x="{x_panel + 8}" y="{y_panel + inner_h - 6}" font-size="9" fill="#6b7280">'
                f'max_rel_time={max_rel / 3600.0:.1f}h</text>'
            )

    parts.append("</svg>")
    write_text(output_path, "\n".join(parts))


def render_boxplot_svg(
    *,
    metric_name: str,
    metric_title: str,
    values_by_label: dict[str, list[float]],
    output_path: Path,
) -> None:
    labels = list(values_by_label.keys())
    width, height = 760, 460
    left, right, top, bottom = 80, 30, 60, 70
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_values = [value for vals in values_by_label.values() for value in vals]
    if not all_values:
        raise RuntimeError(f"{metric_name} 无可用数值。")
    v_min = min(all_values)
    v_max = max(all_values)
    if math.isclose(v_min, v_max):
        v_max = v_min + 1.0
    pad = (v_max - v_min) * 0.08
    y_min = v_min - pad
    y_max = v_max + pad

    def y_of(value: float) -> float:
        ratio = (value - y_min) / (y_max - y_min)
        return top + (1.0 - ratio) * plot_h

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;}</style>',
        f'<text x="{left}" y="30" font-size="18" font-weight="bold" fill="#111827">{svg_escape(metric_title)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#9ca3af"/>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#9ca3af"/>',
    ]

    for t in range(6):
        ratio = t / 5.0
        value = y_min + ratio * (y_max - y_min)
        y = y_of(value)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}" stroke="#f3f4f6"/>')
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.2f}" font-size="10" fill="#6b7280" text-anchor="end">{value:.2f}</text>'
        )

    step = plot_w / max(1, len(labels))
    for idx, label in enumerate(labels):
        vals = sorted(values_by_label[label])
        if not vals:
            continue
        q1 = quantile(vals, 0.25)
        q2 = quantile(vals, 0.50)
        q3 = quantile(vals, 0.75)
        v0 = vals[0]
        v1 = vals[-1]
        mean_val = float(statistics.mean(vals))
        x_center = left + step * (idx + 0.5)
        box_w = min(90.0, step * 0.45)
        color = LABEL_COLORS.get(label, "#6b7280")

        parts.append(
            f'<line x1="{x_center:.2f}" y1="{y_of(v0):.2f}" x2="{x_center:.2f}" y2="{y_of(v1):.2f}" stroke="{color}" stroke-width="1.2"/>'
        )
        parts.append(
            f'<rect x="{x_center - box_w/2:.2f}" y="{y_of(q3):.2f}" width="{box_w:.2f}" height="{max(1.0, y_of(q1)-y_of(q3)):.2f}" '
            f'fill="{color}" fill-opacity="0.18" stroke="{color}" stroke-width="1.4"/>'
        )
        parts.append(
            f'<line x1="{x_center - box_w/2:.2f}" y1="{y_of(q2):.2f}" x2="{x_center + box_w/2:.2f}" y2="{y_of(q2):.2f}" '
            f'stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<circle cx="{x_center:.2f}" cy="{y_of(mean_val):.2f}" r="3.2" fill="{color}" stroke="#ffffff" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{top + plot_h + 24}" font-size="12" fill="#374151" text-anchor="middle">{svg_escape(label)}</text>'
        )
        parts.append(
            f'<text x="{x_center:.2f}" y="{top + plot_h + 40}" font-size="10" fill="#6b7280" text-anchor="middle">n={len(vals)}</text>'
        )

    legend_x = left + plot_w - 170
    legend_y = top + 8
    parts.append(f'<text x="{legend_x}" y="{legend_y}" font-size="11" fill="#6b7280">箱体: Q1-Q3 | 横线: 中位数 | 圆点: 均值</text>')
    parts.append("</svg>")
    write_text(output_path, "\n".join(parts))


def main() -> int:
    args = parse_args()
    label_values = parse_label_values(args.label_values)
    config = resolve_db_config(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = fetch_labeled_roots(
        config,
        label_name=args.label_name,
        label_tier=args.label_tier,
        label_values=label_values,
    )
    by_label: dict[str, list[CandidateRoot]] = defaultdict(list)
    for row in candidates:
        if row.total_nodes >= args.min_total_nodes:
            by_label[row.label_value].append(row)

    for label in label_values:
        if len(by_label.get(label, [])) < max(args.sample_per_label, 1):
            raise RuntimeError(
                f"{label} 可用传播树不足：{len(by_label.get(label, []))}，至少需要 {args.sample_per_label}。"
            )

    sample_roots_by_label: dict[str, list[str]] = {}
    metric_roots_by_label: dict[str, list[str]] = {}
    for label in label_values:
        label_rows = by_label[label]
        sample_roots_by_label[label] = [row.root_id for row in label_rows[: args.sample_per_label]]
        metric_roots_by_label[label] = [row.root_id for row in label_rows[: args.metric_limit_per_label]]

    all_roots = sorted({root_id for roots in metric_roots_by_label.values() for root_id in roots})
    nodes_by_root = fetch_nodes_for_roots(config, all_roots)

    metrics: list[TreeMetric] = []
    metrics_by_root: dict[str, TreeMetric] = {}
    for label in label_values:
        for root_id in metric_roots_by_label[label]:
            node_rows = nodes_by_root.get(root_id, [])
            if not node_rows:
                continue
            metric = compute_tree_metric(root_id, label, node_rows)
            metrics.append(metric)
            metrics_by_root[root_id] = metric

    sample_svg = output_dir / "sample_trees_panel.svg"
    render_sample_trees_svg(
        sample_roots_by_label=sample_roots_by_label,
        nodes_by_root=nodes_by_root,
        metrics_by_root=metrics_by_root,
        output_path=sample_svg,
    )

    metric_specs = [
        ("node_count", "节点数分布对比（Node Count）"),
        ("duration_hours", "传播持续时长对比（Duration Hours）"),
        ("max_depth", "最大深度对比（Max Depth）"),
        ("branching_factor", "分支因子对比（Branching Factor）"),
        ("mean_parent_lag_hours", "平均父子传播时延对比（Mean Parent Lag Hours）"),
    ]

    metric_files: list[str] = []
    for metric_name, metric_title in metric_specs:
        values_by_label: dict[str, list[float]] = defaultdict(list)
        for row in metrics:
            values_by_label[row.label_value].append(float(getattr(row, metric_name)))
        out_path = output_dir / f"{safe_token(metric_name)}_boxplot.svg"
        render_boxplot_svg(
            metric_name=metric_name,
            metric_title=metric_title,
            values_by_label=values_by_label,
            output_path=out_path,
        )
        metric_files.append(str(out_path.resolve()))

    metric_tsv = output_dir / "tree_metrics.tsv"
    with metric_tsv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "root_id",
                "label_value",
                "node_count",
                "edge_count",
                "max_depth",
                "duration_hours",
                "branching_factor",
                "mean_parent_lag_hours",
                "median_parent_lag_hours",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for row in metrics:
            writer.writerow(
                {
                    "root_id": row.root_id,
                    "label_value": row.label_value,
                    "node_count": row.node_count,
                    "edge_count": row.edge_count,
                    "max_depth": row.max_depth,
                    "duration_hours": f"{row.duration_hours:.6f}",
                    "branching_factor": f"{row.branching_factor:.6f}",
                    "mean_parent_lag_hours": f"{row.mean_parent_lag_hours:.6f}",
                    "median_parent_lag_hours": f"{row.median_parent_lag_hours:.6f}",
                }
            )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "db": {
            "host": config.host,
            "port": config.port,
            "database": config.database,
            "user": config.user,
            "psql_path": str(config.psql_path),
        },
        "label_name": args.label_name,
        "label_tier": args.label_tier,
        "label_values": label_values,
        "min_total_nodes": args.min_total_nodes,
        "sample_per_label": args.sample_per_label,
        "metric_limit_per_label": args.metric_limit_per_label,
        "sample_roots_by_label": sample_roots_by_label,
        "metric_tree_count_by_label": {
            label: sum(1 for row in metrics if row.label_value == label)
            for label in label_values
        },
        "files": {
            "sample_trees_panel": str(sample_svg.resolve()),
            "metric_boxplots": metric_files,
            "tree_metrics_tsv": str(metric_tsv.resolve()),
        },
    }
    summary_path = output_dir / "visualization_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] sample panel: {sample_svg.resolve()}")
    for path in metric_files:
        print(f"[OK] boxplot: {path}")
    print(f"[OK] metrics: {metric_tsv.resolve()}")
    print(f"[OK] summary: {summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
