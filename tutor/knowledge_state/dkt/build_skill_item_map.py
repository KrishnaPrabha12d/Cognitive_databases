import os, json
from collections import defaultdict

IDMAP_PATH = os.path.join("external", "models", "dkt", "ednet_v1", "id_map.json")
OUT_PATH = os.path.join("tutor", "knowledge_state", "dkt", "skill_item_map.py")

# Put the skills you actually use in your app/database here:
SKILLS = [
    "fractions",
    "addition",
    "algebra",
]

def load_items():
    with open(IDMAP_PATH, "r", encoding="utf-8") as f:
        m = json.load(f)

    # If mapping is index->item, items are values; else items are keys.
    try:
        first_val = next(iter(m.values()))
        if isinstance(first_val, str):
            return list(m.values())
        else:
            return list(m.keys())
    except StopIteration:
        return []

def find_best_item(skill: str, items: list[str]) -> str | None:
    s = skill.lower()
    # Try keyword match (contains)
    for it in items:
        if s in str(it).lower():
            return str(it)

    # Try softer match: first 4 letters
    key = s[:4]
    for it in items:
        if key in str(it).lower():
            return str(it)

    return None

def main():
    items = load_items()
    mapping = {}

    for skill in SKILLS:
        best = find_best_item(skill, items)
        mapping[skill] = best  # can be None

    # Write python mapping file
    lines = []
    lines.append('"""Auto-generated skill->DKT item mapping."""\n')
    lines.append("SKILL_TO_ITEM = {\n")
    for k, v in mapping.items():
        if v is None:
            lines.append(f'    "{k}": None,\n')
        else:
            lines.append(f'    "{k}": "{v}",\n')
    lines.append("}\n")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("Wrote:", OUT_PATH)
    for k, v in mapping.items():
        print(f"{k:15s} -> {v}")

if __name__ == "__main__":
    main()