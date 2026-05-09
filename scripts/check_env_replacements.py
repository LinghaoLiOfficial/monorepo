#!/usr/bin/env python3
"""检查 /setup 后手工环境变量替换是否完成。"""

from pathlib import Path
import sys


ROOT = Path(__file__).parent.parent


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def check_non_empty(env: dict[str, str], key: str) -> tuple[bool, str]:
    value = env.get(key, "")
    if value:
        return True, f"PASS {key} 已配置"
    return False, f"FAIL {key} 为空"


def check_not_contains(env: dict[str, str], key: str, bad: str) -> tuple[bool, str]:
    value = env.get(key, "")
    if bad in value:
        return False, f"FAIL {key} 包含占位符 {bad}"
    return True, f"PASS {key} 不含占位符 {bad}"


def main() -> int:
    root_env = parse_env_file(ROOT / ".env.example")
    backend_env = parse_env_file(ROOT / "backend" / ".env.example")
    frontend_env_path = ROOT / "frontend" / ".env.example"
    frontend_env = parse_env_file(frontend_env_path)

    failed = 0
    warned = 0

    print("=== Root .env.example ===")
    for key in ("POSTGRES_USER", "POSTGRES_DB"):
        ok, msg = check_non_empty(root_env, key)
        print(msg)
        failed += 0 if ok else 1

    ok, msg = check_not_contains(root_env, "POSTGRES_PASSWORD", "changeme")
    print(msg)
    failed += 0 if ok else 1

    print("\n=== backend/.env.example ===")
    required_backend = [
        "APP_NAME",
        "APP_ENV",
        "DEBUG",
        "DATABASE_URL",
        "DATABASE_TEST_URL",
        "CORS_ORIGINS",
        "JWT_PRIVATE_KEY",
        "JWT_PUBLIC_KEY",
        "OSS_ACCESS_KEY_ID",
        "OSS_ACCESS_KEY_SECRET",
        "OSS_BUCKET_NAME",
        "OSS_ENDPOINT",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "SMTP_FROM_EMAIL",
    ]
    for key in required_backend:
        ok, msg = check_non_empty(backend_env, key)
        print(msg)
        failed += 0 if ok else 1

    for key in ("DATABASE_URL", "DATABASE_TEST_URL"):
        ok, msg = check_not_contains(backend_env, key, "changeme")
        print(msg)
        failed += 0 if ok else 1

    otel = backend_env.get("OTEL_EXPORTER_ENDPOINT", "")
    if otel:
        print("PASS OTEL_EXPORTER_ENDPOINT 已配置")
    else:
        print("WARN OTEL_EXPORTER_ENDPOINT 为空（本地可接受，非本地建议配置）")
        warned += 1

    print("\n=== frontend/.env.example ===")
    if not frontend_env_path.exists():
        print("WARN frontend/.env.example 不存在（如当前前端无环境变量可忽略）")
        warned += 1
    else:
        print("PASS frontend/.env.example 存在")
        for key, value in frontend_env.items():
            if key.startswith("NEXT_PUBLIC_") and ("SECRET" in key or "TOKEN" in key):
                print(f"FAIL {key} 疑似敏感信息，不应暴露为 NEXT_PUBLIC_*")
                failed += 1
            elif not value:
                print(f"FAIL {key} 为空")
                failed += 1

    print("\n=== Summary ===")
    print(f"FAIL: {failed}")
    print(f"WARN: {warned}")
    if failed > 0:
        print("环境变量检查未通过，请先完成替换再继续。")
        return 1
    print("环境变量检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
