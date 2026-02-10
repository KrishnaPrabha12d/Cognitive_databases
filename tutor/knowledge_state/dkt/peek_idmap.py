import os, json

IDMAP_PATH = os.path.join("external", "models", "dkt", "ednet_v1", "id_map.json")

if __name__ == "__main__":
    with open(IDMAP_PATH, "r", encoding="utf-8") as f:
        m = json.load(f)

    # If mapping is index->item, print a few values. Else print keys.
    sample = []
    try:
        first_val = next(iter(m.values()))
        if isinstance(first_val, str):
            sample = list(m.values())[:10]
        else:
            sample = list(m.keys())[:10]
    except StopIteration:
        sample = []

    print("SAMPLE ITEM IDS:")
    for x in sample:
        print(x)