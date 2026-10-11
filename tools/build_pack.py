#!/usr/bin/env python3
"""Compile a framework project (project.json, minigames/, maps/, presets/, pool.json) into a 26.3 datapack.

Usage:
    python tools/build_pack.py <project-dir> [--out DIR] [--no-validate] [--plugin-dir DIR] [--adopt]

Steps: schema + cross-reference checks (tools/mapgen/project.py) -> generate/load every enabled pool map and
run the offline map validators -> copy the framework (tools/framework/pack, placeholders __ns__/__lib__/...)
-> vendor mcdp_lib -> write runtime data (storage <ns>:registry), map structure tiles, the arena dimension,
minigame hook functions, project load/tick tags (#<ns>:extra_load/extra_tick), gallery functions and tests
-> copy the project's pack_src overlay last (a file the build already wrote is an error).
Afterwards run tools/lint_datapack.py and tools/run_tests.py on the output. Contract: knowledge/framework-contract.md.

project.json output_mode: "replace" (default) deletes and rewrites the whole output dir, but only one that
build_pack created (marker .built_by_build_pack). "merge" rewrites only data/, tests/, pack.mcmeta and
.build_pack_owned and keeps every other file (docs, the project dir itself). A merge output that has data/
but no .build_pack_owned is refused unless --adopt is given (then its data/, tests/, pack.mcmeta are replaced).
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mapgen"))
sys.path.insert(0, HERE)
import core  # noqa: E402
import gallery  # noqa: E402
import new_project  # noqa: E402
import pipeline  # noqa: E402
import project as projmod  # noqa: E402
import structure_writer  # noqa: E402

FRAMEWORK = os.path.join(HERE, "framework", "pack")
MARKER = ".built_by_build_pack"
OWNED = ".build_pack_owned"
MERGE_OWNED = ("data", "tests", "pack.mcmeta", OWNED)
SNBT_KEY = re.compile(r"^[A-Za-z0-9_.+-]+$")


# ------------------------------------------------------------------ SNBT
def snbt(v):
    if isinstance(v, bool):
        return "1b" if v else "0b"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v) + "d"
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, dict):
        return "{" + ",".join((k if SNBT_KEY.match(k) else snbt(k)) + ":" + snbt(x) for k, x in v.items()) + "}"
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(snbt(x) for x in v) + "]"
    if v is None:
        raise ValueError("None has no SNBT form")
    raise TypeError(type(v))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------ compile pieces
def rules_lib(rules):
    """Manifest rules -> mcdp_lib:rules/apply struct (see library/INDEX.md rules/apply)."""
    gm = rules["gamemode"]
    if gm == "auto":
        gm = "survival" if (rules["block_break"] or rules["block_place"]) else "adventure"
    out = {"gamemode": gm, "pvp": rules["pvp"], "keep_inventory": rules["keep_inventory"],
           "natural_regeneration": rules["natural_regeneration"], "fall_damage": rules["fall_damage"]}
    if not rules["block_break"] and gm == "survival":
        out["block_break"] = False
    effects = [{"id": e["id"], "duration": e.get("duration", "infinite"), "amplifier": e.get("amplifier", 0),
                "hide": e.get("hide", True)} for e in rules["effects"]]
    if not rules["hunger"]:
        effects.append({"id": "minecraft:saturation", "duration": "infinite", "amplifier": 0, "hide": True})
    if effects:
        out["effects"] = effects
    return out


def game_entry(g, presets, pool_entry):
    variants = {}
    names = (["default"] if pool_entry.get("include_default", True) or not pool_entry.get("presets") else []) + \
        [p["id"] for p in pool_entry.get("presets", [])]
    for name in names:
        settings = {k: s["default"] for k, s in g["settings"].items()}
        rules = dict(g["rules"])
        if name != "default":
            settings.update(presets[name]["settings"])
            rules.update(presets[name].get("rules", {}))
        variants[name] = {"settings": settings, "rules": rules, "rules_lib": rules_lib(rules)}
    return {"id": g["id"], "name": g["display_name"], "players": g["players"], "win": g["win_condition"],
            "payout": g["payout"], "variants": variants}


def map_entry(ns, res, slot, pr, tile_size):
    a = pr.project["arena"]
    m = res.manifest
    ox = a["slot_origin"][0] + slot * a["slot_spacing"]
    oy, oz = a["base_y"], a["slot_origin"][1]
    dim = f"{ns}:{a['dimension']}"
    tiles = []
    for i, ((x0, y0, z0), _) in enumerate(structure_writer.tiles(res.model.size, tile_size)):
        tiles.append({"t": f"{ns}:map/{m['id']}/t{i}", "x": ox + x0, "y": oy + y0, "z": oz + z0})
    sx, sy, sz = res.model.size
    return {
        "id": m["id"], "name": m["display_name"], "tags": m["tags"], "players": m["players"],
        "origin": {"x": ox, "y": oy, "z": oz}, "size": [sx, sy, sz],
        "box": {"x": ox, "y": oy, "z": oz, "dx": sx - 1, "dy": sy - 1, "dz": sz - 1, "dimension": dim},
        "spawns": [{"x": ox + x + 0.5, "y": float(oy + y), "z": oz + z + 0.5, "dimension": dim} for x, y, z in res.spawns],
        "markers": [{"id": k["id"], "type": k["type"], "x": ox + k["pos"][0], "y": oy + k["pos"][1],
                     "z": oz + k["pos"][2]} for k in res.markers],
        "tiles": tiles, "needs_restore": m["needs_restore"], "tag_meta": m["tag_meta"],
    }


def by_count(pr):
    out = {}
    lo, hi = pr.project["players"]["min"], pr.project["players"]["max"]
    for n in range(lo, hi + 1):
        cands = projmod.candidates(pr, n)
        out[f"n{n}"] = [{"weight": max(1, round(w * 100)), "value": {"game": g, "map": mp, "preset": p or "default"}}
                        for g, p, mp, w in cands]
    return out


def _inside(path, parent):
    path, parent = os.path.normcase(os.path.abspath(path)), os.path.normcase(os.path.abspath(parent))
    return path == parent or path.startswith(parent.rstrip(os.sep) + os.sep)


def prepare_output(out, mode, adopt, keep_dirs):
    """Empty the parts of `out` the build owns. keep_dirs: source dirs that must not lie in a deleted part."""
    if mode == "replace":
        # only ever delete a dir this tool created (and never one holding the project)
        for d in keep_dirs:
            if _inside(d, out):
                raise core.MapgenError(f"{d} lies inside the output {out}, which a replace build deletes; "
                                       "use output_mode \"merge\" or another output dir")
        if os.path.exists(out):
            if not os.path.isfile(os.path.join(out, MARKER)):
                if os.listdir(out):
                    raise core.MapgenError(f"{out} exists, is not empty and was not created by build_pack; refusing to delete")
            shutil.rmtree(out)
        return
    for name in ("data", "tests"):
        for d in keep_dirs:
            if _inside(d, os.path.join(out, name)):
                raise core.MapgenError(f"{d} lies inside {os.path.join(out, name)}, which a merge build deletes; "
                                       "move the project (or its tests/pack_src dir) elsewhere")
    if os.path.isdir(os.path.join(out, "data")) and not os.path.isfile(os.path.join(out, OWNED)) \
            and not os.path.isfile(os.path.join(out, MARKER)) and not adopt:
        raise core.MapgenError(f"{out} has data/ but no {OWNED} (not built by build_pack in merge mode); refusing to "
                               "touch it. Pass --adopt to take it over: its data/, tests/ and pack.mcmeta are replaced")
    for name in MERGE_OWNED + (MARKER,):
        p = os.path.join(out, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    write(os.path.join(out, OWNED), "Merge build by tools/build_pack.py: data/, tests/, pack.mcmeta and this file are "
                                    "deleted and rewritten on every build. Other files here are left alone.\n")


def overlay(out, src_dir, tokens):
    """Copy the pack_src tree over the built pack; tokens are replaced in paths and .mcfunction/.json text."""
    todo, clash = [], []
    for dp, _, fns in os.walk(src_dir):
        for fn in sorted(fns):
            src = os.path.join(dp, fn)
            rel = os.path.relpath(src, src_dir)
            for k, v in tokens.items():
                rel = rel.replace(k, v)
            dest = os.path.join(out, rel)
            if os.path.exists(dest):
                clash.append(f"   {src}\n      would override {dest}")
            todo.append((src, dest))
    if clash:
        raise core.MapgenError("pack_src overlay collides with files the build wrote (rename or remove them; "
                               "framework files are never overridden):\n" + "\n".join(clash))
    for src, dest in todo:
        if dest.endswith((".mcfunction", ".json")):
            text = open(src, encoding="utf-8").read()
            for k, v in tokens.items():
                text = text.replace(k, v)
            write(dest, text)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
    return len(todo)


def build(project_dir, out=None, validate=True, extra_dirs=(), adopt=False):
    cfg = core.load_config()
    pr = projmod.load_project(project_dir)
    for i in pr.issues:
        print(i)
    if not pr.ok:
        raise core.MapgenError("project has errors; nothing built")
    P = pr.project
    ns, lib = P["namespace"], P["lib_prefix"]
    if ns in ("minecraft", lib):
        raise core.MapgenError(f"namespace {ns!r} clashes with minecraft or the library prefix")
    out = os.path.abspath(out or os.path.join(pr.dir, P["output"]))
    tests = os.path.join(pr.dir, P["tests"])
    pack_src = os.path.join(pr.dir, P["pack_src"]) if P.get("pack_src") else None
    if pack_src and not os.path.isdir(pack_src):
        raise core.MapgenError(f"pack_src dir {pack_src} not found")

    # maps: generate + validate (offline validators; the server check is the pack's own test run)
    pool_maps = [e["id"] for e in pr.pool["maps"] if e["enabled"]]
    results, failed = {}, False
    for mid in pool_maps:
        res = core.generate_map(pr.maps[mid], cfg, pr.dir, extra_dirs)
        results[mid] = res
        if validate:
            vr = pipeline.run_validators(res, cfg, pr.map_paths[mid], pr.dir, extra_dirs=extra_dirs,
                                         base_y=P["arena"]["base_y"])
            print(f"map {mid}: {'FAIL' if pipeline.failed(vr) else 'PASS'} ({res.model.size[0]}x{res.model.size[1]}x"
                  f"{res.model.size[2]}, {len(res.spawns)} spawns)")
            if pipeline.failed(vr):
                pipeline.print_results([r for r in vr if r[1] == "ERROR"])
                failed = True
            largest = max(res.model.size[0], res.model.size[2]) + P["arena"]["slot_margin"]
            if largest > P["arena"]["slot_spacing"]:
                print(f"   ERROR map {mid} ({largest} with margin) is wider than arena.slot_spacing {P['arena']['slot_spacing']}")
                failed = True
    if failed:
        raise core.MapgenError("map validation failed; nothing built (use --no-validate to force)")

    # output dir: replace = whole dir, merge = only data/, tests/, pack.mcmeta (see the docstring)
    mode = P["output_mode"]
    prepare_output(out, mode, adopt, [pr.dir, tests] + ([pack_src] if pack_src else []))
    tokens = {"__ns__": ns, "__lib__": lib, "__arena__": P["arena"]["dimension"],
              "__currency__": P["currency"]["objective"], "__currency_name__": P["currency"]["display_name"]}
    for dp, _, fns in os.walk(FRAMEWORK):
        for fn in fns:
            src = os.path.join(dp, fn)
            rel = os.path.relpath(src, FRAMEWORK)
            for k, v in tokens.items():
                rel = rel.replace(k, v)
            text = open(src, encoding="utf-8").read()
            for k, v in tokens.items():
                text = text.replace(k, v)
            write(os.path.join(out, rel), text)
    if mode == "replace":
        write(os.path.join(out, MARKER), "This directory is generated by tools/build_pack.py and deleted on rebuild.\n")
    write(os.path.join(out, "pack.mcmeta"), json.dumps(
        {"pack": {"description": P["description"], "min_format": 121, "max_format": 121}}, indent=2) + "\n")
    new_project.vendor(out, lib)
    # set_tag drops every *:_internal/<tag> entry unless it is passed as `first`: keep the library first
    new_project.set_tag(out, "load", f"{lib}:_internal/load", f"{ns}:load")
    new_project.set_tag(out, "tick", f"{lib}:_internal/tick", f"{ns}:tick")
    data = os.path.join(out, "data", ns)

    # arena dimension (void flat world; shape verified on 26.3, knowledge/mapgen.md)
    write(os.path.join(data, "dimension", P["arena"]["dimension"] + ".json"), json.dumps({
        "type": P["arena"]["dimension_type"],
        "generator": {"type": "minecraft:flat", "settings": {
            "biome": P["arena"]["biome"], "features": False, "lakes": False, "layers": []}}}, indent=2) + "\n")

    # structures (tiles) + registry
    tile = cfg["placement"]["tile_size"]
    vol = tile[0] * tile[1] * tile[2]
    tpt = P["placement"].get("tiles_per_tick") or max(1, cfg["placement"]["max_blocks_per_tick"] // vol)
    maps = {}
    for slot, mid in enumerate(pool_maps):
        res = results[mid]
        for i, (a, b) in enumerate(structure_writer.tiles(res.model.size, tile)):
            p = os.path.join(data, "structure", "map", mid, f"t{i}.nbt")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            structure_writer.write(res.model, p, cfg["structure"]["fill_air"], (a, b))
        maps[mid] = map_entry(ns, res, slot, pr, tile)
    games = {}
    for e in pr.pool["minigames"]:
        if e["enabled"]:
            games[e["id"]] = game_entry(pr.minigames[e["id"]], pr.presets, e)
    lines = ["# generated by tools/build_pack.py - do not edit; source: the project's JSON manifests",
             f"scoreboard players set #tiles_per_tick {ns}.cfg {tpt}",
             f"scoreboard players set #end_delay {ns}.cfg {P['end_delay_ticks']}",
             f"scoreboard players set #min_players {ns}.cfg {P['players']['min']}",
             f"scoreboard players set #max_players {ns}.cfg {P['players']['max']}",
             f"data modify storage {ns}:registry games set value {{}}",
             f"data modify storage {ns}:registry maps set value {{}}"]
    for gid, g in games.items():
        lines.append(f"data modify storage {ns}:registry games.{gid} set value {snbt(g)}")
    for mid, m in maps.items():
        lines.append(f"data modify storage {ns}:registry maps.{mid} set value {snbt(m)}")
    lines.append(f"data modify storage {ns}:registry by_count set value {snbt(by_count(pr))}")
    write(os.path.join(data, "function", "_gen", "registry.mcfunction"), "\n".join(lines) + "\n")

    # forceload every map slot (chunks) in the arena dimension
    fl = ["# generated: keep map slots loaded (place template fails in unloaded chunks: 'That position is not loaded')"]
    for m in maps.values():
        b = m["box"]
        fl.append(f"execute in {ns}:{P['arena']['dimension']} run forceload add {b['x']} {b['z']} "
                  f"{b['x'] + b['dx']} {b['z'] + b['dz']}")
    write(os.path.join(data, "function", "_gen", "forceload.mcfunction"), "\n".join(fl) + "\n")

    # minigame hooks: copy the project's files, stub the rest
    hl = ["# generated: run every minigame's load hook"]
    for gid in games:
        g = pr.minigames[gid]
        for hook in projmod.HOOKS:
            dest = os.path.join(data, "function", "game", gid, hook + ".mcfunction")
            if hook in g["functions"]:
                text = open(os.path.join(pr.dir, g["functions"][hook]), encoding="utf-8").read()
                write(dest, text.replace("__ns__", ns).replace("__lib__", lib))
            else:
                write(dest, f"# {gid}: no '{hook}' hook in the manifest (framework stub)\nreturn 0\n")
        hl.append(f"function {ns}:game/{gid}/load")
    write(os.path.join(data, "function", "_gen", "hooks_load.mcfunction"), "\n".join(hl) + "\n")

    # project load/tick functions: framework load ends with function #<ns>:extra_load, tick starts with extra_tick
    for kind in ("load", "tick"):
        write(os.path.join(data, "tags", "function", f"extra_{kind}.json"),
              json.dumps({"values": P["functions"][kind]}, indent=2) + "\n")

    if P["gallery"]:
        gallery.write_functions(out, ns, P, maps, cfg)

    if os.path.isdir(tests):
        shutil.copytree(tests, os.path.join(out, "tests"))
    n_overlay = overlay(out, pack_src, {"__ns__": ns, "__lib__": lib}) if pack_src else 0
    missing = [f for kind in ("load", "tick") for f in P["functions"][kind]
               if not os.path.isfile(os.path.join(out, "data", f.split(":")[0], "function", f.split(":")[1] + ".mcfunction"))]
    if missing:
        raise core.MapgenError(f"project.json functions not found in the built pack: {', '.join(missing)}")
    print(f"built {out} ({mode}): {len(games)} minigame(s), {len(maps)} map(s), "
          f"{sum(len(m['tiles']) for m in maps.values())} structure tile(s), {tpt} tile(s)/tick, "
          f"{n_overlay} pack_src file(s)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--out")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--plugin-dir", action="append", default=[])
    ap.add_argument("--adopt", action="store_true",
                    help="merge mode: take over an output dir with data/ but no .build_pack_owned")
    args = ap.parse_args()
    try:
        out = build(args.project, args.out, not args.no_validate, args.plugin_dir, args.adopt)
    except core.MapgenError as e:
        print(f"FAIL: {e}")
        return 1
    print(f"next: python tools/lint_datapack.py \"{out}\" && python tools/run_tests.py \"{out}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
