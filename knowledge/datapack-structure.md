# Datapack layout, namespaces, resource locations, tags (26.3)

Sources: `generated/reports/datapack.json` (authoritative list of folders), `reference/vanilla-data/`,
server probes (2026-10-09), `tools/corpus/json/*` results in `generated/corpus-results.txt`.

## Layout
```
<pack>/pack.mcmeta
<pack>/data/<namespace>/function/<path>.mcfunction
<pack>/data/<namespace>/<registry>/<path>.json          e.g. loot_table/, advancement/, recipe/
<pack>/data/<namespace>/worldgen/<registry>/<path>.json e.g. worldgen/biome/
<pack>/data/<namespace>/tags/<registry>/<path>.json     e.g. tags/function/, tags/block/, tags/item/
<pack>/data/<namespace>/structure/<path>.nbt
```
- All folder names are **singular** = the registry path (since 1.21). `functions/`, `loot_tables/`,
  `tags/functions/`, `tags/items/` ... are **silently ignored** by 26.3 (verified: no log message at all).
- Full list of valid folders: `python -c "import json;d=json.load(open('generated/reports/datapack.json'));print([k for k,v in d['registries'].items() if v['elements']])"`.
  `elements: true` = you may add files; `tags: true` = `tags/<registry>/` allowed; `stable: false` = experimental-ish.
- Element folders (26.3): advancement, banner_pattern, block_transformer, cat_sound_variant, cat_variant, chat_type,
  chicken_sound_variant, chicken_variant, context_float_provider, context_int_provider, cow_sound_variant, cow_variant,
  damage_type, decorated_pot_pattern, dialog, dimension, dimension_type, enchantment, enchantment_provider,
  frog_variant, instrument, item_modifier, jukebox_song, loot_table, painting_variant, pig_sound_variant, pig_variant,
  predicate, recipe, slot_source, sulfur_cube_archetype, test_environment, test_instance, timeline, trade_set,
  trial_spawner, trim_material, trim_pattern, villager_trade, wolf_sound_variant, wolf_variant, world_clock,
  zombie_nautilus_variant, worldgen/{biome, block_state_provider, carver, density_function, feature,
  flat_level_generator_preset, material_condition, material_rule, multi_noise_biome_source_parameter_list, noise,
  noise_settings, placed_feature, processor_list, structure, structure_set, template_pool, world_preset},
  plus `function` (.mcfunction) and `structure` (.nbt).
- Removed/renamed in 26.3: `worldgen/configured_feature` -> `worldgen/feature`, `worldgen/configured_carver` ->
  `worldgen/carver` (datapack.json); no `number_provider` folder (now `context_int_provider`/`context_float_provider`).

## Namespaces and resource locations
- Namespace: `[a-z0-9_.-]`. Path: `[a-z0-9_.-/]`. One `:`; missing namespace means `minecraft:`.
- **Uppercase namespace folder (`data/Probe/`) is silently ignored** (verified). Same for bad characters in paths.
- Use your own namespace; put only tag files (e.g. `minecraft/tags/function/load.json`) under `minecraft/`.

## Tags
```json
{"values": ["minecraft:diamond", "#minecraft:planks", {"id": "other:x", "required": false}], "replace": false}
```
- Tag folders: `tags/<registry>` for every registry with `tags: true` (block, item, entity_type, fluid, game_event,
  damage_type, enchantment, function, worldgen/biome, ...).
- Missing required entry in a **function** tag: `ERROR Couldn't load tag minecraft:load as it is missing following
  references: t:also_missing` - the server still starts, the tag is dropped (so *none* of its functions run).
- Missing entry in an **item** tag: same message, tag dropped (verified with `tags/item/bad_ref.json`).

## Load behavior (verified by probes)
- Element JSON errors (advancement, loot_table, recipe, predicate, item_modifier, ...) abort server start:
  `Registry loading errors: > Errors in registry minecraft:loot_table: >> Errors in element ns:id` then
  `Failed to load datapacks, can't proceed with server load`. Files are parsed with a strict JSON parser
  (no comments, no trailing commas).
- Function parse errors do NOT abort: `ERROR Failed to load function ns:id` + first error only
  (`Whilst parsing command on line N: ...<--[HERE]`). The function then does not exist (`Unknown function`).
- Unknown keys in JSON are often **silently ignored** (e.g. old `functions`/`conditions` in loot tables) but missing
  required keys are errors (`No key functions in MapLike[...]`).
- New packs found in `world/datapacks/` are enabled automatically on server start (`Found new data pack file/x`).
