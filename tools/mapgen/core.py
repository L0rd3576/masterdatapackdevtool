"""Shared mapgen core: config, palettes, block classes, seeds, and the manifest -> model pipeline."""
import copy
import fnmatch
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import blocks  # noqa: E402
import registry  # noqa: E402
import rng as rngmod  # noqa: E402
import schema  # noqa: E402
import structure_writer  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
CONFIG_PATH = os.path.join(HERE, "config.json")


class MapgenError(Exception):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise MapgenError(f"ERROR: {path}: invalid JSON: {e}")


def load_config(path=None, overrides=None):
    """Load + schema-check config.json; unknown block ids/patterns in it are errors."""
    path = path or CONFIG_PATH
    cfg = load_json(path)
    issues = schema.validate(cfg, "mapgen-config.schema.json", file=path)
    for i in issues:
        if i.level == "WARN":
            print(i, file=sys.stderr)
    errs = schema.errors(issues)
    if errs:
        raise MapgenError("\n".join(map(str, errs)))
    if overrides:
        cfg = deep_merge(cfg, overrides)
    problems = []
    for name, pal in cfg["palettes"].items():
        for role, v in pal.items():
            for st in ([v] if isinstance(v, str) else [e["block"] for e in v]):
                n, p = blocks.parse_state(st)
                problems += [f"palettes.{name}.{role}: {e}" for e in blocks.validate_state(n, p)]
    if cfg["default_palette"] not in cfg["palettes"]:
        problems.append(f"default_palette {cfg['default_palette']!r} is not in palettes")
    for group in ("passable", "not_standable", "hazard"):
        for pat in cfg["blocks"][group]:
            if not any(fnmatch.fnmatchcase(b, pat) for b in blocks.db()):
                problems.append(f"blocks.{group}: pattern {pat!r} matches no 26.3 block")
    if problems:
        raise MapgenError("\n".join(f"ERROR: {path}: {p}" for p in problems))
    return cfg


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


# ------------------------------------------------------------------ palettes
class Palette:
    """Role -> block lookup. Weighted roles pick with the generator's rng."""

    def __init__(self, roles):
        self.roles = roles

    def has(self, role):
        return role in self.roles

    def get(self, role, rng=None, fallback=None):
        v = self.roles.get(role)
        if v is None:
            if fallback is not None:
                return self.get(fallback, rng)
            raise MapgenError(f"palette has no role {role!r} (roles: {', '.join(sorted(self.roles))})")
        if isinstance(v, str):
            return v
        if rng is None:
            return v[0]["block"]
        return rng.weighted([(e["block"], e.get("weight", 1)) for e in v])


def resolve_palette(ref, config):
    base = dict(config["palettes"][config["default_palette"]])
    if ref is None:
        return Palette(base)
    if isinstance(ref, str):
        if ref not in config["palettes"]:
            raise MapgenError(f"unknown palette {ref!r}; config palettes: {', '.join(sorted(config['palettes']))}")
        base.update(config["palettes"][ref])
        return Palette(base)
    base.update(ref)
    for role, v in ref.items():
        for st in ([v] if isinstance(v, str) else [e["block"] for e in v]):
            n, p = blocks.parse_state(st)
            errs = blocks.validate_state(n, p)
            if errs:
                raise MapgenError(f"palette role {role}: {'; '.join(errs)}")
    return Palette(base)


# ------------------------------------------------------------------ block classes
class BlockClasses:
    def __init__(self, config):
        self.cfg = config["blocks"]
        self._cache = {}

    def _match(self, name, group):
        return any(fnmatch.fnmatchcase(name, p) for p in self.cfg[group])

    def classify(self, state):
        """-> (passable, standable_on, hazard) for a full state string or None (untouched = air)."""
        name = "minecraft:air" if state is None else state.split("[", 1)[0]
        c = self._cache.get(name)
        if c is None:
            passable = self._match(name, "passable")
            c = (passable, not passable and not self._match(name, "not_standable"), self._match(name, "hazard"))
            self._cache[name] = c
        return c


class Walk:
    """Walkable-cell graph over a model using config movement values."""

    def __init__(self, model, config):
        self.m = model
        self.bc = BlockClasses(config)
        mv = config["movement"]
        self.headroom, self.jump_up = mv["headroom"], mv["jump_up"]
        self.jump_headroom, self.max_drop = mv["jump_headroom"], mv["max_drop"]
        self.diagonal = mv.get("diagonal", False)

    def free(self, x, y, z):
        """Air-like cell a player can occupy (outside the model above it counts as free; below/sides not)."""
        if not (0 <= x < self.m.size[0] and 0 <= z < self.m.size[2]) or y < 0:
            return False
        if y >= self.m.size[1]:
            return True
        p, _, hz = self.bc.classify(self.m.get(x, y, z))
        return p and not hz

    def standable(self, x, y, z):
        """A player can stand with feet in cell (x, y, z)."""
        if y < 1 or not (0 <= x < self.m.size[0] and 0 <= z < self.m.size[2]):
            return False
        _, on, hz = self.bc.classify(self.m.get(x, y - 1, z))
        if not on or hz:
            return False
        return all(self.free(x, y + h, z) for h in range(self.headroom))

    def neighbours(self, x, y, z):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.diagonal:
            dirs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dz in dirs:
            nx, nz = x + dx, z + dz
            # same level, or step off and fall at most max_drop cells (column must be free on the way down)
            for drop in range(0, self.max_drop + 1):
                ny = y - drop
                if ny < 1:
                    break
                if self.standable(nx, ny, nz) and all(self.free(nx, yy, nz) for yy in range(ny, y + self.headroom)):
                    yield nx, ny, nz
                    break
                if not self.free(nx, ny, nz):
                    break
            # jump up
            for up in range(1, self.jump_up + 1):
                ny = y + up
                if self.standable(nx, ny, nz) and all(self.free(x, y + h, z) for h in range(self.jump_headroom)):
                    yield nx, ny, nz
                    break

    def walkable_cells(self):
        out = []
        sx, sy, sz = self.m.size
        for x in range(sx):
            for z in range(sz):
                for y in range(1, sy + 1):
                    if self.standable(x, y, z):
                        out.append((x, y, z))
        return out

    def reachable_from(self, start, limit=None):
        seen = {start}
        stack = [start]
        while stack:
            c = stack.pop()
            for n in self.neighbours(*c):
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
                    if limit and len(seen) > limit:
                        return seen
        return seen


