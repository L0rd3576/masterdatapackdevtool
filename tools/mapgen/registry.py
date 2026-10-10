"""Plugin discovery: every .py file in the configured plugin dirs that defines NAME is a plugin.

Kinds and their required attributes:
  generators: NAME, DESCRIPTION, PARAMS_SCHEMA (JSON schema dict with defaults), generate(params, rng, ctx)
  validators: NAME, DESCRIPTION, DEFAULTS (thresholds dict), validate(ctx) -> list of (level, message)
              optional NEEDS_SERVER = True (run only by report.py / --server)
Adding a plugin = adding a file to a plugin dir (config.json plugin_dirs); core code never changes.
"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = {
    "generators": ("NAME", "DESCRIPTION", "PARAMS_SCHEMA", "generate"),
    "validators": ("NAME", "DESCRIPTION", "DEFAULTS", "validate"),
}
_loaded = {}


def discover(kind, config, extra_dirs=()):
    dirs = list(config["plugin_dirs"][kind]) + list(extra_dirs)
    key = (kind, tuple(dirs))
    if key in _loaded:
        return _loaded[key]
    found = {}
    for d in dirs:
        d = d if os.path.isabs(d) else os.path.join(ROOT, d)
        if not os.path.isdir(d):
            raise FileNotFoundError(f"plugin dir {d} (config plugin_dirs.{kind}) does not exist")
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            path = os.path.join(d, fn)
            spec = importlib.util.spec_from_file_location(f"mapgen_{kind}_{fn[:-3]}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            missing = [a for a in REQUIRED[kind] if not hasattr(mod, a)]
            if missing:
                raise TypeError(f"{path}: plugin is missing {', '.join(missing)}")
            if mod.NAME in found:
                raise ValueError(f"duplicate {kind} plugin name {mod.NAME!r}: {found[mod.NAME].__file__} and {path}")
            found[mod.NAME] = mod
    _loaded[key] = found
    return found


def get(kind, name, config, extra_dirs=()):
    plugins = discover(kind, config, extra_dirs)
    if name not in plugins:
        raise KeyError(f"unknown {kind[:-1]} {name!r}; available: {', '.join(sorted(plugins))}")
    return plugins[name]
