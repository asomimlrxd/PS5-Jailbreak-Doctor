"""Rule-based diagnostics for PS5 homebrew logs. Offline and dependency-free."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

APP_VERSION = "0.8.0"

from pathlib import Path
import json
from app_paths import resource_path, user_data_path

BUNDLED_KB_PATH = resource_path("knowledge_base.json")
KB_OVERRIDE_PATH = user_data_path("knowledge_base.json")
KB_PATH = KB_OVERRIDE_PATH if KB_OVERRIDE_PATH.is_file() else BUNDLED_KB_PATH

@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    confidence: str
    summary: str
    next_steps: tuple[str, ...]
    evidence: tuple[str, ...]
    fix_summary: str = ""
    fix_type: str = "guia"
    evidence_status: str = "heuristica"
    applicability: str = ""
    sources: tuple[str, ...] = ()
    context_relevance: str = "Não avaliado"
    context_note: str = ""


def _validate_knowledge_base(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Schema da base de conhecimento inválido.")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules or len(rules) > 500:
        raise ValueError("A base de conhecimento não contém uma lista de regras válida.")
    valid_rules = []
    seen_ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or not rule.get("id") or not isinstance(rule.get("patterns"), list) or not rule["patterns"]:
            raise ValueError("Foi encontrada uma regra sem ID ou padrões válidos.")
        rule_id = str(rule["id"])
        if rule_id in seen_ids:
            raise ValueError(f"ID de regra duplicado: {rule_id}")
        seen_ids.add(rule_id)
        for pattern in list(rule.get("patterns", [])) + list(rule.get("all_patterns", [])):
            if not isinstance(pattern, str) or len(pattern) > 1000:
                raise ValueError(f"Padrão inválido ou demasiado longo em {rule_id}.")
            re.compile(pattern, re.IGNORECASE)
        valid_rules.append(rule)
    data["rules"] = valid_rules
    matrix = data.get("compatibility_matrix", [])
    if not isinstance(matrix, list) or len(matrix) > 100:
        raise ValueError("Matriz de compatibilidade inválida.")
    return data


def load_knowledge_base(path: Path | None = None) -> dict:
    """Load a valid local knowledge base. Prefer the user-installed update over the bundled copy."""
    candidates = [path] if path else ([KB_OVERRIDE_PATH, BUNDLED_KB_PATH] if KB_OVERRIDE_PATH.is_file() else [BUNDLED_KB_PATH])
    errors = []
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            with Path(candidate).open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            data = _validate_knowledge_base(data)
            data.setdefault("database_version", "unknown")
            data.setdefault("generated_at", "unknown")
            data.setdefault("description", "")
            return data
        except (OSError, json.JSONDecodeError, ValueError, re.error) as exc:
            errors.append(f"{candidate}: {exc}")
    # Keep the app usable and make the missing KB visible in the status/report.
    return {"schema_version": 1, "database_version": "fallback-empty", "generated_at": "unknown",
            "description": "Não foi possível carregar knowledge_base.json: " + "; ".join(errors), "rules": [], "compatibility_matrix": []}


def reload_knowledge_base(path: Path | None = None) -> dict:
    """Reload a verified database; fall back to the bundled copy if the override is invalid."""
    global KB_PATH, KNOWLEDGE_BASE, RULES
    if path is not None:
        KB_PATH = Path(path)
        KNOWLEDGE_BASE = load_knowledge_base(KB_PATH)
    else:
        KB_PATH = KB_OVERRIDE_PATH if KB_OVERRIDE_PATH.is_file() else BUNDLED_KB_PATH
        KNOWLEDGE_BASE = load_knowledge_base()
    RULES = KNOWLEDGE_BASE.get("rules", [])
    return KNOWLEDGE_BASE


KNOWLEDGE_BASE = load_knowledge_base()
RULES = KNOWLEDGE_BASE["rules"]

SENSITIVE_PATTERNS = [
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP REDACTED]"),
    (re.compile(r"(?i)C:\\Users\\[^\\\s]+"), r"C:\\Users\\[USER]"),
    (re.compile(r"(?i)(?:/users/|/home/)[^/\s]+"), "/[USER]"),
]

def redact(text: str) -> str:
    out = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        out = pattern.sub(replacement, out)
    return out

def _clip(line: str, width: int = 300) -> str:
    line = line.strip()
    return line if len(line) <= width else line[:width - 1] + "…"


def evidence_status_pt(status: str) -> str:
    labels = {
        "heuristica": "Heurística — precisa de contexto",
        "heuristica_comunitaria": "Heurística baseada em relato comunitário",
        "documentacao_tecnica": "Documentação técnica",
        "relato_comunitario": "Relato comunitário",
        "relato_comunitario_aberto": "Relato comunitário — questão aberta",
        "relato_comunitario_corrigido_no_codigo_posterior": "Relato comunitário — correção adicionada ao código após o relato",
        "relato_comunitario_fechado_ou_antigo": "Relato antigo/fechado — pode já ter mudado",
        "relato_comunitario_encerrado_com_pista_do_mantenedor": "Questão encerrada — pista específica do mantenedor",
        "relato_comunitario_nao_especifico": "Relato comunitário genérico",
        "relato_comunitario_com_workaround_nao_confirmado": "Relato com alternativa não confirmada",
        "relato_comunitario_antigo": "Relato comunitário antigo",
        "relatos_comunitarios_mistos": "Vários relatos, causa não isolada",
        "relatos_comunitarios_nao_conclusivos": "Relatos comunitários inconclusivos",
        "relatos_comunitarios_abertos_e_contraditorios": "Relatos abertos e contraditórios",
        "nao_classificado": "Evento ainda não classificado",
    }
    return labels.get(status, status.replace("_", " ").capitalize())


def fix_type_pt(fix_type: str) -> str:
    labels = {
        "guia": "guia manual",
        "solucao_relata_com_cuidado": "solução relatada — confirmar antes de aplicar",
        "workaround_comunitario": "alternativa relatada pela comunidade",
        "report_only": "recolher mais dados; sem correção confirmada",
        "triagem": "triagem manual",
        "triagem_segura": "triagem segura",
        "evitar_operacao": "evitar temporariamente a operação",
        "nao_automatizar": "não automatizar — requer validação manual",
    }
    return labels.get(fix_type, fix_type.replace("_", " "))

def _matching_evidence(lines: list[str], patterns: list[re.Pattern], limit: int = 5) -> tuple[str, ...]:
    found: list[str] = []
    for raw in lines:
        if any(p.search(raw) for p in patterns):
            clipped = _clip(raw)
            if clipped not in found:
                found.append(clipped)
        if len(found) >= limit:
            break
    return tuple(found)


CONTEXT_DISPLAY = {
    "origin_type": {
        "folder": "pasta de jogo", "image_pfs": "imagem .ffpfs/.ffpfsc",
        "image_lz4": "imagem LZ4", "installed_title": "título já instalado", "other": "outro formato",
    },
    "storage": {
        "usb": "USB", "internal": "SSD interno", "transfer_between": "transferência entre USB e SSD interno",
    },
    "trigger": {
        "after_resume": "após retoma do modo de repouso", "after_exit": "após sair/fechar o jogo",
        "after_update": "após atualizar payload/ferramenta", "registration": "durante instalação/registo",
        "launch": "ao iniciar o jogo", "transfer": "durante cópia/movimentação de ficheiros",
        "all_titles": "em vários jogos", "one_title": "apenas num jogo",
    },
}


def _normalized_version_tokens(value: str) -> set[str]:
    """Extract version tokens while treating 1.7beta4 and 1.7-beta4 as equivalent."""
    pattern = re.compile(r"(?<![a-z0-9])v?(\d+(?:\.\d+)+(?:[-._]?[a-z][a-z0-9]*)?(?:[-._][a-z0-9]+)*)", re.IGNORECASE)
    return {re.sub(r"[^a-z0-9]", "", match.group(1).casefold()) for match in pattern.finditer(str(value or ""))}


def _evaluate_context(rule: dict, context: dict | None) -> tuple[str, str, str]:
    """Return context status, adjusted confidence, and note. Context never creates a finding by itself."""
    conditions = rule.get("context_conditions") or {}
    if not conditions:
        return "Não necessário", str(rule.get("confidence", "Baixa")), ""
    context = context or {}
    supplied = []
    for key in ("origin_type", "storage", "trigger", "firmware", "shadowmount_version", "kstuff_version"):
        value = str(context.get(key, "") or "").strip()
        if value and value.casefold() not in {"unknown", "desconhecido", "não indicado", "nao indicado"}:
            supplied.append(value)
    if not supplied:
        return "Sem contexto", str(rule.get("confidence", "Baixa")), "Preenche o contexto opcional para confirmar se este caso corresponde ao cenário documentado."

    matches, mismatches, unknowns = [], [], []
    for key, expected_values in conditions.items():
        observed = str(context.get(key, "") or "").strip()
        if not observed or observed.casefold() in {"unknown", "desconhecido", "não indicado", "nao indicado"}:
            unknowns.append(key)
            continue
        expected = [str(value).casefold() for value in (expected_values if isinstance(expected_values, list) else [expected_values])]
        if key in {"firmware", "shadowmount_version", "kstuff_version"}:
            # Compare version tokens, not substrings (e.g. 1.11 must not match 1.110).
            observed_versions = _normalized_version_tokens(observed)
            expected_versions = set()
            for value in expected:
                tokens = _normalized_version_tokens(value)
                expected_versions.update(tokens or {re.sub(r"[^a-z0-9]", "", value.casefold())})
            if observed_versions & expected_versions:
                matches.append(key)
            else:
                mismatches.append(key)
        else:
            observed_norm = re.sub(r"[^a-z0-9.]", "", observed.casefold())
            expected_norm = [re.sub(r"[^a-z0-9.]", "", value) for value in expected]
            if any(value == observed_norm or value in observed_norm or observed_norm in value for value in expected_norm):
                matches.append(key)
            else:
                mismatches.append(key)

    labels = {"origin_type": "formato da origem", "storage": "armazenamento", "trigger": "quando começou",
              "firmware": "firmware", "shadowmount_version": "versão do ShadowMountPlus", "kstuff_version": "versão do KStuff Lite"}
    if mismatches:
        names = ", ".join(labels.get(k, k) for k in mismatches)
        note = (f"O log corresponde à assinatura, mas o contexto informado diverge do cenário documentado ({names}). "
                "Trata esta hipótese como menos provável e não apliques o workaround específico sem confirmar os detalhes.")
        return "Contexto divergente", "Baixa (contexto divergente)", note
    if not unknowns and matches:
        names = ", ".join(labels.get(k, k) for k in matches)
        return "Contexto compatível", str(rule.get("confidence", "Baixa")), f"Campos compatíveis com o relato/documentação: {names}. Isto reforça a relevância, mas não prova a causa."
    if matches:
        names = ", ".join(labels.get(k, k) for k in matches)
        return "Parcialmente compatível", str(rule.get("confidence", "Baixa")), f"Coincide em: {names}. Ainda falta contexto para confirmar todos os critérios deste cenário."
    return "Sem correspondência suficiente", str(rule.get("confidence", "Baixa")), "Os dados fornecidos não permitem confirmar a aplicabilidade desta regra."


def analyze_logs(text: str, context: dict | None = None) -> list[Finding]:
    """Match local KB signatures, evaluate optional environment context, and preserve unknown errors."""
    if not text.strip():
        return []
    lines = text.splitlines()
    findings: list[Finding] = []
    known_evidence: set[str] = set()
    for rule in RULES:
        try:
            patterns = [re.compile(p, re.IGNORECASE) for p in rule.get("patterns", [])]
            all_patterns = [re.compile(p, re.IGNORECASE) for p in rule.get("all_patterns", [])]
        except re.error:
            continue
        # Any pattern is enough, but some issues add all_patterns to avoid false positives.
        if not any(p.search(text) for p in patterns):
            continue
        if all_patterns and not all(p.search(text) for p in all_patterns):
            continue
        evidence = _matching_evidence(lines, patterns)
        if not evidence and all_patterns:
            evidence = _matching_evidence(lines, all_patterns)
        if not evidence:
            # Context-based rules may distribute their markers across adjacent lines.
            evidence = tuple(_clip(line) for line in lines if any(p.search(line) for p in all_patterns))[:5]
        if not evidence:
            continue
        known_evidence.update(evidence)
        context_relevance, adjusted_confidence, context_note = _evaluate_context(rule, context)
        steps = list(str(s) for s in rule.get("steps", []))
        if context_relevance == "Contexto divergente":
            steps.insert(0, "Não apliques já o workaround específico desta regra: o contexto escolhido não corresponde ao cenário registado. Confirma o formato, as versões e quando começou o erro.")
        findings.append(Finding(
            rule_id=str(rule["id"]), title=str(rule.get("title", rule["id"])),
            severity=str(rule.get("severity", "Aviso")), confidence=adjusted_confidence,
            summary=str(rule.get("summary", "Sem descrição.")),
            next_steps=tuple(steps), evidence=evidence,
            fix_summary=str(rule.get("fix_summary", "")), fix_type=str(rule.get("fix_type", "guia")),
            evidence_status=str(rule.get("evidence_status", "heuristica")),
            applicability=str(rule.get("applicability", "")),
            sources=tuple(str(u) for u in rule.get("sources", [])),
            context_relevance=context_relevance, context_note=context_note))

    # Prefer a specific installation/registration diagnosis over the generic matcher.
    ids_found = {finding.rule_id for finding in findings}
    if ids_found.intersection({"SHADOW_REG_80F50005", "SHADOW_TROPHY_REG_80551618"}):
        findings = [f for f in findings if f.rule_id != "SHADOW_INSTALL_FAILURE"]

    # Do not leave useful errors invisible merely because no signature exists yet.
    # Include relevant unclassified lines, excluding evidence already reported by rules.
    signal_re = re.compile(
        r"\b(?:error|failed|failure|fatal|panic|crash(?:ed)?|sigsegv|sigbus|exception|unavailable|"
        r"not found|invalid argument|device busy|cannot|could not|refused|0x[0-9a-f]{6,})\b|"
        r"\b(?:ce-\d{2,}-\d{3,}-\d|ce-105773-3)\b", re.IGNORECASE)
    unknown: list[str] = []
    for line in lines:
        clipped = _clip(line)
        if signal_re.search(line) and clipped not in known_evidence and clipped not in unknown:
            unknown.append(clipped)
        if len(unknown) >= 12:
            break
    if unknown:
        findings.append(Finding(
            rule_id="UNCLASSIFIED_EVENTS", title="Eventos de erro ainda não classificados",
            severity="Aviso", confidence="Baixa", 
            summary="Encontrei linhas com termos de erro/crash que não foram explicadas pelas regras atuais. A base é incompleta por definição: usa estas linhas para acrescentar uma regra nova, sem assumir uma causa.",
            next_steps=(
                "Lê 20–40 linhas antes do primeiro evento e procura a primeira falha, não apenas a última mensagem.",
                "Confirma firmware, versões de KStuff Lite e ShadowMountPlus, tipo de origem e Title ID.",
                "Guarda o relatório anonimizado e compara com o repositório de issues do projeto correspondente.",
                "Não executes comandos, alteres permissões ou apagues ficheiros só por esta classificação genérica."
            ), evidence=tuple(unknown), fix_summary="Ainda não há uma correção segura associada a estas linhas; é necessária triagem.",
            fix_type="triagem", evidence_status="nao_classificado", applicability="Marcador de fallback adicionado quando existem linhas de erro sem correspondência.", sources=()))

    priority = {"Erro crítico": 0, "Erro": 1, "Aviso": 2, "Informação": 3}
    findings.sort(key=lambda item: (priority.get(item.severity, 4), item.rule_id))
    return findings



_ERROR_EVENT_RE = re.compile(
    r"(?i)\b(?:error|failed|failure|exception|panic|crash(?:ed)?|segfault|sigsegv|sigbus|page fault|"
    r"unavailable|refused|not found|invalid|device busy|rolling back|cache full|duplicate.{0,50}title.?id|"
    r"source.{0,20}not stable|not stable yet|found\s+0\s+games|0x[89a-f][0-9a-f]{6,7}|ce-\d{2,}-\d{3,}-\d)\b"
)


def extract_error_timeline(text: str, limit: int = 8) -> list[dict[str, object]]:
    """Extract a compact, ordered timeline of suspicious log lines for user review.

    This does not infer a root cause and never modifies the input or source logs.
    """
    events: list[dict[str, object]] = []
    for line_no, raw_line in enumerate(text.splitlines(), 1):
        if not _ERROR_EVENT_RE.search(raw_line):
            continue
        cleaned = _clip(raw_line, 240)
        lower = raw_line.lower()
        if any(token in lower for token in ("kernel panic", "panic", "sigsegv", "sigbus", "page fault", "segfault", "crashed")):
            kind = "critical"
        elif any(token in lower for token in ("error", "failed", "failure", "exception", "refused", "unavailable", "not found", "invalid")) or re.search(r"0x[89a-f][0-9a-f]{6,7}|ce-\d{2,}-\d{3,}-\d", lower):
            kind = "error"
        else:
            kind = "warning"
        events.append({"line": line_no, "kind": kind, "text": cleaned})
        if len(events) >= max(1, min(limit, 20)):
            break
    return events


def build_preflight_checks(text: str, context: dict | None = None) -> list[dict[str, object]]:
    """Build non-destructive checks from supplied context and evidence actually present in logs.

    This function evaluates only supplied logs and context. The optional scanner API
    inspection is handled separately and must remain read-only.
    """
    context = context or {}
    checks: list[dict[str, object]] = []
    required_context = {
        "firmware": "firmware",
        "shadowmount_version": "versão do ShadowMountPlus",
        "kstuff_version": "versão do KStuff Lite",
    }
    missing = [label for key, label in required_context.items()
               if not str(context.get(key, "") or "").strip()
               or str(context.get(key, "")).strip().casefold() in {"unknown", "desconhecido", "não indicado", "nao indicado"}]
    version_sensitive_signal = bool(re.search(
        r"shadowmount|kstuff|titledir|appinstallall|0x80f50005|prx_sce_module_load_error|"
        r"kernel panic|sigsegv|sigbus|ce-105773-3|pfs|source.{0,20}not stable|scanpath|scan_depth",
        text, re.IGNORECASE,
    ))
    user_supplied_context = any(
        str(context.get(key, "") or "").strip().casefold() not in {"", "unknown", "desconhecido", "não indicado", "nao indicado"}
        for key in ("firmware", "shadowmount_version", "kstuff_version", "origin_type", "storage", "trigger")
    )
    if missing and (version_sensitive_signal or user_supplied_context):
        checks.append({
            "id": "CONTEXT_INCOMPLETE",
            "severity": "info",
            "title": "Contexto técnico incompleto",
            "summary": "A aplicação não consegue comparar com rigor os relatos dependentes de versão sem estes dados: " + ", ".join(missing) + ".",
            "steps": ["Preenche o firmware da PS5 e as versões exatas do ShadowMountPlus e KStuff Lite, se as conseguires confirmar.",
                      "Não assumes que um relato de outra versão se aplica ao teu caso."],
        })

    lower = text.casefold()
    scan_evidence = bool(re.search(
        r"scanpath|scan_paths?|scan_depth|found\s+0\s+games?|no games found|manual\.lst|"
        r"param\.json.{0,60}(?:missing|invalid|not found)|(?:missing|invalid|not found).{0,60}param\.json",
        lower,
    ))
    if scan_evidence:
        steps = [
            "Confirma no debug.log quais as raízes de varrimento ativas e quantos jogos foram encontrados.",
            "Se existir uma linha scanpath= no config.ini, verifica se inclui a localização pretendida: raízes personalizadas podem substituir as raízes padrão.",
            "Confirma se scan_depth alcança o nível onde está a pasta do jogo e se sce_sys/param.json existe na raiz esperada.",
            "Para origens fora das raízes de varrimento, consulta a documentação da build instalada sobre /data/shadowmount/manual.lst antes de editar a configuração.",
        ]
        checks.append({
            "id": "SCANNER_PREFLIGHT",
            "severity": "warning" if re.search(r"found\s+0\s+games?|no games found|param\.json.{0,60}(?:missing|invalid|not found)|(?:missing|invalid|not found).{0,60}param\.json", lower) else "info",
            "title": "Pré-verificação do scanner e da origem",
            "summary": "Os logs incluem referências a scanpath, scan_depth, param.json ou a uma varredura sem resultados. Verifica a configuração e a estrutura antes de reinstalar ou apagar ficheiros.",
            "steps": steps,
        })

    return checks


def summarize_scanner_snapshot(settings_response=None, manual_response=None, errors=None) -> dict[str, object]:
    """Normalize read-only ShadowMountPlus scanner API responses for display.

    Unsupported endpoints are reported as unavailable rather than treated as a
    failed PS5 connection. The function never initiates a scan or changes config.
    """
    errors = [str(item) for item in (errors or []) if str(item).strip()]

    def successful(response):
        return isinstance(response, dict) and response.get("status", 0) in (0, None)

    settings_ok = successful(settings_response)
    manual_ok = successful(manual_response)
    settings = settings_response if isinstance(settings_response, dict) else {}
    for key in ("settings", "data"):
        nested = settings.get(key)
        if isinstance(nested, dict) and any(k in nested for k in ("scan_paths", "scanpath", "scan_depth")):
            settings = nested
            break

    roots = settings.get("scan_paths", settings.get("scanpath", [])) if settings_ok else []
    if isinstance(roots, str):
        roots = [roots] if roots.strip() else []
    if not isinstance(roots, list):
        roots = []
    scan_paths = [str(item).strip() for item in roots if str(item).strip()]

    manual = manual_response if isinstance(manual_response, dict) else {}
    for key in ("data", "result"):
        nested = manual.get(key)
        if isinstance(nested, dict) and ("paths" in nested or "count" in nested):
            manual = nested
            break
    paths = manual.get("paths", []) if manual_ok else []
    if not isinstance(paths, list):
        paths = []
    manual_paths = []
    for item in paths:
        if isinstance(item, dict):
            value = item.get("path", "")
        else:
            value = item
        value = str(value).strip()
        if value:
            manual_paths.append(value)

    depth = settings.get("scan_depth") if settings_ok else None
    count = manual.get("count", len(manual_paths)) if manual_ok else None
    try:
        count = int(count) if count is not None else None
    except (TypeError, ValueError):
        count = len(manual_paths)

    return {
        "settings_available": settings_ok,
        "manual_available": manual_ok,
        "scan_paths": scan_paths,
        "scan_depth": depth,
        "manual_paths": manual_paths,
        "manual_count": count,
        "errors": errors,
    }


def evaluate_compatibility(context: dict | None = None, knowledge_base: dict | None = None) -> list[dict]:
    """Return only matrix entries whose full, explicitly documented context matches.

    Missing fields never count as a match. Compatibility notes are separate from
    log diagnoses: they are context notices, not claims that an error occurred.
    """
    context = context or {}
    kb = knowledge_base or KNOWLEDGE_BASE
    findings: list[dict] = []
    for entry in kb.get("compatibility_matrix", []):
        conditions = entry.get("conditions", {})
        if not conditions:
            continue
        matches = True
        for key, expected_values in conditions.items():
            observed = str(context.get(key, "") or "").strip()
            if not observed or observed.casefold() in {"unknown", "desconhecido", "não indicado", "nao indicado"}:
                matches = False
                break
            expected = expected_values if isinstance(expected_values, list) else [expected_values]
            if key in {"firmware", "shadowmount_version", "kstuff_version"}:
                tokens = _normalized_version_tokens(observed)
                accepted = set()
                for item in expected:
                    parts = _normalized_version_tokens(str(item))
                    accepted.update(parts or {re.sub(r"[^a-z0-9]", "", str(item).casefold())})
                if not (tokens & accepted):
                    matches = False
                    break
            else:
                normal_observed = re.sub(r"[^a-z0-9.]+", "", observed.casefold())
                normal_expected = [re.sub(r"[^a-z0-9.]+", "", str(item).casefold()) for item in expected]
                if normal_observed not in normal_expected:
                    matches = False
                    break
        if matches:
            findings.append(entry)
    return findings

def extract_metadata(text: str) -> dict[str, list[str]]:
    patterns = {
        "Title IDs": re.compile(r"\b(?:PPSA|CUSA|PPSM|LAPY|FAKE|ITEM|NPXS)[A-Z0-9]{4,6}\b", re.I),
        "Firmware mentions": re.compile(r"(?i)\b(?:firmware|fw|system software)\s*[:=]?\s*(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\b"),
        "Version mentions": re.compile(r"(?i)\b(?:shadowmount(?:plus)?|etahen|kstuff)\s*(?:version|v)?\s*[:= ]\s*(v?\d+(?:\.\d+){1,3}(?:[a-zA-Z0-9.-]+)?)\b"),
    }
    results: dict[str, list[str]] = {}
    for label, pattern in patterns.items():
        values = list(dict.fromkeys(m.group(0).strip() for m in pattern.finditer(text)))
        if values:
            results[label] = values[:12]
    return results

def make_markdown_report(
    text: str,
    findings: Iterable[Finding],
    anonymize: bool = True,
    source_names: Iterable[str] = (),
    context: dict | None = None,
    language: str = "pt",
) -> str:
    """Build a shareable report in Portuguese or English; log evidence is never translated."""
    findings = list(findings)
    source_list = list(source_names)
    evidence_transform = redact if anonymize else (lambda x: x)
    metadata = extract_metadata(text)
    language = "en" if str(language).lower().startswith("en") else "pt"

    if language == "en":
        # Import only when generating an English report to keep the diagnostic core
        # usable without a UI and without making the i18n layer a core dependency.
        from i18n import register_knowledge_base, tr
        register_knowledge_base(KNOWLEDGE_BASE)
        def L(value: str) -> str:
            return tr(value, "en")
    else:
        def L(value: str) -> str:
            return value

    if language == "pt":
        metadata_labels = {
            "Title IDs": "IDs dos títulos",
            "Firmware mentions": "Referências de firmware",
            "Version mentions": "Referências de versão",
        }
    else:
        metadata_labels = {key: key for key in metadata}

    lines = [
        L("# PS5 Jailbreak Doctor — Relatório de diagnóstico"),
        "",
        f"- {L('Versão da ferramenta')}: {APP_VERSION}",
        f"- {L('Base de conhecimento')}: {KNOWLEDGE_BASE.get('database_version', 'desconhecida')} ({len(RULES)} {L('regras locais')})",
        f"- {L('Última revisão da base')}: {KNOWLEDGE_BASE.get('generated_at', 'desconhecida')}",
        f"- {L('Método')}: {L('regras locais; sem envio automático de dados.')}",
        f"- {L('Anonimização de caminhos/IP')}: {L('ativada' if anonymize else 'desativada')}",
        f"- {L('Fontes carregadas')}: {', '.join(source_list) if source_list else L('texto manual / não especificado')}",
        "",
        f"> {L('Este relatório apresenta hipóteses com base nas linhas encontradas. Não confirma a causa sem validação adicional.')}",
        "",
        f"## {L('Metadados detetados')}",
    ]
    if metadata:
        for label, vals in metadata.items():
            lines.append(f"- **{metadata_labels.get(label, label)}:** {', '.join(vals)}")
    else:
        lines.append(f"- {L('Não foram detetados Title IDs, firmware ou versões reconhecíveis.')}")

    if context:
        context_labels = {
            "firmware": "Firmware", "shadowmount_version": "ShadowMountPlus", "kstuff_version": "KStuff Lite",
            "origin_type": "Formato da origem", "storage": "Armazenamento", "trigger": "Quando começou",
        }
        lines.extend(["", f"## {L('Contexto fornecido')}"])
        visible_context = False
        for key, value in context.items():
            if not str(value or "").strip() or str(value).strip().casefold() in {"unknown", "desconhecido", "não indicado", "nao indicado"}:
                continue
            label = L(context_labels.get(key, key))
            display = value
            if key in CONTEXT_DISPLAY:
                display = CONTEXT_DISPLAY[key].get(value, value)
            lines.append(f"- **{label}:** {L(str(display))}")
            visible_context = True
        if not visible_context:
            lines.append(f"- {L('Não foi fornecido contexto adicional.')}")

    timeline = extract_error_timeline(text)
    if timeline:
        kind_labels = {"critical": L("Sinal crítico"), "error": L("Erro"), "warning": L("Aviso")}
        lines.extend(["", f"## {L('Cronologia de eventos')}"])
        for event in timeline:
            event_label = kind_labels.get(str(event.get("kind")), L("Aviso"))
            lines.append(f"- **{L('Linha')} {event['line']} — {event_label}:** {evidence_transform(str(event['text']))}")

    compatibility_notes = evaluate_compatibility(context, KNOWLEDGE_BASE) if context else []
    if compatibility_notes:
        lines.extend(["", f"## {L('Notas de compatibilidade')}"])
        for note in compatibility_notes:
            lines.extend(["", f"### {L(note.get('title', ''))}", f"- **{L('Estado da evidência')}:** {L(note.get('status', ''))}", L(note.get('summary', ''))])
            for source in note.get("sources", []):
                lines.append(f"- {source}")

    lines.extend(["", f"## {L('Resultados')}"])
    if not findings:
        lines.append(L("Não foi encontrada uma regra conhecida. Isso não significa que os logs estejam limpos; pode ser necessária uma regra nova ou contexto adicional."))

    for i, finding in enumerate(findings, 1):
        lines.extend([
            "", f"### {i}. {L(finding.title)}",
            f"- **ID:** `{finding.rule_id}`",
            f"- **{L('Gravidade indicativa')}:** {L(finding.severity)}",
            f"- **{L('Confiança')}:** {L(finding.confidence)}",
            f"- **{L('Tipo de evidência')}:** {L(evidence_status_pt(finding.evidence_status))}",
            f"- **{L('Compatibilidade com contexto')}:** {L(finding.context_relevance)}",
            "", L(finding.summary),
            "", f"**{L('Evidência')}:**",
        ])
        for evidence in finding.evidence:
            lines.append(f"> {evidence_transform(evidence)}")
        if finding.fix_summary:
            fix_type = L(fix_type_pt(finding.fix_type))
            lines.extend(["", f"**{L('Possível correção / orientação')} ({fix_type}):** {L(finding.fix_summary)}"])
        if finding.context_note:
            lines.extend(["", f"**{L('Contexto')}:** {L(finding.context_note)}"])
        if finding.applicability:
            lines.extend(["", f"**{L('Aplicabilidade / limites')}:** {L(finding.applicability)}"])
        if finding.sources:
            lines.extend(["", f"**{L('Fontes')}:**"] + [f"- {url}" for url in finding.sources])
        lines.extend(["", f"**{L('Próximos passos sugeridos')}:**"])
        lines.extend([f"{j}. {L(step)}" for j, step in enumerate(finding.next_steps, 1)])

    lines.extend([
        "", f"## {L('Limites e privacidade')}",
        f"- {L('A análise é local e baseada em assinaturas; a confiança refere-se à interpretação da mensagem, não à causa final.')}",
        f"- {L('Só foram incluídas linhas de evidência correspondentes; o log completo não é incluído automaticamente.')}",
        f"- {L('Revê manualmente o relatório antes de o publicar, especialmente se desativaste a anonimização.')}",
        f"- {L('A ferramenta não executa payloads, não altera configurações, não instala/desinstala títulos e não elimina ficheiros.')}",
        f"- {L('A base inclui relatos de comunidade que podem estar por resolver; uma issue aberta ou workaround relatado não é uma correção universal.')}",
        "",
        f"## {L('Acompanhamento após o teste (opcional)')}",
        f"- **{L('Resultado do diagnóstico')}:** {L('Não testado / Resolveu / Não resolveu')}",
        f"- **{L('Passos que foram testados')}:** ",
        f"- **{L('Informação adicional')}:** ",
        L('Revê e anonimiza o relatório antes de o publicares.'),
        "",
    ])
    return "\n".join(lines)
