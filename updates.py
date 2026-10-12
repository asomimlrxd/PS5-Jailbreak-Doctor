"""Explicit, integrity-checked knowledge-base updates for PS5 Jailbreak Doctor.

The app itself is not auto-updated by this module. Only the JSON diagnostic database
is fetched, after the user requests an update. No logs or console data are uploaded.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_paths import user_data_path
from doctor_core import APP_VERSION, BUNDLED_KB_PATH, _validate_knowledge_base, KB_OVERRIDE_PATH

REPOSITORY_RAW_ROOT = "https://raw.githubusercontent.com/asomimlrxd/PS5-Jailbreak-Doctor/main/"
MANIFEST_URL = REPOSITORY_RAW_ROOT + "updates.json"
EXPECTED_KB_URL = REPOSITORY_RAW_ROOT + "knowledge_base.json"
USER_AGENT = f"PS5-Jailbreak-Doctor/{APP_VERSION} (knowledge-base updater)"
MAX_MANIFEST_BYTES = 256_000
MAX_KB_BYTES = 4_000_000


class UpdateError(RuntimeError):
    """An update was unavailable, invalid, or failed verification."""


def version_key(value: str) -> tuple[int, ...]:
    """Numeric version comparison for app versions and date-like DB versions."""
    tokens = re.findall(r"\d+", str(value or ""))
    if not tokens:
        return (0,)
    return tuple(int(token) for token in tokens)


def is_newer_version(candidate: str, current: str) -> bool:
    return version_key(candidate) > version_key(current)


def _fetch_https(url: str, limit: int, timeout: float = 10.0) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "raw.githubusercontent.com" or parsed.username or parsed.password:
        raise UpdateError("O endereço de atualização não pertence ao alojamento HTTPS esperado.")
    if not url.startswith(REPOSITORY_RAW_ROOT):
        raise UpdateError("O endereço está fora do repositório oficial configurado.")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url_text = response.geturl()
            final_url = urllib.parse.urlparse(final_url_text)
            if (final_url.scheme != "https" or final_url.hostname != "raw.githubusercontent.com"
                    or not final_url_text.startswith(REPOSITORY_RAW_ROOT)):
                raise UpdateError("O servidor redirecionou para fora do repositório esperado.")
            data = response.read(limit + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise UpdateError(f"Não foi possível consultar as atualizações: {exc}") from exc
    if len(data) > limit:
        raise UpdateError("O ficheiro de atualização excede o tamanho permitido.")
    return data


def validate_manifest(manifest: Any) -> dict:
    if not isinstance(manifest, dict) or manifest.get("manifest_version") != 1:
        raise UpdateError("Formato do ficheiro updates.json não suportado.")
    kb = manifest.get("knowledge_base")
    if not isinstance(kb, dict):
        raise UpdateError("O manifesto não contém uma atualização da base de conhecimento.")
    version = str(kb.get("database_version", "")).strip()
    if not re.fullmatch(r"\d{4}\.\d{1,2}\.\d{1,2}\.\d+", version):
        raise UpdateError("A versão da base de conhecimento no manifesto é inválida.")
    if kb.get("url") != EXPECTED_KB_URL:
        raise UpdateError("O manifesto aponta para um endereço de base de conhecimento não autorizado.")
    digest = str(kb.get("sha256", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise UpdateError("O checksum SHA-256 no manifesto é inválido.")
    minimum_app = str(manifest.get("minimum_app_version", "0.0.0"))
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", minimum_app):
        raise UpdateError("A versão mínima da aplicação no manifesto é inválida.")
    changes = kb.get("changelog", [])
    if not isinstance(changes, list) or any(not isinstance(item, str) for item in changes):
        raise UpdateError("A lista de alterações no manifesto é inválida.")
    kb["changelog"] = changes[:20]
    return manifest


def fetch_manifest(timeout: float = 10.0) -> dict:
    raw = _fetch_https(MANIFEST_URL, MAX_MANIFEST_BYTES, timeout)
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError("O manifesto de atualizações não é JSON válido.") from exc
    return validate_manifest(manifest)


def check_for_updates(current_database_version: str, timeout: float = 10.0) -> dict:
    manifest = fetch_manifest(timeout=timeout)
    offered = manifest["knowledge_base"]["database_version"]
    minimum_app = str(manifest.get("minimum_app_version", "0.0.0"))
    app_too_old = is_newer_version(minimum_app, APP_VERSION)
    return {
        "manifest": manifest,
        "current_version": current_database_version,
        "available_version": offered,
        "update_available": is_newer_version(offered, current_database_version) and not app_too_old,
        "minimum_app_version": minimum_app,
        "app_too_old": app_too_old,
    }


def validate_downloaded_database(raw: bytes, expected_sha256: str, expected_version: str) -> dict:
    actual = hashlib.sha256(raw).hexdigest()
    if actual.casefold() != str(expected_sha256).casefold():
        raise UpdateError("O SHA-256 não corresponde ao manifesto. A atualização foi rejeitada.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError("A base de conhecimento transferida não é JSON válido.") from exc
    try:
        data = _validate_knowledge_base(data)
    except (ValueError, re.error) as exc:
        raise UpdateError(f"A base de conhecimento não passou na validação: {exc}") from exc
    if str(data.get("database_version", "")) != expected_version:
        raise UpdateError("A versão do ficheiro não corresponde à versão publicada no manifesto.")
    for rule in data.get("rules", []):
        english = ((rule.get("translations") or {}).get("en") or {})
        for field in ("title", "summary", "fix_summary", "applicability"):
            if rule.get(field) and not str(english.get(field, "")).strip():
                raise UpdateError(f"A regra {rule.get('id')} não tem tradução inglesa para '{field}'.")
        english_steps = english.get("steps", [])
        if not isinstance(english_steps, list) or len(rule.get("steps", [])) != len(english_steps):
            raise UpdateError(f"A regra {rule.get('id')} tem passos sem tradução inglesa correspondente.")
        if any(not isinstance(step, str) or not step.strip() for step in english_steps):
            raise UpdateError(f"A regra {rule.get('id')} contém um passo em inglês vazio ou inválido.")
    matrix = data.get("compatibility_matrix", [])
    matrix_ids: set[str] = set()
    for entry in matrix:
        if not isinstance(entry, dict) or not entry.get("id") or not isinstance(entry.get("conditions"), dict) or not entry.get("conditions"):
            raise UpdateError("A matriz de compatibilidade contém uma entrada inválida.")
        entry_id = str(entry["id"])
        if entry_id in matrix_ids:
            raise UpdateError(f"ID de compatibilidade duplicado: {entry_id}")
        matrix_ids.add(entry_id)
        english = ((entry.get("translations") or {}).get("en") or {})
        for field in ("title", "summary", "status"):
            if entry.get(field) and not str(english.get(field, "")).strip():
                raise UpdateError(f"A compatibilidade {entry.get('id')} não tem tradução inglesa para '{field}'.")
    return data


def download_update(manifest: dict, timeout: float = 12.0) -> tuple[dict, bytes]:
    manifest = validate_manifest(manifest)
    kb_meta = manifest["knowledge_base"]
    raw = _fetch_https(kb_meta["url"], MAX_KB_BYTES, timeout)
    data = validate_downloaded_database(raw, kb_meta["sha256"], kb_meta["database_version"])
    return data, raw


def _active_database_path() -> Path:
    return KB_OVERRIDE_PATH if KB_OVERRIDE_PATH.is_file() else BUNDLED_KB_PATH


def install_update(manifest: dict, data: dict, raw: bytes) -> dict:
    """Back up the previous active DB and atomically install a verified update."""
    meta = manifest["knowledge_base"]
    validate_manifest(manifest)
    # Validate again at the installation boundary instead of trusting a caller.
    validated = validate_downloaded_database(raw, meta["sha256"], meta["database_version"])
    if validated.get("database_version") != data.get("database_version"):
        raise UpdateError("A base validada não corresponde aos dados preparados para instalação.")

    destination = user_data_path("knowledge_base.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    active = _active_database_path()
    backup_path = None
    if active.is_file():
        try:
            active_data = json.loads(active.read_text(encoding="utf-8"))
            active_version = str(active_data.get("database_version", "unknown"))
        except (OSError, json.JSONDecodeError):
            active_version = "unknown"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = destination.parent / f"knowledge_base.backup-{active_version}-{stamp}.json"
        shutil.copy2(active, backup_path)

    temporary = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=destination.parent, prefix="knowledge_base.", suffix=".tmp") as handle:
            temporary = Path(handle.name)
            handle.write(raw)
            handle.flush()
        # Ensure the on-disk bytes still match the advertised checksum.
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != meta["sha256"]:
            raise UpdateError("A verificação do ficheiro temporário falhou.")
        temporary.replace(destination)
    except Exception:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    state = {
        "schema_version": 1,
        "last_updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "database_version": meta["database_version"],
        "sha256": meta["sha256"],
        "backup": str(backup_path) if backup_path else None,
    }
    state_path = user_data_path("knowledge_updates_state.json")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    # Retain only the five most recent backups to avoid unbounded growth.
    backups = sorted(destination.parent.glob("knowledge_base.backup-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in backups[5:]:
        try:
            stale.unlink()
        except OSError:
            pass
    return state


def latest_backup() -> Path | None:
    directory = user_data_path("knowledge_base.json").parent
    candidates = sorted(directory.glob("knowledge_base.backup-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
            _validate_knowledge_base(data)
            return candidate
        except (OSError, json.JSONDecodeError, ValueError, re.error):
            continue
    return None


def restore_last_backup() -> dict:
    backup = latest_backup()
    if backup is None:
        raise UpdateError("Não existe uma cópia de segurança válida para restaurar.")
    raw = backup.read_bytes()
    try:
        data = _validate_knowledge_base(json.loads(raw.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, re.error) as exc:
        raise UpdateError(f"A cópia de segurança não é válida: {exc}") from exc
    destination = user_data_path("knowledge_base.json")
    temporary = destination.with_suffix(".restore.tmp")
    temporary.write_bytes(raw)
    temporary.replace(destination)
    return {"database_version": data.get("database_version", "unknown"), "restored_from": str(backup)}
