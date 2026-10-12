"""Small, explicit and reversible local file-name tests. Never writes to the PS5 API."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from app_paths import data_path

JOURNAL_PATH = data_path("changes_journal.json")
SUPPORTED_EXTENSIONS = {".ffpfs", ".ffpfsc"}
SUPPORTED_RULES = {"SHADOW_PFS_PARENTHESES_PANIC", "SHADOW_FILENAME_TOO_LONG"}


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_journal() -> dict:
    try:
        data = json.loads(JOURNAL_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("actions"), list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"schema_version": 1, "actions": []}


def list_actions() -> list[dict]:
    return list(reversed(_read_journal()["actions"]))


def _write_journal(data: dict) -> None:
    temp = JOURNAL_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(JOURNAL_PATH)


def _unique_destination(folder: Path, name: str) -> Path:
    candidate = folder / name
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    for index in range(2, 1000):
        alt = folder / f"{stem}_{index}{suffix}"
        if not alt.exists():
            return alt
    raise RuntimeError("Não foi possível encontrar um nome de destino livre.")


def suggest_name(rule_id: str, source: Path) -> str:
    suffix = source.suffix
    stem = source.stem
    if rule_id == "SHADOW_PFS_PARENTHESES_PANIC":
        cleaned = re.sub(r"[()]", "", stem)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" ._")
        if not cleaned:
            cleaned = "PFS_Test"
        return cleaned + suffix
    if rule_id == "SHADOW_FILENAME_TOO_LONG":
        match = re.search(r"\b(?:PPSA|PPSM|CUSA)[A-Z0-9]{4,6}\b", stem, re.IGNORECASE)
        prefix = match.group(0).upper() if match else re.sub(r"[^A-Za-z0-9_-]+", "_", stem)[:32].strip("_-")
        if not prefix:
            prefix = "PS5_Image"
        return f"{prefix}_Test{suffix}"
    raise ValueError("Esta regra não tem uma ação local reversível associada.")


def rename_for_rule(rule_id: str, source_path: str | Path) -> dict:
    """Rename only the selected local image filename, preserving content and extension."""
    if rule_id not in SUPPORTED_RULES:
        raise ValueError("Esta regra não disponibiliza uma renomeação assistida.")
    source = Path(source_path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError("O ficheiro selecionado não existe ou não é um ficheiro normal.")
    if source.is_symlink():
        raise ValueError("Por segurança, não renomeio links simbólicos.")
    if str(source).startswith("\\\\"):
        raise ValueError("Seleciona o ficheiro numa unidade local. Caminhos de rede não são suportados neste teste.")
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Seleciona um ficheiro .ffpfs ou .ffpfsc. A extensão não será alterada.")
    if rule_id == "SHADOW_PFS_PARENTHESES_PANIC" and not re.search(r"[()]", source.name):
        raise ValueError("O nome selecionado não contém parênteses; não corresponde ao cenário desta regra.")
    if rule_id == "SHADOW_FILENAME_TOO_LONG" and len(source.name) < 60:
        raise ValueError("Este nome tem menos de 60 caracteres. Como o limite exato não está documentado, a app não vai sugerir uma renomeação automática para este caso.")

    source = source.resolve()
    original_stat = source.stat()
    proposed_name = suggest_name(rule_id, source)
    destination = _unique_destination(source.parent, proposed_name)
    if destination == source:
        raise ValueError("O nome proposto é igual ao atual; não há alteração a fazer.")

    journal = _read_journal()
    action_id = uuid.uuid4().hex[:12]
    record = {
        "id": action_id,
        "created_at": _now(),
        "rule_id": rule_id,
        "action": "rename_file",
        "original_path": str(source),
        "current_path": str(destination),
        "original_name": source.name,
        "new_name": destination.name,
        "size_bytes": original_stat.st_size,
        "mtime_ns": original_stat.st_mtime_ns,
        "status": "renamed",
        "reversible": True,
        "note": "Apenas o nome local foi alterado. O conteúdo do ficheiro não foi editado; esta ação não altera diretamente a PS5."
    }
    source.rename(destination)
    try:
        journal["actions"].append(record)
        _write_journal(journal)
    except Exception:
        # Best effort immediate rollback if journal cannot be persisted.
        if destination.exists() and not source.exists():
            destination.rename(source)
        raise
    return record


def rollback_action(action_id: str) -> dict:
    journal = _read_journal()
    record = next((a for a in journal["actions"] if a.get("id") == action_id), None)
    if not record:
        raise KeyError("A alteração não existe no histórico.")
    if record.get("status") != "renamed":
        raise ValueError("Esta alteração já foi revertida ou não está disponível para reversão.")
    current = Path(record["current_path"])
    original = Path(record["original_path"])
    if not current.exists() or not current.is_file():
        raise FileNotFoundError("O ficheiro renomeado não foi encontrado. Liga a unidade onde está guardado e tenta novamente.")
    if original.exists():
        raise FileExistsError("Já existe um ficheiro com o nome original. Não vou substituir ficheiros durante a reversão.")
    stat = current.stat()
    if stat.st_size != record.get("size_bytes") or stat.st_mtime_ns != record.get("mtime_ns"):
        raise ValueError("O ficheiro parece ter sido modificado após a renomeação. A reversão automática foi bloqueada para evitar perder dados.")
    current.rename(original)
    record["status"] = "reverted"
    record["reverted_at"] = _now()
    _write_journal(journal)
    return record
