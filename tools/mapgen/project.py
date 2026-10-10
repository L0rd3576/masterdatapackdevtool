"""Load and cross-check a framework project: project.json, minigames/, maps/, presets/, pool.json.

Schema problems and cross-reference problems are collected (not raised) so one run shows everything.
"""
import os

import core
import schema

ROOT = core.ROOT
FRAMEWORK_PACK = os.path.join(ROOT, "tools", "framework", "pack")
HOOKS = ("load", "start", "player_start", "tick", "eliminated", "end")


def win_conditions():
    d = os.path.join(FRAMEWORK_PACK, "data", "__ns__", "function", "win")
    return sorted(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n))) if os.path.isdir(d) else []


def tags_ok(game, mp):
    t = set(mp["tags"])
    mt = game.get("map_tags", {})
    if not set(mt.get("all_of", [])) <= t:
        return False
    if mt.get("any_of") and not t & set(mt["any_of"]):
        return False
    return not t & set(mt.get("none_of", []))


class Project:
    def __init__(self, path):
        self.dir = os.path.abspath(path)
        self.issues = []
        self.project = None
        self.minigames, self.maps, self.presets = {}, {}, {}
        self.map_paths = {}
        self.pool = None

    def err(self, file, msg, path=""):
        self.issues.append(schema.Issue("ERROR", file, path, msg))

    def warn(self, file, msg, path=""):
        self.issues.append(schema.Issue("WARN", file, path, msg))

    @property
    def ok(self):
        return not schema.errors(self.issues)

    def _load(self, path, kind):
        try:
            data, issues = core.load_manifest(path, kind)
        except core.MapgenError as e:
            self.err(path, str(e).replace(f"ERROR: {path}: ", ""))
            return None
        self.issues += issues
        return data

    def _load_dir(self, sub, kind, into):
        d = os.path.join(self.dir, sub)
        if not os.path.isdir(d):
            return
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            p = os.path.join(d, fn)
            data = self._load(p, kind)
            if data is None:
                continue
            if data["id"] != fn[:-5]:
                self.err(p, f"id {data['id']!r} must match the file name {fn[:-5]!r}", "id")
            if data["id"] in into:
                self.err(p, f"duplicate {kind} id {data['id']!r}", "id")
            into[data["id"]] = data
            if kind == "map":
                self.map_paths[data["id"]] = p


def load_project(path):
    pr = Project(path)
    pj = os.path.join(pr.dir, "project.json")
    if not os.path.isfile(pj):
        pr.err(pj, "missing project.json")
        return pr
    pr.project = pr._load(pj, "project")
    pr._load_dir("minigames", "minigame", pr.minigames)
    pr._load_dir("maps", "map", pr.maps)
    pr._load_dir("presets", "preset", pr.presets)
    pool_path = os.path.join(pr.dir, "pool.json")
    if os.path.isfile(pool_path):
        pr.pool = pr._load(pool_path, "pool")
    else:
        pr.err(pool_path, "missing pool.json")
    if pr.project is None or pr.pool is None:
        return pr
    _cross_check(pr, pool_path)
    return pr


