from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "test"
ARTIFACT_DIR = TEST_DIR / "legacy_prc_outputs"
BUILD_DIR = TEST_DIR / "legacy_prc_build"
LEGACY_SRC = ROOT / "prc_v0.1.05 (1)" / "prc_v0.1.05_d2013_04_30"
CURRENT_REPRO = ROOT / "experiments" / "reproduce_paper_fig_ari.py"
CURRENT_DIAG = ARTIFACT_DIR / "current_pyprc_paper_fig_diagnostics.json"
CURRENT_PLOT = ARTIFACT_DIR / "current_pyprc_paper_fig.png"
SUMMARY_JSON = ARTIFACT_DIR / "legacy_repro_summary.json"
SUMMARY_MD = ARTIFACT_DIR / "legacy_repro_summary.md"
CONFIG_LOG = ARTIFACT_DIR / "legacy_cmake_configure.log"
BUILD_LOG = ARTIFACT_DIR / "legacy_cmake_build.log"


def run_and_log(cmd: list[str], cwd: Path, log_path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    merged = []
    if completed.stdout:
        merged.append("=== STDOUT ===\n" + completed.stdout.rstrip())
    if completed.stderr:
        merged.append("=== STDERR ===\n" + completed.stderr.rstrip())
    log_path.write_text("\n\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")
    tail_lines = (completed.stdout + "\n" + completed.stderr).strip().splitlines()[-20:]
    return {
        "cmd": cmd,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "log_file": str(log_path),
        "tail": tail_lines,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def top_deltas(section: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    paper_delta = section.get("paper_delta", {})
    ordered = sorted(
        paper_delta.items(),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    return [
        {
            "method": name,
            "delta": float(delta),
            "result": float(section["results"][name]),
        }
        for name, delta in ordered[:limit]
    ]


def write_markdown(summary: dict[str, Any]) -> None:
    blockers = summary["legacy_attempt"]["blockers"]
    iris_top = summary["current_pyprc"]["iris_top_deltas"]
    vote_top = summary["current_pyprc"]["vote_top_deltas"]

    lines = [
        "# Legacy PRC Reproduction Attempt",
        "",
        "## 结论",
        "",
        f"- 判定：{summary['verdict']}",
        f"- 旧版源码路径：`{summary['legacy_attempt']['source_dir']}`",
        f"- 旧版 CLI 构建成功：`{summary['legacy_attempt']['build_succeeded']}`",
        "",
        "## 旧版源码阻塞点",
        "",
    ]
    if blockers:
        lines.extend(f"- {item}" for item in blockers)
    else:
        lines.append("- 未发现阻塞点。")

    lines.extend(
        [
            "",
            "## 当前 Python 版与论文的主要偏差",
            "",
            "### Iris",
            "",
        ]
    )
    lines.extend(
        f"- {item['method']}: result={item['result']:.6f}, delta={item['delta']:+.6f}" for item in iris_top
    )
    lines.extend(
        [
            "",
            "### Vote",
            "",
        ]
    )
    lines.extend(
        f"- {item['method']}: result={item['result']:.6f}, delta={item['delta']:+.6f}" for item in vote_top
    )

    lines.extend(
        [
            "",
            "## 产物",
            "",
            f"- 旧版 CMake 配置日志：`{CONFIG_LOG}`",
            f"- 旧版 CMake 编译日志：`{BUILD_LOG}`",
            f"- 当前 Python 版诊断：`{CURRENT_DIAG}`",
            f"- 当前 Python 版图像：`{CURRENT_PLOT}`",
            f"- 结构化摘要：`{SUMMARY_JSON}`",
        ]
    )

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    legacy_testdata_dir = LEGACY_SRC.parent / "testData"
    legacy_pythonext_readme = LEGACY_SRC / "pythonExt" / "readme.rst"
    pythonext_text = legacy_pythonext_readme.read_text(encoding="utf-8", errors="replace")

    configure_result = run_and_log(
        ["cmake", "-G", "MinGW Makefiles", str(LEGACY_SRC)],
        cwd=BUILD_DIR,
        log_path=CONFIG_LOG,
    )
    build_result = run_and_log(
        ["cmake", "--build", ".", "--target", "pinchRatioClustering", "genSimMatrix", "--", "-j4"],
        cwd=BUILD_DIR,
        log_path=BUILD_LOG,
    )

    legacy_exe = BUILD_DIR / "prc" / "pinchRatioClustering.exe"
    blockers: list[str] = []
    if "does not build with python3" in pythonext_text.lower():
        blockers.append("旧版 pythonExt 自带说明明确写明当前版本不支持 Python 3 构建。")
    if not legacy_testdata_dir.exists():
        blockers.append("旧版 tests/test_iris.sh 依赖的 ../../testData 目录未随源码一起提供。")
    build_log_text = BUILD_LOG.read_text(encoding="utf-8", errors="replace")
    if "Eigen/Core: No such file or directory" in build_log_text:
        blockers.append("旧版 C++ CLI 构建缺少 Eigen 头文件，当前提供的源码包未包含该依赖。")
    if build_result["returncode"] != 0 and not blockers:
        blockers.append("旧版 CLI 构建失败，详见 legacy_cmake_build.log。")

    current_run_result = run_and_log(
        [
            sys.executable,
            str(CURRENT_REPRO),
            "--iris-data",
            str(ROOT / "tests" / "iris_all.txt"),
            "--vote-data",
            str(ROOT / "tests" / "vote_all.txt"),
            "--output",
            str(CURRENT_PLOT),
            "--diagnostics",
            str(CURRENT_DIAG),
        ],
        cwd=ROOT,
        log_path=ARTIFACT_DIR / "current_pyprc_run.log",
    )

    current_diag = load_json(CURRENT_DIAG)
    summary = {
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "executable": sys.executable,
        },
        "legacy_attempt": {
            "source_dir": str(LEGACY_SRC),
            "pythonext_mentions_python3_incompatible": "does not build with python3" in pythonext_text.lower(),
            "legacy_testdata_present": legacy_testdata_dir.exists(),
            "configure": configure_result,
            "build": build_result,
            "build_succeeded": build_result["returncode"] == 0 and legacy_exe.exists(),
            "blockers": blockers,
        },
        "current_pyprc": {
            "run": current_run_result,
            "diagnostics_file": str(CURRENT_DIAG),
            "figure_file": str(CURRENT_PLOT),
            "iris_top_deltas": top_deltas(current_diag["iris"]),
            "vote_top_deltas": top_deltas(current_diag["vote"]),
        },
        "verdict": (
            "不能在当前工作区里用提供的旧版源码完整复现论文图；"
            "旧版 Python 扩展不支持 Python 3，旧版 C++ CLI 也因缺少 Eigen 依赖而无法完成构建。"
            if blockers
            else "旧版源码构建已通过，可以继续补 CLI 驱动脚本做完整复现实验。"
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(summary)

    print(summary["verdict"])
    print(f"[OK] Summary JSON: {SUMMARY_JSON}")
    print(f"[OK] Summary Markdown: {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
