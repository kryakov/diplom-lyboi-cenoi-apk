import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 32, 18


def parse(text, name):
    head, _, body = text.partition("\n---\n")
    meta = {}
    for line in head.splitlines():
        if line.strip() and ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    rows = [r.rstrip("\r") for r in body.strip("\n").split("\n")]
    if len(rows) != H or any(len(r) != W for r in rows):
        raise ValueError(f"{name}: нужно ровно {H} строк по {W} символов (сейчас {len(rows)} строк)")
    for k in ("id", "name", "type", "background"):
        if k not in meta:
            raise ValueError(f"{name}: в шапке нет '{k}:'")
    cells = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            cells.setdefault(ch, []).append((x, y))
    unknown = set(cells) - set("#.PEBN+DV")
    if unknown:
        raise ValueError(f"{name}: неизвестные символы {sorted(unknown)}")
    if len(cells.get("P", [])) != 1:
        raise ValueError(f"{name}: нужен ровно один P (старт героя)")


    runs = []
    for y, row in enumerate(rows):
        x = 0
        while x < W:
            if row[x] == "#":
                s = x
                while x < W and row[x] == "#":
                    x += 1
                runs.append([s, y, x - s, 1])
            else:
                x += 1
    walls = []
    for r in runs:
        for w in walls:
            if w[0] == r[0] and w[2] == r[2] and w[1] + w[3] == r[1]:
                w[3] += 1
                break
        else:
            walls.append(r)

    door = None
    if "D" in cells:
        xs = [c[0] for c in cells["D"]]
        ys = [c[1] for c in cells["D"]]
        x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if w * h != len(cells["D"]):
            raise ValueError(f"{name}: клетки D должны образовывать один прямоугольник")
        door = {"pos": [x0, y0, w, h], "locked_until_clear": meta.get("locked", "false").lower() == "true"}

    enemies = [{"type": meta["enemy"], "pos": list(c)} for c in cells.get("E", [])]
    if cells.get("V") and "bird" not in meta:
        raise ValueError(f"{name}: есть V, но в шапке нет 'bird:'")
    enemies += [{"type": meta["bird"], "pos": list(c)} for c in cells.get("V", [])]
    if cells.get("E") and "enemy" not in meta:
        raise ValueError(f"{name}: есть E, но в шапке нет 'enemy:'")
    for c in cells.get("B", []):
        if "boss" not in meta:
            raise ValueError(f"{name}: есть B, но в шапке нет 'boss:'")
        enemies.append({"type": meta["boss"], "pos": list(c)})
    npcs = []
    for c in cells.get("N", []):
        if "npc" not in meta:
            raise ValueError(f"{name}: есть N, но в шапке нет 'npc:' (id диалога)")
        npcs.append({"id": meta["npc"], "pos": list(c), "dialogue": meta["npc"]})
    pickups = [{"kind": "heal", "pos": list(c), "amount": int(meta.get("heal", "1"))} for c in cells.get("+", [])]

    room = {"id": meta["id"], "name": meta["name"], "type": meta["type"], "background": meta["background"],
            "size": [W, H], "player_spawn": list(cells["P"][0]), "walls": walls}
    if door:
        room["door"] = door
    room.update({"enemies": enemies, "npcs": npcs, "pickups": pickups})
    return room


def convert(path):
    path = Path(path)
    room = parse(path.read_text(encoding="utf-8"), path.name)
    if room["id"] != path.stem:
        raise ValueError(f"{path.name}: id '{room['id']}' не совпадает с именем файла")
    out = ROOT / "data" / "rooms" / f"{room['id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(room, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK:", out.relative_to(ROOT))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    files = sorted((ROOT / "data" / "rooms_src").glob("*.txt")) if args[0] == "--all" else [Path(a) for a in args]
    try:
        for f in files:
            convert(f)
    except ValueError as e:
        print("ОШИБКА:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())