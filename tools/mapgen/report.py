#!/usr/bin/env python3
"""One-command map report: generate from the manifest(s), run every validator (including the real-server load
check), render PNGs + ASCII, and print pass/fail with the render paths. Exit 1 if any map fails.

Usage:
    python tools/mapgen/report.py <maps/<id>.json> [more manifests...] [--no-server] [--out DIR]
                                  [--project-dir DIR] [--plugin-dir DIR]
    python tools/mapgen/report.py --project <project-dir>     (every map of a framework project)
Review the top-down PNG with the Read tool before accepting a map (skill map-authoring).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
import pipeline  # noqa: E402
import render  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifests", nargs="*")
    ap.add_argument("--project")
    ap.add_argument("--no-server", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--project-dir")
    ap.add_argument("--plugin-dir", action="append", default=[])
    args = ap.parse_args()
    cfg = core.load_config()
    out_dir = args.out or os.path.join(core.ROOT, cfg["output_dir"])
    paths = list(args.manifests)
    base_y = None
    project_dir = args.project_dir
    if args.project:
        import project as projmod
        pr = projmod.load_project(args.project)
        for i in pr.issues:
            print(i)
        if not pr.ok:
            print("RESULT: FAIL (project manifests have errors)")
            return 1
        paths = [pr.map_paths[m] for m in sorted(pr.map_paths)]
        project_dir, base_y = pr.dir, pr.project["arena"]["base_y"]
    if not paths:
        ap.error("give manifests or --project")
    loaded, failed = [], False
    for p in paths:
        try:
            man, res = pipeline.load_map(p, cfg, project_dir, args.plugin_dir)
            loaded.append((p, res))
        except core.MapgenError as e:
            print(f"== {p}: FAIL (cannot generate)\n{e}")
            failed = True
    server = None
    if loaded and not args.no_server:
        import server_check
        server = server_check.MapServer([r for _, r in loaded], cfg)
        try:
            server.start()
        except RuntimeError as e:
            print(f"server check unavailable: {e}")
            failed = True
            server = None
    try:
        for p, res in loaded:
            mid = res.manifest["id"]
            pd = project_dir or os.path.dirname(os.path.dirname(os.path.abspath(p)))
            results = pipeline.run_validators(res, cfg, os.path.abspath(p), pd, server=server,
                                              extra_dirs=args.plugin_dir, base_y=base_y)
            renders = render.render_all(res, cfg, out_dir)
            nbt_path = os.path.join(out_dir, f"{mid}.nbt")
            with open(nbt_path, "wb") as f:
                f.write(pipeline.structure_bytes(res.model, cfg))
            bad = pipeline.failed(results)
            failed |= bad
            sx, sy, sz = res.model.size
            print(f"== {mid}: {'FAIL' if bad else 'PASS'}  size {sx}x{sy}x{sz}, {len(res.spawns)} spawns, "
                  f"{len(res.markers)} markers, seed {res.seed!r}")
            pipeline.print_results(results)
            for r in [nbt_path] + renders:
                print(f"   file  {os.path.relpath(r, core.ROOT)}")
    finally:
        if server:
            server.stop()
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({len(paths)} map(s))")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