# ------------------------------------------------------------------ seeds and generation
def resolve_seed(manifest, config):
    src = manifest["source"]
    if "seed" in src:
        return src["seed"]
    if config["seed"]["mode"] == "fixed":
        raise MapgenError(f"map {manifest['id']}: config seed.mode is 'fixed' but source.seed is missing")
    return config["seed"].get("salt", "") + ":" + manifest["id"]


class MapResult:
    def __init__(self, manifest, model, spawns, markers, seed=None, params=None, meta=None):
        self.manifest, self.model, self.spawns, self.markers = manifest, model, spawns, markers
        self.seed, self.params, self.meta = seed, params, meta or {}


class GenContext:
    """What a generator receives besides params and rng."""

    def __init__(self, config, manifest, palette, project_dir="."):
        self.config, self.manifest, self.palette, self.project_dir = config, manifest, palette, project_dir
        self.max_players = manifest["players"]["max"]


def generator_params(manifest, config, extra_plugin_dirs=()):
    src = manifest["source"]
    gen = registry.get("generators", src["generator"], config, extra_plugin_dirs)
    params = src.get("params", {})
    issues = schema.validate(params, gen.PARAMS_SCHEMA, file=f"map {manifest['id']} source.params ({gen.NAME})")
    errs = schema.errors(issues)
    if errs:
        raise MapgenError("\n".join(map(str, errs)))
    for i in issues:
        print(i, file=sys.stderr)
    return gen, schema.apply_defaults(params, gen.PARAMS_SCHEMA)


def run_generator(manifest, config, extra_plugin_dirs=(), project_dir="."):
    gen, params = generator_params(manifest, config, extra_plugin_dirs)
    seed = resolve_seed(manifest, config)
    palette = resolve_palette(params.get("palette"), config)
    out = gen.generate(params, rngmod.Rng(seed), GenContext(config, manifest, palette, project_dir))
    return out, seed, params


def generate_map(manifest, config, project_dir=".", extra_plugin_dirs=()):
    """Manifest (already schema-checked, defaults applied) -> MapResult."""
    src = manifest["source"]
    seed = params = None
    meta = {}
    if "structure" in src:
        path = os.path.join(project_dir, src["structure"])
        if not os.path.isfile(path):
            raise MapgenError(f"map {manifest['id']}: structure file {path} not found")
        model = structure_writer.read(path)
        cand, gen_markers = [], []
    else:
        out, seed, params = run_generator(manifest, config, extra_plugin_dirs, project_dir)
        model = out["model"]
        cand = [tuple(p) for p in out.get("spawns", [])]
        gen_markers = out.get("markers", [])
        meta = out.get("meta", {})
    lim = config["limits"]
    if any(s > m for s, m in zip(model.size, lim["max_size"])) or \
            model.size[0] * model.size[1] * model.size[2] > lim["max_volume"]:
        raise MapgenError(f"map {manifest['id']}: size {model.size} exceeds config limits {lim}")
    if manifest.get("spawns"):
        spawns = [tuple(p) for p in manifest["spawns"]]
    else:
        rules = manifest.get("spawn_rules", {})
        count = rules.get("count", "max_players")
        count = manifest["players"]["max"] if count == "max_players" else int(count)
        spacing = rules.get("min_spacing", config["spawns"]["min_spacing"])
        spawns = pick_spread(cand, count, spacing)
    markers = {m["id"]: dict(m) for m in gen_markers}
    for m in manifest.get("markers", []):
        markers[m["id"]] = dict(m)
    for m in markers.values():
        m.setdefault("type", "objective")
        m.setdefault("reachable", True)
        m["pos"] = list(m["pos"])
    return MapResult(manifest, model, spawns, list(markers.values()), seed, params, meta)


def pick_spread(cands, count, min_spacing):
    """Deterministic farthest-point selection of up to `count` candidates at least min_spacing apart."""
    if not cands:
        return []
    chosen = [cands[0]]
    rest = list(cands[1:])
    while rest and len(chosen) < count:
        def d2(c):
            return min((c[0] - o[0]) ** 2 + (c[2] - o[2]) ** 2 + (c[1] - o[1]) ** 2 for o in chosen)
        best = max(rest, key=lambda c: (d2(c), -cands.index(c)))
        if d2(best) < min_spacing ** 2:
            break
        chosen.append(best)
        rest.remove(best)
    return chosen


def load_manifest(path, kind):
    """Load + schema-check a manifest. kind: map|minigame|preset|pool|project. Returns (data_with_defaults, issues)."""
    data = load_json(path)
    issues = schema.validate(data, f"{kind}.schema.json", file=path)
    if schema.errors(issues):
        return None, issues
    if kind in ("map", "minigame", "project", "pool"):
        data = schema.apply_defaults(data, f"{kind}.schema.json")
    return data, issues
