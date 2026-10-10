"""Small JSON Schema (draft-07 subset) validator, stdlib only.

Supported keywords: $ref (local "#/definitions/x" and "file.schema.json#/..." relative to the schema dir), type,
properties, required, additionalProperties, patternProperties, propertyNames, minProperties, maxProperties,
enum, const, minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf, minLength, maxLength, pattern,
items (schema or list), minItems, maxItems, uniqueItems, allOf, anyOf, oneOf, not, if/then/else, default.

Policy (workspace rule): unknown keys are WARNINGS (unless additionalProperties is a schema, which is then
applied); missing required keys and type/range errors are ERRORS. Every issue carries the file and JSON path.
"""
import copy
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_DIR = os.path.join(ROOT, "schemas")


class Issue:
    def __init__(self, level, file, path, message):
        self.level, self.file, self.path, self.message = level, file, path, message

    def __str__(self):
        where = self.file or "<data>"
        return f"{self.level}: {where}: {self.path or '$'}: {self.message}"

    __repr__ = __str__


_cache = {}


def load_schema(name):
    path = name if os.path.isabs(name) else os.path.join(SCHEMA_DIR, name)
    if path not in _cache:
        with open(path, encoding="utf-8") as f:
            _cache[path] = json.load(f)
    return _cache[path], path


def _resolve(ref, schema_path):
    file_part, _, frag = ref.partition("#")
    if file_part:
        base = os.path.dirname(schema_path) if schema_path else SCHEMA_DIR
        doc, schema_path = load_schema(os.path.normpath(os.path.join(base, file_part)))
    else:
        doc, _ = load_schema(schema_path) if schema_path else ({}, None)
    node = doc
    for part in [p for p in frag.split("/") if p]:
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node, schema_path


def _type_ok(v, t):
    if t == "object":
        return isinstance(v, dict)
    if t == "array":
        return isinstance(v, list)
    if t == "string":
        return isinstance(v, str)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool) or (isinstance(v, float) and v.is_integer())
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "null":
        return v is None
    return True


