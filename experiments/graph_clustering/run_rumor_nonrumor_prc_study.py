"""Batch PRC clustering study for rumor/non-rumor propagation trees with resume support."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CODE_DIR = Path(r"F:\谣言传播\code")
DEFAULT_PSQL_PATH = Path(r"D:\PostgreSQL\bin\psql.exe")
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "graph_clustering" / "prc_study_rumor_nonrumor" / "all_trees"

ROOT_FIELDS = ["index", "root_id", "label_value", "total_nodes", "root_created_at"]
RESULT_FIELDS = [
    "root_id",
    "label_value",
    "root_created_at",
    "total_nodes_from_db",
    "node_count",
    "edge_count",
    "cluster_count",
    "cut_ratio",
    "ncut",
    "cluster_entropy_norm",
    "largest_cluster_ratio",
    "cluster_sizes_json",
    "edge_weight_mode",
    "numpart",
    "seed",
    "runtime_seconds",
    "finished_at_utc",
]
ERROR_FIELDS = [
    "root_id",
    "label_value",
    "root_created_at",
    "total_nodes_from_db",
    "error_type",
    "error_message",
    "traceback",
    "failed_at_utc",
]


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
class NodeRecord:
    node_id: str
    parent_id: str | None
    created_at: datetime
    is_root: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run PRC clustering for many propagation trees and persist progress so interrupted "
            "runs can resume."
        )
    )
    parser.add_argument("--source-code-dir", default=str(DEFAULT_SOURCE_CODE_DIR))
    parser.add_argument("--database", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", default="")
    parser.add_argument("--user", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--psql-path", default="")
    parser.add_argument("--label-name", default="risk")
    parser.add_argument("--label-tier", choices=["all", "strong", "weak"], default="strong")
    parser.add_argument("--label-values", default="rumor,non_rumor")
    parser.add_argument(
        "--min-total-nodes",
        type=int,
        default=0,
        help="Filter roots by minimum total nodes. Use 0 to disable.",
    )
    parser.add_argument(
        "--max-per-label",
        type=int,
        default=0,
        help="Limit roots per label. Use 0 to process all available roots per label.",
    )
    parser.add_argument(
        "--edge-weight-mode",
        choices=["relative_root_seconds", "parent_lag_seconds"],
        default="relative_root_seconds",
    )
    parser.add_argument("--numpart", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep graph/labels files.")
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="Re-run roots that previously failed and were recorded in errors.tsv.",
    )
    parser.add_argument(
        "--refresh-roots",
        action="store_true",
        help="Rebuild roots catalog from DB even if roots_catalog.tsv already exists.",
    )
    parser.add_argument(
        "--resume",
        dest="resume",
        action="store_true",
        help="Resume from existing results/errors/checkpoint if present (default).",
    )
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Ignore existing progress and process according to current catalog.",
    )
    parser.set_defaults(resume=True)
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

    cfg = DbConfig(
        host=pick(args.host, "PGHOST", "localhost"),
        port=pick(args.port, "PGPORT", "5432"),
        database=pick(args.database, "PGDATABASE", "aigc_propagation"),
        user=pick(args.user, "PGUSER", "postgres"),
        password=pick(args.password, "PGPASSWORD", ""),
        psql_path=Path(pick(args.psql_path, "PSQL_PATH", str(DEFAULT_PSQL_PATH))),
    )
    if not cfg.password:
        raise RuntimeError("PGPASSWORD is missing. Provide --password or configure .env/.env.local.")
    if not cfg.psql_path.exists():
        raise RuntimeError(f"psql not found: {cfg.psql_path}")
    return cfg


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def parse_label_values(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for v in values:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
    if not deduped:
        raise RuntimeError("--label-values cannot be empty.")
    return deduped


def run_psql_sql(config: DbConfig, sql: str) -> str:
    env = os.environ.copy()
    env["PGPASSWORD"] = config.password
    env.setdefault("PGCLIENTENCODING", "UTF8")
    cmd = [
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
        cmd,
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


def parse_timestamp(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def build_roots_from_db(
    config: DbConfig,
    *,
    label_name: str,
    label_tier: str,
    label_values: list[str],
    min_total_nodes: int,
    max_per_label: int,
) -> list[CandidateRoot]:
    tier_filter = "" if label_tier == "all" else f"AND el.label_tier = {sql_literal(label_tier)}"
    quoted_values = ", ".join(sql_literal(v) for v in label_values)
    min_clause = f"WHERE sizes.total_nodes >= {int(min_total_nodes)}" if min_total_nodes > 0 else ""
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
        {min_clause}
        ORDER BY canon.label_value, sizes.total_nodes DESC, canon.root_created_at, canon.root_weibo_id
    """
    rows = query_dicts(config, sql)
    grouped: dict[str, list[CandidateRoot]] = defaultdict(list)
    for row in rows:
        grouped[row["label_value"]].append(
            CandidateRoot(
                root_id=row["root_weibo_id"],
                label_value=row["label_value"],
                total_nodes=int(row["total_nodes"]),
                root_created_at=row.get("root_created_at", ""),
            )
        )

    selected: list[CandidateRoot] = []
    for label in label_values:
        options = grouped.get(label, [])
        if not options:
            raise RuntimeError(f"No available roots for label={label!r}.")
        if max_per_label > 0:
            options = options[:max_per_label]
        selected.extend(options)
    return selected


