"""Rule-based diagnostics for PS5 homebrew logs. Offline and dependency-free."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

APP_VERSION = "0.7.2"

from pathlib import Path
import json
from app_paths import resource_path

KB_PATH = resource_path("knowledge_base.json")

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


def load_knowledge_base() -> dict:
    """Load the editable, local JSON knowledge base without network access."""
    try:
        with KB_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if data.get("schema_version") != 1 or not isinstance(data.get("rules"), list):
            raise ValueError("Schema da base de conhecimento inválido.")
        valid_rules = [r for r in data["rules"] if isinstance(r, dict) and r.get("id") and r.get("patterns")]
        data["rules"] = valid_rules
        return data
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        # Keep the app usable and make the missing KB visible in the status/report.
        return {"schema_version": 1, "database_version": "fallback-empty", "generated_at": "unknown",
                "description": f"Não foi possível carregar knowledge_base.json: {exc}", "rules": []}


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
            observed_versions = re.findall(r"\d+(?:\.\d+)+(?:[a-z][a-z0-9]*(?:[-._][a-z0-9]+)*)?", observed.casefold())
            expected_versions = []
            for value in expected:
                tokens = re.findall(r"\d+(?:\.\d+)+(?:[a-z][a-z0-9]*(?:[-._][a-z0-9]+)*)?", value)
                expected_versions.extend(tokens or [value])
            if any(value in observed_versions for value in expected_versions):
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

def make_markdown_report(text: str, findings: Iterable[Finding], anonymize: bool = True, source_names: Iterable[str] = (), context: dict | None = None) -> str:
    findings = list(findings)
    source_list = list(source_names)
    evidence_transform = redact if anonymize else (lambda x: x)
    metadata = extract_metadata(text)
    lines = [
        "# PS5 Homebrew Doctor — Relatório de diagnóstico",
        "",
        f"- Versão da ferramenta: {APP_VERSION}",
        f"- Base de conhecimento: {KNOWLEDGE_BASE.get('database_version', 'desconhecida')} ({len(RULES)} regras locais)",
        "- Método: regras locais; sem envio automático de dados.",
        f"- Anonimização de caminhos/IP: {'ativada' if anonymize else 'desativada'}",
        f"- Fontes carregadas: {', '.join(source_list) if source_list else 'texto manual / não especificado'}",
        "",
        "> Este relatório apresenta hipóteses com base nas linhas encontradas. Não confirma a causa sem validação adicional.",
        "",
        "## Metadados detetados",
    ]
    if metadata:
        for label, vals in metadata.items():
            lines.append(f"- **{label}:** {', '.join(vals)}")
    else:
        lines.append("- Não foram detetados Title IDs, firmware ou versões reconhecíveis.")
    if context:
        context_labels = {"firmware": "Firmware", "shadowmount_version": "ShadowMountPlus", "kstuff_version": "KStuff Lite",
                          "origin_type": "Formato da origem", "storage": "Armazenamento", "trigger": "Quando começou"}
        lines.extend(["", "## Contexto fornecido"])
        visible_context = False
        for key, value in context.items():
            if not str(value or "").strip() or str(value).strip().casefold() in {"unknown", "desconhecido", "não indicado", "nao indicado"}:
                continue
            label = context_labels.get(key, key)
            display = value
            if key in CONTEXT_DISPLAY:
                display = CONTEXT_DISPLAY[key].get(value, value)
            lines.append(f"- **{label}:** {display}")
            visible_context = True
        if not visible_context:
            lines.append("- Não foi fornecido contexto adicional.")
    lines.extend(["", "## Resultados"])
    if not findings:
        lines.append("Não foi encontrada uma regra conhecida. Isso não significa que os logs estejam limpos; pode ser necessária uma regra nova ou contexto adicional.")
    for i, finding in enumerate(findings, 1):
        lines.extend([
            "", f"### {i}. {finding.title}",
            f"- **ID:** `{finding.rule_id}`",
            f"- **Gravidade indicativa:** {finding.severity}",
            f"- **Confiança:** {finding.confidence}",
            f"- **Tipo de evidência:** {evidence_status_pt(finding.evidence_status)}",
            f"- **Compatibilidade com contexto:** {finding.context_relevance}",
            "", finding.summary,
            "", "**Evidência:**",
        ])
        for evidence in finding.evidence:
            lines.append(f"> {evidence_transform(evidence)}")
        if finding.fix_summary:
            lines.extend(["", f"**Possível correção / orientação ({fix_type_pt(finding.fix_type)}):** {finding.fix_summary}"])
        if finding.context_note:
            lines.extend(["", f"**Contexto:** {finding.context_note}"])
        if finding.applicability:
            lines.extend(["", f"**Aplicabilidade / limites:** {finding.applicability}"])
        if finding.sources:
            lines.extend(["", "**Fontes:**"] + [f"- {url}" for url in finding.sources])
        lines.extend(["", "**Próximos passos sugeridos:**"])
        lines.extend([f"{j}. {step}" for j, step in enumerate(finding.next_steps, 1)])
    lines.extend([
        "", "## Limites e privacidade",
        "- A análise é local e baseada em assinaturas; a confiança refere-se à interpretação da mensagem, não à causa final.",
        "- Só foram incluídas linhas de evidência correspondentes; o log completo não é incluído automaticamente.",
        "- Revê manualmente o relatório antes de o publicar, especialmente se desativaste a anonimização.",
        "- A ferramenta não executa payloads, não altera configurações, não instala/desinstala títulos e não elimina ficheiros.",
        "- A base inclui relatos de comunidade que podem estar por resolver; uma issue aberta ou workaround relatado não é uma correção universal.",
        "",
    ])
    return "\n".join(lines)
