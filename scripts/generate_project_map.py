#!/usr/bin/env python3
"""Generate a compact, maintainable project map with low redundancy."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "PROJECT_STRUCTURE_WITH_DEFINITIONS.md"
MAX_BLOCKS_PER_FILE = 6

CORE_PREFIXES = (
    "backend/",
    "frontend/",
    "docs/",
    "scripts/",
    ".github/workflows/",
    ".codex/",
)
ROOT_FILES = {
    "README.md",
    "AGENTS.md",
    "SPRINT.md",
    "BACKLOG.md",
    "CHANGELOG.md",
    "docker-compose.yml",
    ".env.example",
    "LICENSE",
}
EXCLUDE_PARTS = {"node_modules", ".venv", ".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea"}
EXCLUDE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".pyc", ".tsbuildinfo"}


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    files: list[Path] = []
    for line in out.splitlines():
        p = Path(line.strip())
        s = p.as_posix()
        if not s:
            continue
        if any(part in EXCLUDE_PARTS for part in p.parts):
            continue
        if p.suffix.lower() in EXCLUDE_EXT:
            continue
        in_core = any(s.startswith(prefix) for prefix in CORE_PREFIXES)
        in_root = s in ROOT_FILES
        if not (in_core or in_root):
            continue
        if (ROOT / p).is_file():
            files.append(p)
    return sorted(files)


def dir_def(path: Path) -> str:
    s = path.as_posix()
    if s == ".":
        return "项目根目录（Project Root），统一组织前后端代码、规范与工程自动化配置。"
    if s.startswith("backend"):
        return "后端目录（Backend），实现 FastAPI 服务、分层业务能力与测试保障。"
    if s.startswith("frontend"):
        return "前端目录（Frontend），实现 Next.js 页面、组件体系与构建配置。"
    if s.startswith("docs"):
        return "规范目录（Docs），定义架构约束、流程规则与团队协作标准。"
    if s.startswith("scripts"):
        return "脚本目录（Scripts），提供项目自动化生成、检查与维护命令。"
    if s.startswith(".github"):
        return "流水线目录（Workflows），定义 CI 校验任务与触发策略。"
    if s.startswith(".codex"):
        return "智能体运行目录（Codex Runtime），定义本地 Hook 与自动化触发规则。"
    return "模块目录（Module Directory），用于按职责归类相关实现。"


def file_def(path: Path) -> str:
    n = path.name.lower()
    if n == "agents.md":
        return "全局智能体规约（Agent Contract），约束执行流程、质量门禁与输出格式。"
    if n == "readme.md":
        return "项目入口文档（Entry Doc），说明目标、结构、启动方式与贡献流程。"
    if n == "project_structure_with_definitions.md":
        return "目录树总览（Project Map），用于全局理解项目结构与关键文本块语义。"
    if n.endswith(".py"):
        return "Python 模块（Python Module），承载后端逻辑、脚本任务或测试用例。"
    if n.endswith((".ts", ".tsx")):
        return "TypeScript 模块（TypeScript Module），承载页面、组件、状态或类型逻辑。"
    if n.endswith(".md"):
        return "说明文档（Documentation File），用于沉淀规则、设计与执行说明。"
    if n.endswith((".yml", ".yaml")):
        return "YAML 配置（YAML Config），用于容器编排或 CI 流程定义。"
    if n.endswith(".toml"):
        return "TOML 配置（TOML Config），用于依赖与工具链参数管理。"
    if n.endswith(".lock"):
        return "锁文件（Lockfile），固定依赖版本以保证环境可复现。"
    return "工程文件（Project Artifact），用于支撑模块运行、配置或质量保障。"


def split_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip() == "":
            if buf:
                blocks.append(buf)
                buf = []
        else:
            buf.append(line)
    if buf:
        blocks.append(buf)
    return blocks


def classify(block: list[str]) -> tuple[str, str]:
    first = (block[0].strip() if block else "").strip()
    if first.startswith("#"):
        title = re.sub(r"^#+\s*", "", first).strip() or "章节"
        return ("heading", f"该段定义“{title}”主题（Topic），用于组织本文件的核心语义边界。")
    if first.startswith(("import ", "from ")):
        return ("imports", "该段声明依赖导入（Imports），为后续实现提供模块能力与类型引用。")
    if first.startswith("def "):
        m = re.match(r"def\s+([A-Za-z0-9_]+)\s*\(", first)
        fn = m.group(1) if m else "函数"
        return ("function", f"该段定义函数 `{fn}`（Function），封装一个可复用的处理步骤。")
    if first.startswith("class "):
        m = re.match(r"class\s+([A-Za-z0-9_]+)", first)
        cn = m.group(1) if m else "类"
        return ("class", f"该段定义类 `{cn}`（Class），用于组织状态与相关行为。")
    if first.startswith(("describe(", "it(", "test(")):
        return ("test", "该段定义测试场景（Test Case），用于验证行为正确性与边界条件。")
    if first.startswith(("services:", "version:")):
        return ("compose", "该段定义服务编排（Service Compose）配置，描述组件关系与运行参数。")
    if first.startswith("export "):
        return ("export", "该段声明导出（Exports）接口，供其他模块复用能力。")
    if first.startswith("[") and len(first) < 90:
        return ("config", "该段定义配置节（Config Section），用于组织工具或项目参数。")
    snippet = first[:42].replace("`", "'")
    return ("content", f"该段围绕“{snippet}”展开（Content Block），承载一组相关实现或说明。")


def text_file(path: Path) -> bool:
    b = path.read_bytes()
    if b"\x00" in b:
        return False
    try:
        b.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def build_tree(files: list[Path]) -> dict[Path, dict[str, list[Path]]]:
    dirs = {Path(".")}
    for f in files:
        cur = Path(".")
        for part in f.parts[:-1]:
            cur = cur / part
            dirs.add(cur)
    tree = {d: {"dirs": [], "files": []} for d in dirs}
    for d in sorted(dirs):
        if d == Path("."):
            continue
        parent = d.parent if d.parent != Path("") else Path(".")
        tree[parent]["dirs"].append(d)
    for f in files:
        parent = f.parent if f.parent != Path("") else Path(".")
        tree[parent]["files"].append(f)
    for d in tree:
        tree[d]["dirs"].sort()
        tree[d]["files"].sort()
    return tree


def render_blocks(abs_file: Path, level: int, out: list[str]) -> None:
    indent = "  " * level
    if not text_file(abs_file):
        out.append(f"{indent}- [BLOCK 1] 该文件为非文本资产（Non-text Artifact），使用单块占位说明。")
        return
    blocks = split_blocks(abs_file.read_text(encoding="utf-8", errors="ignore"))
    if not blocks:
        out.append(f"{indent}- [BLOCK 1] 该文件为占位文本（Placeholder），当前无可解析内容。")
        return

    reduced: list[str] = []
    prev_kind = None
    collapsed = 0
    for block in blocks:
        kind, desc = classify(block)
        if kind == prev_kind and kind in {"content", "config", "imports"}:
            collapsed += 1
            continue
        reduced.append(desc)
        prev_kind = kind

    shown = reduced[:MAX_BLOCKS_PER_FILE]
    for i, d in enumerate(shown, 1):
        out.append(f"{indent}- [BLOCK {i}] {d}")

    hidden = max(0, len(reduced) - len(shown)) + collapsed
    if hidden > 0:
        out.append(f"{indent}- [BLOCK +] 已合并/省略 {hidden} 个相似或次要段落块（Merged/Omitted Blocks）以保持全局可读性。")


def render() -> str:
    files = tracked_files()
    tree = build_tree(files)
    out: list[str] = []
    out.append("# 项目全局目录树与节点定义（精简版）")
    out.append("")
    out.append("> 说明：本文件由 `scripts/generate_project_map.py` 自动生成；采用核心范围（core scope）与去冗余策略，确保可读、可维护、可快速同步。"
    )
    out.append("")

    def emit_dir(d: Path, level: int) -> None:
        ind = "  " * level
        label = "." if d == Path(".") else d.as_posix()
        out.append(f"{ind}- [DIR] `{label}`：{dir_def(d)}")
        for sd in tree[d]["dirs"]:
            emit_dir(sd, level + 1)
        for f in tree[d]["files"]:
            find = "  " * (level + 1)
            out.append(f"{find}- [FILE] `{f.as_posix()}`：{file_def(f)}")
            render_blocks(ROOT / f, level + 2, out)

    emit_dir(Path("."), 0)
    out.append("")
    return "\n".join(out)


def main() -> None:
    OUTPUT_PATH.write_text(render(), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
