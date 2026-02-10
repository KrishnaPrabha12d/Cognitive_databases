import os, json
from tutor.knowledge_state.dkt.skill_item_map import SKILL_TO_ITEM

IDMAP_PATH = os.path.join("external", "models", "dkt", "ednet_v1", "id_map.json")

if __name__ == "__main__":
    with open(IDMAP_PATH, "r", encoding="utf-8") as f:
        id_map = json.load(f)

    # if id_map is index->item, flip to item->index
    try:
        first_val = next(iter(id_map.values()))
        if isinstance(first_val, str):
            valid_items = set(id_map.values())
        else:
            valid_items = set(id_map.keys())
    except StopIteration:
        valid_items = set()

    print("Total items in id_map:", len(valid_items))

    for skill, item in SKILL_TO_ITEM.items():
        ok = item in valid_items
        print(f"{skill:20s} -> {item:20s} | {'OK' if ok else 'MISSING'}")