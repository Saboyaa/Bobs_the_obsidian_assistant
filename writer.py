import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NOTES_DIR = Path(os.getenv("NOTES_DIR"))
GRAPH_JSON = Path(os.getenv("CONNECTIONS_JSON"))
SECTION_HEADER = "# Related files"

def load_graph():
    with open(GRAPH_JSON, "r", encoding="utf8") as f:
        return json.load(f)["graph"]

def has_related_section(text):
    return SECTION_HEADER in text

def linkify(name):
    """Converte 'Linux Logs.md' para '[[Linux Logs]]'"""
    return f"[[{Path(name).stem}]]"

def build_section(related_files):
    if not related_files:
        return ""  # evita criar seção vazia
    lines = [SECTION_HEADER]
    for f in sorted(set(related_files)):  # remove duplicados, ordena
        lines.append(f"- {linkify(f)}")
    return "\n".join(lines)

def append_section(file_path, section_text):
    with open(file_path, "a", encoding="utf8") as f:
        f.write("\n\n" + section_text)

def process_file(file_path, related):
    with open(file_path, "r", encoding="utf8") as f:
        content = f.read()

    if has_related_section(content):
        print(f"[SKIP] {file_path.name} já tem seção.")
        return

    section = build_section(related)
    if section.strip():
        append_section(file_path, section)
        print(f"[OK] Seção adicionada em {file_path.name}")
    else:
        print(f"[SKIP] {file_path.name} não tem conexões.")

def main():
    graph = load_graph()

    for filename, related_files in graph.items():
        file_path = NOTES_DIR / filename
        if file_path.exists():
            process_file(file_path, related_files)
        else:
            print(f"[WARN] Arquivo não encontrado: {filename}")

if __name__ == "__main__":
    main()
