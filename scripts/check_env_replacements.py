#!/usr/bin/env python3
"""检查 /setup 后手工环境变量替换是否完成，并可同步数据库密码。"""

import argparse
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit
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


def parse_database_url(url: str) -> tuple[str, str, str] | None:
    if not url:
        return None
    parsed = urlsplit(url)
    if not parsed.username or parsed.password is None or not parsed.path:
        return None
    db_name = parsed.path.lstrip("/")
    if not db_name:
        return None
    decoded_password = unquote(parsed.password)
    return parsed.username, decoded_password, db_name


def extract_url_password_raw(url: str) -> str | None:
    match = re.match(r"^postgresql\+asyncpg://[^:\n]+:([^@\n]*)@.+$", url)
    if not match:
        return None
    return match.group(1)


def sync_backend_db_password(
    backend_env_path: Path,
    expected_password: str,
) -> tuple[bool, str]:
    if not backend_env_path.exists():
        return False, "WARN backend/.env.example 不存在，跳过密码同步"
    text = backend_env_path.read_text(encoding="utf-8")
    changed = False
    for key in ("DATABASE_URL", "DATABASE_TEST_URL"):
        pattern = rf"^({key}=postgresql\+asyncpg://[^:\n]+:)([^@\n]*)(@.+)$"
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            continue
        current = match.group(2)
        if current != expected_password:
            replacement = f"{match.group(1)}{quote(expected_password, safe='')}{match.group(3)}"
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
            changed = True
    if changed:
        backend_env_path.write_text(text, encoding="utf-8")
        return True, "PASS 已自动同步 backend/.env.example 的 DATABASE_URL/DATABASE_TEST_URL 密码"
    return True, "PASS backend/.env.example 数据库 URL 密码已与根 .env.example 一致"


def sync_compose_db_password(
    compose_path: Path,
    expected_password: str,
) -> tuple[bool, str]:
    if not compose_path.exists():
        return False, "FAIL docker-compose.yml 不存在，无法同步密码"
    text = compose_path.read_text(encoding="utf-8")
    changed = False

    env_pattern = r"^(\s*POSTGRES_PASSWORD:\s*)(\S+)(\s*)$"
    if re.search(env_pattern, text, flags=re.MULTILINE):
        text = re.sub(env_pattern, rf"\1{expected_password}\3", text, flags=re.MULTILINE)
        changed = True

    encoded_password = quote(expected_password, safe="")

    def replace_compose_database_url(line: str) -> str:
        prefix_match = re.match(r"^(\s*DATABASE_URL:\s*)(.+)$", line)
        if not prefix_match:
            return line
        prefix, url = prefix_match.groups()
        parts = re.match(r"^(postgresql\+asyncpg://)([^:\n]+):([^@\n]*)@([^/\n]+)/(.*)$", url)
        if not parts:
            return line
        scheme, user, _old_password, host_part, db_part = parts.groups()
        new_url = f"{scheme}{user}:{encoded_password}@{host_part}/{db_part}"
        return f"{prefix}{new_url}"

    new_lines: list[str] = []
    for raw_line in text.splitlines():
        replaced = replace_compose_database_url(raw_line)
        if replaced != raw_line:
            changed = True
        new_lines.append(replaced)
    text = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")

    if changed:
        compose_path.write_text(text, encoding="utf-8")
        return True, "PASS 已自动同步 docker-compose.yml 中 POSTGRES_PASSWORD 与 DATABASE_URL 密码段"
    return True, "PASS docker-compose.yml 中数据库密码已与根 .env.example 一致"


def main() -> int:
    parser = argparse.ArgumentParser(description="检查环境变量替换与数据库配置一致性")
    parser.add_argument(
        "--sync-db-password",
        action="store_true",
        help="自动将 docker-compose.yml 与 backend/.env.example 的数据库密码同步为根 .env.example 的 POSTGRES_PASSWORD",
    )
    args = parser.parse_args()

    root_env = parse_env_file(ROOT / ".env.example")
    root_pg_password_raw = unquote(root_env.get("POSTGRES_PASSWORD", ""))
    if args.sync_db_password:
        ok, msg = sync_compose_db_password(ROOT / "docker-compose.yml", root_pg_password_raw)
        print(msg)
        if not ok and msg.startswith("FAIL"):
            return 1
    backend_env_path = ROOT / "backend" / ".env.example"
    if args.sync_db_password:
        ok, msg = sync_backend_db_password(backend_env_path, root_pg_password_raw)
        print(msg)
        if not ok and msg.startswith("FAIL"):
            return 1
    backend_env = parse_env_file(backend_env_path)
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
    ]
    for key in required_backend:
        ok, msg = check_non_empty(backend_env, key)
        print(msg)
        failed += 0 if ok else 1

    for key in ("DATABASE_URL", "DATABASE_TEST_URL"):
        ok, msg = check_not_contains(backend_env, key, "changeme")
        print(msg)
        failed += 0 if ok else 1

    compose_text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    root_pg_user = root_env.get("POSTGRES_USER", "")
    root_pg_password = root_pg_password_raw
    root_pg_db = root_env.get("POSTGRES_DB", "")

    print("\n=== Cross-file DB Consistency ===")
    if f"POSTGRES_USER: {root_pg_user}" in compose_text:
        print("PASS docker-compose POSTGRES_USER 与根 .env.example 一致")
    else:
        print("FAIL docker-compose POSTGRES_USER 与根 .env.example 不一致")
        failed += 1

    if f"POSTGRES_PASSWORD: {root_pg_password}" in compose_text:
        print("PASS docker-compose POSTGRES_PASSWORD 与根 .env.example 一致")
    else:
        print("FAIL docker-compose POSTGRES_PASSWORD 与根 .env.example 不一致")
        failed += 1

    if f"POSTGRES_DB: {root_pg_db}" in compose_text:
        print("PASS docker-compose POSTGRES_DB 与根 .env.example 一致")
    else:
        print("FAIL docker-compose POSTGRES_DB 与根 .env.example 不一致")
        failed += 1

    for key in ("DATABASE_URL", "DATABASE_TEST_URL"):
        parsed = parse_database_url(backend_env.get(key, ""))
        if parsed is None:
            print(f"FAIL {key} 无法解析为有效 PostgreSQL URL")
            failed += 1
            continue
        user, password, db_name = parsed
        password_raw = extract_url_password_raw(backend_env.get(key, ""))
        if password_raw is None:
            print(f"FAIL {key} 无法提取密码段")
            failed += 1
            continue
        password = unquote(password_raw)
        expected_db = root_pg_db if key == "DATABASE_URL" else f"{root_pg_db}_test"
        if user == root_pg_user:
            print(f"PASS {key} 用户名与根 .env.example 一致")
        else:
            print(f"FAIL {key} 用户名与根 .env.example 不一致")
            failed += 1
        if password == root_pg_password:
            print(f"PASS {key} 密码与根 .env.example 一致")
        else:
            print(f"FAIL {key} 密码与根 .env.example 不一致")
            failed += 1
        if db_name == expected_db:
            print(f"PASS {key} 数据库名与约定一致")
        else:
            print(f"FAIL {key} 数据库名不匹配，期望 {expected_db}，实际 {db_name}")
            failed += 1

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
