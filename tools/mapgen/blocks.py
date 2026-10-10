"""Block-state parsing and validation against generated/reports/blocks.json (26.3 data generator output).

A compact cache (generated/mapgen-blocks.json: block -> {properties, default}) is rebuilt when blocks.json changes,
so the 7 MB report is parsed once.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOCKS_JSON = os.path.join(ROOT, "generated", "reports", "blocks.json")
CACHE = os.path.join(ROOT, "generated", "mapgen-blocks.json")

_db = None
STATE_RE = re.compile(r"^([a-z0-9_.\-]+:)?([a-z0-9_./\-]+)(\[([^\]]*)\])?$")


def db():
    global _db
    if _db is None:
        src_m = os.path.getmtime(BLOCKS_JSON)
        if os.path.exists(CACHE) and os.path.getmtime(CACHE) >= src_m:
            with open(CACHE, encoding="utf-8") as f:
                _db = json.load(f)
        else:
            with open(BLOCKS_JSON, encoding="utf-8") as f:
                raw = json.load(f)
            _db = {}
            for name, info in raw.items():
                default = next((s.get("properties", {}) for s in info["states"] if s.get("default")), {})
                _db[name] = {"properties": info.get("properties", {}), "default": default}
            with open(CACHE, "w", encoding="utf-8") as f:
                json.dump(_db, f, separators=(",", ":"))
    return _db


def parse_state(text):
    """'oak_stairs[facing=east]' -> ('minecraft:oak_stairs', {'facing': 'east'}). No validation."""
    m = STATE_RE.match(text.strip())
    if not m:
        raise ValueError(f"bad block state syntax: {text!r}")
    name = (m.group(1) or "minecraft:") + m.group(2)
    props = {}
    if m.group(4):
        for part in m.group(4).split(","):
            if not part.strip():
                continue
            k, _, v = part.partition("=")
            props[k.strip()] = v.strip()
    return name, props


def validate_state(name, props):
    """Return a list of error strings ([] if the block and its properties exist in 26.3)."""
    info = db().get(name)
    if info is None:
        return [f"unknown block {name}"]
    errs = []
    for k, v in props.items():
        if k not in info["properties"]:
            errs.append(f"{name} has no property {k!r}")
        elif v not in info["properties"][k]:
            errs.append(f"{name} does not accept {v!r} for {k} (allowed: {', '.join(info['properties'][k])})")
    return errs


def full_state(name, props):
    """Fill unspecified properties with the block's default state (vanilla structure files store full states)."""
    info = db().get(name)
    if info is None:
        raise ValueError(f"unknown block {name}")
    out = dict(info["default"])
    out.update(props)
    return {k: out[k] for k in sorted(out)}


def state_string(name, props):
    if not props:
        return name
    return name + "[" + ",".join(f"{k}={props[k]}" for k in sorted(props)) + "]"


def is_block(name):
    return name in db()
