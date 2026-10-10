#!/usr/bin/env python3
"""Validate manifests against schemas/ and cross-check a whole project.

Usage:
    python tools/mapgen/validate.py <project-dir> [--maps]          all manifests + cross refs (+ generate maps
                                                                    and run the offline validators with --maps)
    python tools/mapgen/validate.py --kind map|minigame|preset|pool|project <file.json> ...
    python tools/mapgen/validate.py --config                        check tools/mapgen/config.json
Exit 1 on any ERROR. Unknown keys are WARN; missing required keys and bad values are ERROR (file + JSON path).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402
import pipeline  # noqa: E402
import project as projmod  # noqa: E402
import schema  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--kind", choices=["map", "minigame", "preset", "pool", "project"])
    ap.add_argument("--maps", action="store_true", help="also generate every map and run offline validators")
    ap.add_argument("--config", action="store_true")
    ap.add_argument("--plugin-dir", action="append", default=[])
    args = ap.parse_args()
    try:
        cfg = core.load_config()
    except core.MapgenError as e:
        print(e)
        print("RESULT: FAIL")
        return 1
    if args.config:
        print("config OK: tools/mapgen/config.json")
        print("RESULT: PASS")
        return 0
    issues = []
    failed = False
    if args.kind:
        for p in args.paths:
            try:
                _, iss = core.load_manifest(p, args.kind)
            except core.MapgenError as e:
                print(e)
                failed = True
                continue
            issues += iss
    else:
        for d in args.paths:
            pr = projmod.load_project(d)
            issues += pr.issues
            if args.maps and pr.ok:
                for mid, path in sorted(pr.map_paths.items()):
                    try:
                        res = core.generate_map(pr.maps[mid], cfg, pr.dir, args.plugin_dir)
                    except core.MapgenError as e:
                        print(f"map {mid}: {e}")
                        failed = True
                        continue
                    results = pipeline.run_validators(res, cfg, path, pr.dir, extra_dirs=args.plugin_dir,
                                                      base_y=pr.project["arena"]["base_y"])
                    print(f"map {mid}: {'FAIL' if pipeline.failed(results) else 'PASS'}")
                    pipeline.print_results(results)
                    failed |= pipeline.failed(results)
    for i in issues:
        print(i)
    failed |= bool(schema.errors(issues))
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({len(schema.errors(issues))} error(s), "
          f"{sum(1 for i in issues if i.level == 'WARN')} warning(s))")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
