#!/usr/bin/env python3
"""
脚手架验收脚本

验证 /setup Skill 生成的项目是否满足所有规范要求。
分三个阶段：静态检查 → 构建检查 → 运行时检查。

用法：
    uv run scripts/verify_setup.py
    uv run scripts/verify_setup.py --skip-runtime  # 跳过运行时检查
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Literal

# 颜色输出
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

CheckResult = Literal["pass", "fail", "skip"]


class Checker:
    def __init__(self, root: Path):
        self.root = root
        self.backend = root / "backend"
        self.frontend = root / "frontend"
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def check(self, name: str, fn) -> CheckResult:
        """执行单个检查项"""
        try:
            result = fn()
            if result is True:
                print(f"{GREEN}✓{RESET} {name}")
                self.passed += 1
                return "pass"
            elif result is False:
                print(f"{RED}✗{RESET} {name}")
                self.failed += 1
                return "fail"
            else:  # None or "skip"
                print(f"{YELLOW}⚠{RESET} {name} (SKIP: {result})")
                self.skipped += 1
                return "skip"
        except Exception as e:
            print(f"{RED}✗{RESET} {name} - {e}")
            self.failed += 1
            return "fail"

    def file_exists(self, path: Path) -> bool:
        return path.exists()

    def file_contains(self, path: Path, keyword: str) -> bool:
        if not path.exists():
            return False
        return keyword in path.read_text()

    def file_not_contains(self, path: Path, keyword: str) -> bool:
        if not path.exists():
            return False
        return keyword not in path.read_text()

    def run_cmd(self, cmd: list[str], cwd: Path | None = None) -> bool:
        """运行命令，返回是否成功"""
        result = subprocess.run(
            cmd,
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def phase1_static(self):
        """阶段 1：静态检查（无需运行服务）"""
        print(f"\n{BLUE}=== 阶段 1：静态检查 ==={RESET}\n")

        # 后端文件存在性
        self.check("backend/pyproject.toml 存在", lambda: self.file_exists(self.backend / "pyproject.toml"))
        self.check("backend/uv.lock 存在", lambda: self.file_exists(self.backend / "uv.lock"))
        self.check("backend/alembic/script.py.mako 存在", lambda: self.file_exists(self.backend / "alembic" / "script.py.mako"))
        self.check("backend/app/core/config.py 存在", lambda: self.file_exists(self.backend / "app" / "core" / "config.py"))
        self.check("backend/app/core/logging.py 存在", lambda: self.file_exists(self.backend / "app" / "core" / "logging.py"))
        self.check("backend/app/core/security.py 存在", lambda: self.file_exists(self.backend / "app" / "core" / "security.py"))
        self.check("backend/app/core/observability.py 存在", lambda: self.file_exists(self.backend / "app" / "core" / "observability.py"))
        self.check("backend/tests/conftest.py 存在", lambda: self.file_exists(self.backend / "tests" / "conftest.py"))

        # 后端关键内容检查
        self.check(
            "config.py 使用 pydantic-settings",
            lambda: self.file_contains(self.backend / "app" / "core" / "config.py", "pydantic_settings"),
        )
        self.check(
            "config.py 无 os.getenv",
            lambda: self.file_not_contains(self.backend / "app" / "core" / "config.py", "os.getenv"),
        )
        self.check(
            "logging.py 使用 structlog",
            lambda: self.file_contains(self.backend / "app" / "core" / "logging.py", "structlog"),
        )
        self.check(
            "logging.py 无 loguru",
            lambda: self.file_not_contains(self.backend / "app" / "core" / "logging.py", "loguru"),
        )
        self.check(
            "security.py 使用 Argon2id",
            lambda: self.file_contains(self.backend / "app" / "core" / "security.py", "argon2"),
        )
        self.check(
            "observability.py 无裸 any",
            lambda: self.file_not_contains(self.backend / "app" / "core" / "observability.py", "app: any"),
        )
        self.check(
            "script.py.mako 包含 upgrade/downgrade",
            lambda: self.file_contains(self.backend / "alembic" / "script.py.mako", "def upgrade")
            and self.file_contains(self.backend / "alembic" / "script.py.mako", "def downgrade"),
        )
        self.check(
            "conftest.py 使用 httpx.AsyncClient",
            lambda: self.file_contains(self.backend / "tests" / "conftest.py", "httpx")
            and self.file_contains(self.backend / "tests" / "conftest.py", "AsyncClient"),
        )

        # 前端文件存在性
        self.check("frontend/package.json 存在", lambda: self.file_exists(self.frontend / "package.json"))
        self.check("frontend/pnpm-lock.yaml 存在", lambda: self.file_exists(self.frontend / "pnpm-lock.yaml"))
        self.check("frontend/tsconfig.json 存在", lambda: self.file_exists(self.frontend / "tsconfig.json"))
        self.check("frontend/src/lib/providers.tsx 存在", lambda: self.file_exists(self.frontend / "src" / "lib" / "providers.tsx"))
        self.check("frontend/src/app/layout.tsx 存在", lambda: self.file_exists(self.frontend / "src" / "app" / "layout.tsx"))
        self.check("frontend/src/app/globals.css 存在", lambda: self.file_exists(self.frontend / "src" / "app" / "globals.css"))

        # 前端关键内容检查
        tsconfig = self.frontend / "tsconfig.json"
        if tsconfig.exists():
            self.check(
                "tsconfig.json 开启 strict",
                lambda: "strict" in tsconfig.read_text() and '"strict": true' in tsconfig.read_text(),
            )

        self.check(
            "providers.tsx 包含 QueryClientProvider",
            lambda: self.file_contains(self.frontend / "src" / "lib" / "providers.tsx", "QueryClientProvider"),
        )
        self.check(
            "layout.tsx 包含 <Providers>",
            lambda: self.file_contains(self.frontend / "src" / "app" / "layout.tsx", "<Providers>"),
        )
        self.check(
            "layout.tsx 无 'use client'",
            lambda: self.file_not_contains(self.frontend / "src" / "app" / "layout.tsx", "'use client'"),
        )
        self.check(
            "globals.css 无 Geist 字体引用",
            lambda: self.file_not_contains(self.frontend / "src" / "app" / "globals.css", "geist"),
        )

        # 基础设施
        self.check("docker-compose.yml 存在", lambda: self.file_exists(self.root / "docker-compose.yml"))
        self.check(
            "docker-compose.yml 包含 4 个服务",
            lambda: self.file_contains(self.root / "docker-compose.yml", "postgres:")
            and self.file_contains(self.root / "docker-compose.yml", "backend:")
            and self.file_contains(self.root / "docker-compose.yml", "worker:")
            and self.file_contains(self.root / "docker-compose.yml", "frontend:"),
        )
        self.check(".env 不存在（防止误提交）", lambda: not (self.root / ".env").exists())
        self.check(".env.example 存在", lambda: self.file_exists(self.root / ".env.example"))
        self.check(
            ".gitignore 包含 .env",
            lambda: self.file_contains(self.root / ".gitignore", ".env"),
        )
        self.check(".github/workflows/backend-ci.yml 存在", lambda: self.file_exists(self.root / ".github" / "workflows" / "backend-ci.yml"))
        self.check(".github/workflows/frontend-ci.yml 存在", lambda: self.file_exists(self.root / ".github" / "workflows" / "frontend-ci.yml"))

    def phase2_build(self):
        """阶段 2：构建检查（需依赖已安装）"""
        print(f"\n{BLUE}=== 阶段 2：构建检查 ==={RESET}\n")

        # 后端构建检查
        self.check("backend: ruff check", lambda: self.run_cmd(["uv", "run", "ruff", "check", "."], cwd=self.backend))
        self.check("backend: ruff format --check", lambda: self.run_cmd(["uv", "run", "ruff", "format", "--check", "."], cwd=self.backend))
        self.check("backend: mypy", lambda: self.run_cmd(["uv", "run", "mypy", "app", "tests"], cwd=self.backend))

        # 前端构建检查
        self.check("frontend: pnpm type-check", lambda: self.run_cmd(["pnpm", "type-check"], cwd=self.frontend))
        self.check("frontend: pnpm lint", lambda: self.run_cmd(["pnpm", "lint"], cwd=self.frontend))
        self.check("frontend: pnpm build", lambda: self.run_cmd(["pnpm", "build"], cwd=self.frontend))

    def phase3_runtime(self):
        """阶段 3：运行时检查（需 Docker）"""
        print(f"\n{BLUE}=== 阶段 3：运行时检查 ==={RESET}\n")

        # 启动服务
        print(f"{YELLOW}启动 Docker Compose 服务...{RESET}")
        if not self.run_cmd(["docker", "compose", "up", "-d"]):
            print(f"{RED}✗ docker compose up -d 失败{RESET}")
            self.failed += 1
            return

        # 等待服务启动
        print(f"{YELLOW}等待服务启动（15 秒）...{RESET}")
        time.sleep(15)

        # 后端健康检查
        self.check(
            "backend: GET /health 返回 200",
            lambda: self.run_cmd(["curl", "-f", "-s", "http://localhost:8000/health"]),
        )
        self.check(
            "backend: GET /metrics 返回 200",
            lambda: self.run_cmd(["curl", "-f", "-s", "http://localhost:8000/metrics"]),
        )

        # 前端健康检查
        self.check(
            "frontend: 3000 端口响应",
            lambda: self.run_cmd(["curl", "-f", "-s", "-o", "/dev/null", "http://localhost:3000"]),
        )

        # Alembic 迁移链路
        self.check(
            "alembic: current 无报错",
            lambda: self.run_cmd(["uv", "run", "alembic", "current"], cwd=self.backend),
        )

        # 清理
        print(f"\n{YELLOW}清理 Docker Compose 服务...{RESET}")
        self.run_cmd(["docker", "compose", "down"])

    def summary(self):
        """输出汇总"""
        print(f"\n{BLUE}=== 验收汇总 ==={RESET}\n")
        total = self.passed + self.failed + self.skipped
        print(f"总计：{total} 项")
        print(f"{GREEN}通过：{self.passed}{RESET}")
        print(f"{RED}失败：{self.failed}{RESET}")
        print(f"{YELLOW}跳过：{self.skipped}{RESET}")

        if self.failed > 0:
            print(f"\n{RED}❌ 验收失败，请修复上述问题后重试{RESET}")
            sys.exit(1)
        else:
            print(f"\n{GREEN}✅ 验收通过，脚手架符合所有规范要求{RESET}")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="验收脚手架是否符合规范")
    parser.add_argument("--skip-runtime", action="store_true", help="跳过运行时检查（需要 Docker）")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    checker = Checker(root)

    checker.phase1_static()
    checker.phase2_build()

    if not args.skip_runtime:
        checker.phase3_runtime()
    else:
        print(f"\n{YELLOW}⚠ 跳过运行时检查（--skip-runtime）{RESET}")

    checker.summary()


if __name__ == "__main__":
    main()
