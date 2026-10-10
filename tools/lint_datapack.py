#!/usr/bin/env python3
"""Static checker for Minecraft Java 26.3 datapacks (Python 3 stdlib only).

Usage:
    python tools/lint_datapack.py <datapack-dir> [--strict] [--quiet]

Exit code 1 if any ERROR (or any WARNING with --strict). Checks:
  - pack.mcmeta structure and that the format range includes 26.3 (data format 121)
  - folder names vs. the 26.3 registry layout (generated/reports/datapack.json); old plural names flagged
  - resource location validity of every file path and reference
  - JSON parse + old/renamed keys + keys never seen in vanilla 26.3 files of the same type (warning)
  - tag entries resolve; function/tag/loot/predicate references resolve
  - every .mcfunction line walked against generated/reports/commands.json, with registry-ID checks
Source of truth: generated/reports/* and reference/vanilla-data/ built from the 26.3 server jar.
The server (tools/run_tests.py) is the final authority; if it rejects something this passes, fix this file.
"""
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "generated", "reports")
VANILLA = os.path.join(ROOT, "reference", "vanilla-data", "minecraft")
DATA_FORMAT = (121, 0)          # generated from server jar version.json: pack_version.data_major/minor
FUNCTION_PERMISSION_LEVEL = 2   # server.properties default function-permission-level
PERM_LEVELS = {"all": 0, "moderators": 1, "gamemasters": 2, "admins": 3, "owners": 4}

# Folder names used before 1.21 (plural) -> 26.3 name.
OLD_FOLDERS = {
    "functions": "function", "advancements": "advancement", "loot_tables": "loot_table",
    "predicates": "predicate", "item_modifiers": "item_modifier", "recipes": "recipe",
    "structures": "structure", "tags/functions": "tags/function", "tags/blocks": "tags/block",
    "tags/items": "tags/item", "tags/entity_types": "tags/entity_type", "tags/fluids": "tags/fluid",
    "tags/game_events": "tags/game_event",
    "worldgen/configured_feature": "worldgen/feature (26.3: configured_feature removed, config inlined)",
    "worldgen/configured_carver": "worldgen/carver",
}
# Keys that were renamed in loot tables / predicates / item modifiers (26.3: verified in vanilla data,
# where these keys no longer occur at all).
LOOT_OLD_KEYS = {"functions": "modifier", "conditions": "condition", "function": "type"}
TEXT_OLD_KEYS = {"clickEvent": "click_event", "hoverEvent": "hover_event"}

RL_NS = re.compile(r"^[a-z0-9_.\-]+$")
RL_PATH = re.compile(r"^[a-z0-9_.\-/]+$")
WORD = re.compile(r"[0-9A-Za-z_\-.+]+")
NUM = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?")
SELECTOR_KEYS = {"x", "y", "z", "distance", "dx", "dy", "dz", "scores", "tag", "team", "limit", "sort",
                 "level", "gamemode", "name", "x_rotation", "y_rotation", "type", "nbt", "advancements",
                 "predicate"}
MACRO = "\u0001M\u0001"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- reference data
class Ref:
    def __init__(self):
        dp = load_json(os.path.join(REPORTS, "datapack.json"))
        self.element_folders = {k.split(":", 1)[1] for k, v in dp["registries"].items() if v["elements"]}
        self.element_folders |= {k for k, v in dp["others"].items() if v["elements"]}
        self.tag_folders = {k.split(":", 1)[1] for k, v in dp["registries"].items() if v["tags"]}
        self.tag_folders |= {k for k, v in dp["others"].items() if v["tags"]}
        self.commands = load_json(os.path.join(REPORTS, "commands.json"))
        regs = load_json(os.path.join(REPORTS, "registries.json"))
        self.static = {k.split(":", 1)[1]: set(v["entries"]) for k, v in regs.items()}
        self.blocks = load_json(os.path.join(REPORTS, "blocks.json"))
        self.vanilla_elements = {}   # folder -> set of ids
        self.vanilla_tags = {}       # folder -> set of ids
        self.vanilla_keys = {}       # folder -> set of JSON keys seen anywhere in vanilla files
        self.type_values = set()
        self._scan_vanilla()

    def _scan_vanilla(self):
        cache = os.path.join(ROOT, "generated", "lint-cache.json")
        if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(os.path.join(REPORTS, "datapack.json")):
            c = load_json(cache)
            self.vanilla_elements = {k: set(v) for k, v in c["elements"].items()}
            self.vanilla_tags = {k: set(v) for k, v in c["tags"].items()}
            self.vanilla_keys = {k: set(v) for k, v in c["keys"].items()}
            self.type_values = set(c["types"])
            return
        for dirpath, _, files in os.walk(VANILLA):
            rel = os.path.relpath(dirpath, VANILLA).replace(os.sep, "/")
            if rel.startswith("datapacks"):
                continue
            for fn in files:
                relfile = (rel + "/" + fn) if rel != "." else fn
                if relfile.startswith("tags/"):
                    folder, rid = split_registry(relfile[5:], self.tag_folders)
                    if folder:
                        self.vanilla_tags.setdefault(folder, set()).add("minecraft:" + rid)
                    continue
                folder, rid = split_registry(relfile, self.element_folders)
                if not folder:
                    continue
                self.vanilla_elements.setdefault(folder, set()).add("minecraft:" + rid)
                if fn.endswith(".json"):
                    keys = self.vanilla_keys.setdefault(folder, set())
                    collect_keys(load_json(os.path.join(dirpath, fn)), keys, self.type_values)
        try:
            with open(cache, "w", encoding="utf-8") as f:
                json.dump({"elements": {k: sorted(v) for k, v in self.vanilla_elements.items()},
                           "tags": {k: sorted(v) for k, v in self.vanilla_tags.items()},
                           "keys": {k: sorted(v) for k, v in self.vanilla_keys.items()},
                           "types": sorted(self.type_values)}, f)
        except OSError:
            pass


def collect_keys(obj, keys, types):
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            if k == "type" and isinstance(v, str):
                types.add(v)
            collect_keys(v, keys, types)
    elif isinstance(obj, list):
        for x in obj:
            collect_keys(x, keys, types)


def split_registry(relpath, folders):
    """'worldgen/biome/foo/bar.json' -> ('worldgen/biome', 'foo/bar')."""
    parts = relpath.split("/")
    for n in (3, 2, 1):
        if len(parts) > n and "/".join(parts[:n]) in folders:
            return "/".join(parts[:n]), os.path.splitext("/".join(parts[n:]))[0]
    return None, None


def norm_id(s):
    return s if ":" in s else "minecraft:" + s


def valid_rl(s):
    if s.count(":") > 1:
        return False
    ns, _, path = s.rpartition(":")
    return (not ns or RL_NS.match(ns)) and bool(path) and bool(RL_PATH.match(path))


