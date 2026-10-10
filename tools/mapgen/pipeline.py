"""Manifest -> MapResult -> validator results. Used by generate.py, validate.py, report.py and build_pack.py."""
import hashlib
import os
import subprocess
import sys

import core
import nbt
import registry
import structure_writer

HERE = os.path.dirname(os.path.abspath(__file__))


def structure_bytes(model, config):
    return nbt.gzip_bytes(nbt.dumps(structure_writer.to_nbt(model, config["structure"]["fill_air"])))


def load_map(path, config, project_dir=None, extra_dirs=()):
    """Load, schema-check and generate one map manifest. Raises core.MapgenError with all errors."""
    man, issues = core.load_manifest(path, "map")
    errs = [i for i in issues if i.level == "ERROR"]
    if errs:
        raise core.MapgenError("\n".join(map(str, errs)))
    for i in issues:
        print(i, file=sys.stderr)
    project_dir = project_dir or os.path.dirname(os.path.dirname(os.path.abspath(path)))
    return man, core.generate_map(man, config, project_dir, extra_dirs)


class ValidationContext:
    def __init__(self, result, config, settings, manifest_path, project_dir, extra_dirs=(), server=None):
        self.result, self.config, self.settings = result, config, settings
        self.manifest_path, self.project_dir, self.extra_dirs, self.server = manifest_path, project_dir, extra_dirs, server

    def structure_bytes(self, model):
        return structure_bytes(model, self.config)

    def regenerate(self):
        return core.generate_map(self.result.manifest, self.config, self.project_dir, self.extra_dirs)

    def regenerate_subprocess(self):
        cmd = [sys.executable, os.path.join(HERE, "generate.py"), self.manifest_path, "--hash",
               "--project-dir", self.project_dir]
        for d in self.extra_dirs:
            cmd += ["--plugin-dir", d]
        env = dict(os.environ, PYTHONHASHSEED=str(int(hashlib.sha1(self.manifest_path.encode()).hexdigest(), 16) % 4000000 + 7))
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(r.stderr[-2000:], file=sys.stderr)
            return None
        return r.stdout.strip().splitlines()[-1]


def run_validators(result, config, manifest_path, project_dir, server=None, extra_dirs=(), only=None,
                   base_y=None):
    """-> list of (validator_name, level, message). Validators listed in config validators.enabled run in order;
    a manifest `validation: {name: false}` skips one, `{name: {...}}` overrides its thresholds."""
    plugins = registry.discover("validators", config)
    out = []
    per_map = result.manifest.get("validation", {})
    for name in config["validators"]["enabled"]:
        if only and name not in only:
            continue
        if name not in plugins:
            out.append((name, "ERROR", f"validator {name!r} (config validators.enabled) has no plugin"))
            continue
        v = plugins[name]
        if per_map.get(name) is False:
            out.append((name, "SKIP", "disabled by the map manifest"))
            continue
        if getattr(v, "NEEDS_SERVER", False) and server is None:
            out.append((name, "SKIP", "needs a server (run tools/mapgen/report.py)"))
            continue
        settings = dict(v.DEFAULTS)
        settings.update(config["validators"].get("settings", {}).get(name, {}))
        if isinstance(per_map.get(name), dict):
            settings.update(per_map[name])
        if base_y is not None and "base_y" in settings:
            settings["base_y"] = base_y
        ctx = ValidationContext(result, config, settings, manifest_path, project_dir, extra_dirs, server)
        try:
            res = v.validate(ctx) or []
        except Exception as e:  # a crashing validator is a failure, never a silent pass
            res = [("ERROR", f"validator crashed: {type(e).__name__}: {e}")]
        if not any(lvl == "ERROR" for lvl, _ in res):
            out.append((name, "PASS", "; ".join(m for lvl, m in res if lvl in ("INFO", "WARN")) or ""))
        for lvl, msg in res:
            if lvl in ("ERROR", "WARN"):
                out.append((name, lvl, msg))
    return out


def failed(results):
    return any(lvl == "ERROR" for _, lvl, _ in results)


def print_results(results, indent="   "):
    for name, lvl, msg in results:
        print(f"{indent}{lvl:5} {name}{': ' + msg if msg else ''}")
