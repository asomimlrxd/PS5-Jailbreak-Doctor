from __future__ import annotations

import json
import os
import threading
import urllib.error
from datetime import datetime, timezone
import urllib.request
import webbrowser
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path

import doctor_core
from doctor_core import (
    APP_VERSION, KNOWLEDGE_BASE, RULES, analyze_logs, evidence_status_pt,
    fix_type_pt, make_markdown_report, build_preflight_checks, extract_error_timeline, evaluate_compatibility,
    summarize_scanner_snapshot,
)
from safe_actions import list_actions, rename_for_rule, rollback_action
from session_utils import format_source_blocks
from app_paths import data_path
from updates import check_for_updates, download_update, install_update, latest_backup, restore_last_backup, UpdateError
from relay_client import (discover_relay, send_relay_elf, RelayError, RELAY_PORT, LOADER_PORT,
                           preferred_connection_mode, preferred_connection_port)
from i18n import set_language as set_ui_language, tr, register_knowledge_base, install_tkinter_translation

register_knowledge_base(KNOWLEDGE_BASE)
install_tkinter_translation()

# Two accessible, low-clutter desktop palettes. The selected theme is persisted locally.
DEFAULT_THEME = "dark"
THEMES = {
    "light": {
        "BG": "#ffffff", "PANEL": "#f7f9fc", "PANEL_ALT": "#edf2f7",
        "INPUT": "#ffffff", "TEXT": "#1d2735", "MUTED": "#586779",
        "ACCENT": "#3d705b", "GREEN": "#16764b", "AMBER": "#875900",
        "RED": "#b42318", "BORDER": "#d8e0e8", "ACCENT_ACTIVE": "#315b4b",
        "ACCENT_DISABLED": "#a7b8ad", "BUTTON_BG": "#3f725d", "BUTTON_ACTIVE": "#315b4b",
        "BUTTON_DISABLED": "#a7b8ad", "DISABLED_BG": "#eef1f4",
        "DISABLED_TEXT": "#8a96a3", "SELECT_TEXT": "#ffffff",
    },
    "dark": {
        "BG": "#0b0b0d", "PANEL": "#17191d", "PANEL_ALT": "#22252b",
        "INPUT": "#101114", "TEXT": "#f1f3f6", "MUTED": "#a6afbb",
        "ACCENT": "#8bb8a1", "GREEN": "#75d6a3", "AMBER": "#ffd078",
        "RED": "#ff8983", "BORDER": "#383d46", "ACCENT_ACTIVE": "#6f9f87",
        "ACCENT_DISABLED": "#465b4e", "BUTTON_BG": "#456b57", "BUTTON_ACTIVE": "#365744",
        "BUTTON_DISABLED": "#394a3f", "DISABLED_BG": "#202329",
        "DISABLED_TEXT": "#737d8a", "SELECT_TEXT": "#ffffff",
    },
}


def _set_palette(theme_name: str) -> dict:
    """Update the active palette used by Tk widgets and helpers."""
    selected = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    globals().update(selected)
    return selected


_set_palette(DEFAULT_THEME)

SETTINGS_PATH = data_path("settings.json")
RESOLUTION_HISTORY_PATH = data_path("resolution_history.json")

ORIGIN_OPTIONS = {
    "unknown": "Não indicado", "folder": "Pasta de jogo", "image_pfs": "Imagem .ffpfs/.ffpfsc",
    "image_lz4": "Imagem LZ4", "installed_title": "Título já instalado", "other": "Outro formato",
}
STORAGE_OPTIONS = {
    "unknown": "Não indicado", "usb": "USB", "internal": "SSD interno",
    "transfer_between": "Transferência USB ↔ SSD interno",
}
TRIGGER_OPTIONS = {
    "unknown": "Não indicado", "after_resume": "Após modo de repouso", "after_exit": "Após sair do jogo",
    "after_update": "Após atualizar payload/ferramenta", "registration": "Durante instalação/registo",
    "launch": "Ao iniciar o jogo", "transfer": "Ao copiar/mover ficheiros",
    "all_titles": "Em vários jogos", "one_title": "Apenas num jogo",
}

ORIGIN_OPTIONS_PT = dict(ORIGIN_OPTIONS)
STORAGE_OPTIONS_PT = dict(STORAGE_OPTIONS)
TRIGGER_OPTIONS_PT = dict(TRIGGER_OPTIONS)
ORIGIN_OPTIONS_EN = {"unknown": "Not specified", "folder": "Game folder", "image_pfs": "Image .ffpfs/.ffpfsc", "image_lz4": "LZ4 image", "installed_title": "Installed title", "other": "Other format"}
STORAGE_OPTIONS_EN = {"unknown": "Not specified", "usb": "USB", "internal": "Internal SSD", "transfer_between": "USB ↔ Internal SSD transfer"}
TRIGGER_OPTIONS_EN = {"unknown": "Not specified", "after_resume": "After rest mode", "after_exit": "After closing a game", "after_update": "After payload/tool update", "registration": "During install/registration", "launch": "When launching a game", "transfer": "During file copy/move", "all_titles": "Multiple titles", "one_title": "One title only"}

def _set_context_option_language(language: str):
    global ORIGIN_OPTIONS, STORAGE_OPTIONS, TRIGGER_OPTIONS
    if language == "en":
        ORIGIN_OPTIONS, STORAGE_OPTIONS, TRIGGER_OPTIONS = dict(ORIGIN_OPTIONS_EN), dict(STORAGE_OPTIONS_EN), dict(TRIGGER_OPTIONS_EN)
    else:
        ORIGIN_OPTIONS, STORAGE_OPTIONS, TRIGGER_OPTIONS = dict(ORIGIN_OPTIONS_PT), dict(STORAGE_OPTIONS_PT), dict(TRIGGER_OPTIONS_PT)

def _context_option_code(key: str, value: str) -> str:
    """Accept internal codes and labels from either language for old settings files."""
    groups = {
        "origin_type": (ORIGIN_OPTIONS_PT, ORIGIN_OPTIONS_EN),
        "storage": (STORAGE_OPTIONS_PT, STORAGE_OPTIONS_EN),
        "trigger": (TRIGGER_OPTIONS_PT, TRIGGER_OPTIONS_EN),
    }
    for options in groups.get(key, ()): 
        if value in options:
            return value
        for code, label in options.items():
            if value == label:
                return code
    return value or "unknown"


# Store resolution outcomes as stable codes, never as the currently selected UI language.
_RESULT_LABELS_PT = {
    "not_tested": "Ainda não testado",
    "in_progress": "Em teste",
    "resolved": "Resolveu",
    "not_resolved": "Não resolveu",
    "not_applied": "Não apliquei",
}
_RESULT_ALIASES = {label.casefold(): code for code, label in _RESULT_LABELS_PT.items()}
_RESULT_ALIASES.update({tr(label, "en").casefold(): code for code, label in _RESULT_LABELS_PT.items()})


def _result_code(value) -> str:
    """Normalize current and legacy PT/EN outcome labels to a stable history code."""
    raw = str(value or "").strip()
    folded = raw.casefold()
    if folded in _RESULT_LABELS_PT:
        return folded
    return _RESULT_ALIASES.get(folded, raw or "?")


def _result_label(value) -> str:
    """Display a result code or legacy PT/EN label in the active UI language."""
    code = _result_code(value)
    label = _RESULT_LABELS_PT.get(code)
    return tr(label) if label else str(value or "?")


def _action_status_label(value) -> str:
    """Translate the internal status codes used by the reversible-action journal."""
    labels = {
        "renamed": "Nome alterado",
        "reverted": "Revertido",
        "rolled_back": "Revertido",
    }
    raw = str(value or "?")
    return tr(labels.get(raw.casefold(), raw))


def api_post(host: str, port: str, route: str, payload: dict, timeout: float = 5.0):
    host = host.strip().replace("http://", "").replace("https://", "").strip("/")
    if not host or any(ch in host for ch in "/?#@"):
        raise ValueError("Indica o IP ou nome de anfitrião da PS5, sem caminho nem credenciais.")
    port_num = int(port)
    if not 1 <= port_num <= 65535:
        raise ValueError("A porta tem de estar entre 1 e 65535.")
    url = f"http://{host}:{port_num}{route}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(350_000)
        charset = response.headers.get_content_charset() or "utf-8"
    try:
        return json.loads(raw.decode(charset, errors="replace"))
    except json.JSONDecodeError:
        return {"raw_text": raw.decode(charset, errors="replace")}


def response_to_text(obj) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(response_to_text(item) for item in obj)
    if isinstance(obj, dict):
        for key in ("text", "log", "content", "data", "lines", "output", "debug_log", "kernel_log", "message"):
            if key in obj:
                value = obj[key]
                if isinstance(value, (str, list)):
                    return response_to_text(value)
                if isinstance(value, dict):
                    maybe = response_to_text(value)
                    if maybe:
                        return maybe
        if "raw_text" in obj:
            return obj["raw_text"]
        return json.dumps(obj, ensure_ascii=False, indent=2)
    return str(obj)