def ensure_tsv_header(path: Path, fieldnames: list[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()


def append_tsv_row(path: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    ensure_tsv_header(path, fieldnames)
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writerow(row)


def read_tsv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [{str(k).strip(): (v.strip() if isinstance(v, str) else "") for k, v in row.items()} for row in reader]


def write_roots_catalog(path: Path, roots: list[CandidateRoot]) -> None:
    ensure_tsv_header(path, ROOT_FIELDS)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROOT_FIELDS, delimiter="\t")
        writer.writeheader()
        for idx, root in enumerate(roots, start=1):
            writer.writerow(
                {
                    "index": idx,
                    "root_id": root.root_id,
                    "label_value": root.label_value,
                    "total_nodes": root.total_nodes,
                    "root_created_at": root.root_created_at,
                }
            )


def load_roots_catalog(path: Path) -> list[CandidateRoot]:
    rows = read_tsv_dicts(path)
    roots: list[CandidateRoot] = []
    for row in rows:
        roots.append(
            CandidateRoot(
                root_id=row["root_id"],
                label_value=row["label_value"],
                total_nodes=int(row["total_nodes"]),
                root_created_at=row.get("root_created_at", ""),
            )
        )
    return roots


def safe_token(value: str) -> str:
    text = value.strip()
    if not text:
        return "unknown"
    return "".join(ch if (ch.isalnum() or ch in {"-", "_"}) else "_" for ch in text)


def fetch_nodes_for_root(config: DbConfig, root_id: str) -> list[NodeRecord]:
    sql = f"""
        SELECT
            id AS node_id,
            COALESCE(parent_id, '') AS parent_id,
            CASE WHEN is_root THEN 'true' ELSE 'false' END AS is_root,
            created_at::text AS created_at_text
        FROM wbprop.propagation_nodes
        WHERE root_id = {sql_literal(root_id)}
        ORDER BY created_at, id
    """
    rows = query_dicts(config, sql)
    nodes: list[NodeRecord] = []
    for row in rows:
        nodes.append(
            NodeRecord(
                node_id=row["node_id"],
                parent_id=row.get("parent_id") or None,
                created_at=parse_timestamp(row["created_at_text"]),
                is_root=(row.get("is_root", "").lower() == "true"),
            )
        )
    return nodes


def build_graph(nodes: list[NodeRecord], edge_weight_mode: str) -> tuple[list[dict[int, float]], list[NodeRecord], int]:
    node_map = {n.node_id: n for n in nodes}
    roots = [n for n in nodes if n.is_root]
    if len(roots) != 1:
        raise RuntimeError(f"invalid root count: {len(roots)}")
    root = roots[0]
    ordered = sorted(nodes, key=lambda n: (0 if n.is_root else 1, n.created_at, n.node_id))
    idx = {n.node_id: i for i, n in enumerate(ordered)}
    rel_seconds = {n.node_id: max(0.0, (n.created_at - root.created_at).total_seconds()) for n in ordered}

    adjacency: list[dict[int, float]] = [dict() for _ in range(len(ordered))]
    edge_count = 0
    for n in ordered:
        if n.is_root:
            continue
        if not n.parent_id or n.parent_id not in idx:
            continue
        p = node_map[n.parent_id]
        i, j = idx[p.node_id], idx[n.node_id]
        parent_lag = max(0.0, (n.created_at - p.created_at).total_seconds())
        w = parent_lag if edge_weight_mode == "parent_lag_seconds" else rel_seconds[n.node_id]
        adjacency[i][j] = w
        adjacency[j][i] = w
        edge_count += 1
    return adjacency, ordered, edge_count


def write_metis(path: Path, adjacency: list[dict[int, float]]) -> None:
    n = len(adjacency)
    m = sum(len(row) for row in adjacency) // 2
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{n} {m} 1\n")
        for row in adjacency:
            parts: list[str] = []
            for j in sorted(row):
                parts.append(str(j))
                parts.append(f"{float(row[j]):.12g}")
            handle.write(" ".join(parts) + "\n")


def run_prc(graph_path: Path, numpart: int, seed: int, info_suffix: str) -> tuple[list[int], Path]:
    cmd = [
        sys.executable,
        "pinchRatioClustering.py",
        "--dataInput",
        str(graph_path),
        "--fileType",
        "1",
        "--adjNodeOffset",
        "0",
        "--useSparseMatrix",
        "1",
        "--numpart",
        str(numpart),
        "--seed",
        str(seed),
        "--saveOrder",
        "0",
        "--saveLabels",
        "1",
        "--outputLabelSuffix",
        "_prc_part_",
        "--infoSuffix",
        info_suffix,
    ]
    subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    label_path = Path(f"{graph_path}_prc_part_{numpart}{info_suffix}")
    if not label_path.exists():
        raise RuntimeError(f"labels file not found: {label_path}")
    labels: list[int] = []
    with label_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                labels.append(int(text))
    return labels, label_path


def cluster_metrics(labels: list[int], adjacency: list[dict[int, float]]) -> dict[str, Any]:
    n = len(labels)
    if n == 0:
        raise RuntimeError("empty labels")
    if len(adjacency) != n:
        raise RuntimeError("labels/adacency size mismatch")

    clusters: dict[int, list[int]] = defaultdict(list)
    for i, lab in enumerate(labels):
        clusters[int(lab)].append(i)

    degree = [0.0] * n
    total_w = 0.0
    cut_w = 0.0
    for i, row in enumerate(adjacency):
        for j, w in row.items():
            if j < i:
                continue
            ww = float(w)
            total_w += ww
            if labels[i] != labels[j]:
                cut_w += ww
            degree[i] += ww
            if i != j:
                degree[j] += ww

    cut_ratio = cut_w / total_w if total_w > 0 else 0.0

    ncut = 0.0
    for idxs in clusters.values():
        idx_set = set(idxs)
        assoc = sum(degree[i] for i in idxs)
        cut = 0.0
        for i in idxs:
            for j, w in adjacency[i].items():
                if j not in idx_set:
                    cut += float(w)
        if assoc > 0:
            ncut += cut / assoc

    probs = [len(idxs) / n for idxs in clusters.values()]
    entropy = -sum(p * math.log(p + 1e-12) for p in probs)
    max_entropy = math.log(max(1, len(clusters)))
    entropy_norm = entropy / max_entropy if max_entropy > 0 else 0.0
    largest_cluster_ratio = max(probs) if probs else 0.0
    cluster_sizes = {str(k): len(v) for k, v in sorted(clusters.items(), key=lambda kv: kv[0])}

    return {
        "cluster_count": float(len(clusters)),
        "cut_ratio": float(cut_ratio),
        "ncut": float(ncut),
        "cluster_entropy_norm": float(entropy_norm),
        "largest_cluster_ratio": float(largest_cluster_ratio),
        "cluster_sizes_json": json.dumps(cluster_sizes, ensure_ascii=False, separators=(",", ":")),
    }


def summarize_by_label(rows: list[dict[str, str]], label_values: list[str]) -> dict[str, dict[str, float]]:
    metric_fields = [
        "node_count",
        "edge_count",
        "cut_ratio",
        "ncut",
        "cluster_entropy_norm",
        "largest_cluster_ratio",
    ]
    summary: dict[str, dict[str, float]] = {}
    for label in label_values:
        sub = [row for row in rows if row.get("label_value") == label]
        stats: dict[str, float] = {"n": float(len(sub))}
        if not sub:
            summary[label] = stats
            continue
        for field in metric_fields:
            vals = [float(row[field]) for row in sub]
            stats[f"{field}_mean"] = float(statistics.mean(vals))
            stats[f"{field}_median"] = float(statistics.median(vals))
        summary[label] = stats
    return summary


def load_processed_ids(results_path: Path, errors_path: Path, retry_errors: bool) -> tuple[set[str], set[str]]:
    done_ids = {row["root_id"] for row in read_tsv_dicts(results_path) if row.get("root_id")}
    err_ids = {row["root_id"] for row in read_tsv_dicts(errors_path) if row.get("root_id")}
    if retry_errors:
        err_ids = set()
    return done_ids, err_ids


def write_checkpoint(
    path: Path,
    *,
    config: dict[str, Any],
    total: int,
    done: int,
    failed: int,
    pending: int,
    last_root_id: str,
    started_at: datetime,
) -> None:
    payload = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_utc": started_at.isoformat(),
        "elapsed_seconds": time.time() - started_at.timestamp(),
        "config": config,
        "progress": {
            "total": total,
            "done": done,
            "failed": failed,
            "pending": pending,
            "last_root_id": last_root_id,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.numpart < 2:
        raise RuntimeError("--numpart must be >= 2")

    label_values = parse_label_values(args.label_values)
    db = resolve_db_config(args)
    out_dir = Path(args.output_dir)
    graph_dir = out_dir / "graphs"
    roots_catalog_path = out_dir / "roots_catalog.tsv"
    results_path = out_dir / "per_tree_prc_metrics.tsv"
    errors_path = out_dir / "errors.tsv"
    checkpoint_path = out_dir / "checkpoint.json"
    summary_path = out_dir / "study_summary.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)

    if args.resume and roots_catalog_path.exists() and not args.refresh_roots:
        roots = load_roots_catalog(roots_catalog_path)
    else:
        roots = build_roots_from_db(
            db,
            label_name=args.label_name,
            label_tier=args.label_tier,
            label_values=label_values,
            min_total_nodes=args.min_total_nodes,
            max_per_label=args.max_per_label,
        )
        write_roots_catalog(roots_catalog_path, roots)

    ensure_tsv_header(results_path, RESULT_FIELDS)
    ensure_tsv_header(errors_path, ERROR_FIELDS)

    done_ids, err_ids = load_processed_ids(results_path, errors_path, args.retry_errors)
    if not args.resume:
        done_ids = set()
        if args.retry_errors:
            err_ids = set()

    pending = [root for root in roots if root.root_id not in done_ids and root.root_id not in err_ids]
    total_count = len(roots)
    done_count = len(done_ids)
    fail_count = len(err_ids)
    started_at = datetime.now(timezone.utc)

    run_config = {
        "database": db.database,
        "host": db.host,
        "port": db.port,
        "label_name": args.label_name,
        "label_tier": args.label_tier,
        "label_values": label_values,
        "min_total_nodes": args.min_total_nodes,
        "max_per_label": args.max_per_label,
        "edge_weight_mode": args.edge_weight_mode,
        "numpart": args.numpart,
        "seed": args.seed,
        "resume": args.resume,
        "retry_errors": args.retry_errors,
        "keep_intermediate": args.keep_intermediate,
    }

    write_checkpoint(
        checkpoint_path,
        config=run_config,
        total=total_count,
        done=done_count,
        failed=fail_count,
        pending=len(pending),
        last_root_id="",
        started_at=started_at,
    )

    for idx, root in enumerate(pending, start=1):
        root_start = time.time()
        last_root = root.root_id
        try:
            nodes = fetch_nodes_for_root(db, root.root_id)
            if not nodes:
                raise RuntimeError("no nodes fetched")
            adjacency, ordered_nodes, edge_count = build_graph(nodes, args.edge_weight_mode)
            token = safe_token(root.root_id)
            graph_path = graph_dir / f"{token}.metis"
            write_metis(graph_path, adjacency)
            labels, label_path = run_prc(
                graph_path=graph_path,
                numpart=args.numpart,
                seed=args.seed,
                info_suffix=f"_{token}_study",
            )
            if len(labels) != len(ordered_nodes):
                raise RuntimeError(f"label count mismatch: labels={len(labels)} nodes={len(ordered_nodes)}")
            metrics = cluster_metrics(labels, adjacency)
            row = {
                "root_id": root.root_id,
                "label_value": root.label_value,
                "root_created_at": root.root_created_at,
                "total_nodes_from_db": root.total_nodes,
                "node_count": len(ordered_nodes),
                "edge_count": edge_count,
                "edge_weight_mode": args.edge_weight_mode,
                "numpart": args.numpart,
                "seed": args.seed,
                "runtime_seconds": f"{time.time() - root_start:.6f}",
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                **metrics,
            }
            append_tsv_row(results_path, RESULT_FIELDS, row)
            done_count += 1
            done_ids.add(root.root_id)

            if not args.keep_intermediate:
                for path in (graph_path, label_path):
                    if path.exists():
                        path.unlink()

            print(f"[{idx}/{len(pending)}] done root={root.root_id} label={root.label_value}")
        except Exception as exc:
            err_row = {
                "root_id": root.root_id,
                "label_value": root.label_value,
                "root_created_at": root.root_created_at,
                "total_nodes_from_db": root.total_nodes,
                "error_type": exc.__class__.__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(limit=20),
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            append_tsv_row(errors_path, ERROR_FIELDS, err_row)
            fail_count += 1
            err_ids.add(root.root_id)
            print(f"[{idx}/{len(pending)}] failed root={root.root_id} label={root.label_value}: {exc}")
        finally:
            remaining = total_count - done_count - fail_count
            write_checkpoint(
                checkpoint_path,
                config=run_config,
                total=total_count,
                done=done_count,
                failed=fail_count,
                pending=max(0, remaining),
                last_root_id=last_root,
                started_at=started_at,
            )

    result_rows = read_tsv_dicts(results_path)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": run_config,
        "counts": {
            "catalog_total": total_count,
            "done_total": done_count,
            "failed_total": fail_count,
            "pending_total": max(0, total_count - done_count - fail_count),
            "done_by_label": {
                label: int(sum(1 for row in result_rows if row.get("label_value") == label))
                for label in label_values
            },
        },
        "summary_by_label": summarize_by_label(result_rows, label_values),
        "files": {
            "roots_catalog_tsv": str(roots_catalog_path.resolve()),
            "per_tree_metrics_tsv": str(results_path.resolve()),
            "errors_tsv": str(errors_path.resolve()),
            "checkpoint_json": str(checkpoint_path.resolve()),
            "graph_dir": str(graph_dir.resolve()),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] roots catalog: {roots_catalog_path.resolve()}")
    print(f"[OK] metrics: {results_path.resolve()}")
    print(f"[OK] errors: {errors_path.resolve()}")
    print(f"[OK] checkpoint: {checkpoint_path.resolve()}")
    print(f"[OK] summary: {summary_path.resolve()}")
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