class Validator:
    def __init__(self, file=None):
        self.file = file
        self.issues = []

    def err(self, path, msg):
        self.issues.append(Issue("ERROR", self.file, path, msg))

    def warn(self, path, msg):
        self.issues.append(Issue("WARN", self.file, path, msg))

    def check(self, v, s, path, spath):
        if s is True or s is None:
            return
        if s is False:
            self.err(path, "no value allowed here")
            return
        if "$ref" in s:
            sub, sp = _resolve(s["$ref"], spath)
            self.check(v, sub, path, sp)
            return
        t = s.get("type")
        if t is not None:
            types = t if isinstance(t, list) else [t]
            if not any(_type_ok(v, x) for x in types):
                self.err(path, f"expected {' or '.join(types)}, got {type(v).__name__} {json.dumps(v)[:60]}")
                return
        if "enum" in s and v not in s["enum"]:
            self.err(path, f"{json.dumps(v)} is not one of {json.dumps(s['enum'])}")
        if "const" in s and v != s["const"]:
            self.err(path, f"must be {json.dumps(s['const'])}")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if "minimum" in s and v < s["minimum"]:
                self.err(path, f"{v} < minimum {s['minimum']}")
            if "maximum" in s and v > s["maximum"]:
                self.err(path, f"{v} > maximum {s['maximum']}")
            if "exclusiveMinimum" in s and v <= s["exclusiveMinimum"]:
                self.err(path, f"{v} must be > {s['exclusiveMinimum']}")
            if "exclusiveMaximum" in s and v >= s["exclusiveMaximum"]:
                self.err(path, f"{v} must be < {s['exclusiveMaximum']}")
            if "multipleOf" in s and (v / s["multipleOf"]) % 1:
                self.err(path, f"{v} is not a multiple of {s['multipleOf']}")
        if isinstance(v, str):
            if "minLength" in s and len(v) < s["minLength"]:
                self.err(path, f"string shorter than {s['minLength']}")
            if "maxLength" in s and len(v) > s["maxLength"]:
                self.err(path, f"string longer than {s['maxLength']}")
            if "pattern" in s and not re.search(s["pattern"], v):
                self.err(path, f"{json.dumps(v)} does not match /{s['pattern']}/")
        if isinstance(v, list):
            if "minItems" in s and len(v) < s["minItems"]:
                self.err(path, f"needs at least {s['minItems']} item(s), has {len(v)}")
            if "maxItems" in s and len(v) > s["maxItems"]:
                self.err(path, f"at most {s['maxItems']} item(s), has {len(v)}")
            if s.get("uniqueItems"):
                seen = []
                for i, x in enumerate(v):
                    if x in seen:
                        self.err(f"{path}[{i}]", f"duplicate item {json.dumps(x)}")
                    seen.append(x)
            items = s.get("items")
            if isinstance(items, list):
                for i, (x, sub) in enumerate(zip(v, items)):
                    self.check(x, sub, f"{path}[{i}]", spath)
            elif items is not None:
                for i, x in enumerate(v):
                    self.check(x, items, f"{path}[{i}]", spath)
        if isinstance(v, dict):
            self._object(v, s, path, spath)
        for sub in s.get("allOf", []):
            self.check(v, sub, path, spath)
        for key in ("anyOf", "oneOf"):
            if key in s:
                ok = [self._passes(v, sub, path, spath) for sub in s[key]]
                n = sum(ok)
                if n == 0:
                    titles = [sub.get("title") or sub.get("$ref") or json.dumps(sub)[:40] for sub in s[key]]
                    self.err(path, f"matches none of {key}: {', '.join(titles)}"
                             + self._best_reason(v, s[key], path, spath))
                elif key == "oneOf" and n > 1:
                    self.err(path, f"matches {n} oneOf alternatives (must match exactly one)")
        if "not" in s and self._passes(v, s["not"], path, spath):
            self.err(path, "must not match the 'not' schema")
        if "if" in s:
            if self._passes(v, s["if"], path, spath):
                if "then" in s:
                    self.check(v, s["then"], path, spath)
            elif "else" in s:
                self.check(v, s["else"], path, spath)

    def _object(self, v, s, path, spath):
        props = s.get("properties", {})
        for k in s.get("required", []):
            if k not in v:
                self.err(path, f"missing required key {k!r}")
        if "minProperties" in s and len(v) < s["minProperties"]:
            self.err(path, f"needs at least {s['minProperties']} key(s)")
        if "maxProperties" in s and len(v) > s["maxProperties"]:
            self.err(path, f"at most {s['maxProperties']} key(s)")
        pats = [(re.compile(p), sub) for p, sub in s.get("patternProperties", {}).items()]
        addl = s.get("additionalProperties", None)
        for k, x in v.items():
            kp = f"{path}.{k}" if path else k
            if "propertyNames" in s:
                self.check(k, s["propertyNames"], kp + " (key)", spath)
            matched = False
            if k in props:
                self.check(x, props[k], kp, spath)
                matched = True
            for rx, sub in pats:
                if rx.search(k):
                    self.check(x, sub, kp, spath)
                    matched = True
            if matched or k.startswith("$") or k.startswith("_comment"):
                continue
            if isinstance(addl, dict):
                self.check(x, addl, kp, spath)
            elif addl is True:
                continue
            elif props or pats or addl is not None:
                near = _near(k, list(props))
                self.warn(kp, f"unknown key {k!r}" + (f" (did you mean {near!r}?)" if near else ""))

    def _passes(self, v, sub, path, spath):
        probe = Validator(self.file)
        probe.check(v, sub, path, spath)
        return not any(i.level == "ERROR" for i in probe.issues)

    def _best_reason(self, v, alts, path, spath):
        best = None
        for sub in alts:
            probe = Validator(self.file)
            probe.check(v, sub, path, spath)
            errs = [i for i in probe.issues if i.level == "ERROR"]
            if best is None or len(errs) < len(best):
                best = errs
        return f" (closest: {best[0].path or '$'}: {best[0].message})" if best else ""


def _near(k, options):
    def dist(a, b):
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]
    best = min(options, key=lambda o: dist(k, o), default=None)
    return best if best is not None and dist(k, best) <= max(2, len(k) // 3) else None


def validate(instance, schema, file=None, schema_path=None):
    """Return a list of Issues. `schema` may be a dict or a schema file name in schemas/."""
    if isinstance(schema, str):
        schema, schema_path = load_schema(schema)
    v = Validator(file)
    v.check(instance, schema, "", schema_path)
    return v.issues


def apply_defaults(instance, schema, schema_path=None):
    """Deep copy of instance with every missing property that has a `default` filled in (recursively)."""
    if isinstance(schema, str):
        schema, schema_path = load_schema(schema)
    return _defaults(copy.deepcopy(instance), schema, schema_path)


def _defaults(v, s, spath):
    if not isinstance(s, dict):
        return v
    if "$ref" in s:
        sub, sp = _resolve(s["$ref"], spath)
        return _defaults(v, sub, sp)
    for sub in s.get("allOf", []):
        v = _defaults(v, sub, spath)
    if isinstance(v, dict):
        for k, sub in s.get("properties", {}).items():
            if k not in v and isinstance(sub, dict):
                d = _default_of(sub, spath)
                if d is not None:
                    v[k] = copy.deepcopy(d)
            if k in v:
                v[k] = _defaults(v[k], sub, spath)
        addl = s.get("additionalProperties")
        if isinstance(addl, dict):
            for k in v:
                if k not in s.get("properties", {}):
                    v[k] = _defaults(v[k], addl, spath)
    elif isinstance(v, list) and isinstance(s.get("items"), dict):
        v = [_defaults(x, s["items"], spath) for x in v]
    return v


def _default_of(s, spath):
    if "default" in s:
        return s["default"]
    if "$ref" in s:
        sub, sp = _resolve(s["$ref"], spath)
        return _default_of(sub, sp)
    return None


def errors(issues):
    return [i for i in issues if i.level == "ERROR"]