# --------------------------------------------------------------------------- pack model
class Pack:
    def __init__(self, root, ref):
        self.root = root
        self.ref = ref
        self.elements = {}   # folder -> {id: filepath}
        self.tags = {}       # folder -> {id: filepath}
        self.files = []
        self.objectives_created = set()
        self.macro_functions = set()
        self.macro_args = {}  # function id -> set of $(names) it needs
        self.calls = []       # (loc, called id, args text or None)


class Linter:
    def __init__(self, pack_dir):
        self.ref = Ref()
        self.pack = Pack(pack_dir, self.ref)
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append(f"ERROR {where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"WARN  {where}: {msg}")

    def rel(self, path):
        return os.path.relpath(path, self.pack.root).replace(os.sep, "/")

    # ---------------- lookups
    def element_exists(self, folder, rid, allow_tag=False):
        rid = norm_id(rid)
        if rid.startswith("#"):
            return self.tag_exists(folder, rid[1:]) if allow_tag else False
        if rid in self.pack.elements.get(folder, {}) or rid in self.ref.vanilla_elements.get(folder, set()):
            return True
        return rid in self.ref.static.get(folder, set())

    def tag_exists(self, folder, tid):
        tid = norm_id(tid)
        return tid in self.pack.tags.get(folder, {}) or tid in self.ref.vanilla_tags.get(folder, set())

    def check_ref(self, where, folder, value, allow_tag=True, kind=None):
        v = value.strip()
        is_tag = v.startswith("#")
        raw = v[1:] if is_tag else v
        if MACRO in raw:
            return
        if not valid_rl(raw):
            self.err(where, f"invalid resource location '{v}' (lowercase a-z 0-9 _ - . / and one ':')")
            return
        if is_tag and not allow_tag:
            self.err(where, f"tags not allowed here: '{v}'")
            return
        ok = self.tag_exists(folder, raw) if is_tag else self.element_exists(folder, raw)
        if not ok:
            what = kind or folder
            self.err(where, f"unknown {'tag' if is_tag else what} '{v}'"
                     + (f" (no file data/{norm_id(raw).replace(':', '/' + ('tags/' if is_tag else '') + folder + '/', 1)}"
                        f"{'.mcfunction' if folder == 'function' and not is_tag else '.json'})"
                        if folder not in self.ref.static or is_tag else ""))

    # ---------------- top level
    def run(self):
        root = self.pack.root
        if not os.path.isdir(root):
            self.err(root, "not a directory")
            return
        self.check_mcmeta()
        data = os.path.join(root, "data")
        if not os.path.isdir(data):
            self.err("data/", "missing data/ folder")
            return
        roots = [data]
        for ov in self.overlays:
            d = os.path.join(root, ov, "data")
            if os.path.isdir(d):
                roots.append(d)
        for d in roots:
            self.index(d)
        for path, kind, folder, rid in self.pack.files:
            if kind == "function":
                self.lint_function(path, rid)
            elif kind == "json":
                self.lint_json(path, folder, rid)
            elif kind == "tag":
                self.lint_tag(path, folder, rid)
        self.post_checks()

    def check_mcmeta(self):
        self.overlays = []
        p = os.path.join(self.pack.root, "pack.mcmeta")
        if not os.path.isfile(p):
            self.err("pack.mcmeta", "missing (the server ignores the folder: \"Found non-pack entry\")")
            return
        try:
            meta = load_json(p)
        except (ValueError, UnicodeDecodeError) as e:
            self.err("pack.mcmeta", f"invalid JSON: {e}")
            return
        pack = meta.get("pack") if isinstance(meta, dict) else None
        if not isinstance(pack, dict):
            self.err("pack.mcmeta", 'missing "pack" object')
            return
        if "description" not in pack:
            self.err("pack.mcmeta", 'missing "pack.description"')
        lo, hi = self.format_range(pack, "pack.mcmeta pack")
        if lo is not None and not (lo <= DATA_FORMAT <= hi):
            self.err("pack.mcmeta", f"format range {fmt(lo)}..{fmt(hi)} does not include 26.3 data format {fmt(DATA_FORMAT)}")
        ovs = meta.get("overlays")
        if ovs is not None:
            entries = ovs.get("entries") if isinstance(ovs, dict) else None
            if not isinstance(entries, list):
                self.err("pack.mcmeta", '"overlays" must be {"entries": [...]}')
            else:
                for i, e in enumerate(entries):
                    d = e.get("directory") if isinstance(e, dict) else None
                    if not isinstance(d, str) or not re.match(r"^[a-z0-9_.\-]+$", d):
                        self.err("pack.mcmeta", f"overlays.entries[{i}].directory invalid: {d!r}")
                        continue
                    self.overlays.append(d)
                    if "min_format" not in e or "max_format" not in e:
                        self.err("pack.mcmeta", f"overlays.entries[{i}] needs min_format and max_format (1.21.9+)")

    def format_range(self, obj, where):
        def parse(v):
            if isinstance(v, int):
                return (v, 0)
            if isinstance(v, list) and 1 <= len(v) <= 2 and all(isinstance(x, int) for x in v):
                return (v[0], v[1] if len(v) == 2 else 0)
            return None
        if "min_format" not in obj or "max_format" not in obj:
            if "pack_format" in obj:
                self.err(where, '"pack_format" alone is the pre-1.21.9 form; 26.3 needs "min_format" and "max_format" '
                         '(server: "Pack declares support for version newer than 81, but is missing mandatory fields min_format and max_format")')
            else:
                self.err(where, 'missing "min_format" and "max_format"')
            return None, None
        lo, hi = parse(obj["min_format"]), parse(obj["max_format"])
        if lo is None or hi is None:
            self.err(where, "min_format/max_format must be an int or [major, minor]")
            return None, None
        if isinstance(obj["max_format"], int):
            hi = (hi[0], 2 ** 31)   # an int max_format accepts any minor version
        if lo > hi:
            self.err(where, "min_format is greater than max_format")
        if lo[0] <= 81 and "supported_formats" not in obj:
            self.err(where, "min_format <= 81 also requires \"supported_formats\" and \"pack_format\" (server rule for "
                     "packs that claim support for 1.20.2-1.21.8); simplest: set min_format to 121")
        return lo, hi

    def index(self, data_dir):
        for ns in sorted(os.listdir(data_dir)):
            nsdir = os.path.join(data_dir, ns)
            if not os.path.isdir(nsdir):
                self.warn(self.rel(nsdir), "stray file in data/ (ignored by the game)")
                continue
            if not RL_NS.match(ns):
                self.err(self.rel(nsdir), f"invalid namespace '{ns}': only lowercase a-z 0-9 _ - . allowed "
                         "(the server silently ignores this folder)")
                continue
            for dirpath, dirs, files in os.walk(nsdir):
                dirs.sort()
                for fn in sorted(files):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, nsdir).replace(os.sep, "/")
                    self.index_file(ns, rel, full)

    def index_file(self, ns, rel, full):
        where = self.rel(full)
        for old, new in OLD_FOLDERS.items():
            if rel.startswith(old + "/"):
                self.err(where, f"folder '{old}/' is not used in 26.3 (silently ignored); rename to '{new}/'")
                return
        if rel.startswith("tags/"):
            folder, rid = split_registry(rel[5:], self.ref.tag_folders)
            if not folder:
                self.err(where, f"unknown tag folder 'tags/{rel[5:].split('/')[0]}/' (valid: {', '.join(sorted(t for t in self.ref.tag_folders if '/' not in t)[:12])}, ...)")
                return
            if not fn_ok(full, ".json"):
                self.warn(where, "tag files must be .json (ignored)")
                return
            if self.check_path_chars(where, ns, rid):
                self.pack.tags.setdefault(folder, {})[f"{ns}:{rid}"] = full
                self.pack.files.append((full, "tag", folder, f"{ns}:{rid}"))
            return
        folder, rid = split_registry(rel, self.ref.element_folders)
        if not folder:
            first = rel.split("/")[0]
            if "/" not in rel:
                self.warn(where, "file directly in namespace folder (ignored by the game)")
            else:
                self.err(where, f"unknown folder '{first}/' for 26.3 (files here are ignored). "
                         f"See generated/reports/datapack.json for valid registry folders")
            return
        ext = {"function": ".mcfunction", "structure": ".nbt"}.get(folder, ".json")
        if not fn_ok(full, ext):
            self.warn(where, f"files in {folder}/ must end with {ext} (ignored)")
            return
        if not self.check_path_chars(where, ns, rid):
            return
        rid = f"{ns}:{rid}"
        self.pack.elements.setdefault(folder, {})[rid] = full
        if folder == "function":
            self.pack.files.append((full, "function", folder, rid))
        elif ext == ".json":
            self.pack.files.append((full, "json", folder, rid))

    def check_path_chars(self, where, ns, rid):
        if not RL_PATH.match(rid):
            bad = sorted(set(c for c in rid if not re.match(r"[a-z0-9_.\-/]", c)))
            self.err(where, f"invalid character(s) {bad} in resource path '{rid}' (lowercase a-z 0-9 _ - . / only; "
                     "the file is ignored by the game)")
            return False
        return True

    # ---------------- JSON
    def lint_json(self, path, folder, rid):
        where = self.rel(path)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            obj = json.loads(text)
        except UnicodeDecodeError:
            self.err(where, "not UTF-8")
            return
        except ValueError as e:
            self.err(where, f"invalid JSON: {e} (comments and trailing commas are not allowed)")
            return
        loot_like = folder in ("loot_table", "predicate", "item_modifier", "advancement", "enchantment")
        known = self.ref.vanilla_keys.get(folder)
        if loot_like:   # predicates/modifiers share the loot vocabulary; vanilla has few predicate files
            known = set().union(*(self.ref.vanilla_keys.get(f, set()) for f in
                                  ("loot_table", "predicate", "item_modifier", "advancement", "enchantment")))
        if folder == "predicate" and isinstance(obj, list):
            self.err(where, 'a predicate file must be one JSON object; combine several with '
                     '{"type": "minecraft:all_of", "terms": [...]} (server: "Not a JSON object")')
        if folder == "item_modifier" and isinstance(obj, list):
            self.err(where, 'an item modifier file must be one JSON object; chain several with '
                     '{"type": "minecraft:sequence", "functions": [...]} or similar (server: "Not a JSON object")')
        unknown = set()
        self.walk_json(obj, where, folder, loot_like, known, unknown, [])
        if unknown:
            self.warn(where, f"key(s) never used in vanilla 26.3 {folder} files (typo or renamed field?): "
                      + ", ".join(sorted(unknown)))
        self.check_json_type(obj, where, folder)

    FREE_KEYS = ("custom_data", "nbt", "data", "criteria", "components", "storage", "translate_with", "with",
                 "requirements", "entries_by_name")

    def walk_json(self, obj, where, folder, loot_like, known, unknown, keypath):
        if isinstance(obj, dict):
            for k, v in obj.items():
                parent = keypath[-1] if keypath else None
                free = parent in self.FREE_KEYS or (len(keypath) >= 2 and keypath[-2] == "criteria" and False)
                is_seq = loot_like and norm_id(str(obj.get("type", ""))) == "minecraft:sequence"
                if is_seq and k == "type" and "functions" not in obj:
                    self.err(where, '"minecraft:sequence" needs a "functions" list (it was NOT renamed to "modifier"; '
                             'server: "No key functions")')
                if loot_like and k in LOOT_OLD_KEYS and not (folder == "advancement" and k == "conditions"):
                    if not (k == "function" and parent == "rewards") and not (k == "functions" and is_seq):
                        self.err(where, f"key '{k}' was renamed to '{LOOT_OLD_KEYS[k]}' (26.3; vanilla loot tables, "
                                 "predicates and item modifiers no longer use it)")
                if k in TEXT_OLD_KEYS:
                    self.err(where, f"text component key '{k}' was renamed to '{TEXT_OLD_KEYS[k]}' (1.21.5)")
                if loot_like and k in ("condition", "function") and isinstance(v, str) \
                        and norm_id(v) in self.ref.static.get("loot_condition_type", set()) | self.ref.static.get("loot_function_type", set()) \
                        and not self.element_exists("predicate", v):
                    self.err(where, f'"{k}": "{v}" is the old form; use an object with "type": "{v}" (26.3)')
                if known is not None and not free and k not in known and not k.startswith("minecraft:") \
                        and parent not in ("criteria",) and not (keypath and keypath[-1] in ("components",)):
                    close = difflib.get_close_matches(k, known, n=1, cutoff=0.8)
                    if close:
                        self.err(where, f"unknown key '{k}' - did you mean '{close[0]}'? (the server rejects "
                                 "unknown/missing required fields in most data files)")
                    else:
                        unknown.add(k)
                if k in ("icon", "result") and isinstance(v, dict) and "item" in v and "id" not in v:
                    self.err(where, f'"{k}" item stacks use "id", not "item" (1.20.5+)')
                if folder == "recipe" and k in ("ingredients", "key", "ingredient", "base", "addition", "template") \
                        and re.search(r'\{\s*"(item|tag)"\s*:', json.dumps(v)):
                    self.err(where, 'recipe ingredients are plain strings ("minecraft:x" or "#minecraft:tag") or '
                             f'lists of them since 1.21.2, not {{"item": ...}}/{{"tag": ...}} objects ("{k}")')
                if k == "type" and isinstance(v, str) and v.startswith("minecraft:") and v not in self.ref.type_values \
                        and not any(v in s for s in self.ref.static.values()):
                    self.warn(where, f'unknown "type": "{v}" (not used in vanilla 26.3 data nor in any registry)')
                if k == "function" and folder == "advancement" and "rewards" in keypath and isinstance(v, str):
                    self.check_ref(where, "function", v, allow_tag=False)
                if k == "components" and isinstance(v, dict):
                    comps = self.ref.static.get("data_component_type", set())
                    for ck in v:
                        name = norm_id(ck.lstrip("!"))
                        if name not in comps:
                            self.err(where, f"unknown data component '{ck}'")
                self.walk_json(v, where, folder, loot_like, known, unknown, keypath + [k])
        elif isinstance(obj, list):
            for x in obj:
                self.walk_json(x, where, folder, loot_like, known, unknown, keypath)

    def check_json_type(self, obj, where, folder):
        if folder == "loot_table":
            for pool in obj.get("pools", []) if isinstance(obj, dict) else []:
                for e in pool.get("entries", []):
                    self.check_loot_entry(e, where)
        elif folder == "recipe":
            t = obj.get("type") if isinstance(obj, dict) else None
            if not t:
                self.err(where, 'recipe needs "type"')
            elif norm_id(t) not in self.ref.static.get("recipe_serializer", set()):
                self.err(where, f"unknown recipe type '{t}'")
            res = obj.get("result") if isinstance(obj, dict) else None
            if isinstance(res, dict) and "id" in res:
                self.check_ref(where, "item", res["id"], allow_tag=False)
            elif isinstance(res, dict) and "item" in res:
                self.err(where, 'recipe "result" uses "id", not "item" (1.20.5+)')
        elif folder == "advancement":
            if not isinstance(obj, dict) or "criteria" not in obj:
                self.err(where, 'advancement needs "criteria"')
            else:
                for name, c in obj["criteria"].items():
                    t = c.get("trigger") if isinstance(c, dict) else None
                    if not t:
                        self.err(where, f"criterion '{name}' has no trigger")
                    elif norm_id(t) not in self.ref.static.get("trigger_type", set()):
                        self.err(where, f"unknown advancement trigger '{t}'")
            if isinstance(obj, dict) and isinstance(obj.get("parent"), str):
                self.check_ref(where, "advancement", obj["parent"], allow_tag=False)
            elif isinstance(obj, dict) and isinstance(obj.get("display"), dict) and "background" not in obj["display"]:
                self.err(where, 'an advancement with "display" but no "parent" is a tab root and needs '
                         '"display.background" (server: "Visible advancement roots must have background")')

    def check_loot_entry(self, e, where):
        if not isinstance(e, dict):
            return
        t = norm_id(e.get("type", ""))
        if t == "minecraft:item" and isinstance(e.get("name"), str):
            self.check_ref(where, "item", e["name"], allow_tag=False)
        elif t == "minecraft:tag" and isinstance(e.get("name"), str):
            self.check_ref(where, "item", "#" + e["name"].lstrip("#"))
        elif t == "minecraft:loot_table" and isinstance(e.get("value"), str):
            self.check_ref(where, "loot_table", e["value"], allow_tag=False)
        for c in e.get("children", []):
            self.check_loot_entry(c, where)

    def lint_tag(self, path, folder, rid):
        where = self.rel(path)
        try:
            obj = load_json(path)
        except (ValueError, UnicodeDecodeError) as e:
            self.err(where, f"invalid JSON: {e}")
            return
        if not isinstance(obj, dict) or not isinstance(obj.get("values"), list):
            self.err(where, 'tag needs "values": [...]')
            return
        for k in obj:
            if k not in ("values", "replace"):
                self.warn(where, f"unknown tag key '{k}'")
        for v in obj["values"]:
            required = True
            if isinstance(v, dict):
                required = v.get("required", True)
                v = v.get("id")
            if not isinstance(v, str):
                self.err(where, f"tag value must be a string or {{\"id\":..., \"required\":...}}: {v!r}")
                continue
            if not required:
                continue
            self.check_ref(where, folder, v)

    # ---------------- functions
    def lint_function(self, path, rid):
        where = self.rel(path)
        try:
            with open(path, encoding="utf-8") as f:
                raw_lines = f.read().split("\n")
        except UnicodeDecodeError:
            self.err(where, "not UTF-8")
            return
        lines = []
        i = 0
        while i < len(raw_lines):
            start = i
            line = raw_lines[i].rstrip("\r").strip()
            # verified: a trailing backslash joins the next line (leading whitespace of the next line dropped)
            while line.endswith("\\") and not line.startswith("#") and i + 1 < len(raw_lines):
                i += 1
                line = line[:-1] + raw_lines[i].rstrip("\r").strip()
            lines.append((start + 1, line))
            i += 1
        for lineno, line in lines:
            if not line or line.startswith("#"):
                continue
            loc = f"{where}:{lineno}"
            if line.startswith("/"):
                self.err(loc, "commands in functions must not start with '/'")
                continue
            if line.startswith("$"):
                self.pack.macro_functions.add(rid)
                body = line[1:]
                names = re.findall(r"\$\(([^)]*)\)", body)
                if not names:
                    self.err(loc, "macro line ('$') without any $(name) substitution")
                    continue
                if any(not re.fullmatch(r"[A-Za-z0-9_]+", n) for n in names) or re.search(r"\$\((?![A-Za-z0-9_]+\))", body):
                    self.err(loc, "bad macro substitution: use $(name) with name of letters, digits, _ ")
                    continue
                self.pack.macro_args.setdefault(rid, set()).update(names)
                line = re.sub(r"\$\([A-Za-z0-9_]+\)", MACRO, body)
            elif re.search(r"\$\([A-Za-z0-9_]+\)", line):
                self.warn(loc, "contains $(name) but the line does not start with '$', so it is NOT substituted")
            self.record_calls(loc, line)
            CommandParser(self, loc).parse_command(line)

    CALL = re.compile(r"(?:^|\brun |\bif |\bunless |\bschedule )function ([a-z0-9_.\-]+:[a-z0-9_.\-/]+)(?: (.*))?$")

    def record_calls(self, loc, line):
        m = self.CALL.search(line)
        if not m:
            return
        rest = (m.group(2) or "").strip()
        before = line[:m.start()] + line[m.start():m.start(1)]
        if re.search(r"\b(if|unless|schedule) function $", before):
            rest = ""  # these forms cannot pass macro arguments
        if rest.startswith("with "):
            rest = "with"
        elif not rest.startswith("{"):
            rest = None
        self.pack.calls.append((loc, norm_id(m.group(1)), rest))

    @staticmethod
    def compound_keys(text):
        """Top-level keys of an SNBT compound literal, or None if it cannot be read statically."""
        if MACRO in text:
            text = text.replace(MACRO, "0")
        keys, depth, i, quote, expect_key = set(), 0, 0, None, False
        while i < len(text):
            c = text[i]
            if quote:
                if c == "\\":
                    i += 1
                elif c == quote:
                    quote = None
            elif c in "\"'":
                if depth == 1 and expect_key:
                    j = text.find(c, i + 1)
                    keys.add(text[i + 1:j])
                    expect_key = False
                    i = j
                else:
                    quote = c
            elif c in "{[":
                depth += 1
                expect_key = depth == 1 and c == "{"
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    return keys
            elif c == "," and depth == 1:
                expect_key = True
            elif depth == 1 and expect_key and not c.isspace():
                m = re.match(r"[A-Za-z0-9_\-.+]+", text[i:])
                if not m:
                    return None
                keys.add(m.group(0))
                expect_key = False
                i += len(m.group(0)) - 1
            i += 1
        return None

    def post_checks(self):
        # Macro functions fail at runtime with "Missing argument" (silently when nested): check calls statically.
        for loc, fid, args in self.pack.calls:
            need = self.pack.macro_args.get(fid)
            if not need:
                funcs = self.pack.elements.get("function", {})
                if fid.startswith("mcdp_lib:") and fid not in funcs:
                    if any(f.startswith("mcdp_lib:") for f in funcs):
                        self.err(loc, f"no library function '{fid}': look up the name in library/INDEX.md")
                    else:
                        self.err(loc, f"'{fid}' needs the library: vendor it with python tools/new_project.py "
                                      "--update <pack>")
                continue
            if args is None or args == "":
                self.err(loc, f"'{fid}' is a macro function needing {{{', '.join(sorted(need))}}} but is called "
                              "without arguments (runtime: 'Missing argument', nothing runs)")
            elif args != "with":
                keys = self.compound_keys(args)
                if keys is not None and need - keys:
                    self.err(loc, f"call to '{fid}' is missing macro argument(s) {', '.join(sorted(need - keys))} "
                                  "(runtime: 'Missing argument', nothing runs)")
        self.check_vendored_library()

    def check_vendored_library(self):
        lib_load = os.path.join("data", "mcdp_lib", "function", "_internal", "load.mcfunction")
        mine, ref = os.path.join(self.pack.root, lib_load), os.path.join(ROOT, "library", "mcdp_lib", lib_load)
        if os.path.abspath(mine) == os.path.abspath(ref) or not (os.path.isfile(mine) and os.path.isfile(ref)):
            return
        ver = lambda p: (re.search(r'mcdp_lib:meta version set value "([^"]+)"', open(p, encoding="utf-8").read())
                         or [None, "?"])[1]
        if ver(mine) != ver(ref):
            self.warn("data/mcdp_lib", f"vendored mcdp_lib {ver(mine)} differs from library/ {ver(ref)}; "
                                       "re-vendor with python tools/new_project.py --update <pack>")


