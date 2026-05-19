"""从传播数据库读取完整传播树，构建加权图并运行 PRC 聚类实验。"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CODE_DIR = Path(r"F:\谣言传播\code")
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "graph_clustering" / "propagation_tree_graph"
DEFAULT_PSQL_PATH = Path(r"D:\PostgreSQL\bin\psql.exe")


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: str
    database: str
    user: str
    password: str
    psql_path: Path


@dataclass(frozen=True)
class NodeRecord:
    node_id: str
    parent_id: str | None
    created_at: datetime
    is_root: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load one complete propagation tree from PostgreSQL, initialize a weighted graph "
            "using relative time as edge weight, and run PRC clustering."
        )
    )
    parser.add_argument(
        "--source-code-dir",
        default=str(DEFAULT_SOURCE_CODE_DIR),
        help="包含数据库配置文件（.env/.env.local/.env.example）的源码目录。",
    )
    parser.add_argument("--database", default="", help="可选：覆盖数据库名。")
    parser.add_argument("--host", default="", help="可选：覆盖 PGHOST。")
    parser.add_argument("--port", default="", help="可选：覆盖 PGPORT。")
    parser.add_argument("--user", default="", help="可选：覆盖 PGUSER。")
    parser.add_argument("--password", default="", help="可选：覆盖 PGPASSWORD。")
    parser.add_argument("--psql-path", default="", help="可选：覆盖 psql 可执行文件路径。")
    parser.add_argument("--root-id", default="", help="指定根微博 ID；为空时自动选择规模最大的根。")
    parser.add_argument(
        "--edge-weight-mode",
        choices=["relative_root_seconds", "parent_lag_seconds"],
        default="relative_root_seconds",
        help="边权重定义：相对根时间 or 相对父节点时间。",
    )
    parser.add_argument(
        "--min-edge-weight",
        type=float,
        default=0.0,
        help="边权重下限（用于避免 0 权重时可设为极小正数）。",
    )
    parser.add_argument("--numpart", type=int, default=2, help="PRC 聚类簇数（>=2）。")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="输出目录，默认 outputs/experiments/propagation_tree_graph。",
    )
    parser.add_argument("--skip-prc", action="store_true", help="仅导出图与摘要，不执行 PRC。")
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

    host = pick(args.host, "PGHOST", "localhost")
    port = pick(args.port, "PGPORT", "5432")
    database = pick(args.database, "PGDATABASE", "aigc_propagation")
    user = pick(args.user, "PGUSER", "postgres")
    password = pick(args.password, "PGPASSWORD", "")
    psql_path_text = pick(args.psql_path, "PSQL_PATH", str(DEFAULT_PSQL_PATH))
    psql_path = Path(psql_path_text)

    if not password:
        raise RuntimeError(
            "未解析到 PGPASSWORD。请在命令行 --password 提供，或在 source-code-dir 下的 .env/.env.local 配置。"
        )
    if args.numpart < 2:
        raise RuntimeError("--numpart 必须 >= 2。")
    if not psql_path.exists():
        raise RuntimeError(f"psql 不存在：{psql_path}")
    return DbConfig(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        psql_path=psql_path,
    )


def run_psql_sql(config: DbConfig, sql: str) -> subprocess.CompletedProcess[str]:
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
    return subprocess.run(
        args,
        input=sql,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
        env=env,
    )


def query_dicts(config: DbConfig, sql: str) -> list[dict[str, str]]:
    statement = sql.strip().rstrip(";")
    copy_sql = (
        "COPY (\n"
        f"{statement}\n"
        ") TO STDOUT WITH (FORMAT CSV, HEADER TRUE, DELIMITER E'\\t');\n"
    )
    completed = run_psql_sql(config, copy_sql)
    text = completed.stdout
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


def fetch_root_summary(config: DbConfig, root_id: str = "") -> dict[str, Any]:
    if root_id:
        sql = f"""
            SELECT
                root.id AS root_id,
                root.created_at::text AS root_created_at,
                COUNT(nodes.id)::text AS total_nodes
            FROM wbprop.propagation_nodes root
            JOIN wbprop.propagation_nodes nodes
              ON nodes.root_id = root.id
            WHERE root.is_root = TRUE
              AND root.id = {sql_literal(root_id)}
            GROUP BY root.id, root.created_at
        """
        rows = query_dicts(config, sql)
        if not rows:
            raise RuntimeError(f"未找到 root_id={root_id!r} 对应的传播树。")
        row = rows[0]
        return {
            "root_id": row["root_id"],
            "root_created_at": row["root_created_at"],
            "total_nodes": int(row["total_nodes"]),
        }

    sql = """
        SELECT
            root.id AS root_id,
            root.created_at::text AS root_created_at,
            COUNT(nodes.id)::text AS total_nodes
        FROM wbprop.propagation_nodes root
        JOIN wbprop.propagation_nodes nodes
          ON nodes.root_id = root.id
        WHERE root.is_root = TRUE
        GROUP BY root.id, root.created_at
        ORDER BY COUNT(nodes.id) DESC, root.id
        LIMIT 1
    """
    rows = query_dicts(config, sql)
    if not rows:
        raise RuntimeError("数据库中没有可用的根节点。")
    row = rows[0]
    return {
        "root_id": row["root_id"],
        "root_created_at": row["root_created_at"],
        "total_nodes": int(row["total_nodes"]),
    }


def fetch_tree_nodes(config: DbConfig, root_id: str) -> list[NodeRecord]:
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
                parent_id=(row.get("parent_id") or None),
                is_root=(row.get("is_root", "").lower() == "true"),
                created_at=parse_timestamp(row["created_at_text"]),
            )
        )
    return nodes


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def detect_cycle(node_map: dict[str, NodeRecord]) -> bool:
    children: dict[str, list[str]] = defaultdict(list)
    for node in node_map.values():
        if node.parent_id and node.parent_id in node_map:
            children[node.parent_id].append(node.node_id)

    color: dict[str, int] = {}

    def dfs(node_id: str) -> bool:
        color[node_id] = 1
        for child_id in children.get(node_id, []):
            child_color = color.get(child_id, 0)
            if child_color == 1:
                return True
            if child_color == 0 and dfs(child_id):
                return True
        color[node_id] = 2
        return False

    for node_id in node_map:
        if color.get(node_id, 0) == 0 and dfs(node_id):
            return True
    return False


def build_depths(node_map: dict[str, NodeRecord]) -> dict[str, int]:
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


def build_graph_artifacts(
    *,
    root_summary: dict[str, Any],
    nodes: list[NodeRecord],
    edge_weight_mode: str,
    min_edge_weight: float,
) -> dict[str, Any]:
    node_map = {node.node_id: node for node in nodes}
    root_nodes = [node for node in nodes if node.is_root]
    if len(root_nodes) != 1:
        raise RuntimeError(f"期望且仅期望 1 个根节点，实际为 {len(root_nodes)}。")
    root_node = root_nodes[0]
    if root_node.node_id != str(root_summary["root_id"]):
        raise RuntimeError(
            f"根节点 ID 不一致：summary={root_summary['root_id']}，nodes={root_node.node_id}"
        )

    missing_parent_nodes: list[str] = []
    valid_non_root = 0
    for node in nodes:
        if node.is_root:
            continue
        if not node.parent_id or node.parent_id not in node_map:
            missing_parent_nodes.append(node.node_id)
            continue
        valid_non_root += 1

    has_cycle = detect_cycle(node_map)
    depths = build_depths(node_map)

    ordered_nodes = sorted(
        nodes,
        key=lambda n: (
            0 if n.is_root else 1,
            n.created_at,
            n.node_id,
        ),
    )
    index_by_id = {node.node_id: idx for idx, node in enumerate(ordered_nodes)}

    root_time = root_node.created_at
    relative_seconds_by_id: dict[str, float] = {}
    for node in ordered_nodes:
        relative_seconds_by_id[node.node_id] = max(
            0.0,
            float((node.created_at - root_time).total_seconds()),
        )

    adjacency: list[dict[int, float]] = [dict() for _ in range(len(ordered_nodes))]
    edges: list[dict[str, Any]] = []
    weights: list[float] = []
    orphan_edge_count = 0

    for node in ordered_nodes:
        if node.is_root:
            continue
        if not node.parent_id or node.parent_id not in index_by_id:
            orphan_edge_count += 1
            continue
        parent = node_map[node.parent_id]
        parent_index = index_by_id[parent.node_id]
        child_index = index_by_id[node.node_id]

        relative_root_seconds = float(relative_seconds_by_id[node.node_id])
        parent_lag_seconds = max(0.0, float((node.created_at - parent.created_at).total_seconds()))
        if edge_weight_mode == "parent_lag_seconds":
            weight = parent_lag_seconds
        else:
            weight = relative_root_seconds
        weight = max(float(min_edge_weight), float(weight))

        adjacency[parent_index][child_index] = weight
        adjacency[child_index][parent_index] = weight
        weights.append(weight)
        edges.append(
            {
                "parent_id": parent.node_id,
                "child_id": node.node_id,
                "parent_index": parent_index,
                "child_index": child_index,
                "relative_root_seconds": relative_root_seconds,
                "parent_lag_seconds": parent_lag_seconds,
                "edge_weight": weight,
            }
        )

    undirected_edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    if undirected_edge_count != len(edges):
        raise RuntimeError("无向边计数与边列表长度不一致。")

    max_depth = max(depths.values(), default=0)
    tree_validation = {
        "is_single_root": len(root_nodes) == 1,
        "root_id": root_node.node_id,
        "node_count": len(ordered_nodes),
        "non_root_count": len(ordered_nodes) - 1,
        "valid_non_root_with_parent": valid_non_root,
        "missing_parent_count": len(missing_parent_nodes),
        "missing_parent_sample": missing_parent_nodes[:10],
        "has_cycle": has_cycle,
        "orphan_edge_count": orphan_edge_count,
        "edge_count": undirected_edge_count,
        "expected_tree_edge_count": max(len(ordered_nodes) - 1, 0),
        "tree_edge_count_matches_n_minus_1": (undirected_edge_count == max(len(ordered_nodes) - 1, 0)),
        "max_depth": max_depth,
    }

    return {
        "ordered_nodes": ordered_nodes,
        "index_by_id": index_by_id,
        "relative_seconds_by_id": relative_seconds_by_id,
        "depths": depths,
        "adjacency": adjacency,
        "edges": edges,
        "weights": weights,
        "validation": tree_validation,
    }


def format_weight(value: float) -> str:
    text = f"{value:.12g}"
    return text if text else "0"


def safe_token(value: str) -> str:
    text = value.strip()
    if not text:
        return "unknown"
    return "".join(ch if (ch.isalnum() or ch in {"-", "_"}) else "_" for ch in text)


def write_weighted_metis_graph(path: Path, adjacency: list[dict[int, float]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_nodes = len(adjacency)
    edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{n_nodes} {edge_count} 1\n")
        for neighbors in adjacency:
            parts: list[str] = []
            for neighbor_idx in sorted(neighbors):
                parts.append(str(neighbor_idx))
                parts.append(format_weight(neighbors[neighbor_idx]))
            handle.write(" ".join(parts) + "\n")
    return edge_count


def write_nodes_tsv(
    *,
    path: Path,
    ordered_nodes: list[NodeRecord],
    index_by_id: dict[str, int],
    relative_seconds_by_id: dict[str, float],
    depths: dict[str, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "index",
                "node_id",
                "parent_id",
                "is_root",
                "depth",
                "created_at",
                "relative_root_seconds",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for node in ordered_nodes:
            writer.writerow(
                {
                    "index": index_by_id[node.node_id],
                    "node_id": node.node_id,
                    "parent_id": node.parent_id or "",
                    "is_root": "true" if node.is_root else "false",
                    "depth": depths.get(node.node_id, 0),
                    "created_at": node.created_at.isoformat(),
                    "relative_root_seconds": format_weight(relative_seconds_by_id.get(node.node_id, 0.0)),
                }
            )


def write_edges_tsv(path: Path, edges: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "parent_id",
                "child_id",
                "parent_index",
                "child_index",
                "relative_root_seconds",
                "parent_lag_seconds",
                "edge_weight",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for edge in edges:
            writer.writerow(
                {
                    "parent_id": edge["parent_id"],
                    "child_id": edge["child_id"],
                    "parent_index": edge["parent_index"],
                    "child_index": edge["child_index"],
                    "relative_root_seconds": format_weight(float(edge["relative_root_seconds"])),
                    "parent_lag_seconds": format_weight(float(edge["parent_lag_seconds"])),
                    "edge_weight": format_weight(float(edge["edge_weight"])),
                }
            )


def run_prc(graph_path: Path, num_partitions: int, info_suffix: str) -> dict[str, Any]:
    command = [
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
        str(num_partitions),
        "--saveOrder",
        "0",
        "--saveLabels",
        "1",
        "--outputLabelSuffix",
        "_prc_part_",
        "--infoSuffix",
        info_suffix,
    ]
    completed = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    labels_path = Path(f"{graph_path}_prc_part_{num_partitions}{info_suffix}")
    if not labels_path.exists():
        raise RuntimeError(f"PRC 已执行但未生成标签文件：{labels_path}")

    labels: list[int] = []
    with labels_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            labels.append(int(text))

    cluster_sizes = Counter(labels)
    return {
        "command": command,
        "labels_path": str(labels_path.resolve()),
        "cluster_count": len(cluster_sizes),
        "cluster_sizes": {str(k): int(v) for k, v in sorted(cluster_sizes.items())},
        "label_count": len(labels),
        "stdout_tail": completed.stdout.splitlines()[-20:],
        "stderr_tail": completed.stderr.splitlines()[-20:],
    }


def mask_secret(secret: str) -> str:
    if not secret:
        return ""
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"{secret[:2]}***{secret[-2:]}"


def main() -> int:
    args = parse_args()
    config = resolve_db_config(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    root_summary = fetch_root_summary(config, root_id=args.root_id.strip())
    nodes = fetch_tree_nodes(config, root_summary["root_id"])
    if not nodes:
        raise RuntimeError("未读取到传播树节点。")

    graph_artifacts = build_graph_artifacts(
        root_summary=root_summary,
        nodes=nodes,
        edge_weight_mode=args.edge_weight_mode,
        min_edge_weight=float(args.min_edge_weight),
    )
    root_token = safe_token(root_summary["root_id"])
    graph_path = output_dir / f"{root_token}__weighted_tree.metis"
    nodes_path = output_dir / f"{root_token}__nodes.tsv"
    edges_path = output_dir / f"{root_token}__edges.tsv"

    edge_count = write_weighted_metis_graph(graph_path, graph_artifacts["adjacency"])
    write_nodes_tsv(
        path=nodes_path,
        ordered_nodes=graph_artifacts["ordered_nodes"],
        index_by_id=graph_artifacts["index_by_id"],
        relative_seconds_by_id=graph_artifacts["relative_seconds_by_id"],
        depths=graph_artifacts["depths"],
    )
    write_edges_tsv(edges_path, graph_artifacts["edges"])

    weights = graph_artifacts["weights"]
    summary: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_code_dir": str(Path(args.source_code_dir).resolve()),
        "db_config": {
            "host": config.host,
            "port": config.port,
            "database": config.database,
            "user": config.user,
            "password_masked": mask_secret(config.password),
            "psql_path": str(config.psql_path),
        },
        "tree": {
            "root_id": root_summary["root_id"],
            "root_created_at": root_summary["root_created_at"],
            "total_nodes_from_summary": int(root_summary["total_nodes"]),
            **graph_artifacts["validation"],
        },
        "graph": {
            "graph_file": str(graph_path.resolve()),
            "nodes_file": str(nodes_path.resolve()),
            "edges_file": str(edges_path.resolve()),
            "edge_weight_mode": args.edge_weight_mode,
            "min_edge_weight": float(args.min_edge_weight),
            "node_count": len(graph_artifacts["ordered_nodes"]),
            "edge_count": int(edge_count),
            "edge_weight_min": float(min(weights)) if weights else 0.0,
            "edge_weight_max": float(max(weights)) if weights else 0.0,
            "edge_weight_mean": float(sum(weights) / len(weights)) if weights else 0.0,
        },
        "clustering": {
            "skipped": bool(args.skip_prc),
        },
    }

    if not args.skip_prc:
        info_suffix = f"_{root_token}_rtree"
        clustering = run_prc(graph_path, args.numpart, info_suffix)
        summary["clustering"] = {
            "skipped": False,
            **clustering,
            "numpart": int(args.numpart),
        }
        if clustering["label_count"] != len(graph_artifacts["ordered_nodes"]):
            raise RuntimeError(
                f"聚类标签数与节点数不一致：labels={clustering['label_count']} "
                f"nodes={len(graph_artifacts['ordered_nodes'])}"
            )

    summary_path = output_dir / f"{root_token}__experiment_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] root_id={root_summary['root_id']}")
    print(f"[OK] nodes={summary['graph']['node_count']} edges={summary['graph']['edge_count']}")
    print(f"[OK] graph={graph_path.resolve()}")
    if not args.skip_prc:
        print(f"[OK] labels={summary['clustering']['labels_path']}")
    print(f"[OK] summary={summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
