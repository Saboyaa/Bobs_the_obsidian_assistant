import os
import json
import subprocess
from collections import defaultdict


###########################################################
# --- RUN ingest_vault.py AND GET THE TOON OUTPUT ---
###########################################################

def run_ingest_and_get_toon(file_path):
    """Runs ingest_vault.py ingest <file_path> and returns ALL printed TOON."""
    
    result = subprocess.run(
        ["python3", "ingest_vault.py", "ingest", file_path],
        text=True,
        capture_output=True
    )

    toon_output = result.stdout.strip()
    return toon_output


###########################################################
# --- OLLAMA LLM CALL ---
###########################################################

def ollama(prompt, model="llama3.1"):
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True
    )

    return result.stdout.strip()


###########################################################
# --- EXTRACT ENTITIES FROM TOON TEXT ---
###########################################################

def extract_entities_for_toon(toon_text):
    """
    Send raw TOON to the LLM and extract only meaningful tech entities.
    """

    prompt = f"""
You will receive a TOON chunk list from LightRAG.

Extract ONLY meaningful technical entities:
- tools, technologies, protocols, systems, concepts, products, frameworks
- MUST be real-world known concepts
- MUST be unique
- MUST NOT include flags (-k, -I), examples, URLs, headers, numbers, file paths, or verbs
- MUST NOT include code fragments
- MUST NOT include random words

Return ONLY a JSON array. No explanation.

TOON:
{toon_text}

Example of correct style:
["Linux", "Docker", "GitHub", "EDR", "Threat Intelligence"]
"""

    raw = ollama(prompt)
    print("\nMODEL RAW OUTPUT:\n", raw)

    try:
        return json.loads(raw)
    except:
        return []


###########################################################
# --- PROCESS A SINGLE NOTE ---
###########################################################

def process_single_note(path):
    print(f"\n📄 Processing: {path}")

    toon = run_ingest_and_get_toon(path)
    entities = extract_entities_for_toon(toon)

    # Normalize: lowercase + trim
    return set(e.lower().strip() for e in entities)


###########################################################
# --- BUILD ENTITY GRAPH ACROSS ALL FILES ---
###########################################################

def build_graph_for_folder(folder):
    file_entities = {}

    for fname in os.listdir(folder):
        if not fname.endswith(".md"):
            continue

        full_path = os.path.join(folder, fname)
        entities = process_single_note(full_path)

        file_entities[fname] = entities

    # Build graph based on shared entities
    graph = defaultdict(set)
    files = list(file_entities.keys())

    for i, f1 in enumerate(files):
        for f2 in files[i+1:]:
            shared = file_entities[f1].intersection(file_entities[f2])
            if shared:
                graph[f1].add(f2)
                graph[f2].add(f1)

    return {
        "file_entities": {k: list(v) for k, v in file_entities.items()},
        "graph": {k: list(v) for k, v in graph.items()}
    }


###########################################################
# --- MAIN ---
###########################################################

if __name__ == "__main__":
    folder = "/home/sabs/obsidian/Code"  # change if needed

    graph = build_graph_for_folder(folder)

    print("\n=== FINAL GRAPH ===")
    print(json.dumps(graph, indent=4))
    with open("graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4, ensure_ascii=False)