class ScrollableFrame(ttk.Frame):
    """A lightweight scrollable frame suitable for a stack of diagnostic cards."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self, style="App.TFrame")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class DoctorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = self._load_settings()
        saved_connection_mode = preferred_connection_mode(self.settings)
        # Relay mode is the default for fresh and legacy installs: no config.ini edits.
        self.settings["connection_mode"] = saved_connection_mode
        self.language = "en" if self.settings.get("language") == "en" else "pt"
        set_ui_language(self.language)
        _set_context_option_language(self.language)
        self.theme_name = self.settings.get("theme", DEFAULT_THEME)
        if self.theme_name not in THEMES:
            self.theme_name = DEFAULT_THEME
        _set_palette(self.theme_name)
        self.title(f"PS5 Jailbreak Doctor v{APP_VERSION}")
        self.geometry("1120x760")
        self.minsize(920, 620)
        self.configure(bg=BG)
        self._status_kind = "info"
        self._status_source = "Pronto — importa logs ou obtém os logs da PS5."
        self._conn_status_source = "PS5 não ligada"
        self._api_info_source = "Ainda não ligado. Clica em «Testar ligação» para começar."
        self._source_status_source = "Origem: ainda não há logs carregados"
        self.sources: list[str] = []
        self.demo_mode = False
        self.source_status = tk.StringVar(value=tr("Origem: ainda não há logs carregados"))
        self.findings = []
        self.last_api_version = ""
        self.last_scanner_snapshot = None
        self.last_analyzed_text = ""
        self.last_analyzed_context = {}
        self._style()
        self._build()
        self._set_status("Pronto — importa logs ou obtém os logs da PS5.")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Control-o>", lambda _e: self.open_files())
        self.bind("<Control-Return>", lambda _e: self.analyze())
        self.show_welcome()

    @staticmethod
    def _load_settings() -> dict:
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save_settings(self):
        data = {"host": self.host.get().strip(), "port": self.port.get().strip(), "theme": self.theme_name, "language": self.language,
                "connection_mode": getattr(self, "connection_mode_code", self.settings.get("connection_mode", "relay"))}
        if hasattr(self, "context_vars"):
            data["context"] = self._get_context()
        try:
            SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            # Preferences are optional; failure to save must not block closing.
            pass

    def on_close(self):
        self._save_settings()
        self.destroy()

    def _style(self):
        style = ttk.Style(self)
        # Clam provides consistent colours and padding across supported Windows installs.
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("App.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Alt.TFrame", background=PANEL_ALT)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("PanelSub.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 21, "bold"))
        style.configure("Section.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 14, "bold"))
        style.configure("Source.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 9, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(11, 8), background=PANEL,
                        foreground=TEXT, bordercolor=BORDER, focusthickness=1, focuscolor=ACCENT)
        style.map("TButton", background=[("active", PANEL_ALT), ("disabled", DISABLED_BG)],
                  foreground=[("disabled", DISABLED_TEXT)])
        style.configure("TMenubutton", font=("Segoe UI", 10), padding=(11, 8), background=PANEL,
                        foreground=TEXT, bordercolor=BORDER, focusthickness=1, focuscolor=ACCENT)
        style.map("TMenubutton", background=[("active", PANEL_ALT)], foreground=[("active", TEXT)])
        # The primary action uses a restrained sage/green rather than a bright blue.
        style.configure("Accent.TButton", background=BUTTON_BG, foreground=SELECT_TEXT,
                        font=("Segoe UI", 10, "bold"), padding=(13, 9), bordercolor=BUTTON_BG)
        style.map("Accent.TButton", background=[("active", BUTTON_ACTIVE), ("disabled", BUTTON_DISABLED)],
                  bordercolor=[("active", BUTTON_ACTIVE), ("disabled", BUTTON_DISABLED)],
                  foreground=[("disabled", SELECT_TEXT)])
        style.configure("TEntry", fieldbackground=INPUT, foreground=TEXT, insertcolor=TEXT,
                        padding=7, bordercolor=BORDER)
        style.configure("TCombobox", fieldbackground=INPUT, background=PANEL_ALT, foreground=TEXT,
                        arrowcolor=TEXT, padding=6, bordercolor=BORDER)
        style.map("TCombobox", fieldbackground=[("readonly", INPUT), ("disabled", PANEL_ALT)],
                  foreground=[("readonly", TEXT), ("disabled", MUTED)],
                  background=[("readonly", PANEL_ALT), ("active", PANEL_ALT)])
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background=PANEL_ALT, foreground=MUTED, padding=(16, 9),
                        font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", PANEL)], foreground=[("selected", TEXT)])
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", PANEL)], foreground=[("active", TEXT)])
        style.configure("TSeparator", background=BORDER)
        style.configure("TScrollbar", background=PANEL_ALT, troughcolor=BG, bordercolor=BORDER,
                        arrowcolor=TEXT, lightcolor=PANEL_ALT, darkcolor=PANEL_ALT)
        style.configure("Link.TButton", background=PANEL, foreground=ACCENT, borderwidth=0,
                        padding=(0, 5), font=("Segoe UI", 10, "underline"))
        style.map("Link.TButton", background=[("active", PANEL_ALT)], foreground=[("active", ACCENT_ACTIVE)])
        style.configure("ErrorMetric.TLabel", background=PANEL, foreground=RED, font=("Segoe UI", 14, "bold"))
        style.configure("WarningMetric.TLabel", background=PANEL, foreground=AMBER, font=("Segoe UI", 14, "bold"))
        style.configure("AccentMetric.TLabel", background=PANEL, foreground=ACCENT, font=("Segoe UI", 14, "bold"))

    def change_language(self, _event=None):
        """Rebuild the UI in the selected language while preserving the current session."""
        choice = self.language_var.get() if hasattr(self, "language_var") else "PT - Português"
        new_language = "en" if choice.startswith("EN") else "pt"
        if new_language == self.language:
            return

        try:
            log_text = self.log_text.get("1.0", "end-1c")
            active_tab = self.tabs.index(self.tabs.select()) if self.tabs.select() else 0
            current_context = self._get_context()
        except (AttributeError, tk.TclError):
            log_text, active_tab, current_context = "", 0, {}

        state = {
            "log_text": log_text, "active_tab": active_tab, "context": current_context,
            "host": self.host.get().strip() if hasattr(self, "host") else str(self.settings.get("host", "")),
            "port": self.port.get().strip() if hasattr(self, "port") else str(self.settings.get("port", RELAY_PORT)),
            "connection_mode": getattr(self, "connection_mode_code", self.settings.get("connection_mode", "relay")),
            "sources": list(getattr(self, "sources", [])),
            "demo_mode": bool(getattr(self, "demo_mode", False)),
            "findings": list(getattr(self, "findings", [])),
            "last_analyzed_text": getattr(self, "last_analyzed_text", ""),
            "last_analyzed_context": dict(getattr(self, "last_analyzed_context", {})),
            "last_api_version": getattr(self, "last_api_version", ""),
            "status_source": getattr(self, "_status_source", "Pronto para começar"),
            "status_kind": getattr(self, "_status_kind", "info"),
            "conn_status_source": getattr(self, "_conn_status_source", "PS5 não ligada"),
            "api_info_source": getattr(self, "_api_info_source", "Ainda não ligado. Clica em «Testar ligação» para começar."),
            "source_status_source": getattr(self, "_source_status_source", "Origem: ainda não há logs carregados"),
        }
        self.settings["context"] = current_context
        self.settings["language"] = new_language
        self.settings["host"] = state["host"]
        self.settings["port"] = state["port"]
        self.settings["connection_mode"] = state["connection_mode"]
        self.language = new_language
        set_ui_language(new_language)
        _set_context_option_language(new_language)

        # Existing widgets are recreated from the original Portuguese strings; the
        # localization layer renders them in the selected language. Session data stays local.
        for child in self.winfo_children():
            child.destroy()
        _set_palette(self.theme_name)
        self.configure(bg=BG)
        self._style()
        self._build()

        self.sources = state["sources"]
        self.demo_mode = state["demo_mode"]
        self.findings = state["findings"]
        self.last_analyzed_text = state["last_analyzed_text"]
        self.last_analyzed_context = state["last_analyzed_context"]
        self.last_api_version = state["last_api_version"]
        if state["log_text"]:
            self.log_text.insert("1.0", state["log_text"])
        self._set_source_status(state["source_status_source"])
        self._set_conn_status(state["conn_status_source"])
        self._set_api_info(state["api_info_source"])

        self._clear_cards()
        if state["log_text"]:
            self._render_timeline(extract_error_timeline(state["log_text"]))
            self._render_compatibility_notices(state["context"])
        if self.findings:
            for index, finding in enumerate(self.findings, 1):
                self._render_finding(finding, index)
            error_count = sum(1 for finding in self.findings if any(x in finding.severity.lower() for x in ("erro", "crít", "critical")))
            self.metric_vars["errors"].set(str(error_count))
            self.metric_vars["warnings"].set(str(max(0, len(self.findings) - error_count)))
            self.metric_vars["matches"].set(tr(f"{len(self.findings)} resultado(s)"))
        elif state["log_text"].strip():
            self._add_empty_card(
                "Não foram encontrados sinais de erro reconhecíveis",
                "Isto não garante que esteja tudo bem. Confirma se o log inclui as linhas em redor do problema e verifica as notas de contexto acima.",
                icon="i", color=ACCENT,
            )
            self.metric_vars["errors"].set("0")
            self.metric_vars["warnings"].set("0")
            self.metric_vars["matches"].set(tr("0 resultado(s)"))
        else:
            self.show_welcome()
        try:
            self.tabs.select(min(state["active_tab"], len(self.tabs.tabs()) - 1))
        except (tk.TclError, ValueError):
            pass
        self._set_status(state["status_source"], state["status_kind"])
        self._save_settings()

    def _theme_button_text(self) -> str:
        return tr("Tema escuro") if self.theme_name == "light" else tr("Tema claro")

    def toggle_theme(self):
        """Switch white/black appearance and preserve it for the next launch."""
        old_palette = dict(THEMES[self.theme_name])
        new_name = "dark" if self.theme_name == "light" else "light"
        new_palette = dict(THEMES[new_name])
        self.theme_name = new_name
        _set_palette(new_name)
        self.configure(bg=BG)
        self._style()
        self._retheme_tree(self, old_palette, new_palette)
        if hasattr(self, "more_menu"):
            try:
                self.more_menu.configure(bg=PANEL, fg=TEXT, activebackground=PANEL_ALT,
                                         activeforeground=TEXT, disabledforeground=MUTED)
            except tk.TclError:
                pass
        if hasattr(self, "theme_button"):
            self.theme_button.configure(text=tr(self._theme_button_text()))
        if hasattr(self, "status") and hasattr(self, "status_icon"):
            self.status_icon.configure(background=PANEL)
            self._set_status(self._status_source, self._status_kind)
        self._save_settings()

    def _retheme_tree(self, widget, old_palette: dict, new_palette: dict):
        """Refresh non-themed Tk widgets as well as ttk styles in open windows."""
        semantic_foregrounds = ("TEXT", "MUTED", "ACCENT", "GREEN", "AMBER", "RED")
        try:
            if isinstance(widget, (tk.Tk, tk.Toplevel)):
                widget.configure(bg=new_palette["BG"])
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=new_palette["BG"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=new_palette["INPUT"], fg=new_palette["TEXT"],
                                 insertbackground=new_palette["TEXT"],
                                 selectbackground=new_palette["ACCENT"],
                                 selectforeground=new_palette["SELECT_TEXT"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=new_palette["INPUT"], fg=new_palette["TEXT"],
                                 selectbackground=new_palette["ACCENT"],
                                 selectforeground=new_palette["SELECT_TEXT"])
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=new_palette["PANEL"], fg=new_palette["TEXT"],
                                 activebackground=new_palette["PANEL"],
                                 activeforeground=new_palette["TEXT"], selectcolor=new_palette["INPUT"])
            elif isinstance(widget, tk.Menu):
                widget.configure(bg=new_palette["PANEL"], fg=new_palette["TEXT"],
                                 activebackground=new_palette["PANEL_ALT"],
                                 activeforeground=new_palette["TEXT"], disabledforeground=new_palette["MUTED"])
            else:
                # Some ttk labels use explicit semantic foregrounds instead of a named style.
                if isinstance(widget, ttk.Label):
                    try:
                        old_fg = str(widget.cget("foreground"))
                        for key in semantic_foregrounds:
                            if old_fg.lower() == old_palette[key].lower():
                                widget.configure(foreground=new_palette[key])
                                break
                    except tk.TclError:
                        pass
                # The status dot is the only ttk label with an explicit panel background.
                if getattr(self, "status_icon", None) is widget:
                    widget.configure(background=new_palette["PANEL"])
        except tk.TclError:
            pass
        try:
            children = widget.winfo_children()
        except (tk.TclError, AttributeError):
            children = []
        for child in children:
            self._retheme_tree(child, old_palette, new_palette)

    def _build(self):
        # Compact, conventional desktop layout: a few clear actions and one status line.
        header = ttk.Frame(self, padding=(20, 16, 20, 10))
        header.pack(fill="x")
        left = ttk.Frame(header)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text="PS5 Jailbreak Doctor", style="Title.TLabel").pack(anchor="w")
        ttk.Label(left, text="Ajuda a perceber erros em homebrew da PS5.", style="Sub.TLabel").pack(anchor="w", pady=(3, 0))
        right = ttk.Frame(header)
        right.pack(side="right", anchor="n")
        ttk.Label(right, text=f"v{APP_VERSION}", font=("Segoe UI", 9, "bold")).pack(anchor="e")
        self.rules_count_label = ttk.Label(right, text=f"{len(RULES)} verificações locais", style="Sub.TLabel")
        self.rules_count_label.pack(anchor="e", pady=(2, 0))

        actions = ttk.Frame(self, padding=(20, 0, 20, 10))
        actions.pack(fill="x")
        self.btn_fetch = ttk.Button(actions, text="Obter logs da PS5", command=self.fetch_logs)
        self.btn_fetch.pack(side="left", padx=(0, 8))
        self.btn_import = ttk.Button(actions, text="Importar logs…", command=self.open_files)
        self.btn_import.pack(side="left", padx=(0, 8))
        self.btn_sample = ttk.Button(actions, text="Ver exemplo fictício", command=self.load_sample)
        self.btn_sample.pack(side="left", padx=(0, 8))
        self.btn_analyze = ttk.Button(actions, text="Analisar logs", style="Accent.TButton", command=self.analyze)
        self.btn_analyze.pack(side="left", padx=(4, 0))

        self.anonymize = tk.BooleanVar(value=True)
        more_button = ttk.Menubutton(actions, text="Mais opções ▾")
        self.more_menu = tk.Menu(more_button, tearoff=0, bg=PANEL, fg=TEXT,
                                 activebackground=PANEL_ALT, activeforeground=TEXT,
                                 disabledforeground=MUTED, relief="solid", borderwidth=1)
        self.more_menu.add_command(label="Guardar relatório…", command=self.save_report)
        self.more_menu.add_command(label="Histórico e reversões…", command=self.open_history)
        self.more_menu.add_separator()
        self.more_menu.add_command(label="Atualizar base de diagnósticos…", command=self.check_diagnostic_updates)
        self.more_menu.add_command(label="Reverter atualização da base…", command=self.rollback_diagnostic_update)
        self.more_menu.add_separator()
        self.more_menu.add_checkbutton(label="Anonimizar relatório", variable=self.anonymize)
        self.more_menu.add_command(label="Limpar sessão", command=self.clear)
        more_button["menu"] = self.more_menu
        more_button.pack(side="right")
        self.theme_button = ttk.Button(actions, text=self._theme_button_text(), command=self.toggle_theme)
        self.theme_button.pack(side="right", padx=(0, 8))
        self.language_var = tk.StringVar(value="PT - Português" if self.language == "pt" else "EN - English")
        self.language_combo = ttk.Combobox(actions, textvariable=self.language_var, values=("PT - Português", "EN - English"), state="readonly", width=13)
        self.language_combo.pack(side="right", padx=(0, 8))
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)

        status_frame = ttk.Frame(self, style="Panel.TFrame", padding=(12, 8))
        status_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.status_icon = ttk.Label(status_frame, text="●", background=PANEL, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        self.status_icon.pack(side="left", padx=(0, 8))
        self.status = tk.StringVar(value=tr("Pronto para começar"))
        ttk.Label(status_frame, textvariable=self.status, style="Panel.TLabel").pack(side="left", fill="x", expand=True)
        self.conn_status = tk.StringVar(value=tr("PS5 não ligada"))
        ttk.Label(status_frame, textvariable=self.conn_status, style="Panel.TLabel", font=("Segoe UI", 9)).pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        self.diag_tab = ttk.Frame(self.tabs, style="App.TFrame", padding=(0, 6, 0, 0))
        self.logs_tab = ttk.Frame(self.tabs, style="App.TFrame", padding=(0, 6, 0, 0))
        self.connection_tab = ttk.Frame(self.tabs, style="App.TFrame", padding=(0, 6, 0, 0))
        self.tabs.add(self.diag_tab, text="Resultado")
        self.tabs.add(self.logs_tab, text="Logs")
        self.tabs.add(self.connection_tab, text="Ligação à PS5")
        self._build_diagnostics_tab()
        self._build_logs_tab()
        self._build_connection_tab()

        footer = ttk.Frame(self, padding=(20, 0, 20, 10))
        footer.pack(fill="x")
        ttk.Label(footer, text="Os logs são analisados neste PC. A app não altera a consola.", style="Sub.TLabel").pack(anchor="w")

    def _build_diagnostics_tab(self):
        intro = ttk.Frame(self.diag_tab, padding=(14, 8, 14, 8))
        intro.pack(fill="x")
        title_line = ttk.Frame(intro)
        title_line.pack(fill="x")
        ttk.Label(title_line, text="Resultado da análise", style="Section.TLabel").pack(side="left")
        self.context_open = False
        self.context_button = ttk.Button(title_line, text="Detalhes técnicos (opcional) ▸", style="Link.TButton", command=self.toggle_context)
        self.context_button.pack(side="right")
        ttk.Label(intro, text="Abre um resultado para ver o que foi encontrado e os passos a seguir.", style="Sub.TLabel").pack(anchor="w", pady=(3, 0))
        self.source_status_label = ttk.Label(intro, textvariable=self.source_status, style="Source.TLabel")
        self.source_status_label.pack(anchor="w", pady=(5, 0))

        self.context_vars = {}
        saved_context = self.settings.get("context", {}) if isinstance(self.settings.get("context", {}), dict) else {}
        context_panel = ttk.Frame(self.diag_tab, style="Panel.TFrame", padding=(12, 9))
        self.context_panel = context_panel
        ttk.Label(context_panel, text="Informação opcional para afinar o diagnóstico", style="Panel.TLabel", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 7))
        ttk.Label(context_panel, text="Firmware", style="PanelSub.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.context_vars["firmware"] = tk.StringVar(value=saved_context.get("firmware", ""))
        ttk.Entry(context_panel, textvariable=self.context_vars["firmware"], width=10).grid(row=1, column=1, sticky="w", padx=(0, 12))
        ttk.Label(context_panel, text="ShadowMountPlus", style="PanelSub.TLabel").grid(row=1, column=2, sticky="w", padx=(0, 5))
        self.context_vars["shadowmount_version"] = tk.StringVar(value=saved_context.get("shadowmount_version", ""))
        ttk.Entry(context_panel, textvariable=self.context_vars["shadowmount_version"], width=15).grid(row=1, column=3, sticky="w", padx=(0, 12))
        ttk.Label(context_panel, text="KStuff Lite", style="PanelSub.TLabel").grid(row=1, column=4, sticky="w", padx=(0, 5))
        self.context_vars["kstuff_version"] = tk.StringVar(value=saved_context.get("kstuff_version", ""))
        ttk.Entry(context_panel, textvariable=self.context_vars["kstuff_version"], width=13).grid(row=1, column=5, sticky="w")

        ttk.Label(context_panel, text="Formato", style="PanelSub.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(8, 0))
        self.context_vars["origin_type"] = tk.StringVar(value=saved_context.get("origin_type", "unknown"))
        self.origin_combo = ttk.Combobox(context_panel, textvariable=self.context_vars["origin_type"], width=21, state="readonly", values=list(ORIGIN_OPTIONS.values()))
        self.origin_combo.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=(8, 0))
        ttk.Label(context_panel, text="Onde está o jogo", style="PanelSub.TLabel").grid(row=2, column=2, sticky="w", padx=(0, 5), pady=(8, 0))
        self.context_vars["storage"] = tk.StringVar(value=saved_context.get("storage", "unknown"))
        self.storage_combo = ttk.Combobox(context_panel, textvariable=self.context_vars["storage"], width=24, state="readonly", values=list(STORAGE_OPTIONS.values()))
        self.storage_combo.grid(row=2, column=3, sticky="w", padx=(0, 12), pady=(8, 0))
        ttk.Label(context_panel, text="Quando começou", style="PanelSub.TLabel").grid(row=2, column=4, sticky="w", padx=(0, 5), pady=(8, 0))
        self.context_vars["trigger"] = tk.StringVar(value=saved_context.get("trigger", "unknown"))
        self.trigger_combo = ttk.Combobox(context_panel, textvariable=self.context_vars["trigger"], width=25, state="readonly", values=list(TRIGGER_OPTIONS.values()))
        self.trigger_combo.grid(row=2, column=5, sticky="w", pady=(8, 0))
        self.context_vars["origin_type"].set(ORIGIN_OPTIONS.get(_context_option_code("origin_type", str(saved_context.get("origin_type", "unknown"))), ORIGIN_OPTIONS["unknown"]))
        self.context_vars["storage"].set(STORAGE_OPTIONS.get(_context_option_code("storage", str(saved_context.get("storage", "unknown"))), STORAGE_OPTIONS["unknown"]))
        self.context_vars["trigger"].set(TRIGGER_OPTIONS.get(_context_option_code("trigger", str(saved_context.get("trigger", "unknown"))), TRIGGER_OPTIONS["unknown"]))
        ttk.Button(context_panel, text="Limpar", command=self.clear_context).grid(row=3, column=5, sticky="e", pady=(8, 0))
        ttk.Label(context_panel, text="Estes dados só ajudam a comparar o teu caso com os relatos existentes.", style="PanelSub.TLabel", wraplength=980).grid(row=3, column=0, columnspan=5, sticky="w", pady=(8, 0))

        self.summary_row = ttk.Frame(self.diag_tab, padding=(14, 0, 14, 8))
        self.summary_row.pack(fill="x")
        self.metric_vars = {
            "errors": tk.StringVar(value="—"),
            "warnings": tk.StringVar(value="—"),
            "matches": tk.StringVar(value=tr("Ainda não analisado")),
        }
        self._metric(self.summary_row, "ERROS", self.metric_vars["errors"], RED, 0)
        self._metric(self.summary_row, "AVISOS", self.metric_vars["warnings"], AMBER, 1)
        self._metric(self.summary_row, "RESULTADO", self.metric_vars["matches"], ACCENT, 2, wide=True)
        self.context_panel.pack_forget()  # Advanced fields start collapsed to keep the main view simple.
        self.cards = ScrollableFrame(self.diag_tab)
        self.cards.pack(fill="both", expand=True, padx=14, pady=(0, 10))

    def toggle_context(self):
        if self.context_open:
            self.context_panel.pack_forget()
            self.context_open = False
            self.context_button.configure(text=tr("Detalhes técnicos (opcional) ▸"))
        else:
            self.context_panel.pack(fill="x", padx=14, pady=(0, 9), before=self.summary_row)
            self.context_open = True
            self.context_button.configure(text=tr("Ocultar detalhes técnicos ▾"))

    def _metric(self, parent, title, var, color, column, wide=False):
        card = ttk.Frame(parent, style="Panel.TFrame", padding=(12, 9))
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 0))
        parent.columnconfigure(column, weight=2 if wide else 1)
        ttk.Label(card, text=title, style="PanelSub.TLabel", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        value_style = {"ERROS": "ErrorMetric.TLabel", "AVISOS": "WarningMetric.TLabel"}.get(title, "AccentMetric.TLabel")
        ttk.Label(card, textvariable=var, style=value_style).pack(anchor="w", pady=(4, 0))

    def _build_logs_tab(self):
        toolbar = ttk.Frame(self.logs_tab, padding=(14, 8, 14, 10))
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Logs completos", style="Section.TLabel").pack(side="left")
        ttk.Button(toolbar, text="Importar ficheiros…", command=self.open_files).pack(side="right")
        ttk.Label(self.logs_tab, text="Podes colar texto diretamente nesta área. Os logs ficam neste computador.", style="Sub.TLabel").pack(anchor="w", padx=16, pady=(0, 8))
        self.log_text = ScrolledText(self.logs_tab, wrap="word", undo=True, bg=INPUT, fg=TEXT,
                                     insertbackground=TEXT, selectbackground=ACCENT,
                                     selectforeground=SELECT_TEXT, relief="flat", borderwidth=0,
                                     font=("Consolas", 10), padx=14, pady=14)
        self.log_text.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_connection_tab(self):
        intro = ttk.Frame(self.connection_tab, padding=(16, 10, 16, 12))
        intro.pack(fill="x")
        ttk.Label(intro, text="Ligar à PS5", style="Section.TLabel").pack(anchor="w")
        ttk.Label(intro, text="Liga ao ShadowMountPlus sem editar manualmente o config.ini.", style="Sub.TLabel", wraplength=850).pack(anchor="w", pady=(3, 0))

        panel = ttk.Frame(self.connection_tab, style="Panel.TFrame", padding=18)
        panel.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Label(panel, text="MODO DE LIGAÇÃO", style="Panel.TLabel", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 12))
        self.connection_mode_code = self.settings.get("connection_mode", "relay")
        self.connection_mode_var = tk.StringVar(value=tr("Relay ELF (sem alterar config.ini)") if self.connection_mode_code == "relay" else tr("API direta (requer acesso pela LAN)"))
        self.connection_mode_combo = ttk.Combobox(
            panel, textvariable=self.connection_mode_var, state="readonly", width=38,
            values=(tr("Relay ELF (sem alterar config.ini)"), tr("API direta (requer acesso pela LAN)")),
        )
        self.connection_mode_combo.grid(row=0, column=1, columnspan=3, sticky="w", pady=(0, 12))
        self.connection_mode_combo.bind("<<ComboboxSelected>>", self._on_connection_mode_change)

        ttk.Label(panel, text="IP da PS5", style="Panel.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.host = tk.StringVar(value=str(self.settings.get("host", "")))
        ttk.Entry(panel, textvariable=self.host, width=24).grid(row=1, column=1, sticky="w", padx=(0, 22))
        ttk.Label(panel, text="Porta", style="Panel.TLabel").grid(row=1, column=2, sticky="w", padx=(0, 8))
        self.port = tk.StringVar(value=preferred_connection_port(self.settings, self.connection_mode_code))
        self.port_entry = ttk.Entry(panel, textvariable=self.port, width=10,
                                    state="readonly" if self.connection_mode_code == "relay" else "normal")
        self.port_entry.grid(row=1, column=3, sticky="w")

        buttons_primary = ttk.Frame(panel, style="Panel.TFrame")
        buttons_primary.grid(row=2, column=0, columnspan=4, sticky="w", pady=(14, 0))
        self.btn_activate_relay = ttk.Button(buttons_primary, text="Ligação automática (sem config.ini)", style="Accent.TButton", command=self.activate_relay)
        self.btn_activate_relay.pack(side="left", padx=(0, 8))
        self.btn_find_relay = ttk.Button(buttons_primary, text="Procurar relay na rede", command=self.find_relay)
        self.btn_find_relay.pack(side="left")

        buttons = ttk.Frame(panel, style="Panel.TFrame")
        buttons.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self.btn_test = ttk.Button(buttons, text="Testar ligação", command=self.test_api)
        self.btn_test.pack(side="left", padx=(0, 8))
        self.btn_fetch = ttk.Button(buttons, text="Obter logs e analisar", style="Accent.TButton", command=self.fetch_logs)
        self.btn_fetch.pack(side="left", padx=(0, 8))
        self.btn_scanner = ttk.Button(buttons, text=tr("Verificar scanner"), command=self.inspect_scanner)
        self.btn_scanner.pack(side="left")
        self.api_info = tk.StringVar(value=tr("Ainda não ligado. Clica em «Testar ligação» para começar."))
        self.api_info_label = ttk.Label(panel, textvariable=self.api_info, style="PanelSub.TLabel", wraplength=900, justify="left")
        self.api_info_label.grid(row=4, column=0, columnspan=4, sticky="w", pady=(12, 0))

        config_help = ttk.Frame(self.connection_tab, style="Panel.TFrame", padding=16)
        config_help.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Label(config_help, text="Como funciona a ligação automática", style="Panel.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(
            config_help,
            text=("O modo recomendado carrega um pequeno relay ELF na PS5 através do loader de payloads (normalmente a porta 9021). "
                  "O relay lê a configuração existente para localizar a API, não altera config.ini e permite que o launcher local continue a usar 127.0.0.1:10101, "
                  "mesmo se a API tiver sido associada a um IP específico. O Doctor procura o relay automaticamente; se a descoberta por broadcast for bloqueada, podes introduzir o IP da PS5 acima."),
            style="PanelSub.TLabel", wraplength=950, justify="left"
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(
            config_help,
            text=("O relay expõe pela rede apenas endpoints de leitura de versão, logs e configuração do scanner. Precisa de ser carregado novamente após um reinício completo, "
                  "salvo se já utilizares um autoloader de payloads. O modo «API direta» continua disponível para quem já tenha acesso LAN configurado no ShadowMountPlus."),
            style="PanelSub.TLabel", wraplength=950, justify="left"
        ).pack(anchor="w", pady=(7, 0))

        safety = ttk.Frame(self.connection_tab, style="Panel.TFrame", padding=16)
        safety.pack(fill="x", padx=14)
        ttk.Label(safety, text="Privacidade e segurança", style="Panel.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(safety, text=(
            "A ligação só acontece quando carregas num botão. O relay não altera ficheiros nem definições persistentes; inicia apenas um serviço temporário de diagnóstico. As leituras pela rede ficam limitadas a rotas de diagnóstico. "
            "Como os logs podem conter identificadores, usa apenas uma rede privada de confiança e nunca encaminhes as portas 10102 ou 10103 para a Internet."
        ), style="PanelSub.TLabel", wraplength=950, justify="left").pack(anchor="w", pady=(6, 0))

    def _on_connection_mode_change(self, _event=None):
        direct_label = tr("API direta (requer acesso pela LAN)")
        self.connection_mode_code = "direct" if self.connection_mode_var.get() == direct_label else "relay"
        self.settings["connection_mode"] = self.connection_mode_code
        self.port.set("10101" if self.connection_mode_code == "direct" else str(RELAY_PORT))
        if hasattr(self, "port_entry"):
            self.port_entry.configure(state="normal" if self.connection_mode_code == "direct" else "readonly")
        self._save_settings()

    def _connection_action_buttons(self):
        return [button for button in (
            getattr(self, "btn_activate_relay", None), getattr(self, "btn_find_relay", None),
            getattr(self, "btn_test", None), getattr(self, "btn_fetch", None), getattr(self, "btn_scanner", None),
        ) if button is not None]

    @staticmethod
    def _check_api_version(host: str, port: int | str, timeout: float = 4.0):
        data = api_post(host, str(port), "/api/v1/version", {}, timeout=timeout)
        if not isinstance(data, dict) or data.get("status", 0) not in (0, None):
            raise RelayError(f"O endpoint de versão não devolveu uma resposta válida: {data}")
        return data

    def _relay_ready(self, host: str, port: int, data: dict, note: str = ""):
        self.host.set(host)
        self.port.set(str(port))
        self.connection_mode_code = "relay"
        self.settings["connection_mode"] = "relay"
        self.connection_mode_var.set(tr("Relay ELF (sem alterar config.ini)"))
        self.last_api_version = str(data.get("shadowmount_version", "desconhecida"))
        self._save_settings()
        self._set_conn_status("✅ Ligação confirmada")
        self._set_api_info(tr("Relay ativo. Agora podes obter os logs reais da PS5."))
        extra = f" {note}" if note else ""
        self._set_status(f"Relay ligado a {host}:{port}. Configuração do ShadowMountPlus não alterada.{extra}", "ok")

    def find_relay(self):
        def job():
            found = discover_relay(timeout=2.5)
            if not found:
                raise RelayError("Não foi encontrado um relay ativo na rede local. Clica em «Ligação automática» para carregar o ELF, ou confirma que o PC e a PS5 estão na mesma rede.")
            host, port = found
            data = self._check_api_version(host, port)
            return lambda app: app._relay_ready(host, port, data, "Relay encontrado na rede.")
        self._async_action(self._connection_action_buttons(), job)

    def activate_relay(self):
        def job():
            # First reuse a relay that is already running; avoid loading duplicates.
            found = None
            try:
                found = discover_relay(timeout=1.4)
            except RelayError:
                pass
            if found:
                host, port = found
                data = self._check_api_version(host, port)
                return lambda app: app._relay_ready(host, port, data, "Relay já estava ativo.")

            host = self.host.get().strip()
            if not host:
                raise RelayError("Não encontrei um relay ativo. Introduz o IP atual da PS5 para carregar o ELF através do loader.")

            # A broadcast response can be blocked by some access points. Try a direct
            # check against the saved console address before injecting another payload.
            try:
                data = self._check_api_version(host, RELAY_PORT, timeout=1.2)
                return lambda app: app._relay_ready(host, RELAY_PORT, data, "Relay já estava ativo.")
            except Exception:
                pass

            sent_bytes = send_relay_elf(host, port=LOADER_PORT)
            last_error = None
            for _ in range(10):
                try:
                    found = discover_relay(timeout=0.8)
                    if found:
                        found_host, found_port = found
                        data = self._check_api_version(found_host, found_port, timeout=1.2)
                        return lambda app: app._relay_ready(found_host, found_port, data, f"Payload enviado ({sent_bytes:,} bytes).")
                except Exception as exc:
                    last_error = exc
                # Discovery broadcasts can be blocked; query the selected console IP too.
                try:
                    data = self._check_api_version(host, RELAY_PORT, timeout=1.2)
                    return lambda app: app._relay_ready(host, RELAY_PORT, data, f"Payload enviado ({sent_bytes:,} bytes).")
                except Exception as exc:
                    last_error = exc
            reason = f" Último erro: {last_error}" if last_error else ""
            raise RelayError(
                f"O payload foi enviado ({sent_bytes:,} bytes), mas o relay não respondeu na porta {RELAY_PORT}. "
                "Confirma que o loader da PS5 aceita payloads na porta 9021, que a consola e o PC estão na mesma rede e que a versão do ShadowMountPlus tem a API ativa. "
                "Se o broadcast for bloqueado, tenta «Procurar relay na rede» ou reinicia a ligação." + reason
            )
        self._async_action(self._connection_action_buttons(), job)

    def _get_context(self) -> dict:
        reverse_maps = {
            "origin_type": {label: code for code, label in ORIGIN_OPTIONS.items()},
            "storage": {label: code for code, label in STORAGE_OPTIONS.items()},
            "trigger": {label: code for code, label in TRIGGER_OPTIONS.items()},
        }
        result = {}
        for key, var in self.context_vars.items():
            value = var.get().strip()
            result[key] = reverse_maps.get(key, {}).get(value, value)
        return result

    def clear_context(self):
        self.context_vars["firmware"].set("")
        self.context_vars["shadowmount_version"].set("")
        self.context_vars["kstuff_version"].set("")
        self.context_vars["origin_type"].set(ORIGIN_OPTIONS["unknown"])
        self.context_vars["storage"].set(STORAGE_OPTIONS["unknown"])
        self.context_vars["trigger"].set(TRIGGER_OPTIONS["unknown"])
        self._set_status("Contexto limpo. Os logs continuam carregados.", "info")

    def _set_status(self, message: str, kind: str = "info"):
        self._status_source = message
        self.status.set(tr(message))
        self._status_kind = kind
        color = {"ok": GREEN, "warning": AMBER, "error": RED, "info": ACCENT}.get(kind, ACCENT)
        if hasattr(self, "status_icon"):
            self.status_icon.configure(background=PANEL, foreground=color)

    def _set_conn_status(self, message: str):
        self._conn_status_source = message
        self.conn_status.set(tr(message))

    def _set_api_info(self, message: str):
        self._api_info_source = message
        self.api_info.set(tr(message))

    def _set_source_status(self, message: str):
        self._source_status_source = message
        self.source_status.set(tr(message))

    def check_diagnostic_updates(self):
        """Explicitly check for a newer diagnostic database; never sends log data."""
        self._set_status("A verificar atualizações da base de diagnósticos…", "info")
        def worker():
            try:
                result = check_for_updates(str(doctor_core.KNOWLEDGE_BASE.get("database_version", "0")))
                self.after(0, lambda result=result: self._finish_update_check(result=result))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self._finish_update_check(error=error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_update_check(self, result=None, error=None):
        if error:
            self._set_status("Não foi possível verificar as atualizações.", "warning")
            messagebox.showerror("Erro ao procurar atualizações", error, parent=self)
            return
        manifest = result["manifest"]
        if result.get("app_too_old"):
            self._set_status("É necessária uma versão mais recente da aplicação para esta base.", "warning")
            messagebox.showwarning(
                "Atualização da aplicação necessária",
                f"Esta base requer a aplicação versão {result['minimum_app_version']} ou superior.\n\n"
                "A base não foi transferida. Atualiza primeiro a aplicação através do repositório oficial.", parent=self)
            return
        if not result["update_available"]:
            self._set_status("A base de diagnósticos já está atualizada.", "ok")
            messagebox.showinfo(
                "Base de diagnósticos",
                f"A versão instalada é {result['current_version']} e não foi encontrada uma versão mais recente.\n\n"
                "A procura de atualizações não envia logs nem dados da PS5.", parent=self)
            return
        meta = manifest["knowledge_base"]
        changes = "\n".join(f"• {item}" for item in meta.get("changelog", [])) or "• Melhorias na base de conhecimento."
        question = (
            "Existe uma atualização da base de diagnósticos.\n\n"
            f"Versão instalada: {result['current_version']}\nVersão disponível: {result['available_version']}\n\n"
            f"Alterações incluídas:\n{changes}\n\n"
            "A aplicação irá transferir apenas regras e notas de diagnóstico. Os logs não são enviados. Instalar agora?"
        )
        if messagebox.askyesno("Atualização disponível", question, parent=self):
            self._install_diagnostic_update(manifest)
        else:
            self._set_status("Atualização cancelada.", "info")

    def _install_diagnostic_update(self, manifest):
        self._set_status("A transferir e validar a base de diagnósticos…", "info")
        def worker():
            try:
                data, raw = download_update(manifest)
                state = install_update(manifest, data, raw)
                self.after(0, lambda state=state: self._finish_update_install(state=state))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self._finish_update_install(error=error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_update_install(self, state=None, error=None):
        if error:
            self._set_status("A atualização não foi instalada.", "error")
            messagebox.showerror("Falha na atualização", error, parent=self)
            return
        global KNOWLEDGE_BASE, RULES
        KNOWLEDGE_BASE = doctor_core.reload_knowledge_base()
        RULES = KNOWLEDGE_BASE.get("rules", [])
        register_knowledge_base(KNOWLEDGE_BASE)
        self.rules_count_label.configure(text=tr(f"{len(RULES)} verificações locais"))
        raw = self.log_text.get("1.0", "end-1c") if hasattr(self, "log_text") else ""
        if raw.strip():
            self.analyze()
        version = state.get("database_version", "desconhecida")
        self._set_status(f"Base de diagnósticos atualizada para {version}.", "ok")
        messagebox.showinfo(
            "Atualização concluída",
            f"Base de diagnósticos atualizada para {version}.\n\n"
            "Foi guardada uma cópia de segurança da versão anterior. A aplicação e os logs não foram enviados.", parent=self)

    def rollback_diagnostic_update(self):
        backup = latest_backup()
        if backup is None:
            messagebox.showinfo("Restaurar base de diagnósticos", "Não existe uma cópia de segurança válida para restaurar.", parent=self)
            return
        try:
            backup_data = json.loads(backup.read_text(encoding="utf-8"))
            backup_version = backup_data.get("database_version", "desconhecida")
        except (OSError, json.JSONDecodeError):
            backup_version = "desconhecida"
        if not messagebox.askyesno(
            "Confirmar reversão",
            f"Queres restaurar a cópia de segurança da base de diagnósticos {backup_version}?\n\n"
            "A base atual será substituída pela cópia local selecionada. Os logs e as definições da PS5 não serão alterados.", parent=self):
            return
        try:
            state = restore_last_backup()
            global KNOWLEDGE_BASE, RULES
            KNOWLEDGE_BASE = doctor_core.reload_knowledge_base()
            RULES = KNOWLEDGE_BASE.get("rules", [])
            register_knowledge_base(KNOWLEDGE_BASE)
            self.rules_count_label.configure(text=tr(f"{len(RULES)} verificações locais"))
            if self.log_text.get("1.0", "end-1c").strip():
                self.analyze()
            self._set_status(f"Base de diagnósticos restaurada para {state['database_version']}.", "ok")
            messagebox.showinfo("Reversão concluída", f"Base de diagnósticos restaurada para {state['database_version']}.", parent=self)
        except Exception as exc:
            messagebox.showerror("Não foi possível restaurar a base", str(exc), parent=self)

    def _render_timeline(self, events):
        if not events:
            return
        card = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 10), padx=1)
        ttk.Label(card, text="Cronologia de erros (linhas do log)", style="Panel.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(card, text="Ordem em que os sinais aparecem no ficheiro; isto não prova uma causa-raiz.", style="PanelSub.TLabel", wraplength=930).pack(anchor="w", pady=(3, 7))
        for event in events[:6]:
            kind = event["kind"]
            label = "Possível sinal crítico" if kind == "critical" else "Possível erro" if kind == "error" else "Aviso / estado"
            ttk.Label(card, text=f"{tr('Linha ')}{event['line']} · {label}", style="Panel.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 1))
            # Log content is data; use a raw Text widget so localisation never rewrites it.
            excerpt = tk.Text(card, height=2, wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT,
                              relief="flat", borderwidth=0, font=("Consolas", 9), padx=5, pady=3)
            excerpt.pack(fill="x", pady=(0, 2))
            excerpt.insert("1.0", str(event["text"]))
            excerpt.configure(state="disabled")

    def _render_preflight_checks(self, raw: str, context: dict):
        checks = build_preflight_checks(raw, context)
        if not checks:
            return
        section = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=14)
        section.pack(fill="x", pady=(0, 10), padx=1)
        ttk.Label(section, text=tr("Pré-verificação antes de alterar ficheiros"), style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 7))
        for index, check in enumerate(checks):
            if index:
                ttk.Separator(section).pack(fill="x", pady=8)
            title = tr(str(check.get("title", "")))
            ttk.Label(section, text=title, style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(section, text=tr(str(check.get("summary", ""))), style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(4, 4))
            steps = check.get("steps", [])
            for number, step in enumerate(steps, 1):
                ttk.Label(section, text=f"{number}. {tr(str(step))}", style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(2, 0))

    def _render_compatibility_notices(self, context):
        entries = evaluate_compatibility(context, doctor_core.KNOWLEDGE_BASE)
        if not entries:
            return
        for entry in entries:
            card = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=14)
            card.pack(fill="x", pady=(0, 10), padx=1)
            ttk.Label(card, text=tr("Notas de compatibilidade para o contexto indicado"), style="Panel.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ttk.Label(card, text=entry.get("title", ""), style="Panel.TLabel", font=("Segoe UI", 11, "bold"), wraplength=930).pack(anchor="w", pady=(4, 4))
            ttk.Label(card, text=entry.get("severity", "Informação"), style="PanelSub.TLabel").pack(anchor="w")
            ttk.Label(card, text=entry.get("status", ""), style="PanelSub.TLabel", wraplength=930).pack(anchor="w", pady=(2, 4))
            ttk.Label(card, text=entry.get("summary", ""), style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w")
            if entry.get("sources"):
                row = ttk.Frame(card, style="Panel.TFrame")
                row.pack(fill="x", pady=(7, 0))
                for index, url in enumerate(entry["sources"], 1):
                    ttk.Button(row, text=f"Abrir fonte {index}", command=lambda target=url: webbrowser.open(target)).pack(side="left", padx=(0, 6))

    def _add_empty_card(self, title: str, body: str, icon: str = "i", color: str = ACCENT):
        card = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=18)
        card.pack(fill="x", pady=(0, 10))
        ttk.Label(card, text=icon, style="Panel.TLabel", foreground=color, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(card, text=title, style="Panel.TLabel", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(5, 4))
        ttk.Label(card, text=body, style="PanelSub.TLabel", wraplength=900, justify="left").pack(anchor="w")

    def _clear_cards(self):
        for child in self.cards.inner.winfo_children():
            child.destroy()

    def show_welcome(self):
        self._clear_cards()
        card = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=22)
        card.pack(fill="x", pady=(0, 10), padx=1)
        ttk.Label(card, text="Ainda não há uma análise", style="Panel.TLabel", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(card, text=(
            "Começa por obter os logs da PS5 ou importar um ficheiro usando os botões acima. "
            "Também podes abrir um exemplo fictício para conhecer a aplicação; esse exemplo não representa a tua consola.\n\n"
            "Quando os logs estiverem carregados, escolhe ‘Analisar logs’. Depois abre um resultado para consultar "
            "as linhas encontradas e os passos sugeridos."
        ), style="PanelSub.TLabel", justify="left", wraplength=850).pack(anchor="w", pady=(8, 0))
        ttk.Label(self.cards.inner, text="A análise é feita neste computador. Nenhum ficheiro é enviado automaticamente.", style="Sub.TLabel", wraplength=850).pack(anchor="w", padx=2, pady=(2, 0))

    def _append_logs(self, text: str, source: str):
        if not text.strip():
            return
        current = self.log_text.get("1.0", "end-1c")
        marker = f"\n\n===== SOURCE: {source} =====\n"
        if current.strip():
            self.log_text.insert("end", marker + text)
        else:
            self.log_text.insert("1.0", f"===== SOURCE: {source} =====\n{text}")
        self.log_text.see("end")
        if source not in self.sources:
            self.sources.append(source)
        self.tabs.select(self.logs_tab)

    def open_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar logs da PS5",
            filetypes=[("Logs e texto", "*.log *.txt *.out *.json"), ("Todos os ficheiros", "*.*")],
        )
        if not paths:
            return
        errors, loaded = [], 0
        was_demo = self.demo_mode
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
                    content = handle.read(5_000_000)
                # Demonstration data must never be silently mixed with imported logs.
                if was_demo and loaded == 0:
                    self.log_text.delete("1.0", "end")
                    self.sources = []
                    self.findings = []
                    self.demo_mode = False
                self._append_logs(content, os.path.basename(path))
                loaded += 1
            except OSError as exc:
                errors.append(f"{os.path.basename(path)}: {exc}")
        if loaded:
            self.demo_mode = False
            self._set_source_status(f"Origem: {loaded} ficheiro(s) importado(s) do computador.")
        self._set_status(f"Importados {loaded} ficheiro(s)." + (f" Alguns falharam: {'; '.join(errors)}" if errors else ""), "warning" if errors else "ok")
        if loaded:
            self.tabs.select(self.logs_tab)

    def load_sample(self):
        sample = (
            "[ShadowMount+] version 1.7beta3 | Firmware 13.60\n"
            "[INFO] source not stable yet: /mnt/usb0/Dispatch/\n"
            "[REG] AppInstallAll hook is no longer installed: TitleDir bridge unavailable\n"
            "[REG] FAIL: 0x80F50005 for PPSA34015\n"
            "[Debug] PPSA27158 crashed before KStuff pause: 0xa0020102 (PRX_SCE_MODULE_LOAD_ERROR)\n"
            "[etaHEN] send_klog open /dev/klog failed Device busy\n"
        )
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", sample)
        self.sources = ["exemplo integrado (dados fictícios)"]
        self.demo_mode = True
        self._set_source_status("MODO DE DEMONSTRAÇÃO · Dados fictícios; não são logs da tua PS5.")
        self._set_status("Exemplo fictício carregado. Ao obter logs da PS5, este exemplo será substituído.", "warning")
        self.analyze()

    def clear(self):
        self.log_text.delete("1.0", "end")
        self.sources = []
        self.demo_mode = False
        self._set_source_status("Origem: ainda não há logs carregados")
        self.findings = []
        self.last_analyzed_text = ""
        self.last_analyzed_context = {}
        self.metric_vars["errors"].set("—")
        self.metric_vars["warnings"].set("—")
        self.metric_vars["matches"].set(tr("À espera dos logs"))
        self.show_welcome()
        self._set_status("Logs limpos. Podes começar uma nova análise.")

    def _async_action(self, btns, job):
        for button in btns:
            button.configure(state="disabled")
        self._set_status("A contactar a PS5 na rede local…")

        def runner():
            try:
                result = job()
                self.after(0, lambda result=result: self._finish_async(btns, result=result))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self._finish_async(btns, error=error))
        threading.Thread(target=runner, daemon=True).start()

    def _finish_async(self, btns, result=None, error=None):
        for button in btns:
            try:
                button.configure(state="normal")
            except tk.TclError:
                pass
        if error:
            self._set_conn_status("PS5: não ligada")
            if hasattr(self, "api_info"):
                self._set_api_info("❌ Não foi possível ligar. Confirma o IP, a porta e se a API está ativa.")
            self._set_status("Ligação não estabelecida.", "error")
            messagebox.showerror("Não foi possível contactar a PS5", self._friendly_error(error))
            return
        result(self)

    @staticmethod
    def _friendly_error(error: str) -> str:
        low = error.lower()
        if "timed out" in low or "timeout" in low:
            return "A ligação expirou. Confirma que a PS5 e o PC estão na mesma rede. No modo relay, carrega em «Ligação automática»; no modo API direta, confirma se a API aceita ligações pela LAN."
        if "connection refused" in low or "actively refused" in low or "winerror 10061" in low:
            return ("A ligação foi recusada. Confirma que o ShadowMountPlus e a API local estão ativos. "
                    "Para evitar alterar config.ini, seleciona «Relay ELF» e carrega em «Ligação automática». "
                    "O relay usa a API local existente e disponibiliza apenas os endpoints de leitura necessários ao Doctor.")
        if "forbidden" in low or "unauthorized" in low:
            return "A API respondeu, mas não autorizou o pedido. Confirma a versão e a configuração da API do ShadowMountPlus."
        return error

    def test_api(self):
        def job():
            data = api_post(self.host.get(), self.port.get(), "/api/v1/version", {})
            if isinstance(data, dict) and data.get("status", 0) not in (0, None):
                raise RuntimeError(f"A API respondeu com erro: {data}")
            return lambda app: app._show_api_result(data)
        self._async_action(self._connection_action_buttons(), job)

    def _show_api_result(self, data):
        version = data.get("shadowmount_version", "desconhecida") if isinstance(data, dict) else "desconhecida"
        self.last_api_version = version
        self._set_conn_status("✅ Ligação confirmada")
        self._set_api_info("Agora clica em «Obter logs e analisar» para analisar os logs reais da PS5.")
        self._set_status("Ligação confirmada ✅", "ok")

    def fetch_logs(self):
        def job():
            host, port = self.host.get(), self.port.get()
            version = api_post(host, port, "/api/v1/version", {})
            if isinstance(version, dict) and version.get("status", 0) not in (0, None):
                raise RuntimeError(f"Falha no endpoint de versão: {version}")
            outputs, errors = [], []
            for label, route in (("ShadowMountPlus debug.log", "/api/v1/debug-log"), ("Kernel log", "/api/v1/kernel-log")):
                try:
                    body = api_post(host, port, route, {"max_bytes": 131072})
                    if isinstance(body, dict) and body.get("status", 0) not in (0, None):
                        raise RuntimeError(str(body.get("error", body)))
                    content = response_to_text(body).strip()
                    if content and content not in ("{}", "[]"):
                        outputs.append((label, content))
                    else:
                        errors.append(f"{label}: a API não devolveu texto de log reconhecível.")
                except Exception as exc:
                    errors.append(f"{label}: {exc}")
            if not outputs:
                raise RuntimeError("Não foi possível importar nenhum log. " + " | ".join(errors))
            version_name = version.get("shadowmount_version", "desconhecida") if isinstance(version, dict) else "desconhecida"
            return lambda app: app._logs_fetched(outputs, errors, version_name)
        self._async_action(self._connection_action_buttons(), job)

    def inspect_scanner(self):
        """Read scanner configuration and manual sources from supported API routes."""
        def job():
            host, port = self.host.get(), self.port.get()
            version = api_post(host, port, "/api/v1/version", {})
            if not isinstance(version, dict) or version.get("status", 0) not in (0, None):
                raise RuntimeError(tr("A API não devolveu uma resposta de versão válida."))
            capabilities = version.get("capabilities", [])
            capabilities = set(capabilities) if isinstance(capabilities, list) else set()
            errors = []
            settings_response = None
            manual_response = None

            if capabilities and "manage_settings" not in capabilities:
                errors.append(tr("A versão da API não anuncia leitura das definições do scanner."))
            else:
                try:
                    candidate = api_post(host, port, "/api/v1/settings", {})
                    if isinstance(candidate, dict) and candidate.get("status", 0) in (0, None):
                        settings_response = candidate
                    else:
                        errors.append(tr("Não foi possível ler as definições do scanner."))
                except Exception as exc:
                    errors.append(f"{tr('Definições do scanner')}: {exc}")

            if capabilities and "list_manual_sources" not in capabilities:
                errors.append(tr("A versão da API não anuncia a lista de origens manuais."))
            else:
                try:
                    candidate = api_post(host, port, "/api/v1/manual/list", {})
                    if isinstance(candidate, dict) and candidate.get("status", 0) in (0, None):
                        manual_response = candidate
                    else:
                        errors.append(tr("Não foi possível ler a lista de origens manuais."))
                except Exception as exc:
                    errors.append(f"{tr('Origens manuais')}: {exc}")

            # A successful version check means the connection works even when these newer,
            # read-only scanner endpoints are unsupported. Show their availability instead.
            snapshot = summarize_scanner_snapshot(settings_response, manual_response, errors)
            version_name = str(version.get("shadowmount_version", "desconhecida"))
            return lambda app: app._show_scanner_snapshot(snapshot, version_name)

        self._async_action(self._connection_action_buttons(), job)

    def _show_scanner_snapshot(self, snapshot, version):
        self.last_scanner_snapshot = snapshot
        self.last_api_version = version
        self._set_conn_status("✅ Ligação confirmada")
        win = tk.Toplevel(self)
        win.title(tr("Estado do scanner — leitura apenas"))
        win.geometry("760x600")
        win.minsize(600, 420)
        win.configure(bg=BG)
        win.transient(self)
        outer = ttk.Frame(win, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=tr("Estado do scanner"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(outer, text=f"ShadowMountPlus {version} · {tr('Apenas leitura; não altera a consola.')}", style="Sub.TLabel", wraplength=700).pack(anchor="w", pady=(4, 10))
        output = ScrolledText(outer, wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT,
                              relief="flat", borderwidth=0, font=("Consolas", 10), padx=12, pady=12)
        output.pack(fill="both", expand=True)

        def line(value=""):
            output.insert("end", str(value) + "\n")

        line(tr("Raízes de varrimento personalizadas (scan_paths)"))
        if snapshot.get("settings_available"):
            paths = snapshot.get("scan_paths", [])
            if paths:
                for path in paths:
                    line(f"  • {path}")
            else:
                line(tr("A API não devolveu raízes personalizadas. Isto não significa que as raízes predefinidas estejam desativadas."))
            depth = snapshot.get("scan_depth")
            if depth is not None:
                line(f"{tr('Profundidade de varrimento (scan_depth)')}: {depth}")
        else:
            line(tr("As definições do scanner não estão disponíveis nesta versão da API."))

        line()
        line(tr("Origens manuais (manual.lst)"))
        if snapshot.get("manual_available"):
            paths = snapshot.get("manual_paths", [])
            line(f"{tr('Origens listadas')}: {snapshot.get('manual_count', len(paths))}")
            if paths:
                for path in paths:
                    line(f"  • {path}")
            else:
                line(tr("A lista não contém origens manuais."))
        else:
            line(tr("A lista de origens manuais não está disponível nesta versão da API."))

        errors = snapshot.get("errors", [])
        if errors:
            line()
            line(tr("Avisos"))
            for error in errors:
                line(f"• {error}")
        line()
        line(tr("Nota: a API apresenta definições e origens manuais; esta consulta não executa uma nova varredura nem confirma que cada jogo pode ser iniciado."))
        output.configure(state="disabled")
        self._set_api_info(tr("Estado do scanner lido. Consulta o painel para veres os caminhos configurados."))
        self._set_status(tr("Verificação do scanner concluída; não foram feitas alterações."), "ok")

    def _logs_fetched(self, outputs, errors, version):
        # A PS5 fetch is a fresh snapshot, not an append operation. Replacing the
        # buffer is essential so demo or old imported logs cannot contaminate results.
        fetched_text, fetched_sources = format_source_blocks(outputs)
        if not fetched_text.strip():
            self._set_status("A PS5 não devolveu logs com conteúdo.", "warning")
            return
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", fetched_text)
        self.sources = fetched_sources
        self.demo_mode = False
        self.findings = []
        self.last_analyzed_text = ""
        self.last_analyzed_context = {}
        self._set_source_status("ORIGEM: logs reais recolhidos da PS5 · o exemplo fictício foi descartado.")
        self.last_api_version = version
        self._set_conn_status("✅ PS5 ligada")
        self._set_api_info(f"✅ Logs recebidos. Foram obtidos {len(outputs)} ficheiro(s) de log. Clica em «Resultado» para ver a análise.")
        message = f"Recolhidos {len(outputs)} log(s) da PS5. Os dados anteriores foram substituídos."
        if errors:
            message += " Avisos: " + "; ".join(errors)
        self._set_status(message, "warning" if errors else "ok")
        self.analyze()

    def _render_finding(self, finding, number: int):
        severity = finding.severity.lower()
        color = RED if "crít" in severity or "erro" in severity else AMBER if "aviso" in severity else ACCENT
        card = ttk.Frame(self.cards.inner, style="Panel.TFrame", padding=(14, 12))
        card.pack(fill="x", pady=(0, 8), padx=1)

        heading = ttk.Frame(card, style="Panel.TFrame")
        heading.pack(fill="x")
        title_frame = ttk.Frame(heading, style="Panel.TFrame")
        title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(title_frame, text=f"{number}. {finding.title}", style="Panel.TLabel", font=("Segoe UI", 11, "bold"), wraplength=790).pack(anchor="w")
        ttk.Label(heading, text=finding.severity, style="Panel.TLabel", foreground=color, font=("Segoe UI", 9, "bold")).pack(side="right", anchor="n", padx=(8, 0))
        ttk.Label(card, text=finding.summary, style="PanelSub.TLabel", wraplength=940, justify="left").pack(anchor="w", pady=(7, 4))

        info_line = f"Fiabilidade estimada: {finding.confidence}" if finding.confidence else ""
        if info_line:
            ttk.Label(card, text=info_line, style="PanelSub.TLabel", wraplength=930).pack(anchor="w", pady=(0, 2))

        details = ttk.Frame(card, style="Panel.TFrame")
        state = {"built": False}
        toggle = ttk.Button(card, text="Ver evidência e passos ▾", style="Link.TButton")
        toggle.pack(anchor="w", pady=(5, 0))

        def build_details():
            ttk.Separator(details).pack(fill="x", pady=(3, 10))
            ttk.Label(details, text=f"Identificador: {finding.rule_id}", style="PanelSub.TLabel").pack(anchor="w", pady=(0, 3))
            ttk.Label(details, text=f"Referência: {evidence_status_pt(finding.evidence_status)}", style="PanelSub.TLabel", wraplength=930).pack(anchor="w", pady=(0, 7))
            if finding.context_relevance and finding.context_relevance != "Não necessário":
                relevance_color = GREEN if finding.context_relevance == "Contexto compatível" else RED if finding.context_relevance == "Contexto divergente" else AMBER
                ttk.Label(details, text=f"Contexto: {finding.context_relevance}", style="Panel.TLabel", foreground=relevance_color, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
            if finding.context_note:
                ttk.Label(details, text=finding.context_note, style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(0, 8))
            if finding.evidence:
                ttk.Label(details, text="Linha(s) encontrada(s)", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
                evidence_box = tk.Text(details, height=min(4, max(1, len(finding.evidence))), wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT, selectbackground=ACCENT, selectforeground=SELECT_TEXT, relief="solid", borderwidth=1, highlightthickness=0, font=("Consolas", 9), padx=8, pady=7)
                evidence_box.pack(fill="x", pady=(4, 8))
                evidence_box.insert("1.0", "\n".join(f"• {line}" for line in finding.evidence))
                evidence_box.configure(state="disabled")
            if finding.fix_summary:
                ttk.Label(details, text="Orientação", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
                ttk.Label(details, text=finding.fix_summary, style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(4, 8))
            if finding.next_steps:
                ttk.Label(details, text="O que fazer a seguir", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
                for index, step in enumerate(finding.next_steps, 1):
                    ttk.Label(details, text=f"{index}. {step}", style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(4, 0))
            if finding.applicability:
                ttk.Label(details, text="Limites", style="Panel.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(9, 0))
                ttk.Label(details, text=finding.applicability, style="PanelSub.TLabel", wraplength=930, justify="left").pack(anchor="w", pady=(3, 0))
            if finding.sources:
                links = ttk.Frame(details, style="Panel.TFrame")
                links.pack(fill="x", pady=(10, 0))
                ttk.Label(links, text="Referências:", style="PanelSub.TLabel").pack(side="left", padx=(0, 7))
                for index, source in enumerate(finding.sources, 1):
                    ttk.Button(links, text=f"Abrir fonte {index}", command=lambda url=source: webbrowser.open(url)).pack(side="left", padx=(0, 5))
            ttk.Button(details, text="Acompanhar resolução passo a passo…", style="Accent.TButton",
                       command=lambda item=finding: self.open_resolution_assistant(item)).pack(anchor="w", pady=(12, 0))

        def toggle_details():
            if details.winfo_manager():
                details.pack_forget()
                toggle.configure(text=tr("Ver evidência e passos ▾"))
            else:
                if not state["built"]:
                    build_details()
                    state["built"] = True
                details.pack(fill="x", pady=(5, 0))
                toggle.configure(text=tr("Ocultar detalhes ▴"))

        toggle.configure(command=toggle_details)

    def analyze(self):
        raw = self.log_text.get("1.0", "end-1c")
        if not raw.strip():
            self.tabs.select(self.logs_tab)
            messagebox.showinfo("Ainda não há logs", "Importa um ficheiro, cola logs ou usa ‘Obter logs da PS5’. Depois carrega em ‘Iniciar diagnóstico’.")
            return
        self.last_analyzed_context = self._get_context()
        self.last_analyzed_text = raw
        self.findings = analyze_logs(raw, context=self.last_analyzed_context)
        timeline = extract_error_timeline(raw)
        compatibility_notes = evaluate_compatibility(self.last_analyzed_context, doctor_core.KNOWLEDGE_BASE)
        self._clear_cards()
        self._render_preflight_checks(raw, self.last_analyzed_context)
        self._render_timeline(timeline)
        self._render_compatibility_notices(self.last_analyzed_context)
        errors = sum(1 for item in self.findings if item.severity in ("Erro", "Erro crítico"))
        warnings = sum(1 for item in self.findings if item.severity == "Aviso")
        self.metric_vars["errors"].set(str(errors))
        self.metric_vars["warnings"].set(str(warnings))
        self.metric_vars["matches"].set(tr(f"{len(self.findings)} resultado(s)"))

        if not self.findings:
            self._add_empty_card(
                "Não foram encontrados sinais de erro reconhecíveis",
                "Isto não garante que esteja tudo bem. Confirma se importaste o log certo e se inclui as linhas em redor do problema. "
                "Podes pesquisar termos como ‘error’, ‘failed’, ‘crash’, ‘panic’ ou voltar a recolher os logs depois de reproduzir o erro.",
                icon="i", color=ACCENT,
            )
        else:
            title = "1 resultado para rever" if len(self.findings) == 1 else f"{len(self.findings)} resultados para rever"
            self._add_empty_card(
                title,
                "Abre um resultado para ver as linhas encontradas e os passos sugeridos. A análise não altera a consola.",
                icon="!" if errors else "i", color=RED if errors else AMBER,
            )
            for number, finding in enumerate(self.findings, 1):
                self._render_finding(finding, number)
        self.tabs.select(self.diag_tab)
        origin = "exemplo fictício" if self.demo_mode else ("logs da PS5" if any("PS5" in src or "ShadowMountPlus debug.log" in src or "Kernel log" in src for src in self.sources) else "logs carregados")
        self._set_status(f"Análise concluída: {len(self.findings)} resultado(s) · origem: {origin}. A consola não foi alterada.", "ok" if self.findings else "warning")

    @staticmethod
    def _read_resolution_history() -> dict:
        try:
            data = json.loads(RESOLUTION_HISTORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("entries"), list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return {"schema_version": 1, "entries": []}

    @staticmethod
    def _write_resolution_history(data: dict):
        temp = RESOLUTION_HISTORY_PATH.with_suffix(".json.tmp")
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(RESOLUTION_HISTORY_PATH)

    def open_resolution_assistant(self, finding):
        win = tk.Toplevel(self)
        win.title(tr(f"Assistente de resolução — {finding.rule_id}"))
        win.geometry("760x700")
        win.minsize(650, 560)
        win.configure(bg=BG)
        win.transient(self)
        outer = ttk.Frame(win, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=finding.title, style="Section.TLabel", wraplength=700).pack(anchor="w")
        ttk.Label(outer, text=f"{finding.severity} · Confiança: {finding.confidence} · {evidence_status_pt(finding.evidence_status)}", style="Sub.TLabel", wraplength=700).pack(anchor="w", pady=(4, 10))

        scroll = ScrollableFrame(outer)
        scroll.pack(fill="both", expand=True, pady=(0, 12))
        body = scroll.inner
        self._add_dialog_section(body, "Resumo", finding.fix_summary or finding.summary)
        self._add_dialog_section(body, "Antes de começar", "A app não vai alterar a PS5 pela API. Lê cada passo, confirma que corresponde ao teu caso e evita operações destrutivas. As referências comunitárias podem ser específicas de versões antigas.")
        if finding.context_note:
            self._add_dialog_section(body, "Verificação de contexto", finding.context_note)
        ttk.Label(body, text="Lista de verificação", style="Panel.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 6))
        step_vars = []
        for index, step in enumerate(finding.next_steps, 1):
            var = tk.BooleanVar(value=False)
            step_vars.append(var)
            tk.Checkbutton(body, text=f"{index}. {step}", variable=var, wraplength=660, anchor="w", justify="left",
                           bg=PANEL, fg=TEXT, activebackground=PANEL, activeforeground=TEXT,
                           selectcolor=INPUT, relief="flat", highlightthickness=0,
                           font=("Segoe UI", 9)).pack(anchor="w", fill="x", pady=(2, 4))
        if finding.sources:
            ttk.Label(body, text="Fontes consultadas", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 4))
            for index, url in enumerate(finding.sources, 1):
                ttk.Button(body, text=f"Abrir fonte {index}", command=lambda u=url: webbrowser.open(u)).pack(anchor="w", pady=2)

        reversible_applicable = finding.rule_id in {"SHADOW_PFS_PARENTHESES_PANIC", "SHADOW_FILENAME_TOO_LONG"} and finding.context_relevance != "Contexto divergente"
        if reversible_applicable:
            ttk.Separator(body).pack(fill="x", pady=12)
            ttk.Label(body, text="Teste de nome reversível (opcional)", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(body, text="Só funciona com um ficheiro .ffpfs/.ffpfsc acessível ao Windows. A app altera apenas o nome local; não edita o conteúdo nem escreve na PS5. Para nomes com limite desconhecido, a sugestão é experimental.", style="PanelSub.TLabel", wraplength=660, justify="left").pack(anchor="w", pady=(4, 6))
            ttk.Button(body, text="Escolher ficheiro e preparar teste…", command=lambda: self._apply_reversible_rename(finding, win)).pack(anchor="w", pady=(0, 8))

        footer = ttk.Frame(outer)
        footer.pack(fill="x")
        ttk.Label(footer, text="Resultado do teste", style="Sub.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        result_var = tk.StringVar(value=_result_label("not_tested"))
        result_box = ttk.Combobox(
            footer, textvariable=result_var, state="readonly", width=22,
            values=tuple(_result_label(code) for code in _RESULT_LABELS_PT),
        )
        result_box.grid(row=0, column=1, sticky="w")
        ttk.Label(footer, text="Notas (opcional)", style="Sub.TLabel").grid(row=1, column=0, sticky="nw", pady=(8, 0))
        notes = tk.Text(footer, height=3, width=58, wrap="word", bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat")
        notes.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        footer.columnconfigure(1, weight=1)
        ttk.Button(footer, text="Guardar progresso", style="Accent.TButton",
                   command=lambda: self._save_resolution_progress(finding, [v.get() for v in step_vars], result_var.get(), notes.get("1.0", "end-1c"), win)).grid(row=2, column=1, sticky="e", pady=(10, 0))

    @staticmethod
    def _add_dialog_section(parent, title, text):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.pack(fill="x", pady=(0, 8))
        ttk.Label(panel, text=title, style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(panel, text=text, style="PanelSub.TLabel", wraplength=660, justify="left").pack(anchor="w", pady=(4, 0))

    def _apply_reversible_rename(self, finding, owner):
        if finding.context_relevance == "Contexto divergente":
            messagebox.showwarning("Contexto divergente", "Os dados fornecidos não correspondem ao cenário documentado. Não vou preparar esta alteração.", parent=owner)
            return
        path = filedialog.askopenfilename(parent=owner, title="Escolhe a imagem PFS de origem", filetypes=[("Imagens PFS", "*.ffpfs *.ffpfsc"), ("Todos os ficheiros", "*.*")])
        if not path:
            return
        yes = messagebox.askyesno(
            "Confirmar teste reversível",
            "A app vai alterar APENAS o nome deste ficheiro no Windows; não altera o conteúdo.\n\n"
            "Antes de continuar, confirma que:\n• escolheste a origem exata mencionada no log;\n"
            "• o ShadowMountPlus deixou de examinar/montar esse ficheiro;\n"
            "• aceitas o teste comunitário (não é uma correção garantida).\n\n"
            "A operação ficará registada em Histórico / Reverter. Continuar?", parent=owner)
        if not yes:
            return
        try:
            record = rename_for_rule(finding.rule_id, path)
        except Exception as exc:
            messagebox.showerror("Não foi possível preparar o teste", str(exc), parent=owner)
            return
        self._set_status(f"Teste reversível preparado: {record['original_name']} → {record['new_name']}", "ok")
        messagebox.showinfo(
            "Teste preparado",
            f"Nome anterior:\n{record['original_name']}\n\nNovo nome:\n{record['new_name']}\n\n"
            f"ID para reversão: {record['id']}\n\nO conteúdo do ficheiro não foi alterado. Se o teste não ajudar, abre ‘Histórico / Reverter…’ para restaurar o nome original.", parent=owner)

    def _save_resolution_progress(self, finding, checked_steps, result, notes, owner):
        history = self._read_resolution_history()
        history["entries"].append({
            "id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{len(history['entries'])+1}",
            "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "rule_id": finding.rule_id, "title": finding.title, "result": _result_code(result),
            "checked_steps": [index + 1 for index, checked in enumerate(checked_steps) if checked],
            "total_steps": len(checked_steps), "notes": notes.strip(), "context": self._get_context(),
        })
        try:
            self._write_resolution_history(history)
        except OSError as exc:
            messagebox.showerror("Não foi possível guardar", f"O progresso não foi guardado: {exc}", parent=owner)
            return
        self._set_status(f"Progresso guardado: {finding.rule_id} — {_result_label(result)}.", "ok")
        messagebox.showinfo("Progresso guardado", "O progresso foi guardado localmente. Ainda não foi enviada nenhuma ação à PS5.", parent=owner)

    def open_history(self):
        win = tk.Toplevel(self)
        win.title(tr("Histórico e reversão de alterações"))
        win.geometry("850x560")
        win.minsize(700, 470)
        win.configure(bg=BG)
        win.transient(self)
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=14, pady=14)

        rename_tab = ttk.Frame(notebook, padding=12)
        notebook.add(rename_tab, text="Renomeações reversíveis")
        ttk.Label(rename_tab, text="A aplicação só pode reverter os testes de nome que registou. Não sobrescreve o nome original se já existir um ficheiro com esse nome.", style="Sub.TLabel", wraplength=780).pack(anchor="w", pady=(0, 8))
        listbox = tk.Listbox(rename_tab, bg=INPUT, fg=TEXT, selectbackground=ACCENT, selectforeground=SELECT_TEXT, relief="flat", height=12, font=("Consolas", 9))
        listbox.pack(fill="both", expand=True)
        records = list_actions()
        for record in records:
            label = f"[{_action_status_label(record.get('status'))}] {record.get('new_name','?')}  |  ID {record.get('id','?')}"
            listbox.insert("end", label)
        detail = tk.StringVar(value=tr("Seleciona uma alteração para ver os caminhos e o estado."))
        ttk.Label(rename_tab, textvariable=detail, style="Panel.TLabel", wraplength=780).pack(anchor="w", pady=(8, 8))
        buttonrow = ttk.Frame(rename_tab)
        buttonrow.pack(fill="x")
        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection:
                detail.set(tr("Seleciona uma alteração."))
                return
            rec = records[selection[0]]
            detail.set(
                f"{rec.get('original_path')}  ←  {rec.get('current_path')}\n"
                f"{tr('Estado: ')}{_action_status_label(rec.get('status'))} · ID: {rec.get('id')}"
            )
        def do_rollback():
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("Seleciona uma alteração", "Seleciona uma renomeação no histórico.", parent=win)
                return
            rec = records[selection[0]]
            if rec.get("status") != "renamed":
                messagebox.showinfo("Não disponível", "Esta ação já foi revertida ou não está disponível.", parent=win)
                return
            if not messagebox.askyesno("Confirmar reversão", f"Restaurar o nome original?\n\n{rec.get('new_name')}\n→ {rec.get('original_name')}\n\nA app não irá substituir ficheiros existentes.", parent=win):
                return
            try:
                rollback_action(rec["id"])
            except Exception as exc:
                messagebox.showerror("Não foi possível reverter", str(exc), parent=win)
                return
            messagebox.showinfo("Reversão concluída", "O nome original foi restaurado. O conteúdo não foi modificado.", parent=win)
            win.destroy()
            self.open_history()
        listbox.bind("<<ListboxSelect>>", on_select)
        ttk.Button(buttonrow, text="Reverter selecionada…", style="Accent.TButton", command=do_rollback).pack(side="left")

        resolution_tab = ttk.Frame(notebook, padding=12)
        notebook.add(resolution_tab, text="Planos de resolução")
        ttk.Label(resolution_tab, text="Progresso guardado no computador. Estes registos são notas locais; não indicam que a app tenha executado uma correção na PS5.", style="Sub.TLabel", wraplength=780).pack(anchor="w", pady=(0, 8))
        plan_list = tk.Listbox(resolution_tab, bg=INPUT, fg=TEXT, selectbackground=ACCENT, selectforeground=SELECT_TEXT, relief="flat", height=12, font=("Consolas", 9))
        plan_list.pack(fill="both", expand=True)
        history = self._read_resolution_history()["entries"]
        for item in reversed(history):
            plan_list.insert("end", f"[{_result_label(item.get('result', '?'))}] {item.get('rule_id','?')} · {item.get('created_at','')}")
        plan_detail = tk.StringVar(value=tr("Seleciona um plano para ver as notas."))
        ttk.Label(resolution_tab, textvariable=plan_detail, style="Panel.TLabel", wraplength=780).pack(anchor="w", pady=(8, 0))
        def on_plan_select(_event=None):
            sel = plan_list.curselection()
            if not sel:
                return
            item = list(reversed(history))[sel[0]]
            note = item.get("notes") or "Sem notas."
            plan_title = tr(str(item.get("title") or ""))
            plan_detail.set(
                f"{plan_title}{tr(' · passos concluídos: ')}{item.get('checked_steps')} / {item.get('total_steps')}\n{note}"
            )
        plan_list.bind("<<ListboxSelect>>", on_plan_select)

    def save_report(self):
        raw = self.log_text.get("1.0", "end-1c")
        if not raw.strip():
            messagebox.showinfo("Sem logs", "Importa ou cola logs antes de guardar um relatório.")
            return
        current_context = self._get_context()
        if not self.findings or raw != self.last_analyzed_text or current_context != self.last_analyzed_context:
            self.analyze()
            current_context = self._get_context()
        path = filedialog.asksaveasfilename(
            title="Guardar relatório de diagnóstico", defaultextension=".md",
            filetypes=[("Relatório Markdown", "*.md"), ("Ficheiro de texto", "*.txt")],
            initialfile="ps5-homebrew-doctor-report.md",
        )
        if not path:
            return
        report = make_markdown_report(
            raw,
            self.findings,
            anonymize=self.anonymize.get(),
            source_names=self.sources,
            context=current_context,
            language=self.language,
        )
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(report)
        except OSError as exc:
            messagebox.showerror("Erro ao guardar", str(exc))
            return
        self._set_status(f"Relatório guardado: {os.path.basename(path)}. Revê-o antes de o partilhares.", "ok")
        messagebox.showinfo("Relatório guardado", "Relatório guardado. Confirma o conteúdo antes de o partilhares, mesmo com a anonimização ativada.")


def main():
    app = DoctorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
