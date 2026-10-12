#!/usr/bin/env python3
"""Levantamento mecânico de um projeto web para a skill page-control.

Emite um JSON com o que pode ser detectado sem julgamento: arquivos, sinais de
tecnologia, persistencia, sistema administrativo existente e restricoes. O
objetivo e padronizar o passo 1 (Inspecionar) e nao gastar contexto relendo o
projeto inteiro a cada invocacao.

O script detecta; nao decide. A escolha de arquitetura continua sendo do agente.

Uso:
    python3 scripts/inspect_project.py <diretorio-ou-arquivo> [--max-bytes N]

Aceita um diretorio (Claude Code) ou um unico arquivo HTML (Claude App, onde
so existe o anexo da conversa). Depende apenas da biblioteca padrao.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

CODE_EXT = {".html", ".htm", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".css", ".scss"}
CONFIG_NAMES = {
    "package.json", "vite.config.js", "vite.config.ts", "next.config.js",
    "firebase.json", "firestore.rules", ".firebaserc", "tsconfig.json",
    "tailwind.config.js", "webpack.config.js", "astro.config.mjs",
}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".cache", "vendor", "__pycache__", ".venv"}

# (chave, regex). Buscados no conteudo concatenado dos arquivos de codigo.
SIGNALS = [
    ("localStorage",        r"\blocalStorage\b"),
    ("sessionStorage",      r"\bsessionStorage\b"),
    ("indexedDB",           r"\bindexedDB\b|\bIDBDatabase\b"),
    ("firebase",            r"firebase|firebaseapp\.com"),
    ("firestore",           r"firestore|collection\s*\(|onSnapshot"),
    ("firebase_auth",       r"getAuth|signInWith|onAuthStateChanged|FirebaseAuth"),
    ("firestore_realtime",  r"onSnapshot"),
    ("fetch_api",           r"\bfetch\s*\(|axios"),
    ("react",               r"from\s+['\"]react['\"]|React\.createElement|useState\s*\("),
    ("vue",                 r"from\s+['\"]vue['\"]|createApp\s*\(|<template>"),
    ("svelte",              r"\.svelte|svelte/internal"),
    ("angular",             r"@angular/|ngOnInit"),
    ("jquery",              r"\$\(\s*document\s*\)|jquery"),
    ("tailwind",            r"tailwind|class=\"[^\"]*\b(flex|grid|px-\d)"),
    ("json_import_export",  r"JSON\.stringify|JSON\.parse"),
    ("file_upload",         r"type=\"file\"|FileReader|createObjectURL"),
    ("splash",              r"splash|Splash|SPLASH"),
    ("timer_delay",         r"setTimeout|setInterval|requestAnimationFrame"),
    ("css_animation",       r"@keyframes|transition:|animation:"),
    ("router",              r"createRouter|react-router|history\.pushState"),
]

# Indicios de sistema de controle ja existente.
ADMIN_SIGNALS = [
    ("admin_file",          r"admin\.html|/admin\b|AdminPanel|admin-panel"),
    ("overlay_panel",       r"overlay|modal|drawer|painel|panel"),
    ("hidden_discovery",    r"dblclick|detail\s*===\s*3|clickCount|longPress|keydown.*(Shift|Ctrl|Alt)"),
    ("password_gate",       r"password|senha|PASSWORD|prompt\s*\("),
    ("config_object",       r"\b(config|CONFIG|settings|SETTINGS|defaults|DEFAULTS)\s*[=:]"),
    ("render_function",     r"function\s+(render|update|apply|refresh)\w*|const\s+(render|update|apply)\w*\s*="),
    ("reset_restore",       r"\breset\b|\brestore\b|\bdefault(s)?\b"),
]


def collect_files(root: str) -> tuple[list[str], str]:
    """Retorna (lista de caminhos relativos, modo). Modo e 'file' ou 'dir'."""
    if os.path.isfile(root):
        return [os.path.basename(root)], "file"

    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            found.append(rel)
    return sorted(found), "dir"


def read_code(root: str, files: list[str], mode: str, max_bytes: int) -> tuple[str, list[str]]:
    """Concatena o conteudo dos arquivos de codigo, respeitando um teto de bytes."""
    chunks: list[str] = []
    read_files: list[str] = []
    budget = max_bytes

    for rel in files:
        ext = os.path.splitext(rel)[1].lower()
        base = os.path.basename(rel)
        if ext not in CODE_EXT and base not in CONFIG_NAMES:
            continue
        path = root if mode == "file" else os.path.join(root, rel)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                data = fh.read(budget)
        except OSError:
            continue
        if not data:
            continue
        chunks.append(data)
        read_files.append(rel)
        budget -= len(data)
        if budget <= 0:
            break

    return "\n".join(chunks), read_files


def detect(blob: str, table: list[tuple[str, str]]) -> list[str]:
    return [key for key, pattern in table if re.search(pattern, blob)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspeciona um projeto web para a skill page-control.")
    parser.add_argument("target", help="diretorio do projeto ou um unico arquivo HTML")
    parser.add_argument("--max-bytes", type=int, default=2_000_000,
                        help="teto de bytes lidos no total (padrao: 2000000)")
    args = parser.parse_args()

    root = os.path.abspath(args.target)
    if not os.path.exists(root):
        print(json.dumps({"error": f"caminho inexistente: {args.target}"}, ensure_ascii=False))
        return 1

    files, mode = collect_files(root)
    blob, read_files = read_code(root, files, mode, args.max_bytes)

    html_files = [f for f in files if os.path.splitext(f)[1].lower() in {".html", ".htm"}]
    js_files = [f for f in files if os.path.splitext(f)[1].lower() in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}]
    css_files = [f for f in files if os.path.splitext(f)[1].lower() in {".css", ".scss"}]
    configs = [f for f in files if os.path.basename(f) in CONFIG_NAMES]

    inline_script = bool(re.search(r"<script(?![^>]*\bsrc=)[^>]*>", blob))
    single_file = len(html_files) == 1 and not js_files and not css_files and inline_script

    report = {
        "target": root,
        "mode": mode,
        "counts": {
            "total_files": len(files),
            "html": len(html_files),
            "js": len(js_files),
            "css": len(css_files),
            "config": len(configs),
            "files_read": len(read_files),
        },
        "files": {
            "html": html_files[:50],
            "js": js_files[:50],
            "css": css_files[:50],
            "config": configs,
        },
        "signals": detect(blob, SIGNALS),
        "admin_signals": detect(blob, ADMIN_SIGNALS),
        "constraints": {
            "single_file": single_file,
            "inline_script": inline_script,
            "no_build_config": not configs,
        },
        "notes": [
            "Deteccao por regex: um sinal presente indica mencao, nao uso correto.",
            "Ausencia de sinal em arquivos nao lidos nao prova ausencia no projeto.",
            "Leia os arquivos apontados antes de decidir a arquitetura.",
        ],
    }

    if len(read_files) < len([f for f in files if os.path.splitext(f)[1].lower() in CODE_EXT]):
        report["notes"].append("Teto de bytes atingido: parte do codigo nao foi lida.")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
