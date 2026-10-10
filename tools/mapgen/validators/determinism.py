"""determinism: generating twice with the same seed and params gives byte-identical structure files, both
in-process (global `random` reseeded in between) and in a fresh interpreter with a different PYTHONHASHSEED
(catches set-order and hash() dependence)."""
NAME = "determinism"
DESCRIPTION = "Same seed + params -> byte-identical .nbt (in-process and in a subprocess)."
DEFAULTS = {"subprocess": True}


def validate(ctx):
    import hashlib
    import random
    if "generator" not in ctx.result.manifest["source"]:
        return [("INFO", "structure source: static file, nothing to regenerate")]
    first = ctx.structure_bytes(ctx.result.model)
    random.seed(12345)
    again = ctx.structure_bytes(ctx.regenerate().model)
    random.seed(987654321)
    if first != again:
        return [("ERROR", "regenerating in-process with the same seed gave different bytes "
                          f"({hashlib.sha1(first).hexdigest()[:10]} vs {hashlib.sha1(again).hexdigest()[:10]})")]
    if ctx.settings["subprocess"]:
        other = ctx.regenerate_subprocess()
        if other is None:
            return [("ERROR", "subprocess regeneration failed to run")]
        if other != hashlib.sha256(first).hexdigest():
            return [("ERROR", "a fresh interpreter (different PYTHONHASHSEED) produced different bytes")]
    return [("INFO", f"sha256 {hashlib.sha256(first).hexdigest()[:16]} stable")]