def component_old_shape(name, value):
    """Detect pre-1.21.5 (unflattened) component values. Verified against the 26.3 server."""
    v = re.sub(r"\s", "", value)
    if name in ("minecraft:enchantments", "minecraft:stored_enchantments") and re.match(r"\{\"?levels\"?:", v):
        return f"'{name}' is a plain map of enchantment -> level since 1.21.5 (no 'levels' wrapper)"
    if name == "minecraft:attribute_modifiers" and re.match(r"\{\"?modifiers\"?:", v):
        return "'attribute_modifiers' is a plain list since 1.21.5 (no 'modifiers' wrapper)"
    if re.search(r"show_in_tooltip", v):
        return "'show_in_tooltip' was removed in 1.21.5; use the tooltip_display component"
    return None


def fn_ok(path, ext):
    return path.endswith(ext)


def fmt(v):
    return f"{v[0]}.{v[1]}" if v[1] < 2 ** 31 else f"{v[0]}.*"


# --------------------------------------------------------------------------- command parsing
class ParseError(Exception):
    def __init__(self, pos, msg):
        super().__init__(msg)
        self.pos = pos
        self.msg = msg


class MacroStop(Exception):
    """Macro placeholder reached in a position we cannot statically resolve: accept rest of line."""


class CommandParser:
    def __init__(self, linter, loc):
        self.lt = linter
        self.ref = linter.ref
        self.loc = loc
        self.root = self.ref.commands
        self.s = ""

    def node_at(self, path):
        n = self.root
        for p in path:
            n = n["children"][p]
        return n

    def parse_command(self, line):
        self.s = line
        try:
            self.parse_from(self.root, 0, top=True)
        except MacroStop:
            pass
        except ParseError as e:
            ctx = self.s[max(0, e.pos - 25):e.pos].replace(MACRO, "$(..)")
            self.lt.err(self.loc, f"{e.msg} at col {e.pos + 1}: ...{ctx}<--[HERE]")

    def parse_from(self, node, pos, top=False):
        """Parse children of node starting at pos (pos at start of a word)."""
        s = self.s
        children = node.get("children", {})
        end = s.find(" ", pos)
        word = s[pos:] if end < 0 else s[pos:end]
        if MACRO in word and not word.startswith(MACRO + "{"):
            # cannot know which literal/argument a macro fills; accept the rest
            raise MacroStop()
        if top:
            if word not in children:
                raise ParseError(pos, f"unknown command '{word}'")
            perm = children[word].get("permissions", {}).get("permission", {}).get("level")
            if perm and PERM_LEVELS.get(perm, 0) > FUNCTION_PERMISSION_LEVEL:
                raise ParseError(pos, f"'/{word}' needs permission level '{perm}' and is not available in functions "
                                      f"(function-permission-level={FUNCTION_PERMISSION_LEVEL})")
        lits = {k: v for k, v in children.items() if v["type"] == "literal"}
        if word in lits:
            return self.after_node(lits[word], [word], pos + len(word))
        args = [(k, v) for k, v in children.items() if v["type"] == "argument"]
        if not args:
            raise ParseError(pos, f"expected one of: {', '.join(sorted(lits))}" if lits else "unexpected argument")
        best = None
        for name, child in args:
            try:
                newpos = self.parse_arg(child, pos)
            except ParseError as e:
                if best is None or e.pos > best.pos:
                    best = e
                continue
            try:
                return self.after_node(child, None, newpos)
            except ParseError as e:
                if best is None or e.pos > best.pos:
                    best = e
        if lits and best is not None and best.pos == pos:
            raise ParseError(pos, f"expected one of: {', '.join(sorted(lits))} or <{args[0][0]}>")
        raise best

    def after_node(self, node, _, pos):
        s = self.s
        if pos >= len(s):
            if node.get("executable"):
                return pos
            raise ParseError(pos, "incomplete command")
        if s[pos] != " ":
            raise ParseError(pos, "expected whitespace to end one argument, but found trailing data")
        pos += 1
        if pos >= len(s):
            raise ParseError(pos, "trailing space at end of command")
        if "redirect" in node:
            return self.parse_from(self.node_at(node["redirect"]), pos)
        if not node.get("children"):
            if node.get("executable"):
                raise ParseError(pos, "expected end of command (too many arguments)")
            return self.parse_from(self.root, pos, top=True)   # e.g. 'execute ... run <command>'
        return self.parse_from(node, pos)

    # ---------------- readers
    def read_until_space(self, pos):
        end = self.s.find(" ", pos)
        return self.s[pos:] if end < 0 else self.s[pos:end]

    def read_balanced(self, pos, stop=" "):
        """Read an SNBT/JSON-ish value; returns end position. Brackets/quotes balanced."""
        s = self.s
        i = pos
        depth = 0
        while i < len(s):
            c = s[i]
            if c in "\"'":
                j = i + 1
                while j < len(s) and s[j] != c:
                    j += 2 if s[j] == "\\" else 1
                if j >= len(s):
                    raise ParseError(i, "unclosed quoted string")
                i = j + 1
                continue
            if c in "{[(":
                depth += 1
            elif c in "}])":
                depth -= 1
                if depth < 0:
                    if stop != " ":
                        return i
                    raise ParseError(i, f"unbalanced '{c}'")
            elif depth == 0 and c in stop:
                break
            i += 1
        if depth > 0:
            raise ParseError(pos, "unclosed bracket")
        if i == pos:
            raise ParseError(pos, "expected a value")
        return i

    def read_bracket(self, pos):
        """pos at an opening bracket; return index after its matching close (quotes respected)."""
        s = self.s
        depth = 0
        i = pos
        while i < len(s):
            c = s[i]
            if c in "\"'":
                j = i + 1
                while j < len(s) and s[j] != c:
                    j += 2 if s[j] == "\\" else 1
                i = j + 1
                continue
            if c in "{[(":
                depth += 1
            elif c in "}])":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        raise ParseError(pos, "unclosed bracket")

    def read_rl(self, pos, allow_tag=False):
        m = re.compile(r"#?[A-Za-z0-9_.\-:/\u0001]+").match(self.s, pos)
        if not m:
            raise ParseError(pos, "expected a resource location")
        v = m.group(0)
        if v.startswith("#") and not allow_tag:
            raise ParseError(pos, "tag not allowed here")
        raw = v.lstrip("#")
        if MACRO not in raw and not valid_rl(raw):
            raise ParseError(pos, f"invalid resource location '{v}' (lowercase a-z 0-9 _ - . / only)")
        return v, m.end()

    def check(self, pos, folder, v, allow_tag=True, kind=None):
        if MACRO in v:
            return
        before = len(self.lt.errors)
        self.lt.check_ref(self.loc, folder, v, allow_tag=allow_tag, kind=kind)
        if len(self.lt.errors) > before:
            msg = self.lt.errors.pop()
            raise ParseError(pos, msg.split(": ", 1)[1])

    # ---------------- argument parsers
    def parse_arg(self, node, pos):
        p = node["parser"]
        props = node.get("properties", {})
        s = self.s
        tok = self.read_until_space(pos)
        if tok.startswith(MACRO) and p not in ("brigadier:string",):
            # whole-argument macro: skip this token (balanced if it starts a compound)
            return pos + len(tok) if not tok.startswith(MACRO + "{") else self.read_balanced(pos)
        if p == "brigadier:bool":
            if tok not in ("true", "false"):
                raise ParseError(pos, f"expected true or false, got '{tok}'")
            return pos + len(tok)
        if p in ("brigadier:integer", "brigadier:float", "brigadier:double"):
            pat = r"[+-]?\d+" if p == "brigadier:integer" else NUM.pattern
            m = re.compile(pat).match(s, pos)
            if not m:
                raise ParseError(pos, f"expected {'integer' if p.endswith('integer') else 'number'}, got '{tok}'")
            v = float(m.group(0))
            if "min" in props and v < props["min"] or "max" in props and v > props["max"]:
                raise ParseError(pos, f"{m.group(0)} out of range [{props.get('min')}, {props.get('max')}]")
            return m.end()
        if p == "brigadier:string":
            t = props.get("type")
            if t == "greedy":
                return len(s)
            if t == "phrase" and s[pos:pos + 1] in "\"'":
                return self.read_balanced(pos)
            m = WORD.match(s, pos)
            if not m and MACRO not in tok:
                raise ParseError(pos, "expected a word")
            return pos + len(tok) if MACRO in tok else m.end()
        if p in ("minecraft:block_pos", "minecraft:vec3", "minecraft:vec2", "minecraft:column_pos", "minecraft:rotation"):
            n = 2 if p in ("minecraft:vec2", "minecraft:column_pos", "minecraft:rotation") else 3
            return self.read_coords(pos, n, integer=p in ("minecraft:block_pos", "minecraft:column_pos"),
                                    local_ok=p not in ("minecraft:rotation", "minecraft:column_pos"))
        if p == "minecraft:entity":
            return self.read_entity(pos, props)
        if p == "minecraft:game_profile":
            return self.read_entity(pos, {"type": "players"}, profile=True)
        if p == "minecraft:score_holder":
            if tok == "*" or not tok.startswith("@"):
                if not tok:
                    raise ParseError(pos, "expected a score holder")
                return pos + len(tok)
            return self.read_entity(pos, {"type": "entities", "amount": props.get("amount", "multiple")})
        if p in ("minecraft:objective", "minecraft:team"):
            m = WORD.match(s, pos)
            if not m:
                raise ParseError(pos, "expected a name (characters 0-9 A-Z a-z _ - . +)")
            return m.end()
        if p == "minecraft:objective_criteria":
            if MACRO not in tok:
                self.check_criteria(pos, tok)
            return pos + len(tok)
        if p in ("minecraft:resource", "minecraft:resource_key", "minecraft:resource_or_tag",
                 "minecraft:resource_or_tag_key", "minecraft:resource_selector"):
            reg = props["registry"].split(":", 1)[1]
            allow_tag = p.startswith("minecraft:resource_or_tag")
            if p == "minecraft:resource_selector":
                return pos + len(tok)
            v, end = self.read_rl(pos, allow_tag)
            self.check(pos, reg, v, allow_tag)
            return end
        if p == "minecraft:function":
            v, end = self.read_rl(pos, allow_tag=True)
            self.check(pos, "function", v, kind="function")
            return end
        if p in ("minecraft:loot_table", "minecraft:loot_predicate", "minecraft:loot_modifier", "minecraft:dialog"):
            if s[pos:pos + 1] in "{[":
                return self.read_balanced(pos)
            folder = {"minecraft:loot_table": "loot_table", "minecraft:loot_predicate": "predicate",
                      "minecraft:loot_modifier": "item_modifier", "minecraft:dialog": "dialog"}[p]
            v, end = self.read_rl(pos)
            self.check(pos, folder, v, allow_tag=False)
            return end
        if p in ("minecraft:resource_location", "minecraft:dimension", "minecraft:feature"):
            v, end = self.read_rl(pos)
            if p == "minecraft:dimension":
                if norm_id(v) not in ("minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"):
                    self.check(pos, "dimension", v, allow_tag=False)
            return end
        if p == "minecraft:item_stack":
            return self.read_item(pos, predicate=False)
        if p == "minecraft:item_predicate":
            return self.read_item(pos, predicate=True)
        if p in ("minecraft:block_state", "minecraft:block_predicate"):
            return self.read_block(pos, predicate=p == "minecraft:block_predicate")
        if p == "minecraft:particle":
            v, end = self.read_rl(pos)
            if norm_id(v) not in self.ref.static["particle_type"] and MACRO not in v:
                raise ParseError(pos, f"unknown particle '{v}'")
            if end < len(s) and s[end] == "{":
                end = self.read_bracket(end)
            return end
        if p in ("minecraft:nbt_compound_tag", "minecraft:style"):
            if not s.startswith("{", pos):
                raise ParseError(pos, "expected compound '{...}'")
            return self.read_balanced(pos)
        if p in ("minecraft:nbt_tag", "minecraft:component", "minecraft:nbt_path", "minecraft:slot_source",
                 "minecraft:context_float_provider", "minecraft:context_int_provider"):
            end = self.read_balanced(pos)
            if p == "minecraft:component":
                self.check_text(pos, s[pos:end])
            elif p == "minecraft:nbt_path":
                # verified 26.3: `list[-1]{c:1b}` fails at load ("Invalid NBT path element"); use list[-1].c
                m = re.search(r"\[-?\d+\]\{", s[pos:end])
                if m:
                    raise ParseError(pos + m.start() + 1, "invalid NBT path: an index [n] cannot be followed by a "
                                     "{compound} filter; test a field instead (list[-1].key)")
            return end
        if p == "minecraft:message":
            return len(s)
        if p == "minecraft:time":
            m = re.compile(NUM.pattern + r"[dst]?").match(s, pos)
            if not m or m.end() != pos + len(tok):
                raise ParseError(pos, f"invalid time '{tok}' (number with optional d/s/t)")
            return m.end()
        if p in ("minecraft:int_range", "minecraft:float_range"):
            if not re.fullmatch(r"(-?[\d.]+)?(\.\.)?(-?[\d.]+)?", tok) or tok in ("", ".."):
                raise ParseError(pos, f"invalid range '{tok}'")
            return pos + len(tok)
        if p == "minecraft:uuid":
            if not re.fullmatch(r"[0-9a-fA-F]{1,8}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,12}", tok):
                raise ParseError(pos, "invalid UUID")
            return pos + len(tok)
        if p == "minecraft:swizzle":
            if not re.fullmatch(r"[xyz]{1,3}", tok) or len(set(tok)) != len(tok):
                raise ParseError(pos, "expected combination of x, y, z")
            return pos + len(tok)
        if p == "minecraft:entity_anchor":
            if tok not in ("eyes", "feet"):
                raise ParseError(pos, "expected eyes or feet")
            return pos + len(tok)
        if p == "minecraft:gamemode":
            if tok not in ("survival", "creative", "adventure", "spectator"):
                raise ParseError(pos, f"unknown gamemode '{tok}'")
            return pos + len(tok)
        if p == "minecraft:operation":
            if tok not in ("=", "+=", "-=", "*=", "/=", "%=", "<", ">", "><"):
                raise ParseError(pos, f"invalid operation '{tok}'")
            return pos + len(tok)
        if p == "minecraft:hex_color":
            if not re.fullmatch(r"[0-9a-fA-F]{6}", tok):
                raise ParseError(pos, "expected 6 hex digits")
            return pos + len(tok)
        if p == "minecraft:team_color":
            colors = {"black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray",
                      "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white", "reset"}
            if tok not in colors:
                raise ParseError(pos, f"unknown color '{tok}'")
            return pos + len(tok)
        if p == "minecraft:swing_animation":
            if tok not in ("whack", "stab", "none"):
                raise ParseError(pos, f"unknown swing animation '{tok}' (whack, stab, none)")
            return pos + len(tok)
        # word-like enums: heightmap, item_slot, scoreboard_slot, template_*, swing_animation
        if not tok:
            raise ParseError(pos, f"expected <{p}>")
        return pos + len(tok)

    STAT_REGISTRY = {"mined": "block", "crafted": "item", "used": "item", "broken": "item", "picked_up": "item",
                     "dropped": "item", "killed": "entity_type", "killed_by": "entity_type", "custom": "custom_stat"}
    SIMPLE_CRITERIA = {"dummy", "trigger", "deathCount", "playerKillCount", "totalKillCount", "health", "xp",
                       "level", "food", "air", "armor"}
    COLORS = {"black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray",
              "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"}

    def check_criteria(self, pos, tok):
        if tok in self.SIMPLE_CRITERIA:
            return
        m = re.fullmatch(r"(teamkill|killedByTeam)\.([a-z_]+)", tok)
        if m and m.group(2) in self.COLORS:
            return
        m = re.fullmatch(r"(?:([a-z0-9_]+)\.)?([a-z_]+):(?:([a-z0-9_]+)\.)?([a-z0-9_./]+)", tok)
        if m:
            stat = m.group(2)
            if (m.group(1) or "minecraft") == "minecraft" and stat in self.STAT_REGISTRY:
                rid = (m.group(3) or "minecraft") + ":" + m.group(4)
                if rid in self.ref.static.get(self.STAT_REGISTRY[stat], set()):
                    return
                raise ParseError(pos, f"unknown {self.STAT_REGISTRY[stat]} '{rid}' in criterion '{tok}'")
        raise ParseError(pos, f"unknown criterion '{tok}' (dummy, trigger, deathCount, health, ..., or "
                              "minecraft.<stat>:minecraft.<id> e.g. minecraft.mined:minecraft.stone)")

    def check_text(self, pos, text):
        for old, new in TEXT_OLD_KEYS.items():
            if re.search(r"[{,]\s*\"?" + old + r"\"?\s*:", text):
                raise ParseError(pos, f"text component key '{old}' was renamed to '{new}' (1.21.5)")

    def read_coords(self, pos, n, integer, local_ok):
        s = self.s
        kinds = []
        for k in range(n):
            if k:
                if pos >= len(s) or s[pos] != " ":
                    raise ParseError(pos, f"expected {n} coordinates")
                pos += 1
            tok = self.read_until_space(pos)
            if MACRO in tok:
                kinds.append("m")
                pos += len(tok)
                continue
            m = re.fullmatch(r"([~^]?)(" + NUM.pattern + r")?", tok)
            if not tok or not m or (not m.group(1) and not m.group(2)):
                raise ParseError(pos, f"invalid coordinate '{tok}'")
            if m.group(1) == "^" and not local_ok:
                raise ParseError(pos, "local coordinates (^) not allowed here")
            if integer and not m.group(1) and not re.fullmatch(r"[+-]?\d+", tok):
                raise ParseError(pos, f"block position needs whole numbers, got '{tok}'")
            kinds.append("^" if m.group(1) == "^" else "w")
            pos += len(tok)
        if "^" in kinds and "w" in kinds:
            raise ParseError(pos, "cannot mix local (^) and world coordinates")
        return pos

    def read_entity(self, pos, props, profile=False):
        s = self.s
        players_only = props.get("type") == "players"
        single = props.get("amount") == "single"
        if s.startswith("@", pos):
            m = re.compile(r"@([aenprs])").match(s, pos)
            if not m:
                raise ParseError(pos, "unknown selector type (use @a @e @n @p @r @s)")
            kind = m.group(1)
            end = m.end()
            args = {}
            if end < len(s) and s[end] == "[":
                close = self.read_bracket(end)
                body = s[end + 1:close - 1]
                self.check_selector_args(end + 1, body, args)
                end = close
            if single and kind in "ae" and args.get("limit") != "1":
                raise ParseError(pos, "only one entity is allowed, but the selector allows more (add limit=1 or use @n/@p/@s)")
            if players_only and kind in "en" and args.get("type", "").lstrip("!") != "minecraft:player" \
                    and args.get("type") != "player":
                raise ParseError(pos, "only players may be affected here, but the selector includes entities")
            return end
        tok = self.read_until_space(pos)
        if re.fullmatch(r"[0-9a-fA-F]{1,8}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,4}-[0-9a-fA-F]{1,12}", tok):
            return pos + len(tok)
        if not re.fullmatch(r"[A-Za-z0-9_\-.+\u0001]{1,40}", tok or "!"):
            raise ParseError(pos, f"invalid player name or selector '{tok}'")
        return pos + len(tok)

    def check_selector_args(self, pos, body, args):
        i = 0
        while i < len(body):
            m = re.compile(r"\s*([A-Za-z_]+)\s*=\s*").match(body, i)
            if not m:
                raise ParseError(pos + i, "expected selector argument key=value")
            key = m.group(1)
            if key not in SELECTOR_KEYS:
                raise ParseError(pos + i, f"unknown selector option '{key}'")
            j = m.end()
            # value: balanced up to ',' at depth 0
            depth = 0
            k = j
            while k < len(body):
                c = body[k]
                if c in "\"'":
                    q = body.find(c, k + 1)
                    k = q + 1 if q > 0 else len(body)
                    continue
                if c in "{[":
                    depth += 1
                elif c in "}]":
                    depth -= 1
                elif c == "," and depth == 0:
                    break
                k += 1
            val = body[j:k].strip()
            args[key] = val
            if key == "type" and MACRO not in val:
                t = val.lstrip("!")
                self.check(pos + j, "entity_type", t)
                if norm_id(t) == "minecraft:player":
                    args["type"] = "minecraft:player" if not val.startswith("!") else val
            if key == "predicate" and MACRO not in val:
                self.check(pos + j, "predicate", val.lstrip("!"), allow_tag=False)
            if key == "sort" and val not in ("nearest", "furthest", "random", "arbitrary"):
                raise ParseError(pos + j, f"invalid sort '{val}'")
            if key == "gamemode" and val.lstrip("!") not in ("survival", "creative", "adventure", "spectator"):
                raise ParseError(pos + j, f"invalid gamemode '{val}'")
            i = k + 1

    def read_item(self, pos, predicate):
        s = self.s
        if predicate and s.startswith("*", pos):
            end = pos + 1
        else:
            v, end = self.read_rl(pos, allow_tag=predicate)
            if MACRO not in v:
                if v.startswith("#"):
                    self.check(pos, "item", v)
                elif norm_id(v) not in self.ref.static["item"]:
                    raise ParseError(pos, f"unknown item '{v}'")
        if end < len(s) and s[end] == "[":
            close = self.read_bracket(end)
            self.check_components(end + 1, s[end + 1:close - 1], predicate)
            end = close
        if end < len(s) and s[end] == "{":
            raise ParseError(end, "item NBT '{...}' after the item id is the pre-1.20.5 form; use components "
                                  "id[component=value], e.g. custom_data={...}")
        return end

    def check_components(self, pos, body, predicate):
        comps = self.ref.static.get("data_component_type", set())
        preds = self.ref.static.get("data_component_predicate_type", set())
        # split top-level entries by ',' (and '|' for predicates)
        depth, start, parts = 0, 0, []
        i = 0
        while i < len(body):
            c = body[i]
            if c in "\"'":
                q = i + 1
                while q < len(body) and body[q] != c:
                    q += 2 if body[q] == "\\" else 1
                i = q + 1
                continue
            if c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
            elif depth == 0 and (c == "," or (predicate and c == "|")):
                parts.append((start, body[start:i]))
                start = i + 1
            i += 1
        parts.append((start, body[start:]))
        for off, part in parts:
            part_s = part.strip()
            if not part_s or MACRO in part_s.split("=")[0].split("~")[0]:
                continue
            m = re.match(r"!?\s*([a-z0-9_.\-:/]+)\s*(=|~)?", part_s)
            if not m:
                raise ParseError(pos + off, f"invalid component entry '{part_s[:30]}'")
            name = norm_id(m.group(1))
            op = m.group(2)
            if predicate:
                if op == "~":
                    if name not in preds:
                        raise ParseError(pos + off, f"unknown item sub-predicate '{m.group(1)}'")
                elif name not in comps and name not in ("minecraft:count",):
                    raise ParseError(pos + off, f"unknown data component '{m.group(1)}'")
            else:
                if name not in comps:
                    raise ParseError(pos + off, f"unknown data component '{m.group(1)}' (see knowledge/item-components.md)")
                if not op and not part_s.startswith("!"):
                    raise ParseError(pos + off, f"component '{m.group(1)}' needs '=value'")
                value = part_s[m.end():].lstrip()
                old = component_old_shape(name, value)
                if old:
                    raise ParseError(pos + off, old)

    def read_block(self, pos, predicate):
        s = self.s
        v, end = self.read_rl(pos, allow_tag=predicate)
        block = None
        if MACRO not in v:
            if v.startswith("#"):
                self.check(pos, "block", v)
            else:
                block = self.ref.blocks.get(norm_id(v))
                if block is None:
                    raise ParseError(pos, f"unknown block '{v}'")
        if end < len(s) and s[end] == "[":
            close = self.read_bracket(end)
            body = s[end + 1:close - 1]
            if block is not None and MACRO not in body:
                props = block.get("properties", {})
                for kv in filter(None, (x.strip() for x in body.split(","))):
                    k, _, val = kv.partition("=")
                    k, val = k.strip(), val.strip()
                    if k not in props:
                        raise ParseError(end + 1, f"block {v} has no property '{k}' (has: {', '.join(props) or 'none'})")
                    if val not in props[k]:
                        raise ParseError(end + 1, f"invalid value '{val}' for {v}[{k}] (allowed: {', '.join(props[k])})")
            end = close
        if end < len(s) and s[end] == "{":
            end = self.read_bracket(end)
        return end


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    strict = "--strict" in argv
    lt = Linter(os.path.abspath(args[0]))
    lt.run()
    if "--quiet" not in argv:
        for w in lt.warnings:
            print(w)
    for e in lt.errors:
        print(e)
    n_fn = len(lt.pack.elements.get("function", {}))
    print(f"lint: {len(lt.errors)} error(s), {len(lt.warnings)} warning(s); "
          f"{len(lt.pack.files)} files checked ({n_fn} functions)")
    return 1 if lt.errors or (strict and lt.warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
