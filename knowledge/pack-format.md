# pack.mcmeta and pack format (Minecraft Java 26.3)

Sources: `server/versions/26.3/server-26.3.jar!/version.json` (read 2026-10-09), vanilla feature packs
`reference/vanilla-data/minecraft/datapacks/*/pack.mcmeta`, server log probes, `tools/selftest/old_layout`.

## Facts (verified)
- Version 26.3: world_version 5023, protocol 777, Java 25 (`java_version: 25`).
- **Data pack format 121.0**, resource pack format 97.1 (`pack_version.data_major/minor`, `resource_major/minor`).
- Versioning: game versions are `<year>.<drop>[.<hotfix>]` (26.1, 26.2, 26.3); pack formats are `major.minor`
  (since 1.21.9). Earlier data formats: 1.21.9 88.0, 1.21.11 94.1, 26.1 101.1, 26.2 107.1 (wiki, unverified).

## Correct pack.mcmeta for 26.3 (verified: loads with no warning)
```json
{
  "pack": {
    "description": "My pack",
    "min_format": 121,
    "max_format": 121
  }
}
```
- `min_format` / `max_format`: int or `[major, minor]` (`[121, 0]` also loads without warning, verified).
  An int `max_format` accepts any minor version of that major.
- `description` is a text component (string or object).
- Vanilla's own feature packs use exactly `"min_format": 121, "max_format": 121`.

## Do NOT use
| Old form | What the 26.3 server does (verified) |
|---|---|
| `"pack_format": 121` alone | WARN `Pack declares support for version newer than 81, but is missing mandatory fields min_format and max_format`, falls back and still loads |
| `"min_format": 81` (<=81) without `supported_formats` | WARN `game versions supporting formats 15 to 81 require a supported_formats field` |
| `supported_formats` alone | pre-1.21.9 field; needs min/max_format for 26.3 |
| folder with no `pack.mcmeta` | `Found non-pack entry '...', ignoring` (pack silently not loaded) |

Important: the **dedicated server still enabled a pack whose range (130..131) excluded 121** (probe). So a wrong
range is not a hard error on servers, only in the client UI: the linter enforces `min <= 121 <= max`.

## Overlays (1.21.9+ form; from wiki, structure not server-tested)
```json
{"pack": {...}, "overlays": {"entries": [{"directory": "overlay_121", "min_format": 121, "max_format": 121}]}}
```
Overlay `formats` was replaced by `min_format`/`max_format` in 1.21.9 (wiki). Directory names: `[a-z0-9_.-]`.

## Feature-flag packs
Vanilla experimental packs declare `"features": {"enabled": ["minecraft:trade_rebalance"]}` at top level.
