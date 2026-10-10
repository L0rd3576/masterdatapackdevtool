#!/usr/bin/env python3
"""Generate a map from its manifest: writes <out>/<id>.nbt (26.3 structure) and <id>.meta.json.

Usage:
    python tools/mapgen/generate.py <maps/<id>.json> [--out DIR] [--project-dir DIR] [--plugin-dir DIR]
                                    [--seed S] [--hash] [--render]
--hash prints only the sha256 of the structure bytes (used by the determinism validator).
--seed overrides source.seed (explore variants; record the one you like in the manifest).
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
import pipeline  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--out")
    ap.add_argument("--project-dir")
    ap.add_argument("--plugin-dir", action="append", default=[])
    ap.add_argument("--seed")
    ap.add_argument("--hash", action="store_true")
    ap.add_argument("--render", action="store_true", help="also write top-down and layer PNGs")
    args = ap.parse_args()
    try:
        cfg = core.load_config()
        man, issues = core.load_manifest(args.manifest, "map")
        if man is None:
            print("\n".join(map(str, issues)))
            return 1
        if args.seed is not None:
            man["source"]["seed"] = int(args.seed) if args.seed.lstrip("-").isdigit() else args.seed
        project_dir = args.project_dir or os.path.dirname(os.path.dirname(os.path.abspath(args.manifest)))
        res = core.generate_map(man, cfg, project_dir, args.plugin_dir)
    except core.MapgenError as e:
        print(e)
        return 1
    data = pipeline.structure_bytes(res.model, cfg)
    if args.hash:
        print(hashlib.sha256(data).hexdigest())
        return 0
    out = args.out or os.path.join(core.ROOT, cfg["output_dir"])
    os.makedirs(out, exist_ok=True)
    nbt_path = os.path.join(out, f"{man['id']}.nbt")
    with open(nbt_path, "wb") as f:
        f.write(data)
    meta = {"id": man["id"], "size": list(res.model.size), "seed": res.seed, "params": res.params,
            "spawns": [list(s) for s in res.spawns], "markers": res.markers, "generator_meta": res.meta,
            "blocks_set": len(res.model.blocks), "sha256": hashlib.sha256(data).hexdigest()}
    with open(os.path.join(out, f"{man['id']}.meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print(f"wrote {nbt_path} size={list(res.model.size)} spawns={len(res.spawns)} markers={len(res.markers)} "
          f"seed={res.seed!r}")
    if args.render:
        import render
        for p in render.render_all(res, cfg, out):
            print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