def _cross_check(pr, pool_path):
    wins = win_conditions()
    for gid, g in pr.minigames.items():
        f = os.path.join(pr.dir, "minigames", gid + ".json")
        if g["players"]["min"] > g["players"]["max"]:
            pr.err(f, "players.min > players.max", "players")
        if g["win_condition"] not in wins:
            pr.err(f, f"unknown win_condition {g['win_condition']!r}; framework provides: {', '.join(wins)}",
                   "win_condition")
        for name, spec in g["settings"].items():
            _check_setting_value(pr, f, f"settings.{name}.default", spec, spec["default"])
            if spec["type"] == "int" and "min" in spec and "max" in spec and spec["min"] > spec["max"]:
                pr.err(f, "min > max", f"settings.{name}")
        for hook, rel in g["functions"].items():
            hp = os.path.join(pr.dir, rel)
            if not os.path.isfile(hp):
                pr.err(f, f"hook file {rel} not found (resolved {hp})", f"functions.{hook}")
            elif not rel.endswith(".mcfunction"):
                pr.err(f, "hook files must end in .mcfunction", f"functions.{hook}")
        r = g["rules"]
        if r.get("gamemode", "auto") in ("auto", "survival") and r.get("block_break") and not r.get("block_place"):
            pr.warn(f, "block_place:false cannot be enforced in survival mode (only adventure mode stops placing); "
                       "players will be able to place blocks", "rules")
        if r.get("gamemode") == "adventure" and (r.get("block_break") or r.get("block_place")):
            pr.warn(f, "adventure mode prevents breaking/placing; block_break/block_place true has no effect", "rules")
    for mid, mp in pr.maps.items():
        f = pr.map_paths[mid]
        if mp["players"]["min"] > mp["players"]["max"]:
            pr.err(f, "players.min > players.max", "players")
        for t in mp["tag_meta"]:
            if t not in mp["tags"]:
                pr.warn(f, f"tag_meta for tag {t!r} that the map does not have", "tag_meta")
    for pid, p in pr.presets.items():
        f = os.path.join(pr.dir, "presets", pid + ".json")
        g = pr.minigames.get(p["minigame"])
        if g is None:
            pr.err(f, f"unknown minigame {p['minigame']!r}", "minigame")
            continue
        for k, v in p["settings"].items():
            if k not in g["settings"]:
                pr.err(f, f"minigame {g['id']} has no setting {k!r} (has: {', '.join(g['settings']) or 'none'})",
                       f"settings.{k}")
            else:
                _check_setting_value(pr, f, f"settings.{k}", g["settings"][k], v)
    # pool references
    games = [e for e in pr.pool["minigames"] if e["enabled"]]
    maps = [e for e in pr.pool["maps"] if e["enabled"]]
    for i, e in enumerate(pr.pool["minigames"]):
        if e["id"] not in pr.minigames:
            pr.err(pool_path, f"unknown minigame {e['id']!r}", f"minigames[{i}].id")
        for j, ps in enumerate(e.get("presets", [])):
            if ps["id"] not in pr.presets:
                pr.err(pool_path, f"unknown preset {ps['id']!r}", f"minigames[{i}].presets[{j}]")
            elif pr.presets[ps["id"]]["minigame"] != e["id"]:
                pr.err(pool_path, f"preset {ps['id']!r} belongs to {pr.presets[ps['id']]['minigame']!r}",
                       f"minigames[{i}].presets[{j}]")
    for i, e in enumerate(pr.pool["maps"]):
        if e["id"] not in pr.maps:
            pr.err(pool_path, f"unknown map {e['id']!r}", f"maps[{i}].id")
    if not pr.ok:
        return
    lo, hi = pr.project["players"]["min"], pr.project["players"]["max"]
    used = set()
    for e in games:
        g = pr.minigames[e["id"]]
        pairs = [m for m in maps if tags_ok(g, pr.maps[m["id"]]) and
                 max(g["players"]["min"], pr.maps[m["id"]]["players"]["min"]) <=
                 min(g["players"]["max"], pr.maps[m["id"]]["players"]["max"])]
        used |= {m["id"] for m in pairs}
        if not pairs:
            pr.err(pool_path, f"minigame {g['id']!r} has no compatible enabled map (tags + player range)")
    for m in maps:
        if m["id"] not in used:
            pr.warn(pool_path, f"map {m['id']!r} is not used by any enabled minigame")
    empty = [n for n in range(lo, hi + 1) if not candidates(pr, n)]
    if empty:
        pr.warn(pr.dir + os.sep + "project.json", f"no minigame/map combination for player counts {empty}")


def _check_setting_value(pr, f, path, spec, v):
    t = spec["type"]
    ok = (t == "int" and isinstance(v, int) and not isinstance(v, bool)) or (t == "bool" and isinstance(v, bool)) \
        or (t == "string" and isinstance(v, str))
    if not ok:
        pr.err(f, f"value {v!r} is not of type {t}", path)
        return
    if t == "int":
        if "min" in spec and v < spec["min"]:
            pr.err(f, f"{v} < min {spec['min']}", path)
        if "max" in spec and v > spec["max"]:
            pr.err(f, f"{v} > max {spec['max']}", path)
    if t == "string" and spec.get("options") and v not in spec["options"]:
        pr.err(f, f"{v!r} is not one of {spec['options']}", path)


def candidates(pr, n):
    """All (game, preset_or_None, map, weight) playable with n participants."""
    out = []
    for ge in pr.pool["minigames"]:
        if not ge["enabled"] or ge["id"] not in pr.minigames:
            continue
        g = pr.minigames[ge["id"]]
        variants = ([(None, 1)] if ge.get("include_default", True) or not ge.get("presets") else []) + \
            [(p["id"], p.get("weight", 1)) for p in ge.get("presets", [])]
        for me in pr.pool["maps"]:
            if not me["enabled"] or me["id"] not in pr.maps:
                continue
            mp = pr.maps[me["id"]]
            if not tags_ok(g, mp):
                continue
            if not (max(g["players"]["min"], mp["players"]["min"]) <= n <= min(g["players"]["max"], mp["players"]["max"])):
                continue
            for preset, pw in variants:
                w = ge["weight"] * me["weight"] * pw
                if w > 0:
                    out.append((g["id"], preset, mp["id"], w))
    return out
